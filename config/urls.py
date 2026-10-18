from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Compliance Checker"
admin.site.site_title = "Compliance Checker"
admin.site.index_title = "Administration des audits"

urlpatterns = [
    path("", include("audits.urls")),
    path("comptes/", include("django.contrib.auth.urls")),  # connexion / déconnexion
    path("admin/", admin.site.urls),
]
