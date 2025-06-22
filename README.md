# planning_PE

Application de planification développée avec Django, utilisant HTMX et Alpine.js pour une interface utilisateur moderne et réactive.

## Fonctionnalités

- **Interface utilisateur moderne** : UI responsive avec Tailwind CSS
- **Interactions fluides** : HTMX pour les requêtes AJAX sans rechargement de page
- **Composants réactifs** : Alpine.js pour l'interactivité côté client
- **Gestion des agents** : CRUD complet avec recherche et pagination
- **Gestion des fonctions** : CRUD complet avec interface modale
- **Authentification** : Interface d'administration sécurisée
- **Support multi-utilisateurs** : Permissions basées sur le statut staff

## Installation

Installer un environnement virtuel :
```bash
python -m venv venv
```

Activer l'environnement virtuel :
```bash
source venv/bin/activate
```

Installer les dépendances :
```bash
pip install -r requirements.txt
```

Effectuer les migrations :
```bash
python manage.py migrate
```

## Utilisation

Lancer le serveur de développement :
```bash
python manage.py runserver
```

### Accès à l'application

- **Page d'accueil** : http://127.0.0.1:8000/
- **Interface d'administration Django** : http://127.0.0.1:8000/admin/

### Identifiants d'administration

- **Utilisateur** : azerty
- **Email** : azerty@azerty.com
- **Mot de passe** : azerty

### Navigation

L'interface principale propose :
- **Accueil** : Vue d'ensemble avec placeholder pour le planning
- **Administration** (menu déroulant pour les utilisateurs staff) :
  - Gestion des Agents
  - Gestion des Fonctions
  - Interface d'Administration Django

## Tests

Lancer les tests :
```bash
DJANGO_SETTINGS_MODULE=planning_pe.settings python -m pytest tests/ -v
```

## Modèles

### Agent
- **matricule** : Une lettre suivie de 4 chiffres (ex: A1234)
- **first_name** : Prénom
- **last_name** : Nom de famille
- **grade** : Agent, Maitrise, ou Cadre
- **hire_date** : Date d'embauche (par défaut: date de création)
- **departure_date** : Date de départ (optionnel, doit être postérieure à la date d'embauche)

### Fonction
- **designation** : Nom de la fonction
- **description** : Description de la fonction (optionnel)
- **status** : Statut actif/inactif (par défaut: actif)