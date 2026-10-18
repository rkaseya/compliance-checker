from connexion import executer

ID = "comptes_sans_mdp"
DESCRIPTION = "Aucun compte ne possède de mot de passe vide"


def run(client):
    sortie = executer(client, "awk -F: '$2==\"\" {print $1}' /etc/shadow")
    comptes = sortie.split()
    preuve = "comptes sans mot de passe : " + ", ".join(comptes) if comptes else "aucun compte sans mot de passe"
    return {"conforme": not comptes, "preuve": preuve}
