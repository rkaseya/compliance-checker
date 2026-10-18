from connexion import executer

ID = "journalisation"
DESCRIPTION = "Un service de journalisation (rsyslog) est actif"


def run(client):
    # Lecture directe de /proc : pgrep n'est pas toujours installé sur les systèmes minimaux
    sortie = executer(client, "grep -lx rsyslogd /proc/[0-9]*/comm 2>/dev/null")
    pids = [ligne.split("/")[2] for ligne in sortie.splitlines() if ligne.startswith("/proc/")]
    if pids:
        return {"conforme": True, "preuve": f"rsyslogd actif (PID {', '.join(pids)})"}
    return {"conforme": False, "preuve": "aucun processus rsyslogd"}
