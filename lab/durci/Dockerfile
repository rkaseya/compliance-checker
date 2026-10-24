FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Paquets nécessaires + application de toutes les mises à jour
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y openssh-server sudo ufw rsyslog libpam-pwquality && mkdir /run/sshd

# Compte d'audit dédié, authentifié uniquement par clé
RUN useradd -m -s /bin/bash auditeur && \
    echo 'auditeur ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/auditeur && \
    chmod 440 /etc/sudoers.d/auditeur
RUN mkdir -p /home/auditeur/.ssh && chown auditeur:auditeur /home/auditeur/.ssh && \
    chmod 700 /home/auditeur/.ssh
# Script de démarrage + clé publique si elle existe (le motif [b] la rend facultative)
COPY demarrage.sh cle_audit.pu[b] /opt/lab/

# Durcissement SSH : pas de root, pas de mot de passe
RUN printf 'PermitRootLogin no\nPasswordAuthentication no\n' > /etc/ssh/sshd_config.d/00-durcissement.conf

# Politique de mots de passe : 12 caractères minimum
RUN echo 'minlen = 12' >> /etc/security/pwquality.conf

# Journalisation : le module des logs noyau est inutilisable dans un conteneur
RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf

# Pare-feu : on autorise SSH, tout le reste est bloqué en entrée
RUN ufw default deny incoming && ufw allow 22/tcp

EXPOSE 22
CMD ["sh", "/opt/lab/demarrage.sh"]
