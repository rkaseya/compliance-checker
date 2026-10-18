from django.contrib import admin
from django.utils.html import format_html

from .models import Audit, Cible, ResultatControle, ResultatMesure


def badge(conforme):
    couleur, texte = ("#1a7f37", "OK") if conforme else ("#cf222e", "KO")
    return format_html('<b style="color:{}">{}</b>', couleur, texte)


class LectureSeuleMixin:
    """Les résultats d'audit sont des preuves : ils ne se créent et ne se modifient
    pas à la main, seul le moteur les produit."""

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Cible)
class CibleAdmin(admin.ModelAdmin):
    list_display = ("nom", "host", "port", "user", "active", "dernier_taux")
    list_filter = ("active",)
    search_fields = ("nom", "host")

    @admin.display(description="dernier taux")
    def dernier_taux(self, obj):
        audit = obj.audits.filter(statut=Audit.Statut.TERMINE).first()
        return f"{audit.taux} %" if audit else "–"


class ResultatMesureInline(LectureSeuleMixin, admin.TabularInline):
    model = ResultatMesure
    fields = ("statut", "mesure_id", "titre")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    @admin.display(description="statut")
    def statut(self, obj):
        return badge(obj.conforme)


@admin.register(Audit)
class AuditAdmin(LectureSeuleMixin, admin.ModelAdmin):
    list_display = ("cible", "date", "statut", "taux_affiche")
    list_filter = ("cible", "statut")
    date_hierarchy = "date"
    inlines = [ResultatMesureInline]

    @admin.display(description="conformité", ordering="taux")
    def taux_affiche(self, obj):
        return "–" if obj.taux is None else f"{obj.taux} %"


class ResultatControleInline(LectureSeuleMixin, admin.TabularInline):
    model = ResultatControle
    fields = ("statut", "description", "preuve")
    readonly_fields = fields
    extra = 0
    can_delete = False

    @admin.display(description="statut")
    def statut(self, obj):
        return badge(obj.conforme)


@admin.register(ResultatMesure)
class ResultatMesureAdmin(LectureSeuleMixin, admin.ModelAdmin):
    list_display = ("audit", "mesure_id", "titre", "conforme")
    list_filter = ("conforme", "mesure_id")
    inlines = [ResultatControleInline]
