"""Pont entre le moteur d'audit existant (main.py) et la base de données Django."""
from django.db import transaction

from main import auditer, charger_checks, charger_yaml, evaluer

from .models import Audit, ResultatControle, ResultatMesure

FICHIER_REFERENTIEL = "referentiels/anssi.yaml"


def executer_audit(cible):
    referentiel = charger_yaml(FICHIER_REFERENTIEL)
    tous_les_checks = charger_checks()

    audit = Audit.objects.create(
        cible=cible,
        referentiel=f"{referentiel['referentiel']} (v{referentiel['version']})",
    )

    try:
        resultats = auditer(cible.en_dict(), tous_les_checks)
    except Exception as e:
        audit.statut = Audit.Statut.ERREUR
        audit.erreur = str(e)
        audit.save()
        return audit

    evaluation = evaluer(resultats, referentiel, tous_les_checks)

    # Tout ou rien : un audit n'est jamais enregistré à moitié
    with transaction.atomic():
        for ordre, m in enumerate(evaluation["mesures"]):
            mesure = ResultatMesure.objects.create(
                audit=audit, ordre=ordre, mesure_id=m["id"], titre=m["titre"], conforme=m["ok"],
            )
            ResultatControle.objects.bulk_create([
                ResultatControle(
                    mesure=mesure, check_id=c["id"], description=c["description"],
                    conforme=c["conforme"], preuve=c["preuve"],
                )
                for c in m["controles"]
            ])
        audit.conformes = evaluation["conformes"]
        audit.total = evaluation["total"]
        audit.taux = evaluation["taux"]
        audit.statut = Audit.Statut.TERMINE
        audit.save()

    return audit
