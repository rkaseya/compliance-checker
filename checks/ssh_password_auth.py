from connexion import executer

ID = "ssh_password_auth"
DESCRIPTION = "L'authentification SSH par mot de passe est désactivée (clés uniquement)"

def run(client):
    valeur = executer(client, "sshd -T | grep -i '^passwordauthentication'")
    return {"conforme": valeur.lower() == "passwordauthentication no", "preuve": valeur}
