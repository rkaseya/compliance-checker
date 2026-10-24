import os
from pathlib import Path

import paramiko

# Empreintes des serveurs autorisés, au format OpenSSH (voir README)
FICHIER_EMPREINTES = Path(os.environ.get("KNOWN_HOSTS", "known_hosts"))


def _mot_de_passe(cible):
    """Le mot de passe n'est jamais écrit dans cibles.yaml :
    on y indique seulement le nom de la variable d'environnement qui le contient."""
    variable = cible.get("password_env")
    if not variable:
        return None
    valeur = os.environ.get(variable)
    if valeur is None:
        raise RuntimeError(f"variable d'environnement {variable} non définie (voir le fichier .env)")
    return valeur


def connecter(cible):
    if not FICHIER_EMPREINTES.exists():
        raise RuntimeError("fichier known_hosts absent : enregistre d'abord les empreintes des cibles (voir README)")

    client = paramiko.SSHClient()
    client.load_host_keys(str(FICHIER_EMPREINTES))
    # Serveur inconnu = connexion refusée (protection contre l'homme du milieu)
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(
            cible["host"],
            port=cible["port"],
            username=cible["user"],
            password=_mot_de_passe(cible),
            key_filename=cible.get("cle"),
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )
    except paramiko.BadHostKeyException:
        raise RuntimeError(
            "ALERTE : l'empreinte du serveur a changé (machine reconstruite ou "
            "attaque de l'homme du milieu). Connexion refusée."
        ) from None
    except paramiko.SSHException as e:
        if "not found in known_hosts" in str(e):
            raise RuntimeError("serveur inconnu : son empreinte n'est pas dans known_hosts. Connexion refusée.") from None
        raise

    # Compte non-root : les commandes d'audit passent par sudo
    client.prefixe = "" if cible["user"] == "root" else "sudo "
    return client


def executer(client, commande):
    _, stdout, _ = client.exec_command(client.prefixe + commande)
    return stdout.read().decode().strip()
