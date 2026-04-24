.PHONY: up down build shell migrate createsuperuser test

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

shell:
	docker-compose exec -it django python manage.py shell

migrate:
	docker-compose run --rm django python manage.py migrate

makemigrations:
	docker-compose run --rm django python manage.py makemigrations

createsuperuser:
	docker-compose run --rm django python manage.py createsuperuser

test:
	docker-compose run --rm django pytest
