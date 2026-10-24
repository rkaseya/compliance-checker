#!/bin/sh
# Démarrage de la machine durcie : installation de la clé du compte d'audit, puis services.
CLE=""
if [ -d /cle_publique ]; then
  # Mode docker compose : la clé publique est déposée par l'application dans un volume partagé
  for i in $(seq 1 120); do
    [ -s /cle_publique/cle_audit.pub ] && CLE=/cle_publique/cle_audit.pub && break
    sleep 1
  done
elif [ -s /opt/lab/cle_audit.pub ]; then
  # Mode manuel : clé copiée dans l'image au moment du build
  CLE=/opt/lab/cle_audit.pub
fi

if [ -n "$CLE" ]; then
  install -o auditeur -g auditeur -m 600 "$CLE" /home/auditeur/.ssh/authorized_keys
else
  echo "Attention : aucune clé publique pour le compte auditeur" >&2
fi

ufw --force enable
rsyslogd
exec /usr/sbin/sshd -D
