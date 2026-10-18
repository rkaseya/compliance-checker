FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Paquets nécessaires + application de toutes les mises à jour
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y openssh-server sudo ufw && mkdir /run/sshd

# Compte d'audit dédié, authentifié uniquement par clé
RUN useradd -m -s /bin/bash auditeur && \
    echo 'auditeur ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/auditeur && \
    chmod 440 /etc/sudoers.d/auditeur
COPY cle_audit.pub /home/auditeur/.ssh/authorized_keys
RUN chown -R auditeur:auditeur /home/auditeur/.ssh && \
    chmod 700 /home/auditeur/.ssh && chmod 600 /home/auditeur/.ssh/authorized_keys

# Durcissement SSH : pas de root, pas de mot de passe
RUN printf 'PermitRootLogin no\nPasswordAuthentication no\n' > /etc/ssh/sshd_config.d/00-durcissement.conf

# Pare-feu : on autorise SSH, tout le reste est bloqué en entrée
RUN ufw default deny incoming && ufw allow 22/tcp

EXPOSE 22
CMD ["sh", "-c", "ufw --force enable; exec /usr/sbin/sshd -D"]
