# Journal des décisions — planning_PE

Une entrée par décision structurante : contexte, décision, alternatives écartées, conséquences. Les décisions non tranchées restent en « À décider ».

---

## D-001 — Infrastructure d'orchestration d'agents IA dans le dépôt (2026-10-16)

**Contexte** : le projet va être développé avec des agents IA (OpenCode + Hermes). Sans contrats écrits (rôles, périmètre, portes de vérification), le risque est connu : branches qui se réécrivent, revues qui valident les erreurs de l'auteur, coûts non bornés.

**Décision** : ajouter dans le dépôt les artefacts d'infrastructure — `AGENTS.md` (contexte projet pour agents), `docs/WORKFLOW.md` (rôles + boucle), `docs/MODELS.md` (routage des modèles), `docs/PLAN.md` (unités), `docs/DECISIONS.md` (ce journal), `docs/specs/` (specs), `.opencode/agents/` (agents spécialisés), `scripts/verify.sh` (portes déterministes), CI GitHub.

**Alternatives écartées** : garder la méthode dans des notes externes (perd le contexte au moment utile) ; tout mettre dans le README (le README est destiné aux humains et déjà volumineux).

**Conséquences** : toute unité de travail doit désormais annoncer son périmètre et sa commande de preuve avant de démarrer.

---

## D-002 — Correction de `pytest.ini` (2026-10-16)

**Contexte** : `pytest.ini` utilisait l'en-tête `[tool:pytest]`, qui n'est valide que dans `setup.cfg`. Résultat : les 22 tests ne se lançaient pas sans `DJANGO_SETTINGS_MODULE` exporté manuellement (erreur `ImproperlyConfigured`).

**Décision** : en-tête `[pytest]`. Vérifié : `22 passed`.

**Conséquences** : `pytest` fonctionne tel quel, la CI peut s'appuyer dessus.

---

## D-003 — CI minimale (2026-10-16)

**Décision** : GitHub Actions sur `push`/`pull_request` : installation des dépendances, puis `./scripts/verify.sh` (`manage.py check`, `makemigrations --check --dry-run`, `pytest -q`).

**Pourquoi** : la porte déterministe doit tourner sans intervention humaine — c'est le seul verrou vraiment fiable sur du code généré.

---

## À décider

| # | Sujet | Options | Impact |
| --- | --- | --- | --- |
| A-1 | `SECRET_KEY` et `DEBUG` en dur dans `planning_pe/settings.py`, dépôt **public** | (a) variables d'environnement + `python-decouple`/`django-environ` ; (b) `local_settings.py` non versionné | Sécurité ; prérequis à toute mise en ligne |
| A-2 | Identifiants d'administration (`azerty/azerty`) dans `README.md` d'un dépôt public | Retirer du README, garder la procédure de création (`createsuperuser`) | Sécurité |
| A-3 | Visibilité du dépôt : **public** aujourd'hui, projet à connotation professionnelle (planning d'équipes) | (a) passer en privé ; (b) garder public | Confidentialité des données métier (le code, pas les données) |
| A-4 | Fuseau horaire et langue : `TIME_ZONE='UTC'`, `LANGUAGE_CODE='en-us'` alors que l'usage est en Nouvelle-Calédonie | `Pacific/Noumea` + `fr-fr` | Exactitude des horaires de roulement, cohérence des libellés |
| A-5 | Base de données : SQLite en dev — quelle cible en production ? | Postgres (recommandé pour les contraintes d'intégrité), SQLite si usage mono-poste | Fiabilité multi-utilisateurs, migrations |
| A-6 | Fichiers parasites versionnés (`cookies.txt`, `.DS_Store`) | `git rm --cached` + `.gitignore` | Bruit dans le dépôt |
| A-7 | Environnement d'exécution : VM `ai-workstation` (code-server) et/ou LXC dédié | À trancher quand le déploiement devient un sujet | Séparation dev/exécution |

---

## Modèle d'entrée

```
## D-0NN — <titre> (AAAA-MM-JJ)
**Contexte** : ...
**Décision** : ...
**Alternatives écartées** : ...
**Conséquences** : ...
```
