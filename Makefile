up:
	docker compose up -d --build --remove-orphans

down:
	docker compose down --remove-orphans

.PHONY: config
config:
	docker cp config/ meshtoaprs:/
	docker restart meshtoaprs

restart: 
	docker restart meshtoaprs
