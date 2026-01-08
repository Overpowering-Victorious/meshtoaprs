# MeshToAPRS Gateway
MeshToAPRS is a gateway solution which allow to send weather information from Mestastic network to APRS network.
Whole solution is based on Docker containers to be able to use it as a one building block for biger projects.

## Prerequisits
Server with installed docker environment connected to Internet.

## Architecture
Gateway acts a MQTT client connected to MQTT broker. Broker itself is not part of the project. It has to be configured to be subscribed on primary channel (such as MediumFast) which is used for weather information transport. On the other site it uses TCP connection to APRS server to inject wether information into APRS Network. 

## Operation tests
It is tested on RPi3 with Debian Buster on top of it. All test were done with Mosquitto broker running in container on the same host.

## Building
Almost everything is automated via docker compose. You just need to download the project and run docker compose build and GNU make.
```
git clone https://github.com/saidlm/meshtoaprs
cd meshtoaprs
make up
```
## Configuration
There are two configuration file config.yml and nodes.yml which needs to be created in advance and ready in config directory. You can see examples in config.example. As soon as container is ready make config command can be used to apply the config files.

## Running
Build and start container:
```
make up
```

Stop container:
```
make down
```

Restart container:
```
make restart
```

Copy confiuration from host into container and restart container:
```
make config
```

Logs:
```
docker compose logs
```
