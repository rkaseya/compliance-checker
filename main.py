import importlib
import pkgutil

import yaml

import checks
from connexion import connecter


def charger_yaml(chemin):
    with open(chemin, encoding="utf-8") as f:
        return yaml.safe_load(f)


def charger_checks():
    """Découvre automatiquement tous les fichiers du dossier checks/."""
    modules = {}
    for info in pkgutil.iter_modules(checks.__path__):
        module = importlib.import_module(f"checks.{info.name}")
        modules[module.ID] = module
    return modules


def auditer(cible, tous_les_checks):
    client = connecter(cible)
    resultats = {}
    for check_id, module in tous_les_checks.items():
        try:
            resultats[check_id] = module.run(client)
        except Exception as e:
            resultats[check_id] = {"conforme": False, "preuve": f"Erreur : {e}"}
    client.close()
    return resultats


def afficher_rapport(nom, resultats, referentiel, tous_les_checks):
    print(f"\n=== {nom} | {referentiel['referentiel']} (v{referentiel['version']}) ===\n")
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
    taux = conformes * 100 // total
    print(f"\nTaux de conformité : {conformes}/{total} mesures ({taux} %)")
    return taux


def main():
    referentiel = charger_yaml("referentiels/anssi.yaml")
    cibles = charger_yaml("cibles.yaml")["cibles"]
    tous_les_checks = charger_checks()

    synthese = {}
    for cible in cibles:
        try:
            resultats = auditer(cible, tous_les_checks)
        except Exception as e:
            print(f"\n[!] Impossible d'auditer {cible['nom']} : {e}")
            synthese[cible["nom"]] = None
            continue
        synthese[cible["nom"]] = afficher_rapport(cible["nom"], resultats, referentiel, tous_les_checks)

    print("\n=== Synthèse ===")
    for nom, taux in synthese.items():
        etat = "inaccessible" if taux is None else f"{taux} %"
        print(f"  {nom:<20} {etat}")
    print()


if __name__ == "__main__":
    main()
