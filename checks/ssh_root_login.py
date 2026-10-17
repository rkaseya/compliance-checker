import paramiko

def run(host, port, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password)
    _, stdout, _ = client.exec_command("sshd -T | grep -i permitrootlogin")
    valeur = stdout.read().decode().strip()
    client.close()

    conforme = valeur.lower() == "permitrootlogin no"
    return {"conforme": conforme, "preuve": valeur}

if __name__ == "__main__":
    print(run("127.0.0.1", 2222, "root", "root"))
