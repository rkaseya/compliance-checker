import importlib
import pkgutil

import yaml
from dotenv import load_dotenv

import checks
from connexion import connecter
from rapport import generer_rapport


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


def evaluer(resultats, referentiel, tous_les_checks):
    """Croise les résultats techniques avec les mesures du référentiel."""
    mesures = []
    for mesure in referentiel["mesures"]:
        controles = [
            {"description": tous_les_checks[c].DESCRIPTION, **resultats[c]}
            for c in mesure["checks"]
        ]
        mesures.append({
            "id": mesure["id"],
            "titre": mesure["titre"],
            "ok": all(c["conforme"] for c in controles),
            "controles": controles,
        })
    conformes = sum(m["ok"] for m in mesures)
    total = len(mesures)
    return {"mesures": mesures, "conformes": conformes, "total": total,
            "taux": conformes * 100 // total}


def afficher_console(audit):
    print(f"\n=== {audit['nom']} ===\n")
    if audit["erreur"]:
        print(f"[!] Impossible d'auditer : {audit['erreur']}")
        return
    e = audit["evaluation"]
    for m in e["mesures"]:
        print(f"[{'OK' if m['ok'] else 'KO'}] Mesure {m['id']} - {m['titre']}")
        for c in m["controles"]:
            print(f"      {'✔' if c['conforme'] else '✘'} {c['description']}")
            print(f"        preuve : {c['preuve']}")
    print(f"\nTaux de conformité : {e['conformes']}/{e['total']} mesures ({e['taux']} %)")


def main():
    load_dotenv()  # charge les secrets depuis .env
    referentiel = charger_yaml("referentiels/anssi.yaml")
    cibles = charger_yaml("cibles.yaml")["cibles"]
    tous_les_checks = charger_checks()

    audits = []
    for cible in cibles:
        audit = {"nom": cible["nom"], "erreur": None, "evaluation": None}
        try:
            resultats = auditer(cible, tous_les_checks)
            audit["evaluation"] = evaluer(resultats, referentiel, tous_les_checks)
        except Exception as e:
            audit["erreur"] = str(e)
        audits.append(audit)
        afficher_console(audit)

    print("\n=== Synthèse ===")
    for a in audits:
        etat = "inaccessible" if a["erreur"] else f"{a['evaluation']['taux']} %"
        print(f"  {a['nom']:<20} {etat}")

    chemin = generer_rapport(audits, referentiel)
    print(f"\nRapport HTML : {chemin}\n")


if __name__ == "__main__":
    main()
