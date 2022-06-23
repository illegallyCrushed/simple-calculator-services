SERVICES := gateway result user celery spawner

build-base:
	docker build -t simple-calculator-base .

build: build-base
	for service in $(SERVICES); do make -C ./services/$$service build-image; done
	