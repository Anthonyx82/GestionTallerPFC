.PHONY: test test-local test-docker build up down logs

# Ejecutar tests usando Docker Compose de testing
test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Ejecutar tests localmente en tu máquina (requiere venv + dependencias instaladas)
test-local:
	pytest tests/ --disable-warnings -v

# Comandos auxiliares del entorno normal (producción/dev)
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f
