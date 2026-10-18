from django.core.management.base import BaseCommand

from audits.models import Cible
from main import charger_yaml

CHAMPS = ("host", "port", "user", "cle", "password_env")


class Command(BaseCommand):
    help = "Importe (ou met à jour) les cibles décrites dans cibles.yaml."

    def add_arguments(self, parser):
        parser.add_argument("--fichier", default="cibles.yaml")

    def handle(self, *args, fichier, **options):
        for donnees in charger_yaml(fichier)["cibles"]:
            valeurs = {champ: donnees.get(champ) or "" for champ in CHAMPS}
            valeurs["port"] = donnees.get("port", 22)
            cible, cree = Cible.objects.update_or_create(nom=donnees["nom"], defaults=valeurs)
            self.stdout.write(f"{'Créée' if cree else 'Mise à jour'} : {cible.nom}")
