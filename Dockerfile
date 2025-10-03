# Imagen base ligera de Python
FROM python:3.11-slim

# Instalar curl y dependencias básicas
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para cache)
COPY pyproject.toml uv.lock ./

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Instalar flet directamente con pip para evitar problemas de rutas
RUN pip install --no-cache-dir flet[all]==0.28.3

# Copiar código fuente
COPY ./src ./src

# Puerto por defecto de Flet Web
EXPOSE 8550

# Comando para ejecutar Flet en modo web
CMD ["python", "src/main.py", "--web"]
