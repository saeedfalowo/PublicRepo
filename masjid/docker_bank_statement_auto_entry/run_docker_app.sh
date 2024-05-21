#!/bin/bash

image_name="auto_load"
container_name="auto_load_container"
mkdir statements/log
touch statements/log/history.json
docker build -t "$image_name" .
docker run --name $container_name $image_name
container_id=$(docker ps -aqf "name=$container_name")
echo "container_id: $container_id"
ls statements
docker cp $container_id:/usr/app/src/statements/log/history.json statements/log/history.json
python3 move_processed_files.py
# mv statements/*.pdf statements/processed/
docker rm "$container_name"
echo "removed $container_name docker container"
echo y | docker system prune
echo "pruned unused docker images"