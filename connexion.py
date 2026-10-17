import paramiko

def connecter(host, port, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password)
    return client

def executer(client, commande):
    _, stdout, _ = client.exec_command(commande)
    return stdout.read().decode().strip()
