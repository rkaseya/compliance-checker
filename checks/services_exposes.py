from connexion import executer

ID = "services_exposes"
DESCRIPTION = "Seuls les services autorisés (SSH) sont en écoute"

PORTS_AUTORISES = {22}
PORTS_CONNUS = {21: "FTP", 23: "Telnet", 80: "HTTP", 3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis"}


def ports_en_ecoute(contenu):
    """Analyse /proc/net/tcp(6) : ne dépend d'aucun outil installé sur la cible (ss, netstat...)."""
    ports = set()
    for ligne in contenu.splitlines():
        champs = ligne.split()
        # champs[1] = adresse:port locale en hexadécimal, champs[3] = état ("0A" = LISTEN)
        if len(champs) > 3 and champs[3] == "0A":
            ports.add(int(champs[1].rsplit(":", 1)[1], 16))
    return ports


def run(client):
    ports = ports_en_ecoute(executer(client, "cat /proc/net/tcp /proc/net/tcp6 2>/dev/null"))
    interdits = sorted(ports - PORTS_AUTORISES)
    liste = ", ".join(f"{p} ({PORTS_CONNUS[p]})" if p in PORTS_CONNUS else str(p) for p in sorted(ports))
    preuve = f"ports en écoute : {liste or 'aucun'}"
    if interdits:
        preuve += f" | non autorisés : {', '.join(map(str, interdits))}"
    return {"conforme": not interdits, "preuve": preuve}
