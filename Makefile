all: test

build: 
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

run-prod: 
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

build-test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d --build

run-test: 
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up

test: 
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run app pytest /tests


