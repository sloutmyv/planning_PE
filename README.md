# planning_PE

Application de planification développée avec Django.

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

Accéder à l'interface d'administration : http://127.0.0.1:8000/admin/
- Utilisateur : azerty
- Email : azerty@azerty.com
- Mot de passe : azerty

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