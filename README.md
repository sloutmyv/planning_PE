# planning_PE

Application de planification développée avec Django, utilisant HTMX et Alpine.js pour une interface utilisateur moderne et réactive.

## Fonctionnalités

### Interface utilisateur
- **Interface moderne et responsive** : UI avec Tailwind CSS
- **Interactions fluides** : HTMX pour les requêtes AJAX sans rechargement de page
- **Composants réactifs** : Alpine.js pour l'interactivité côté client
- **Split buttons** : Actions d'édition et suppression combinées
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Design harmonisé** : Boutons de création avec palette de couleurs bleue unifiée
- **Indicateurs visuels** : Statuts actif/expiré pour les périodes avec codes couleur

### Gestion des agents
- **CRUD complet** : Création, lecture, modification, suppression
- **Recherche en temps réel** : Recherche par matricule, prénom ou nom avec délai de 300ms
- **Tri multi-colonnes** : Tri par matricule, nom, grade, permission ou date d'embauche (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Filtrage avancé** : Option pour masquer les agents partis
- **Noms en capitales** : Affichage des noms de famille en MAJUSCULES
- **Statuts visuels** : Badges colorés pour les grades et statuts (actif/parti)
- **Gestion des permissions** : Modification des niveaux de permission directement dans la liste
- **Permissions intégrées** : Création d'utilisateurs automatique avec comptes Django liés

