#!/bin/sh -x

docker-compose exec -T db psql -f /db/conf/db_init.sql -U postgres -d toybox