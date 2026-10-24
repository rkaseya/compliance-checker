#!/bin/sh
# Initialisation du conteneur de l'application, puis lancement du serveur web.
# Les étapes de préparation tournent en root, le serveur tourne ensuite sans privilèges.
set -e
D=/donnees
mkdir -p "$D/cles"

# 1. Clé secrète Django : générée au premier démarrage, jamais écrite dans le code
if [ ! -s "$D/secret_key" ]; then
  python -c "import secrets; print(secrets.token_urlsafe(50))" > "$D/secret_key"
fi
export DJANGO_SECRET_KEY="$(cat "$D/secret_key")"

# 2. Clé SSH du compte d'audit : la clé privée reste dans ce conteneur,
#    seule la clé publique est partagée avec la machine durcie
if [ ! -s "$D/cles/cle_audit" ]; then
  ssh-keygen -q -t ed25519 -N "" -C auditeur -f "$D/cles/cle_audit"
fi
cp "$D/cles/cle_audit.pub" /cle_publique/cle_audit.pub

# 3. Empreintes des cibles : enregistrées une seule fois, puis vérifiées à chaque audit.
#    Si une cible est reconstruite, son empreinte change et l'audit est refusé.
touch "$KNOWN_HOSTS"
for hote in cible durci; do
  if ! grep -q "^$hote " "$KNOWN_HOSTS"; then
    echo "Enregistrement de l'empreinte SSH de $hote..."
    for i in $(seq 1 60); do
      ssh-keyscan -T 2 "$hote" >> "$KNOWN_HOSTS" 2>/dev/null || true
      grep -q "^$hote " "$KNOWN_HOSTS" && break
      sleep 2
    done
  fi
done

# 4. Base de données et cibles
python manage.py migrate --noinput
python manage.py importer_cibles --fichier cibles.docker.yaml

# 5. Premier démarrage : compte administrateur au mot de passe aléatoire + premier audit
MESSAGE=""
if [ ! -f "$D/.initialise" ]; then
  MDP="$(python -c "import secrets; print(secrets.token_urlsafe(12))")"
  DJANGO_SUPERUSER_PASSWORD="$MDP" python manage.py createsuperuser --noinput --username admin --email admin@example.com
  touch "$D/.initialise"
  python manage.py lancer_audit || true
  MESSAGE="Compte créé : admin / $MDP  (affiché une seule fois, note-le)"
fi

# 6. Les fichiers appartiennent à l'utilisateur sans privilèges, qui lance le serveur
chown -R 1000:1000 "$D"
echo "============================================================"
echo " Compliance Checker est prêt : http://127.0.0.1:8000"
[ -n "$MESSAGE" ] && echo " $MESSAGE"
echo "============================================================"
exec setpriv --reuid=1000 --regid=1000 --clear-groups \
  python manage.py runserver 0.0.0.0:8000 --noreload --insecure
