#!/bin/sh
set -e
# Levanta los templates definidos en este docker-compose en la red 'hosting_net'
docker-compose up -d --build
echo "Templates levantados."
