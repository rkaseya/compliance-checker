from connexion import executer

ID = "pare_feu"
DESCRIPTION = "Un pare-feu local (ufw) est installé et actif"

def run(client):
    valeur = executer(client, "ufw status 2>/dev/null || echo 'ufw non installé'")
    return {"conforme": "Status: active" in valeur, "preuve": valeur}
