import importlib
import pkgutil

import yaml

import checks
from connexion import connecter

CIBLE = {"host": "127.0.0.1", "port": 2222, "user": "root", "password": "root"}


def charger_checks():
    """Découvre automatiquement tous les fichiers du dossier checks/."""
    modules = {}
    for info in pkgutil.iter_modules(checks.__path__):
        module = importlib.import_module(f"checks.{info.name}")
        modules[module.ID] = module
    return modules


def main():
    with open("referentiels/anssi.yaml", encoding="utf-8") as f:
        referentiel = yaml.safe_load(f)

    tous_les_checks = charger_checks()

    client = connecter(**CIBLE)
    resultats = {}
    for check_id, module in tous_les_checks.items():
        try:
            resultats[check_id] = module.run(client)
        except Exception as e:
            resultats[check_id] = {"conforme": False, "preuve": f"Erreur : {e}"}
    client.close()

    print(f"\n=== {referentiel['referentiel']} (v{referentiel['version']}) ===\n")
    conformes = 0
    for mesure in referentiel["mesures"]:
        ok = all(resultats[c]["conforme"] for c in mesure["checks"])
        conformes += ok
        print(f"[{'OK' if ok else 'KO'}] Mesure {mesure['id']} - {mesure['titre']}")
        for c in mesure["checks"]:
            r = resultats[c]
            print(f"      {'✔' if r['conforme'] else '✘'} {tous_les_checks[c].DESCRIPTION}")
            print(f"        preuve : {r['preuve']}")

    total = len(referentiel["mesures"])
    print(f"\nTaux de conformité : {conformes}/{total} mesures ({conformes * 100 // total} %)\n")


if __name__ == "__main__":
    main()