### Gestion des postes
- **CRUD complet** : Création, lecture, modification, suppression
- **Recherche en temps réel** : Recherche par désignation ou description avec délai de 300ms
- **Tri multi-colonnes** : Tri par désignation ou statut (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Filtrage avancé** : Option pour masquer les postes inactifs
- **Split buttons** : Actions d'édition et suppression combinées
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Statuts visuels** : Badges colorés pour les statuts (actif/inactif)
- **Descriptions complètes** : Affichage intégral des descriptions sans troncature

### Gestion des types d'horaire
- **CRUD complet** : Création, lecture, modification, suppression
- **Recherche en temps réel** : Recherche par désignation ou abréviation avec délai de 300ms
- **Tri multi-colonnes** : Tri par désignation, abréviation ou couleur (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Split buttons** : Actions d'édition et suppression combinées
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Sélecteur de couleur** : Choix de couleur hexadécimale pour identification visuelle
- **Abréviation optionnelle** : Code court de 2-3 lettres majuscules (ex: MAT, APM, NUIT)
- **Validation automatique** : Contrôle du format des couleurs et abréviations
- **Affichage coloré** : Aperçu des couleurs dans la liste avec codes hexadécimaux
- **Protection contre suppression** : Avertissements visuels et blocage de suppression pour les types liés à des plans de rotation

### Gestion des plans de rotation quotidienne
- **Interface accordion** : Expansion/contraction des plans pour visualiser les périodes
- **Visualisation multiple** : Plusieurs plans peuvent être ouverts simultanément
- **Gestion des périodes intégrée** : Ajout/modification/suppression des périodes directement dans chaque plan
- **Chargement à la demande** : Les périodes se chargent uniquement à l'expansion du plan
- **Validation métier** : Contrôle des chevauchements de périodes et validation des horaires de nuit
- **Association automatique** : Les nouvelles périodes sont automatiquement liées au plan courant
- **Affichage structuré** : Grille alignée avec colonnes dédiées (Nom, Type d'horaire, Nombre de périodes, Date de création)
- **Indicateurs de statut** : Identification visuelle des périodes expirées avec couleurs et badges
- **Terminologie cohérente** : Utilisation systématique de "plans de rotation quotidienne" dans toute l'interface

### Authentification et sécurité
- **Système de permissions à 4 niveaux** : 
  - **SA (Super Administrateur)** : Accès complet Django Admin + gestion application
  - **A (Administrateur)** : Gestion agents/postes + modification permissions
  - **E (Éditeur)** : Édition du planning (à implémenter)
  - **R (Lecteur)** : Visualisation seulement
- **Connexion personnalisée** : Interface de login moderne avec logo d'entreprise centré
- **Changement de mot de passe obligatoire** : Premier login force la mise à jour du mot de passe
- **Comptes automatiques** : Création automatique d'utilisateurs Django pour chaque agent
- **Protection CSRF** : Tokens CSRF pour toutes les requêtes HTMX
- **Validation des permissions** : Contrôles server-side pour tous les changements
- **Gestion transactionnelle** : Transactions atomiques pour toutes les opérations critiques

## Architecture technique

### Base de données et intégrité des données
- **Gestion transactionnelle complète** : Toutes les opérations critiques sont protégées par `@transaction.atomic`
- **Opérations atomiques** : Création d'agents, modifications de permissions, suppression avec rollback automatique
- **Intégrité référentielle** : Contraintes de clés étrangères entre Agent et User Django
- **Validation côté serveur** : Validation complète des données avant persistance
- **Prêt pour PostgreSQL** : Architecture préparée pour migration vers base de données production

### Opérations transactionnelles protégées
- **Création d'agents** : Création Agent + compte User Django en une transaction
- **Modification de permissions** : Mise à jour Agent + permissions Django User atomique
- **Changement de mot de passe** : Mise à jour User + statut Agent synchronisée
- **Suppression d'agents** : Suppression cascadée Agent + User avec rollback
- **Édition d'agents** : Modifications des données Agent + User en transaction

### Gestion des erreurs et récupération
- **Rollback automatique** : Annulation complète des opérations en cas d'erreur
- **Messages d'erreur détaillés** : Feedback utilisateur en cas de problème
- **Logging des exceptions** : Traçabilité des erreurs pour debugging
- **Validation préalable** : Contrôles avant exécution des transactions

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
python manage.py create_test_agents --update
python manage.py create_test_functions
python manage.py create_test_functions --update
python manage.py create_test_schedule_types
python manage.py create_test_schedule_types --update
```

La commande **create_test_agents** charge les agents depuis une base de données JSON :
- **Mode création** : Crée de nouveaux agents, ignore les existants
- **Mode mise à jour** (`--update`) : Met à jour les agents existants si les données JSON ont changé
- **Mode nettoyage** (`--clear`) : Supprime tous les agents existants avant de créer
- Données réelles d'employés avec matricules, grades et permissions
- Détection automatique des changements de données
- Statistiques détaillées par grade et niveau de permission

La commande **create_test_functions** charge les fonctions depuis une base de données JSON :
- **Mode création** : Crée de nouvelles fonctions, ignore les existantes
- **Mode mise à jour** (`--update`) : Met à jour les fonctions existantes si les données JSON ont changé
- **Mode nettoyage** (`--clear`) : Supprime toutes les fonctions existantes avant de créer
- Fonctions spécialisées pour une centrale électrique (exploitation, maintenance, logistique)
- Détection automatique des changements de description et statut
- Statistiques détaillées par statut (actif/inactif)

La commande **create_test_schedule_types** charge les types d'horaire depuis une base de données JSON :
- **Mode création** : Crée de nouveaux types d'horaire, ignore les existants
- **Mode mise à jour** (`--update`) : Met à jour les types d'horaire existants si les données JSON ont changé
- **Mode nettoyage** (`--clear`) : Supprime tous les types d'horaire existants avant de créer
- Types d'horaire prédéfinis avec codes couleur (JT, CP, JTC, NTC, FE, FS, etc.)
- Détection automatique des changements d'abréviation et couleur
- Statistiques détaillées avec taux d'abréviations définies

Réinitialiser la base de données (optionnel) :
```bash
python manage.py reset_database --confirm
```

La commande **reset_database** effectue une remise à zéro complète de la base de données :
- **Suppression totale** : Tous les agents, fonctions et comptes utilisateurs
- **Préservation des superutilisateurs** : Sauvegarde et restauration automatique
- **Nettoyage complet** : Élimine tous les comptes utilisateurs réguliers
- **Sécurité** : Nécessite le flag `--confirm` pour confirmation
- **Restauration intégrale** : Recrée les superutilisateurs avec toutes leurs données

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
  - Gestion des Postes
  - Types d'Horaire
  - Plans de Rotation
  - Interface d'Administration Django

## Tests

Lancer les tests :
```bash
DJANGO_SETTINGS_MODULE=planning_pe.settings python -m pytest tests/ -v
```

## Modèles

### Agent
- **last_name** : Nom de famille (ordre d'affichage 1)
- **first_name** : Prénom (ordre d'affichage 2)
- **matricule** : Une lettre suivie de 4 chiffres (ex: A1234) (ordre d'affichage 3)
- **grade** : Agent, Maîtrise, ou Cadre (ordre d'affichage 4)
- **hire_date** : Date d'embauche (par défaut: date de création) (ordre d'affichage 5)
- **departure_date** : Date de départ (optionnel, doit être postérieure à la date d'embauche) (ordre d'affichage 6)
- **permission_level** : Niveau de permission (V/E/A/S) (ordre d'affichage 7, visible aux admins seulement)
- **user** : Liaison avec compte utilisateur Django (créé automatiquement)
- **password_changed** : Indicateur de changement de mot de passe initial

### Fonction (Poste)
- **designation** : Nom du poste
- **description** : Description du poste (optionnel, affichage complet sans troncature)
- **status** : Statut actif/inactif (par défaut: actif)

### ScheduleType (Type d'Horaire)
- **designation** : Nom complet du type d'horaire (unique)
- **short_designation** : Abréviation optionnelle de 2-3 lettres majuscules (unique, ex: MAT, APM, NUIT)
- **color** : Code couleur hexadécimal pour identification visuelle (ex: #FF0000)
- **Validation automatique** : Format hexadécimal pour les couleurs et format alphabétique majuscule pour les abréviations

### DailyRotationPlan (Plan de Rotation Quotidienne)
- **designation** : Nom du plan de rotation (unique)
- **description** : Description optionnelle du plan
- **schedule_type** : Type d'horaire associé (clé étrangère vers ScheduleType)
- **Relation avec RotationPeriod** : Un plan peut avoir plusieurs périodes

### RotationPeriod (Période de Rotation)
- **daily_rotation_plan** : Plan de rotation parent (clé étrangère)
- **start_date** / **end_date** : Période de validité (dates)
- **start_time** / **end_time** : Horaires quotidiens (heures)
- **Validation métier** : Contrôle des chevauchements et validation des horaires de nuit (22h-6h)
- **Méthodes calculées** : Detection automatique des équipes de nuit et calcul de durée
- **Statut d'activité** : Méthode `is_active()` pour détecter les périodes expirées (date de fin antérieure à aujourd'hui)