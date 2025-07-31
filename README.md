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
- **Navigation iconographique** : Menus avec icônes thématiques (📖 Manuel, 🗃️ Bases de données, ⚙️ Administration)
- **Footer corporate** : Pied de page unifié avec identité "🚀 CCORP 2025"
- **Manuel utilisateur intégré** : Guide complet accessible depuis le menu Administration avec sommaire interactif

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
- **Export/Import sécurisé** : Fonctionnalités d'export et import JSON pour superutilisateurs uniquement via Django Admin

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
- **Protection contre suppression** : Avertissements visuels et blocage de suppression pour les types liés à des rythmes quotidiens

### Gestion des rythmes quotidiens
- **Interface accordion** : Expansion/contraction des rythmes pour visualiser les périodes
- **Visualisation multiple** : Plusieurs rythmes peuvent être ouverts simultanément
- **Gestion des périodes intégrée** : Ajout/modification/suppression des périodes directement dans chaque rythme
- **Chargement à la demande** : Les périodes se chargent uniquement à l'expansion du rythme
- **Validation métier** : Contrôle des chevauchements de périodes et validation des horaires de nuit
- **Association automatique** : Les nouvelles périodes sont automatiquement liées au rythme courant
- **Affichage structuré** : Grille alignée avec colonnes dédiées (Nom, Type d'horaire, Nombre de périodes, Date de création)
- **Indicateurs de statut** : Identification visuelle des périodes expirées avec couleurs et badges
- **Terminologie cohérente** : Utilisation systématique de "rythmes quotidiens" dans toute l'interface

### Gestion des roulements hebdomadaires
- **Interface accordion moderne** : Expansion/contraction des plannings pour visualiser les périodes, identique aux rythmes quotidiens
- **Tableau hebdomadaire interactif** : Visualisation des 7 jours de la semaine en format tableau avec assignation directe
- **Gestion multiple des rythmes** : Possibilité d'assigner plusieurs rythmes quotidiens par jour pour couvrir toute la journée
- **Interface sans détails** : Suppression complète des vues détail, toute la gestion se fait depuis la liste principale
- **Assignation visuelle intuitive** : Pills/badges colorés pour chaque rythme assigné avec boutons de suppression individuels
- **Ajout simplifié** : Boutons "Ajouter" dans chaque cellule de jour pour assignation rapide via modal
- **Renumération automatique** : Les semaines se renumèrent automatiquement lors de suppression (S1, S2, S3, etc.)
- **Actions intégrées** : Boutons d'édition/suppression directement dans chaque ligne d'accordion
- **Modales HTMX cohérentes** : Formulaires de création/modification avec la même expérience utilisateur que les autres modules
- **Chargement dynamique** : Les périodes se chargent à la demande lors de l'expansion
- **Gestion complète des périodes** : Ajout, modification, suppression et visualisation des périodes dans l'interface accordion
- **API dédiée** : Endpoints REST pour le chargement des données de périodes et semaines
- **Validation métier** : Contrôle des chevauchements de périodes et cohérence des dates
- **Interface simplifiée** : Suppression de l'affichage du type et des pauses dans la vue liste pour plus de clarté
- **Workflow optimisé** : Interface qui reste ouverte après ajout/suppression de rythmes pour un travail continu
- **Validation anti-doublons** : Prévention de l'assignation du même rythme plusieurs fois sur un même jour
- **Mise à jour temps réel** : Actualisation immédiate des données sans rechargement de page
- **Duplication de périodes** : Fonction de copie complète des périodes avec toutes leurs semaines et rythmes quotidiens
- **Création de semaines instantanée** : Ajout de nouvelles semaines sans formulaire avec numérotation automatique (S1, S2, S3, etc.)
- **Duplication de semaines instantanée** : Copie complète des semaines avec tous leurs rythmes quotidiens assignés, sans confirmation
- **Actions silencieuses** : Création et duplication sans interruption, avec mise à jour immédiate de l'interface
- **Préservation du contexte** : Maintien de la position dans les accordéons et de l'état des dropdowns lors des opérations
- **Tooltips informatifs** : Survol des rythmes quotidiens affiche leur description complète dans une infobulle

### Gestion des jours fériés
- **CRUD complet** : Création, lecture, modification, suppression des jours fériés
- **Recherche en temps réel** : Recherche par nom ou date avec délai de 300ms
- **Tri intelligent par année** : Tri automatique par année puis par date lors du tri par date (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Fonction de duplication** : Bouton de copie pour créer rapidement des jours fériés récurrents avec même nom mais nouvelle date
- **Validation anti-doublons** : Prévention stricte des doublons sur la même date avec messages d'erreur informatifs
- **Compteurs par année** : Badges d'affichage du nombre de jours fériés par année, triés du plus récent au plus ancien
- **Interface cohérente** : Même design et expérience utilisateur que les autres modules d'administration
- **Accès sécurisé** : Réservé aux administrateurs uniquement
- **Affichage français** : Format de date français (jj/mm/aaaa) avec indication de l'année sous chaque date
- **Messages informatifs** : Notifications de succès et erreurs en français
- **Mise à jour dynamique** : Les compteurs par année se mettent à jour automatiquement lors des suppressions

### Gestion des départements
- **CRUD complet** : Création, lecture, modification, suppression des départements
- **Recherche en temps réel** : Recherche par nom de département avec délai de 300ms
- **Tri multi-colonnes** : Tri par nom ou ordre d'affichage (ASC/DESC)
- **Pagination** : Navigation par pages avec conservation des filtres
- **Modales HTMX** : Formulaires de création/modification sans navigation
- **Ordre hiérarchique intelligent** : Auto-incrémentation par 10 (10, 20, 30, etc.) pour faciliter les réorganisations
- **Validation anti-doublons** : Prévention stricte des doublons d'ordre avec messages d'erreur informatifs
- **Suggestions automatiques** : Placeholder montrant l'ordre suggéré pour les nouveaux départements
- **Champ optionnel** : Ordre peut être laissé vide pour attribution automatique
- **Interface cohérente** : Même design et expérience utilisateur que les autres modules d'administration
- **Accès sécurisé** : Réservé aux administrateurs uniquement
- **Affichage français** : Format de date français (jj/mm/aaaa) pour les dates de création
- **Messages informatifs** : Notifications de succès et erreurs en français
- **Mise à jour dynamique** : Interface HTMX pour des interactions fluides

### Gestion des équipes
- **Interface en cartes moderne** : Affichage des équipes en grille responsive avec couleurs distinctives
- **Gestion séquentielle des postes** : Création d'équipe puis ajout progressif des postes de travail
- **Recherche et filtrage avancés** : Recherche par nom d'équipe, description ou département avec filtre par département
- **Modales HTMX fluides** : Formulaires de création/modification d'équipes et postes sans rechargement de page
- **Validation intelligente des prérequis** : 
  - Vérification de l'existence des départements avant création d'équipe
  - Contrôle de l'existence des fonctions actives avant ajout de poste
  - Messages informatifs pour les plans de roulement et agents manquants
- **Affectation flexible des postes** :
  - Sélection de fonction parmi les postes actifs
  - **Postes multiples autorisés** : Possibilité d'ajouter plusieurs postes de la même fonction dans une équipe
  - **Système d'affectations historiques** : Gestion des assignations d'agents et roulements avec dates de validité non chevauchantes
  - Configuration par poste de la prise en compte des jours fériés
  - Ordre d'affichage personnalisé pour organiser les postes dans l'équipe
- **Gestion d'affectations avancée** :
  - **Affectations multiples avec historique** : Assignation de plusieurs agents/roulements par poste avec périodes de validité
  - **Prévention des chevauchements** : Validation automatique des dates pour éviter les conflits d'affectation
  - **Interface d'édition intégrée** : Gestion complète des affectations directement dans l'interface métier
  - **CRUD complet des affectations** : Ajout, modification, suppression des assignations avec validation en temps réel
  - **Messages d'erreur spécifiques** : Feedback détaillé pour les conflits de recouvrement d'affectations
  - **Affichage des affectations actuelles** : Visualisation en temps réel des agents et roulements actuellement assignés
  - **Interface adaptative** : Messages informatifs quand aucune affectation n'est définie sur un poste
- **Contraintes métier optimisées** :
  - Validation des dates d'affectation avec prévention des chevauchements
  - Filtrage automatique des fonctions inactives et plans sans période
  - Ordre unique par poste dans chaque équipe pour l'affichage
- **Interface visuelle riche** :
  - Codes couleur personnalisés par équipe pour identification rapide
  - Badges colorés pour les plans de roulement selon leur type d'horaire
  - Indicateurs visuels pour la prise en compte des jours fériés
  - Affichage du statut d'assignation des agents (assigné/vacant)
  - **Messages d'état contextuels** : "Pas d'agent affecté au poste à ce jour" / "Pas de roulement affecté au poste à ce jour"
- **Actions contextuelles simplifiées** :
  - Menu déroulant par équipe (modifier, ajouter poste, supprimer)
  - Actions individuelles par poste (modifier, supprimer)
  - **Gestion d'affectations intégrée** : Modification/suppression/ajout d'affectations directement dans le formulaire de poste
  - **Navigation optimisée** : Bouton "Sauvegarder et retourner" qui sauvegarde les modifications avant de revenir à la liste
  - Modales de confirmation pour les suppressions critiques
- **Intégration dashboard** : Compteur d'équipes en temps réel dans le tableau de bord administrateur
- **Navigation intégrée** : Lien "Équipes" dans le menu Administration, positionné après "Agents"

### Authentification et sécurité
- **Système de permissions à 4 niveaux** : 
  - **SA (Super Administrateur)** : Accès complet Django Admin + gestion application + export/import
  - **A (Administrateur)** : Gestion agents/postes + modification permissions
  - **E (Éditeur)** : Édition du planning (à implémenter)
  - **R (Lecteur)** : Visualisation seulement
- **Navigation intelligente** : Menu Administration adaptatif selon le niveau de permission utilisateur
- **Accès superutilisateur** : Interface d'administration complète accessible via dropdown pour les superutilisateurs
- **Connexion personnalisée** : Interface de login moderne avec logo d'entreprise centré
- **Changement de mot de passe obligatoire** : Premier login force la mise à jour du mot de passe
- **Comptes automatiques** : Création automatique d'utilisateurs Django pour chaque agent
- **Protection CSRF** : Tokens CSRF pour toutes les requêtes HTMX
- **Validation des permissions** : Contrôles server-side pour tous les changements
- **Gestion transactionnelle** : Transactions atomiques pour toutes les opérations critiques

## Améliorations récentes

### Refonte complète du système d'affectations d'équipes (Juillet 2025)
- **Système d'affectations historiques** : Remplacement des affectations uniques par un système de périodes multiples avec dates de validité
- **Gestion des chevauchements** : Validation automatique empêchant les affectations simultanées d'agents ou roulements sur un même poste
- **Interface d'édition intégrée** : Suppression de la dépendance à Django Admin, gestion complète des affectations dans l'interface métier
- **CRUD complet des affectations** : Ajout, modification et suppression des assignations directement dans le formulaire de poste d'équipe
- **Messages d'erreur détaillés** : Feedback spécifique pour les conflits de recouvrement ("Cette période chevauche avec une autre affectation d'agent/roulement")
- **Interface adaptative améliorée** : Messages contextuels "Pas d'agent/roulement affecté au poste à ce jour" quand aucune affectation n'est définie
- **Navigation optimisée** : Bouton "Sauvegarder et retourner" remplace les actions séparées pour une expérience utilisateur fluide
- **Historique complet** : Conservation de toutes les affectations passées, présentes et futures avec tri automatique (actuelles en premier)
- **Validation en temps réel** : Contrôles de cohérence des dates et prévention des erreurs de saisie
- **Simplification interface** : Suppression des doublons "Ajouter nouveau poste" sur les cartes d'équipes
- **Corrections JavaScript** : Résolution des problèmes d'édition qui disparaissait et des erreurs "Load failed" lors de suppressions
- **Architecture transactionnelle** : Toutes les opérations d'affectation protégées par des transactions atomiques Django

## Améliorations précédentes

### Optimisations UX des roulements hebdomadaires (Juillet 2025)
- **Résolution du problème de fermeture des accordéons** : Les dropdowns restent désormais ouverts après ajout/suppression de rythmes
- **Workflow continu amélioré** : Plus besoin de rouvrir les sections après chaque modification
- **Validation anti-doublons renforcée** : Impossible d'assigner le même rythme deux fois sur la même journée avec message d'erreur explicite
- **Correction de l'édition des périodes** : Résolution du bug empêchant la modification des dates de fin de période
- **Mise à jour temps réel optimisée** : Actualisation immédiate des données via API sans rechargement complet
- **Gestion d'erreurs améliorée** : Affichage approprié des erreurs de validation dans les modales HTMX

### Gestion instantanée des semaines (Juillet 2025)
- **Actions directes sans formulaire** : Suppression complète des modales de confirmation pour la création et duplication de semaines
- **Création instantanée** : Bouton "Ajouter une semaine" exécute l'action immédiatement avec numérotation automatique
- **Duplication instantanée** : Bouton de duplication copie immédiatement la semaine avec tous ses rythmes quotidiens assignés
- **Interface fluide** : Aucune interruption, alerte ou rechargement de page - les semaines apparaissent instantanément
- **Préservation de l'état** : Maintien de la position dans les accordéons et de l'état d'expansion des dropdowns
- **Workflow accéléré** : Possibilité de créer/dupliquer plusieurs semaines rapidement en succession
- **Numérotation intelligente** : Auto-incrémentation des numéros de semaine (S1 → S2 → S3, etc.) sans intervention manuelle
- **Tooltips de validation** : Survol des rythmes quotidiens affiche nom et description pour vérification rapide

### Gestion des données et sécurité (Juillet 2025)
- **Export JSON sécurisé** : Export complet de tous les modèles au format JSON avec datage automatique (YYYY-MM-DD_model.json)
- **Import avec remplacement** : Import JSON avec remplacement complet de la base de données et confirmations multiples
- **Protection superutilisateur** : Préservation automatique des comptes superutilisateurs lors des imports
- **Interface Django Admin** : Fonctionnalités d'export/import accessibles uniquement via l'interface d'administration Django
- **Export global unifié** : Bouton d'export global sur la page admin principale générant un fichier ZIP avec tous les modèles
- **Export individuel par modèle** : Boutons d'export/import spécifiques pour chaque modèle (Agents, Départements, Fonctions, etc.)
- **Validation anti-conflit** : Résolution automatique des conflits UNIQUE constraint lors des imports
- **Réinitialisation sécurisée** : Tous les mots de passe sont réinitialisés à "azerty" lors des imports d'agents
- **Navigation superutilisateur** : Menu Administration unifié pour accès rapide aux fonctionnalités app et Django Admin
- **Import/Export complet** : Support de tous les modèles système (9 modèles) avec validation des dépendances hiérarchiques

### Améliorations interface et documentation (Juillet 2025)
- **Manuel utilisateur métier** : Guide complet refondu pour administrateurs métier avec contenu spécialisé et workflow détaillé
- **Documentation Import/Export** : Section complète dans le manuel utilisateur expliquant les fonctionnalités d'import/export avec ordre d'importation obligatoire
- **Navigation iconographique** : Ajout d'icônes thématiques pour tous les menus (📖 Manuel, 🗃️ Bases de données, ⚙️ Administration)
- **Footer corporate unifié** : Pied de page avec identité "🚀 CCORP 2025" sur toutes les pages
- **Ordre logique des menus** : Réorganisation selon la séquence de création recommandée (Départements → Postes → Agents → Jours fériés → Types → Rythmes → Roulements)
- **Documentation workflow** : Explication détaillée des deux fonctions principales et des 6 étapes critiques de création
- **Cas d'usage automatiques** : Documentation complète des comportements système selon configuration des postes
- **Amélioration visuelle** : Listes hiérarchiques avec puces visuelles et meilleure typography pour la lisibilité
- **Design cohérent** : Harmonisation visuelle avec icônes et codes couleur dans toute l'interface
- **Guide des dépendances** : Documentation détaillée de l'ordre d'importation en 10 étapes avec noms de fichiers JSON spécifiques

### Corrections techniques récentes (Juillet 2025)
- **Validation des équipes de nuit améliorée** : Support complet des équipes de nuit débutant dès 16:00 avec validation automatique (16:00-08:00, 22:00-06:00)
- **Mise à jour dynamique des compteurs de périodes** : Les badges de nombre de périodes se mettent à jour automatiquement sans rechargement de page
- **Stabilité de l'interface** : Amélioration de la stabilité visuelle de la liste des rythmes quotidiens lors de l'ouverture des modales
- **Désactivation de la validation HTML5** : Suppression des conflits entre validation navigateur et validation Django pour les horaires de nuit
- **Formulaires HTMX** : Correction des champs cachés manquants dans l'édition des périodes
- **Validation côté serveur** : Amélioration de la gestion des erreurs de validation avec retour approprié des formulaires
- **Actualisation des données** : Implémentation d'un système de refresh ciblé via Alpine.js et API REST
- **Messages d'erreur** : Affichage cohérent des erreurs de validation dans toutes les modales
- **Validation des chevauchements** : Prévention des périodes qui se chevauchent pour les rythmes quotidiens et roulements hebdomadaires
- **Couleurs dynamiques des rythmes** : Badges de rythmes quotidiens avec couleurs correspondant aux types d'horaire
- **Contraste automatique** : Adaptation du texte (blanc/noir) selon la luminosité des couleurs de fond
- **Suppression de la pagination** : Toutes les pages d'administration affichent maintenant les listes complètes sur une seule page pour une navigation simplifiée
- **Optimisation de la largeur des pages** : Ajustement de la largeur des pages pour une meilleure cohérence visuelle entre les modules d'administration
- **Validation des rythmes quotidiens** : Protection complète empêchant l'assignation de rythmes quotidiens sans période définie aux roulements hebdomadaires

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
- **Administration** (menu déroulant adaptatif selon les permissions, ordre logique de création) :
  - 📖 Manuel Utilisateur (guide métier complet avec sommaire interactif)
  - 🗃️ Départements (base hiérarchique obligatoire)
  - 🗃️ Liste des Postes (fonctions de l'organisation)
  - 🗃️ Liste des Agents (personnel avec permissions)
  - 🗃️ Équipes (groupes de travail avec postes assignés)
  - 🗃️ Jours Fériés (dates exceptionnelles)
  - 🗃️ Types d'Horaires (catégories de travail)
  - 🗃️ Rythmes Quotidien (modèles d'horaires quotidiens)
  - 🗃️ Roulements Hebdomadaires (plannings récurrents)
  - ⚙️ Interface d'Administration Django (pour superutilisateurs)

### Manuel utilisateur intégré

**Guide métier complet pour administrateurs** accessible depuis le menu Administration :
- **📋 Sommaire interactif** : Navigation rapide par ancres vers les différentes sections
- **🏠 Introduction** : Présentation de Planning PE et objectifs pour administrateurs métier
- **⚙️ Deux fonctions principales** : 
  1. Création d'équipes et gestion des affectations (départements → équipes → postes → agents/plans/règles)
  2. Création de plans de roulement (rythmes hebdomadaires réutilisables)
- **📋 Ordre recommandé de création** : Séquence critique en 6 étapes pour éviter les erreurs de dépendances
  1. Départements (obligatoire, base hiérarchique)
  2. Équipes (rattachées aux départements)
  3. Postes (avec affectation agent/plan/règles jours fériés)
  4. Types d'horaires (catégories de travail)
  5. Rythmes quotidiens (compositions journalières + types d'horaire)
  6. Plans de roulement (séquences hebdomadaires de rythmes quotidiens)
- **🔄 Cas particuliers** : Comportements automatiques du système selon la configuration des postes
  - Poste avec plan mais sans agent → "Poste Vacant" (PV)
  - Poste avec agent mais sans plan → Planning vide
  - Poste avec agent et plan → Génération automatique
  - Gestion des jours fériés (inclusion/exclusion)
  - Principe de préservation des données manuelles

### Fonctionnalités spéciales superutilisateur

**Export global de toutes les données** (accessible via Django Admin uniquement) :
1. Se connecter à l'interface Django Admin : http://127.0.0.1:8000/admin/
2. Naviguer vers **Core** (page principale de l'application)
3. Utiliser le bouton **📊 Exporter Toutes les Données**
4. L'export génère un fichier ZIP `YYYY-MM-DD_HHMMSS_export_global_planning.zip` contenant tous les modèles au format JSON

**Export/Import par modèle** (accessible via Django Admin uniquement) :
1. Se connecter à l'interface Django Admin : http://127.0.0.1:8000/admin/
2. Naviguer vers **Core > [Modèle]** (Agents, Départements, Fonctions, Types d'Horaires, etc.)
3. Utiliser les boutons **📊 Exporter JSON** et **⚠️ Importer JSON**
4. L'export génère un fichier `YYYY-MM-DD_model.json`
5. L'import remplace complètement la base du modèle avec confirmations de sécurité

**Modèles supportés pour export/import individuel** :
- Agents, Départements, Fonctions, Types d'Horaires, Rythmes Quotidiens, Périodes de Rotation
- Plannings de Poste, Périodes de Planning, Semaines de Planning, Plans Quotidiens de Planning

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

### DailyRotationPlan (Rythme Quotidien)
- **designation** : Nom du rythme quotidien (unique)
- **description** : Description optionnelle du rythme
- **schedule_type** : Type d'horaire associé (clé étrangère vers ScheduleType)
- **Relation avec RotationPeriod** : Un rythme peut avoir plusieurs périodes

### RotationPeriod (Période pour rythme quotidien)
- **daily_rotation_plan** : Rythme quotidien parent (clé étrangère)
- **start_date** / **end_date** : Période de validité (dates)
- **start_time** / **end_time** : Horaires quotidiens (heures)
- **Validation métier** : Contrôle des chevauchements et validation des horaires de nuit (22h-6h)
- **Méthodes calculées** : Detection automatique des équipes de nuit et calcul de durée
- **Statut d'activité** : Méthode `is_active()` pour détecter les périodes expirées (date de fin antérieure à aujourd'hui)

### ShiftSchedule (Roulement Hebdomadaire)
- **name** : Nom du roulement hebdomadaire (unique, ex: "Planning Été 2024")
- **type** : Type de planning - choix entre "Journée" et "Quart"
- **break_times** : Nombre de pauses par défaut (généralement 2)
- **Relation avec ShiftSchedulePeriod** : Un roulement peut avoir plusieurs périodes

### ShiftSchedulePeriod (Période de Roulement Hebdomadaire)
- **shift_schedule** : Roulement hebdomadaire parent (clé étrangère)
- **start_date** / **end_date** : Période de validité (dates)
- **Validation métier** : Contrôle des chevauchements de périodes
- **Relation avec ShiftScheduleWeek** : Une période peut avoir plusieurs semaines

### ShiftScheduleWeek (Semaine de Planning)
- **period** : Période parent (clé étrangère vers ShiftSchedulePeriod)
- **week_number** : Numéro de la semaine dans la période (1, 2, 3, etc.)
- **Relation avec ShiftScheduleDailyPlan** : Une semaine peut avoir jusqu'à 7 plans quotidiens
- **Contrainte unique** : Combinaison période + numéro de semaine unique

### ShiftScheduleDailyPlan (Rythme Quotidien de Planning)
- **week** : Semaine parent (clé étrangère vers ShiftScheduleWeek)
- **weekday** : Jour de la semaine (1=Lundi, 7=Dimanche)
- **daily_rotation_plan** : Rythme quotidien assigné (clé étrangère vers DailyRotationPlan)
- **Méthodes utilitaires** : `get_weekday_display_french()` pour affichage des jours en français
- **Contrainte unique** : Combinaison semaine + jour de la semaine unique

### PublicHoliday (Jour Férié)
- **designation** : Nom du jour férié (ex: "Fête du Travail", "Noël")
- **date** : Date du jour férié (format DateField, contrainte unique au niveau base de données)
- **Validation métier** : Prévention des doublons sur la même date avec messages d'erreur informatifs détaillés
- **Méthodes calculées** : `__str__()` retourne "Nom - dd/mm/yyyy" pour affichage français
- **Contrainte unique** : Une seule déclaration de jour férié par date (base de données + formulaire)
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Fonction de duplication** : Vue dédiée pour copier un jour férié existant avec pré-remplissage du nom
- **Tri intelligent** : Tri automatique par année (descendante) puis par date pour une organisation chronologique optimale

### Department (Département)
- **name** : Nom du département (format CharField, contrainte unique au niveau base de données)
- **order** : Ordre d'affichage hiérarchique (PositiveIntegerField, contrainte unique)
- **Auto-incrémentation intelligente** : Ordre automatique par incréments de 10 (10, 20, 30, etc.) si non spécifié
- **Validation métier** : Prévention des doublons d'ordre avec messages d'erreur informatifs détaillés
- **Méthodes calculées** : `get_next_order()` classe method pour calculer le prochain ordre suggéré
- **Contrainte unique** : Un seul département par ordre d'affichage (base de données + formulaire)
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Tri par défaut** : Tri par ordre puis par nom pour affichage hiérarchique cohérent
- **Flexibilité** : Possibilité de modifier l'ordre manuellement pour réorganiser la hiérarchie

### Team (Équipe)
- **designation** : Nom de l'équipe (ex: "Équipe Alpha", "Salle de contrôle A")
- **description** : Description détaillée de l'équipe (optionnel)
- **color** : Code couleur hexadécimal pour identification visuelle (ex: #FF6B6B)
- **department** : Département auquel appartient l'équipe (clé étrangère vers Department)
- **Validation automatique** : Format hexadécimal pour les couleurs
- **Relation avec TeamPosition** : Une équipe peut avoir plusieurs postes
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Tri par défaut** : Tri par ordre de département puis par nom d'équipe

### TeamPosition (Poste d'Équipe)
- **team** : Équipe à laquelle appartient ce poste (clé étrangère vers Team)
- **function** : Fonction/poste assigné à l'équipe (clé étrangère vers Function)
- **considers_holidays** : Ce poste prend-il en compte les jours fériés ? (booléen, défaut: True)
- **order** : Ordre d'affichage du poste dans l'équipe (entier positif)
- **Postes multiples autorisés** : Possibilité d'avoir plusieurs postes de la même fonction dans une équipe
- **Contrainte unique** : Combinaison équipe + ordre unique (pour l'affichage ordonné)
- **Propriétés calculées** : `current_agent` et `current_rotation_plan` pour les affectations actuelles
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Tri par défaut** : Tri par ordre puis par nom de fonction

### TeamPositionAgentAssignment (Affectation d'Agent)
- **team_position** : Poste d'équipe concerné (clé étrangère vers TeamPosition)
- **agent** : Agent assigné (clé étrangère vers Agent)
- **start_date** / **end_date** : Période d'affectation de l'agent
- **Validation anti-chevauchement** : Prévention des affectations qui se chevauchent pour un même poste
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Historique complet** : Conservation de tous les changements d'affectation

### TeamPositionRotationAssignment (Affectation de Roulement)
- **team_position** : Poste d'équipe concerné (clé étrangère vers TeamPosition)
- **rotation_plan** : Roulement hebdomadaire assigné (clé étrangère vers ShiftSchedule)
- **start_date** / **end_date** : Période d'affectation du roulement
- **Validation anti-chevauchement** : Prévention des affectations qui se chevauchent pour un même poste
- **Champs d'audit** : created_at et updated_at pour traçabilité
- **Historique complet** : Conservation de tous les changements de planning

### Gestion des roulements hebdomadaires
- **Architecture hiérarchique** : Roulement hebdomadaire > Période > Semaine > Rythme quotidien
- **Types de planning** : Journée ou Quart
- **Gestion des périodes** : Définition de périodes avec dates de début et fin, validation des chevauchements
- **Planification hebdomadaire** : Ajout de semaines numérotées dans chaque période
- **Assignation quotidienne** : Liaison de rythmes quotidiens à chaque jour de la semaine
- **Interface moderne** : Navigation fluide avec breadcrumbs, modales HTMX et recherche en temps réel
- **Validation métier** : Contrôle des dates et prévention des conflits de planification
- **Flexibilité** : Possibilité d'avoir plusieurs semaines avec des rythmes différents
- **Intégration complète** : Utilisation des rythmes quotidiens existants
- **Recherche simplifiée** : Barre de recherche HTMX sans boutons ni filtres, cohérente avec les autres modules

## Relations et interactions entre les modèles

### Architecture des données
Le système de planification repose sur une architecture relationnelle hiérarchique permettant de créer des plannings complexes et flexibles :

#### 1. Gestion des utilisateurs et permissions
- **Agent ↔ User Django** : Relation OneToOne obligatoire. Chaque agent possède automatiquement un compte utilisateur Django avec authentification
- **Permissions cascadées** : Les niveaux de permission Agent (V/E/A/S) déterminent les droits d'accès aux fonctionnalités de l'application
- **Intégrité transactionnelle** : Création/modification/suppression d'agents synchronisée avec les comptes utilisateurs Django

#### 2. Types d'horaire et rythmes quotidiens
- **ScheduleType → DailyRotationPlan** : Relation ForeignKey. Un type d'horaire peut être utilisé par plusieurs rythmes quotidiens
- **DailyRotationPlan → RotationPeriod** : Relation OneToMany. Un rythme quotidien peut avoir plusieurs périodes de validité dans le temps
- **Validation temporelle** : Les périodes ne peuvent pas se chevaucher pour un même rythme quotidien
- **Statut calculé** : Les périodes expirées (end_date < aujourd'hui) sont automatiquement identifiées

#### 3. Roulements hebdomadaires - Architecture en cascade
L'organisation hiérarchique permet une planification flexible sur plusieurs niveaux :

**ShiftSchedule (Roulement) → ShiftSchedulePeriod (Période) → ShiftScheduleWeek (Semaine) → ShiftScheduleDailyPlan (Plan quotidien)**

- **Niveau 1** : Un roulement hebdomadaire contient plusieurs périodes (ex: "Planning Été", "Planning Hiver")
- **Niveau 2** : Chaque période définit des dates de validité et contient plusieurs semaines
- **Niveau 3** : Chaque semaine est numérotée (S1, S2, S3...) et contient jusqu'à 7 plans quotidiens
- **Niveau 4** : Chaque plan quotidien lie un jour de la semaine à un rythme quotidien existant

#### 4. Contraintes d'intégrité et validation
- **Unicité temporelle** : 
  - Un agent ne peut avoir qu'un seul matricule
  - Une date ne peut avoir qu'un seul jour férié
  - Un département ne peut avoir qu'un seul ordre d'affichage
- **Cohérence relationnelle** :
  - Une semaine ne peut avoir qu'un plan par jour (contrainte unique semaine + jour)
  - Les périodes d'un même roulement ne peuvent se chevaucher
  - Les rythmes quotidiens référencés doivent exister
- **Validation métier** :
  - Les dates de départ d'agents doivent être postérieures aux dates d'embauche
  - Les périodes de rythmes quotidiens doivent avoir des horaires cohérents
  - Les horaires de nuit (22h-6h) sont automatiquement détectés

#### 5. Flux de données et dépendances
- **Création en cascade** : La création d'un agent génère automatiquement un utilisateur Django avec mot de passe par défaut
- **Suppression protégée** : 
  - Les types d'horaire liés à des rythmes quotidiens ne peuvent être supprimés
  - Les rythmes quotidiens assignés à des roulements sont protégés
- **Mise à jour propagée** : Les modifications de permissions d'agents se répercutent sur les comptes utilisateurs Django
- **Export/Import transactionnel** : Les opérations d'export/import préservent l'intégrité référentielle et les contraintes d'unicité