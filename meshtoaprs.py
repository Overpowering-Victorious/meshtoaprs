import paho.mqtt.client as mqtt
from time import sleep, gmtime, strftime
import json
import yaml
import socket

def yml_load(file):
    try:
        with open(file) as fh:
            yaml_data = yaml.safe_load(fh)
            return yaml_data

    except:
        print(f"Unable to open {file} config file, will try it again in 1 minute.")
        sleep(60)
        exit(1)

def aprs_msg_create(node, loc, temp, hum, pres):
    timestamp = strftime("%d%H%M", gmtime())
    
    msg = "@" + timestamp + "z" + loc + "_"
    msg = msg + ".../...g..."
    msg = msg + "t" + format(temp, "02.0f")
    msg = msg + "r...p...P..."
    msg = msg + "h" + format(hum, "03d") + "b" + format(pres * 10, "05d") 
    msg = msg + "Meshtastic:" + str(node)

    return msg

def aprs_send(sock, ssid, msg):
    print(f"APRS message: {msg}")

    frame = ssid + ">APRS,TCPIP*:" + msg + "\n\r"
    sock.send(frame.encode())
    server_return = sock.recv(1024)
    server_return = server_return.decode("utf-8", "strict")
    server_return = server_return.rstrip()
    
    print(f"Server replay: {server_return}")
    
def aprs_connect(server, port, call, password):
    try:
        addr_info = socket.getaddrinfo(server, port)
        sock = socket.socket(*addr_info[0][0:3])

        # Connect to APRSIS
        print(f"Connect to: {addr_info[0][4][0]}:{port}")
        sock.connect(addr_info[0][4])
        server_hello = sock.recv(1024)
        server_hello = server_hello.decode("utf-8", "strict")
        server_hello = server_hello.rstrip()
        print(f"Connect Result: {server_hello}")

        # Auth to APRSIS
        auth = "user " + str(call) + " pass " + str(password) + "\n\r"
        sock.send(auth.encode())
        server_return = sock.recv(1024)
        server_return = server_return.decode("utf-8", "strict")
        server_return = server_return.rstrip()
        print(f"Auth Result: {server_return}")

        return sock

    except socket.error as ex:
        print(f"Error when connecting to {server}:{port}: {str(ex)}")

def aprs_disconnect(sock):
    sock.close()
    print("Connection closed.\n")

def mqtt_on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect to {mqtt_server}:{mqtt_port}: {reason_code}.")

        exit(1)
    else:
        print(f"Connected to: {mqtt_server}:{mqtt_port} with result code {reason_code}")
        client.subscribe(mqtt_topic)

def mqtt_on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def mqtt_on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    if data["type"] == "telemetry":
        mesh_node = data["from"]
        if mesh_node in nodes and "temperature" in data["payload"]:
            
            ssid = nodes[mesh_node]["ssid"]
            loc = nodes[mesh_node]["loc"]
            elev = nodes[mesh_node]["elev"]

            temp_c = round(data["payload"]["temperature"],1)
            temp_f = round((temp_c * 1.8)+32)
            hum = round(data["payload"]["relative_humidity"])
            pres_abs = round(data["payload"]["barometric_pressure"])
            pres_rel = round(pres_abs / ((273.15 + temp_c - 0.0065 * elev) / (273.15 + temp_c))**5.255)

            print(f"Mesh node: {mesh_node}: temperatue: {temp_c}, humidity: {hum}, pressure: {pres_rel}")

            aprs_msg = aprs_msg_create(mesh_node, loc, temp_f, hum, pres_rel)
            aprs_socket = aprs_connect(aprs_server, aprs_port, aprs_call, aprs_pass)
            aprs_send(aprs_socket, ssid, aprs_msg)
            aprs_disconnect(aprs_socket)

# load configuration
config = yml_load("/config/config.yml")

try:
    mqtt_server = config["mqtt_server"]
    mqtt_port = config["mqtt_port"]
    mqtt_topic = config["mqtt_topic"]

    aprs_server = config["aprs_server"]
    aprs_port = config["aprs_port"]
    aprs_call = config["aprs_call"]
    aprs_pass = config["aprs_pass"]
except:
    print(f"Missing mandatory configuration in config.yml, will try it again in 1 minute.")
    time.sleep(60)
    exit(1)

# Load nodes database
nodes = yml_load("/config/nodes.yml")

# Open connection to MQTT broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = mqtt_on_message
mqtt_client.on_connect = mqtt_on_connect
mqtt_client.on_subscribe = mqtt_on_subscribe

mqtt_client.connect(mqtt_server, mqtt_port, 60)

# Loop
mqtt_client.loop_forever()
