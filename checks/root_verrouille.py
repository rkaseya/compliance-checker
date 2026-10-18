from connexion import executer

ID = "root_verrouille"
DESCRIPTION = "Le mot de passe du compte root est verrouillé (administration via comptes nominatifs + sudo)"


def run(client):
    # 1er caractère du champ mot de passe de root dans /etc/shadow : ! ou * = verrouillé
    debut = executer(client, "awk -F: '$1==\"root\" {print substr($2,1,1)}' /etc/shadow")
    verrouille = debut in ("!", "*")
    etat = "verrouillé" if verrouille else "défini (connexion possible avec ce mot de passe)"
    return {"conforme": verrouille, "preuve": f"mot de passe root : {etat}"}
