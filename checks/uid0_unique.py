from connexion import executer

ID = "uid0_unique"
DESCRIPTION = "Seul le compte root possède l'UID 0 (aucun administrateur caché)"


def run(client):
    sortie = executer(client, "awk -F: '$3==0 {print $1}' /etc/passwd")
    comptes = sortie.split()
    return {"conforme": comptes == ["root"], "preuve": "comptes UID 0 : " + (", ".join(comptes) or "aucun")}
