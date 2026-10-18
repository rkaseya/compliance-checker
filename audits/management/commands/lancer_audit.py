from django.core.management.base import BaseCommand, CommandError

from audits.models import Audit, Cible
from audits.services import executer_audit


class Command(BaseCommand):
    help = "Audite les cibles actives (ou celles nommées) et enregistre les résultats en base."

    def add_arguments(self, parser):
        parser.add_argument("noms", nargs="*", help="Noms des cibles à auditer (toutes par défaut)")

    def handle(self, *args, noms, **options):
        cibles = Cible.objects.filter(active=True)
        if noms:
            cibles = cibles.filter(nom__in=noms)
        if not cibles.exists():
            raise CommandError("Aucune cible à auditer. Lance d'abord : python manage.py importer_cibles")

        for cible in cibles:
            audit = executer_audit(cible)
            if audit.statut == Audit.Statut.ERREUR:
                self.stdout.write(self.style.ERROR(f"{cible.nom:<20} inaccessible : {audit.erreur}"))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"{cible.nom:<20} {audit.taux} % ({audit.conformes}/{audit.total} mesures)"
                ))
