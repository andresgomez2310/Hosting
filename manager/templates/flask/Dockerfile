# ========================================
# Template Flask corregido
# ========================================

FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación Flask
COPY . .

EXPOSE 5000

# CORREGIDO: CMD sin errores de sintaxis
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
