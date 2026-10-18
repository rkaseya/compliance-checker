from connexion import executer

ID = "pare_feu"
DESCRIPTION = "Un pare-feu local (ufw) est installé et actif"

ACTIONS = ("ALLOW", "DENY", "REJECT", "LIMIT")


def run(client):
    sortie = executer(client, "ufw status 2>/dev/null || echo 'ufw non installé'")
    lignes = sortie.splitlines() or ["aucune réponse"]
    actif = lignes[0].strip() == "Status: active"

    # Preuve condensée : l'état, puis les règles sur une seule ligne chacune
    regles = [" ".join(l.split()) for l in lignes if any(a in l for a in ACTIONS)]
    preuve = lignes[0].strip()
    if regles:
        preuve += " | règles : " + " ; ".join(regles)
    return {"conforme": actif, "preuve": preuve}
