.PHONY: run stop build migrate superuser shell logs restart test makemigrations

run:
	docker compose up

build:
	docker compose up --build

stop:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web

restart:
	docker compose restart web

test:
	docker compose exec web python manage.py test
