import paramiko


def connecter(cible):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        cible["host"],
        port=cible["port"],
        username=cible["user"],
        password=cible.get("password"),
        key_filename=cible.get("cle"),
        look_for_keys=False,
        allow_agent=False,
        timeout=10,
    )
    # Compte non-root : les commandes d'audit passent par sudo
    client.prefixe = "" if cible["user"] == "root" else "sudo "
    return client


def executer(client, commande):
    _, stdout, _ = client.exec_command(client.prefixe + commande)
    return stdout.read().decode().strip()
