from django.db import models
from django.utils import timezone


class Cible(models.Model):
    """Une machine à auditer (équivalent d'une entrée de cibles.yaml)."""

    nom = models.CharField(max_length=100, unique=True)
    host = models.CharField("adresse", max_length=255)
    port = models.PositiveIntegerField(default=22)
    user = models.CharField("utilisateur", max_length=100)
    cle = models.CharField("clé SSH (chemin)", max_length=255, blank=True)
    password_env = models.CharField(
        "variable du mot de passe", max_length=100, blank=True,
        help_text="Nom de la variable d'environnement (.env) contenant le mot de passe. "
                  "Le mot de passe lui-même n'est jamais stocké en base.",
    )
    active = models.BooleanField(default=True)
    cree_le = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def en_dict(self):
        """Format attendu par le moteur d'audit (connexion.py)."""
        return {
            "nom": self.nom,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "cle": self.cle or None,
            "password_env": self.password_env or None,
        }


class Audit(models.Model):
    """Une exécution du moteur sur une cible, à un instant donné."""

    class Statut(models.TextChoices):
        EN_COURS = "en_cours", "En cours"
        TERMINE = "termine", "Terminé"
        ERREUR = "erreur", "Erreur"

    cible = models.ForeignKey(Cible, on_delete=models.PROTECT, related_name="audits")
    date = models.DateTimeField(auto_now_add=True)
    referentiel = models.CharField("référentiel", max_length=200)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_COURS)
    conformes = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    taux = models.PositiveIntegerField("taux (%)", null=True, blank=True)
    erreur = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.cible} – {timezone.localtime(self.date):%d/%m/%Y %H:%M}"

    @property
    def niveau(self):
        """Code couleur : bon (≥ 80 %), moyen (≥ 50 %), mauvais, ou erreur."""
        if self.taux is None:
            return "erreur"
        if self.taux >= 80:
            return "bon"
        return "moyen" if self.taux >= 50 else "mauvais"


class ResultatMesure(models.Model):
    """Résultat d'une mesure du référentiel lors d'un audit."""

    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name="mesures")
    ordre = models.PositiveIntegerField(default=0)
    mesure_id = models.CharField("mesure", max_length=20)
    titre = models.CharField(max_length=300)
    conforme = models.BooleanField()

    class Meta:
        ordering = ["audit", "ordre"]
        verbose_name = "résultat de mesure"
        verbose_name_plural = "résultats de mesures"

    def __str__(self):
        return f"Mesure {self.mesure_id} – {'OK' if self.conforme else 'KO'}"


class ResultatControle(models.Model):
    """Résultat d'une vérification technique, avec sa preuve."""

    mesure = models.ForeignKey(ResultatMesure, on_delete=models.CASCADE, related_name="controles")
    check_id = models.CharField("vérification", max_length=100)
    description = models.CharField(max_length=300)
    conforme = models.BooleanField()
    preuve = models.TextField()

    class Meta:
        verbose_name = "résultat de contrôle"
        verbose_name_plural = "résultats de contrôles"

    def __str__(self):
        return self.check_id
