#!/bin/bash

# Este script se ejecuta en la VM remota de Oracle Cloud.

# 1. Obtener los argumentos pasados desde GitHub Actions
# El primer argumento es el nombre de usuario de SSH (SSH_USER)
SSH_USER="$1"
# El segundo argumento es la contraseña de Docker Hub (DOCKER_PASSWORD)
DOCKER_PASSWORD="$2"
# El tercer argumento es el nombre de usuario de Docker Hub (DOCKER_USER)
DOCKER_USER="$3"

DEPLOY_PATH="/home/$SSH_USER/deploy"
IMAGE_NAME="$DOCKER_USER/front_web:latest"

echo "--- 1. Entrando al directorio de despliegue: $DEPLOY_PATH ---"
cd $DEPLOY_PATH

echo "--- 2. Deteniendo y limpiando contenedores e imágenes anteriores ---"
# Detiene y elimina el contenedor definido en docker-compose (si existe) y sus imágenes
# Usamos '|| true' para que el script no falle si no hay nada que detener.
docker-compose down --rmi all || true

echo "--- 3. Limpieza general del sistema Docker (contenedores detenidos, volúmenes no usados) ---"
docker system prune -f

echo "--- 4. Iniciando sesión en Docker Hub ---"
# El login se realiza con la contraseña pasada como argumento
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin

echo "--- 5. Descargando la última imagen: $IMAGE_NAME ---"
docker pull "$IMAGE_NAME"

echo "--- 6. Levantando contenedor con docker-compose ---"
# Levanta el servicio en modo detached (-d) y fuerza la recreación
docker-compose up -d --force-recreate

echo "--- 7. Cerrando sesión en Docker Hub ---"
docker logout

echo "--- Despliegue completado ---"