# Imagen base ligera de Python
FROM python:3.11-slim

# Instalar curl para poder instalar uv
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instalar uv (gestor de dependencias)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para aprovechar la caché de Docker)
COPY pyproject.toml uv.lock ./

# Instalar dependencias en el sistema
RUN uv sync --frozen --no-dev

# Copiar el código fuente y assets
COPY ./src ./src

# Puerto por defecto de Flet Web
EXPOSE 8550

# Comando para ejecutar Flet en modo web
CMD ["python", "src/main.py", "--web"]
