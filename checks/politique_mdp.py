import re

from connexion import executer

ID = "politique_mdp"
DESCRIPTION = "Une longueur minimale de 12 caractères est imposée aux mots de passe (pam_pwquality)"

LONGUEUR_MIN = 12


def run(client):
    sortie = executer(client, "grep -E '^[[:space:]]*minlen' /etc/security/pwquality.conf 2>/dev/null")
    trouve = re.search(r"minlen\s*=\s*(\d+)", sortie)
    if not trouve:
        return {"conforme": False, "preuve": "aucune longueur minimale configurée (pwquality absent ou minlen non défini)"}
    longueur = int(trouve.group(1))
    return {"conforme": longueur >= LONGUEUR_MIN, "preuve": f"minlen = {longueur}"}
