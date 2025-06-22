# planning_PE

Application de planification développée avec Django, utilisant HTMX et Alpine.js pour une interface utilisateur moderne et réactive.

## Fonctionnalités

### Interface utilisateur
- **Interface moderne et responsive** : UI avec Tailwind CSS
- **Interactions fluides** : HTMX pour les requêtes AJAX sans rechargement de page
- **Composants réactifs** : Alpine.js pour l'interactivité côté client
- **Split buttons** : Actions d'édition et suppression combinées
- **Modales HTMX** : Formulaires de création/modification sans navigation

### Gestion des agents
- **CRUD complet** : Création, lecture, modification, suppression
- **Recherche en temps réel** : Recherche par matricule, prénom ou nom avec délai de 300ms
- **Tri multi-colonnes** : Tri par matricule, nom, grade ou date d'embauche (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Filtrage avancé** : Option pour masquer les agents partis
- **Noms en capitales** : Affichage des noms de famille en MAJUSCULES
- **Statuts visuels** : Badges colorés pour les grades et statuts (actif/parti)

### Gestion des fonctions
- **CRUD complet** : Création, lecture, modification, suppression
- **Recherche en temps réel** : Recherche par désignation ou description avec délai de 300ms
- **Tri multi-colonnes** : Tri par désignation ou statut (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Filtrage avancé** : Option pour masquer les fonctions inactives
- **Split buttons** : Actions d'édition et suppression combinées
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Statuts visuels** : Badges colorés pour les statuts (actif/inactif)

### Authentification et sécurité
- **Interface d'administration sécurisée** : Accès restreint aux utilisateurs staff
- **Protection CSRF** : Tokens CSRF pour toutes les requêtes HTMX
- **Permissions** : Contrôle d'accès basé sur le statut utilisateur

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

Générer des données de test (optionnel) :
```bash
python manage.py create_test_agents
python manage.py create_test_functions
```

La commande **create_test_agents** crée 50 agents avec :
- Noms français aléatoires
- Grades distribués (Execution, Maitrise, Cadre)
- Dates d'embauche entre 2010-2024
- ~10% d'agents partis

La commande **create_test_functions** crée 30 fonctions avec :
- Fonctions techniques (10) : Développeur, DevOps, etc.
- Fonctions management (10) : Chef de projet, Directeur, etc.
- Fonctions opérationnelles (10) : Comptable, Secrétaire, etc.
- Descriptions détaillées pour chaque fonction
- ~20% de fonctions inactives

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