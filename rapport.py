from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def generer_rapport(audits, referentiel, dossier="rapports"):
    env = Environment(
        loader=FileSystemLoader("templates"),
        # Les preuves viennent des machines auditées : on les échappe
        # pour qu'un contenu malveillant ne puisse pas injecter de HTML/JS.
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("rapport.html")

    maintenant = datetime.now()
    html = template.render(
        audits=audits,
        referentiel=referentiel,
        date=maintenant.strftime("%d/%m/%Y à %H:%M"),
    )

    Path(dossier).mkdir(exist_ok=True)
    chemin = Path(dossier) / f"rapport_{maintenant:%Y%m%d_%H%M%S}.html"
    chemin.write_text(html, encoding="utf-8")
    return chemin
