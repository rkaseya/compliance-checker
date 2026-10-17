from connexion import executer

ID = "mises_a_jour"
DESCRIPTION = "Aucune mise à jour de paquet en attente"

def run(client):
    valeur = executer(client, "apt-get -s upgrade | grep -c '^Inst'")
    nb = int(valeur) if valeur.isdigit() else -1
    return {"conforme": nb == 0, "preuve": f"{nb} paquet(s) en attente de mise à jour"}
