# Workflow d'orchestration des agents IA — planning_PE

Ce document décrit **comment** le travail est découpé, exécuté et vérifié sur ce dépôt. Voir `AGENTS.md` pour le contexte projet et `docs/MODELS.md` pour le choix des modèles.

## 1. Les trois rôles

| Rôle | Fait | Ne fait pas | Livrable |
| --- | --- | --- | --- |
| **Planner** | Découpe l'objectif en unités, nomme les fichiers possédés par chaque unité, écrit les critères d'acceptation et la commande de preuve | Écrire du code d'implémentation | Une spec dans `docs/specs/` + les unités dans `docs/PLAN.md` |
| **Worker** | Implémente **une** unité, dans son worktree, avec ses tests | Toucher hors périmètre, modifier les tests qui le jugent | Une branche + branche + sortie de `./scripts/verify.sh` |
| **Verifier** | Lance les portes déterministes, puis relit le diff **contre la spec** | Modifier le code jugé, savoir qui a écrit quoi | Un verdict avec preuves (commandes, codes de sortie, fichier:ligne) |

**Pourquoi la séparation** : quand le même agent écrit et évalue, l'erreur de génération survit à la relecture (même chemin de raisonnement). Le verifier doit être un **modèle d'une autre famille** que le worker, et travailler dans un contexte différent.

**Quand ne PAS orchestrer** : correction mono-fichier, renommage, petite retouche de template. Un seul agent suffit — la coordination coûte plus cher que le risque évité.

## 2. La boucle, porte par porte

```
SPEC  →  PLAN  →  [WORKER → portes déterministes → VERIFIER]  →  revue humaine  →  merge
(1)      (2)                    (3)         (4)          (5)            (6)
```

1. **Spec** (`docs/specs/NNN-<slug>.md`) : objectif, périmètre, hors-périmètre, critères d'acceptation **vérifiables**.
2. **Plan** (`docs/PLAN.md`) : unités, fichiers possédés, dépendances, commande de preuve. **Validation humaine obligatoire avant d'implémenter.**
3. **Worker** : `git worktree add ../planning_PE-<unite> -b feat/<unite>`, puis agent `build` dans ce worktree.
4. **Portes déterministes** (gratuites, objectives) — `./scripts/verify.sh` :
   - `manage.py check`
   - `makemigrations --check --dry-run`
   - `pytest -q`
   Ce sont elles qui attrapent l'essentiel. Pas de jugement LLM avant.
5. **Verifier** : agent `reviewer`, modèle d'une autre famille, lecture seule, **contre la spec** → verdict avec preuves.
6. **Revue humaine** : sécurité, données, architecture, contrats publics → merge.

## 3. Contrats d'isolation

- Un worktree par unité de travail ; jamais deux agents dans le même dossier.
- Un worker ne touche que les fichiers annoncés dans sa ligne du plan.
- Les tests d'une unité sont écrits/validés **avant** que le worker l'implémente (ou au moins le critère déterministe).
- Les workers n'ont **pas** le droit d'assouplir un test pour le faire passer.
- Aucune nouvelle dépendance sans décision écrite dans `docs/DECISIONS.md`.

## 4. Quand paralléliser (et quand s'abstenir)

Parallélisation autorisée uniquement si les unités sont **indépendantes et vérifiables séparément** :

| Pattern | Ici, typiquement |
| --- | --- |
| Fan-out/fan-in | Deux entités CRUD distinctes, ou une entité + sa documentation |
| Pipeline | Spec → plan → implémentation → tests → manuel utilisateur |
| Best-of-N + juge | Choix d'approche sur un point délicat (ex. moteur de détection de conflit de roulement) |
| Writer/Reviewer | **Par défaut** sur toute unité non triviale |

Interdit : deux workers sur les mêmes fichiers (`core/models.py`, `core/views.py`, `core/urls.py` sont des points de collision naturels sur ce projet — découper par entité, pas par couche).

## 5. Répartition Hermes / OpenCode

| Situation | Où |
| --- | --- |
| Cadrage, recherche, rédaction de spec/plan, veille | **Hermes** |
| Dispatcher plusieurs unités indépendantes | **Hermes** (`delegate_task`) |
| Écrire/modifier du code dans le repo, itérer avec les tests | **OpenCode** (agent `build`, worktree dédié) |
| Relire un diff contre la spec | **Hermes** (skill revue) ou agent `reviewer` OpenCode |
| Vérification répétée (tests, check) | **Hermes** cron `no_agent` ou CI GitHub |
| Débogage d'un test qui échoue | **OpenCode** (il faut éditer, instrumenter, relancer) |

Règle : **éditer du code dans un repo → OpenCode. Décider, chercher, coordonner, mémoriser → Hermes.**

## 6. Journal et reprise de session

- Commit par unité, message au format `type(scope): résumé` (ex. `feat(shift-schedule): duplicate a schedule period`).
- `docs/DECISIONS.md` : chaque choix structurant, avec alternatives écartées.
- `docs/PLAN.md` : état des unités (à faire / en cours / fait) pour reprendre sans recharger tout le contexte.

## 7. Anti-patterns constatés ailleurs, à ne pas reproduire

- Verifier qui valide tout ce que l'outil a dit « OK » (rubber-stamp) → aucun apport.
- Verifier sans rien d'observable à comparer (pas de test) → valide du vide.
- Replanification à chaque micro-écart → boucle coûteuse sans progression.
- Un agent qui joue deux rôles sans le déclarer (première cause d'échec).
- Empiler toute la spec + tout l'historique dans le prompt du worker → budget d'attention saturé, le modèle décroche.
- Lancer la boucle « génère → teste → corrige » **sans** porte déterministe : la répétition n'est pas une preuve.
