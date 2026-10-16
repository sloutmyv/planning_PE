# PLAN — planning_PE

État des unités de travail. Une unité = un périmètre de fichiers + une commande de preuve. **Aucune unité ne démarre sans validation humaine du plan.**

## Format d'une unité

```
### U-<n> — <titre court>
- Statut : à faire | en cours | en revue | fait
- Spec : docs/specs/NNN-<slug>.md
- Périmètre (fichiers possédés) : ...
- Hors périmètre : ...
- Critère d'acceptation : <comportement observable>
- Commande de preuve : ./scripts/verify.sh  (ou test ciblé)
- Worktree : ../planning_PE-<n>  (branche feat/<n>)
- Modèle worker : ...  /  Verifier : ...
```

---

## Backlog

### U-0 — Assainissement de base (infra, aucune fonctionnalité)
- Statut : **fait (partiel)** — `pytest.ini` corrigé (`[pytest]`), CI ajoutée, gates scriptées, doc d'orchestration.
- Reste à décider (voir `DECISIONS.md`) : `SECRET_KEY`/`DEBUG` hors du code, identifiants retirés du README, fuseau horaire et langue.

### U-1 — (à définir)
- Statut : à faire
- Spec : à écrire
- Périmètre : à définir

---

## Notes de méthode

- Découper **par entité métier**, pas par couche technique : `core/models.py`, `core/views.py` et `core/urls.py` sont des points de collision si deux workers y touchent en parallèle.
- Une unité qui ne peut pas être vérifiée par une commande n'est pas prête à être lancée : écrire d'abord le test ou le critère observable.
