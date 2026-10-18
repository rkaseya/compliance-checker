FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y openssh-server netcat-openbsd && mkdir /run/sshd

# Mot de passe root faible + connexion root et par mot de passe autorisées
RUN echo 'root:root' | chpasswd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Compte "invite" sans mot de passe
RUN useradd -m -s /bin/bash invite && passwd -d invite

# Administrateur caché : un second compte avec l'UID 0
RUN useradd -o -u 0 -g 0 -M -s /bin/bash maintenance

EXPOSE 22
# Un faux service Telnet (port 23) tourne à côté de SSH
CMD ["sh", "-c", "nc -lk 23 >/dev/null 2>&1 & exec /usr/sbin/sshd -D"]
