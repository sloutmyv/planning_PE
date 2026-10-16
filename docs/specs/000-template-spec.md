# Spec NNN — <titre de la fonctionnalité>

Statut : brouillon | validée | implémentée
Date :
Auteur (humain) :
Unité(s) de plan liée(s) : U-<n>

## 1. Objectif

En une ou deux phrases : quel problème métier cette fonctionnalité résout, pour qui.

## 2. Périmètre

- Ce qui est inclus.
- Ce qui est explicitement **hors périmètre** (le plus important : c'est ce qui empêche la dérive des agents).

## 3. Règles métier

Liste numérotée et non ambiguë. Chaque règle doit être vérifiable par un test.

1. …
2. …

## 4. Modèle de données

- Entités touchées : …
- Nouveaux champs / nouvelles entités : …
- Contraintes d'intégrité (unicité, suppression en cascade, `transaction.atomic`) : …
- Migration nécessaire : oui / non

## 5. Interface

- Écrans / URLs : …
- Templates et partials HTMX concernés (convention `core/templates/core/<entite>/…`) : …
- États vides, erreurs utilisateur attendues : …

## 6. Critères d'acceptation (vérifiables)

| # | Critère | Vérifié par |
| --- | --- | --- |
| 1 | … | test `tests/test_xxx.py::test_yyy` |
| 2 | … | `./scripts/verify.sh` |

Un critère qui ne peut pas être vérifié par une commande n'est pas un critère : le reformuler ou l'écarter.

## 7. Risques et points d'attention

- Données existantes à migrer / compatibilité : …
- Impacts sur les fonctionnalités voisines (roulements, affectations d'équipes) : …
- Sécurité / permissions : …

## 8. Décisions ouvertes

- … (à trancher avant implémentation, sinon à consigner dans `DECISIONS.md`)
