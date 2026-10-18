from django.urls import path

from . import views

urlpatterns = [
    path("", views.tableau_de_bord, name="tableau_de_bord"),
    path("cibles/<int:pk>/", views.cible_detail, name="cible_detail"),
    path("cibles/<int:pk>/auditer/", views.auditer, name="auditer"),
    path("audits/<int:pk>/", views.audit_detail, name="audit_detail"),
]
