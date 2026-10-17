# Compliance Checker

Outil d'audit de conformité automatisé, écrit en Python. Il se connecte à une machine Linux, vérifie sa configuration de sécurité et rattache chaque résultat aux mesures du **Guide d'hygiène informatique de l'ANSSI**, avec une preuve pour chaque contrôle et un taux de conformité global.

> Projet personnel en cours de développement : il évoluera vers une plateforme web de conformité et d'analyse de risques (voir la [feuille de route](#feuille-de-route)).

## Fonctionnalités

- **Vérifications techniques automatisées** via SSH (configuration SSH, pare-feu, mises à jour, permissions de fichiers sensibles).
- **Rattachement à un référentiel** : chaque vérification est liée à une ou plusieurs mesures du guide ANSSI, décrites dans un fichier YAML séparé du code.
- **Preuve pour chaque résultat** : la valeur réellement observée sur la machine est conservée, comme dans un audit.
- **Architecture à plugins** : une vérification = un fichier, découvert automatiquement par le moteur.
- **Robustesse** : une vérification en erreur n'interrompt pas l'audit, l'erreur apparaît dans le rapport.
- **Lab Docker** fourni : une machine cible volontairement mal configurée pour tester l'outil sans risque.

## Architecture

```
compliance-checker/
├── lab/Dockerfile           # Machine cible de test (Ubuntu + SSH, mal configurée)
├── connexion.py             # Connexion SSH et exécution de commandes
├── checks/                  # Une vérification = un fichier
│   ├── ssh_root_login.py
│   ├── ssh_password_auth.py
│   ├── pare_feu.py
│   ├── mises_a_jour.py
│   └── permissions_shadow.py
├── referentiels/
│   └── anssi.yaml           # Correspondance mesures ANSSI ↔ vérifications
└── main.py                  # Moteur d'audit et rapport
```

**Fonctionnement :**

1. `main.py` découvre automatiquement les vérifications présentes dans `checks/`.
2. Il ouvre une seule connexion SSH vers la cible et exécute chaque vérification.
3. Chaque vérification renvoie un résultat au format commun `{"conforme": bool, "preuve": str}`.
4. Les résultats sont croisés avec le référentiel YAML pour produire le rapport par mesure.

Séparer le code technique (les vérifications) du référentiel (le YAML) permet d'ajouter un nouveau référentiel, par exemple ISO 27001, sans réécrire les vérifications.

## Vérifications actuelles

| Mesure ANSSI | Vérification | Contrôle effectué |
|---|---|---|
| 8 | `ssh_root_login` | La connexion SSH directe en root est interdite |
| 11 | `permissions_shadow` | `/etc/shadow` n'est pas lisible par tous |
| 13 | `ssh_password_auth` | L'authentification SSH par mot de passe est désactivée |
| 17 | `pare_feu` | Un pare-feu local (ufw) est installé et actif |
| 34 | `mises_a_jour` | Aucune mise à jour de paquet en attente |

## Installation

Prérequis : Python 3.12+, Docker, Git.

```bash
git clone https://github.com/rkaseya/compliance-checker.git
cd compliance-checker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Lancer la machine cible de test :

```bash
docker build -t lab-cible lab/
docker run -d --name cible -p 127.0.0.1:2222:22 lab-cible
```

## Utilisation

```bash
python main.py
```

Exemple de rapport sur le lab :

```
=== Guide d'hygiène informatique ANSSI (v2.0) ===

[KO] Mesure 8 - Identifier nommément chaque personne accédant au système et distinguer les rôles utilisateur/administrateur
      ✘ La connexion SSH directe en root est interdite
        preuve : permitrootlogin yes
[OK] Mesure 11 - Protéger les mots de passe stockés sur les systèmes
      ✔ Le fichier des mots de passe (/etc/shadow) n'est pas lisible par tous
        preuve : /etc/shadow : permissions 640
[KO] Mesure 13 - Privilégier lorsque c'est possible une authentification forte
      ✘ L'authentification SSH par mot de passe est désactivée (clés uniquement)
        preuve : passwordauthentication yes
[KO] Mesure 17 - Activer et configurer le pare-feu local
      ✘ Un pare-feu local (ufw) est installé et actif
        preuve : ufw non installé
[OK] Mesure 34 - Définir une politique de mise à jour des composants du système d'information
      ✔ Aucune mise à jour de paquet en attente
        preuve : 0 paquet(s) en attente de mise à jour

Taux de conformité : 2/5 mesures (40 %)
```

## Ajouter une vérification

1. Créer un fichier dans `checks/` respectant ce contrat :

```python
from connexion import executer

ID = "mon_controle"
DESCRIPTION = "Description lisible du contrôle"

def run(client):
    valeur = executer(client, "commande à exécuter sur la cible")
    return {"conforme": ..., "preuve": valeur}
```

2. Rattacher son `ID` à une mesure dans `referentiels/anssi.yaml`.

Aucune modification du moteur n'est nécessaire.

## Limites connues

- Les identifiants de la cible sont pour l'instant écrits dans `main.py` (à externaliser).
- Le contrôle du pare-feu a peu de sens dans un conteneur Docker, où le filtrage est généralement assuré par l'hôte. Il est pertinent pour une VM ou un serveur physique.
- Une seule machine auditée à la fois.

## Feuille de route

- [x] Lab Docker et premières vérifications SSH
- [x] Moteur d'audit à plugins rattaché au guide ANSSI
- [ ] Machine cible « durcie » pour comparer les résultats
- [ ] Rapport HTML / PDF
- [ ] Configuration externalisée et audit de plusieurs machines
- [ ] Interface web (Django) avec historique des audits
- [ ] Module d'analyse de risques inspiré d'EBIOS Risk Manager
- [ ] Ajout du référentiel ISO 27001 avec correspondances inter-référentiels
- [ ] Authentification, rôles et journal d'audit de l'application
- [ ] Pipeline CI/CD avec tests et analyse de sécurité (pytest, Bandit, pip-audit)

## Avertissement

Cet outil est destiné à auditer des machines dont vous êtes propriétaire ou pour lesquelles vous disposez d'une autorisation explicite. Le lab fourni est volontairement vulnérable : ne l'exposez jamais sur un réseau.
