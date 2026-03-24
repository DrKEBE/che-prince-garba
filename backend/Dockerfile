# Étape de build : installation des dépendances
FROM python:3.11-slim AS builder

WORKDIR /app

# Dépendances système nécessaires pour psycopg2 et autres
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements et installer les dépendances Python
COPY backend/requirements.txt .
RUN pip install --user -r requirements.txt

# Étape finale : image légère
FROM python:3.11-slim

WORKDIR /app

# Copier les dépendances depuis l'étape builder
COPY --from=builder /root/.local /root/.local

# Copier le code source
COPY backend/ .

# S'assurer que les scripts locaux sont dans le PATH
ENV PATH=/root/.local/bin:$PATH

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]