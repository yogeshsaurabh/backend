init_db:
	docker run --name evolve-db -e MYSQL_ROOT_PASSWORD=admin -p 127.0.0.1:5432:3306 -d mysql
build_server:
	docker build -t evolve-server .
start_server:
	docker run --rm --env-file .env -e DATABASE_URL='mysql://root:admin@localhost:5432/evolve' evolve-server

prisma_init:
	prisma generate
	prisma db push

remove_db: stop_db
	docker container prune -f

reset_db: remove_db init_db

start_db:
	docker start evolve-db

stop_db:
	docker stop evolve-db

seed:
	python -m scripts.seed

clean:
	docker rmi $(docker images -a -q)
