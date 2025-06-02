.PHONY: test test-local test-docker build up down logs

test:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

test-local:
	pytest tests/ --disable-warnings -v

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f
