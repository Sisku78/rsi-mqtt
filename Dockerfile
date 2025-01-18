# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY . /app

# Instalar las dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    && pip install --no-cache-dir -r requeriments.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el punto de entrada
CMD ["python", "server.py"]
