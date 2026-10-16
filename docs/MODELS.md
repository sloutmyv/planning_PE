# Choix des modèles par tâche — planning_PE

Tous les modèles ci-dessous sont disponibles via le proxy **LiteLLM** local (`http://localhost:4000/v1`), déjà déclaré comme provider `litellm` dans `~/.config/opencode/opencode.jsonc`. Prix en $ / million de tokens (entrée–sortie), relevés dans la configuration LiteLLM locale (oct. 2026).

## Règle de base

Le **rôle** détermine le besoin, pas l'inverse :

| Rôle | Besoin | Modèle conseillé | Alternative | Pourquoi |
| --- | --- | --- | --- | --- |
| **Planner** (spec, découpage, architecture) | Raisonnement long, peu de tokens | `litellm/opencode/glm-5.3` | `opencode/deepseek-v4-pro` | La qualité du plan conditionne tout le reste |
| **Worker** (implémentation Django) | Volume élevé, outils, vitesse | `litellm/opencode/deepseek-v4.1-flash` (0.30–1.20) | `qwen3.8-flash` (0.15–0.47), `glm-5.3-flash` (0.15–0.50) | C'est là que passent 80 % des tokens → optimiser le coût |
| **Code délicat** (migrations, transactions, logique de conflits) | Précision | `litellm/opencode/kimi-k2.7-code` (0.95–4.00) | `minimax-m3` (0.30–1.20) | Modèle orienté code |
| **Verifier / Reviewer** | Recul, lecture seule | `litellm/opencode/qwen3.8-flash` | `glm-5.3`, `gpt-6-luna` | **Famille différente du worker** : décorréler les erreurs |
| **Explorer** (lecture seule : où est quoi) | Volume, coût quasi nul | `litellm/opencode/mimo-v2.6-flash` (gratuit) | `space-bunny-free`, `longcat-2.5-preview-free` | Lecture seule uniquement |
| **Juge best-of-N** | Arbitrage | `litellm/opencode/grok-4.7` | `gpt-6-luna` | Avec une grille de notation écrite |

## Trois règles à ne pas enfreindre

1. **Jamais le même modèle pour écrire et pour juger.** Si `deepseek-v4.1-flash` implémente, le verifier doit être `glm-5.3` ou `qwen3.8-flash`.
2. **Jamais un modèle frontier pour du travail mécanique** (renommage, formatage, mise à jour de templates répétitifs) → `glm-5.3-flash` ou `qwen3.8-flash`.
3. **Les modèles `*-free` peuvent s'entraîner sur les requêtes** → exploration non sensible uniquement. Jamais de secrets, d'identifiants, de données RH ou de dumps de base.

## Températures recommandées

| Usage | Température |
| --- | --- |
| Analyse, revue, vérification | 0.0 – 0.2 |
| Implémentation courante | 0.2 – 0.4 |
| Exploration, brainstorming d'approches | 0.6 – 0.8 |

## Côté Hermes

- Garder le **modèle principal** (parent) sur un modèle fort pour la planification, et épingler les **enfants de délégation** sur un modèle bon marché : `delegation.model` / `delegation.provider` dans `~/.hermes/config.yaml`. Les enfants portent l'essentiel des tokens.
- Tâches auxiliaires Hermes (titres de session, résumés, extraction) : `glm-5.3-flash`.
- Vérifications répétées : cron `no_agent` (aucun LLM, test uniquement).

## Cadence de mise à jour

Ces choix doivent être revus quand : un nouveau modèle arrive dans le proxy LiteLLM, un rôle échoue de façon répétée (mauvais plan, revue qui rate des bugs), ou le coût par unité dérive. Consigner les changements dans `DECISIONS.md`.
