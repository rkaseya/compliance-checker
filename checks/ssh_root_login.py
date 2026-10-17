from connexion import executer

ID = "ssh_root_login"
DESCRIPTION = "La connexion SSH directe en root est interdite"

def run(client):
    valeur = executer(client, "sshd -T | grep -i '^permitrootlogin'")
    return {"conforme": valeur.lower() == "permitrootlogin no", "preuve": valeur}
