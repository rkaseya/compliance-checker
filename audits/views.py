from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Audit, Cible
from .services import executer_audit


@login_required
def tableau_de_bord(request):
    cibles = list(Cible.objects.filter(active=True))
    for cible in cibles:
        cible.dernier_audit = cible.audits.first()  # les audits sont triés du plus récent au plus ancien

    termines = [c.dernier_audit for c in cibles
                if c.dernier_audit and c.dernier_audit.statut == Audit.Statut.TERMINE]
    moyenne = round(sum(a.taux for a in termines) / len(termines)) if termines else None

    return render(request, "audits/tableau_de_bord.html", {
        "cibles": cibles,
        "moyenne": moyenne,
        "nb_audits": Audit.objects.count(),
        "derniers_audits": Audit.objects.select_related("cible")[:8],
    })


def points_graphique(audits, largeur=600, hauteur=200, marge=30):
    """Coordonnées SVG de la courbe d'évolution (calculées côté serveur, sans JavaScript)."""
    zone_l, zone_h = largeur - 2 * marge, hauteur - 2 * marge
    n = len(audits)
    points = []
    for i, audit in enumerate(audits):
        x = marge + (zone_l * i / (n - 1) if n > 1 else zone_l / 2)
        y = marge + zone_h * (1 - audit.taux / 100)
        points.append({"x": round(x, 1), "y": round(y, 1), "audit": audit})
    return {
        "points": points,
        "ligne": " ".join(f"{p['x']},{p['y']}" for p in points),
        "largeur": largeur, "hauteur": hauteur,
        "grille": [{"taux": t, "y": marge + zone_h * (1 - t / 100)} for t in (0, 50, 100)],
        "marge": marge,
    }


@login_required
def cible_detail(request, pk):
    cible = get_object_or_404(Cible, pk=pk)
    audits = cible.audits.all()
    # Les 20 derniers audits réussis, remis dans l'ordre chronologique pour la courbe
    historique = list(audits.filter(statut=Audit.Statut.TERMINE)[:20])[::-1]
    return render(request, "audits/cible_detail.html", {
        "cible": cible,
        "audits": audits,
        "graphique": points_graphique(historique) if historique else None,
    })


@login_required
def audit_detail(request, pk):
    audit = get_object_or_404(
        Audit.objects.select_related("cible").prefetch_related("mesures__controles"), pk=pk
    )
    return render(request, "audits/audit_detail.html", {"audit": audit})


@login_required
@require_POST  # une action qui modifie des données ne passe jamais par un simple lien (GET)
def auditer(request, pk):
    cible = get_object_or_404(Cible, pk=pk, active=True)
    audit = executer_audit(cible)
    if audit.statut == Audit.Statut.ERREUR:
        messages.error(request, f"Audit de {cible.nom} impossible : {audit.erreur}")
    else:
        messages.success(request, f"Audit de {cible.nom} terminé : {audit.taux} % de conformité.")
    return redirect("audit_detail", pk=audit.pk)
