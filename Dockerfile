# Image de l'application web (Django + moteur d'audit)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Client SSH : ssh-keygen (clé du compte d'audit) et ssh-keyscan (empreintes des cibles)
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Utilisateur sans privilèges qui fera tourner le serveur web
RUN useradd --uid 1000 --create-home appli && mkdir -p /donnees /cle_publique

EXPOSE 8000
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
