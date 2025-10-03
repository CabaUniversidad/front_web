# Imagen base ligera
FROM python:3.11-slim

# Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo archivos de dependencias primero
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY ./src ./src

# Puerto por defecto de Flet Web
EXPOSE 8550

# Comando de ejecución
CMD ["python", "src/main.py", "--web"]
