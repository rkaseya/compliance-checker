from connexion import executer

ID = "permissions_shadow"
DESCRIPTION = "Le fichier des mots de passe (/etc/shadow) n'est pas lisible par tous"

def run(client):
    valeur = executer(client, "stat -c '%a' /etc/shadow")
    conforme = valeur.isdigit() and int(valeur, 8) & 0o007 == 0
    return {"conforme": conforme, "preuve": f"/etc/shadow : permissions {valeur}"}
