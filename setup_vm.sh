#!/bin/bash

# Este script se ejecuta en la VM de Oracle Cloud a través de SSH.
# Nota: Asume que el sistema operativo es Ubuntu/Debian.

USER_TO_ADD="$1" # Recibe el nombre de usuario de SSH

echo "--- 1. Actualizando e instalando Docker y Docker Compose ---"
# Usamos 'sudo' para tener permisos de instalación
sudo apt update -y
sudo apt install -y docker.io docker-compose

echo "--- 2. Configurando permisos de Docker ---"
# Agrega el usuario al grupo docker para permitir ejecutar comandos sin sudo (aunque en el pipeline usamos sudo por seguridad)
sudo usermod -aG docker $USER_TO_ADD

echo "--- 3. Configurando Firewall Interno (UFW en Puerto 80) ---"
# Instala e inicializa UFW si no está activo
sudo apt install -y ufw
# Abre el puerto 80 (HTTP) y 8000 (FastAPI)
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8550/tcp

# Habilita el firewall (si no está activo)
sudo ufw enable -y 
sudo ufw status verbose

echo "--- 4. Asegurando Directorio de Despliegue ---"
DEPLOY_PATH="/home/$USER_TO_ADD/deploy"
# Crea la carpeta y cualquier carpeta padre si es necesario (-p)
mkdir -p $DEPLOY_PATH

echo "--- Configuración inicial de la VM completada ---"