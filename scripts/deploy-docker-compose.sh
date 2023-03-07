#! /bin/bash

GIT_URL="git@github.com:exellentcoin26/news-finder.git"
APP_DIR="news-finder"

DOCKER_COMPOSE_FILE="docker/docker-compose.yml"

# clean up old docker containers
docker stop $(docker ps -a -q)
docker container prune -f

# make sure we are in the HOME directory
cd $HOME

# clone repository
if [[ -d "$APP_DIR" ]] ; then
    cd "$APP_DIR" && git checkout main && git pull
else
    git clone "$GIT_URL" && cd "$APP_DIR"
fi

# run docker compose file
if [[ ! -f "$DOCKER_COMPOSE_FILE" ]] ; then
    echo "Could not find docker compose file"
    exit 1
else
    docker compose -f "$DOCKER_COMPOSE_FILE" build
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d
    exit 0
fi
