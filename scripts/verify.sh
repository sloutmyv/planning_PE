#!/usr/bin/env bash
# Portes de vérification déterministes de planning_PE.
# Usage : ./scripts/verify.sh      (code de sortie 0 = tout est vert)
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

PY=".venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "[verify] .venv absent — création et installation des dépendances…"
  python3 -m venv .venv || exit 2
  .venv/bin/pip install -q -r requirements.txt || exit 2
fi

fail=0
run() {
  local label="$1"; shift
  echo ""
  echo "=== $label ==="
  if "$@"; then
    echo "[verify] OK — $label"
  else
    echo "[verify] ÉCHEC — $label"
    fail=1
  fi
}

run "django check"                 "$PY" manage.py check
run "migrations à jour"            "$PY" manage.py makemigrations --check --dry-run
run "tests (pytest)"               "$PY" -m pytest -q

echo ""
if [[ $fail -eq 0 ]]; then
  echo "[verify] TOUT EST VERT"
else
  echo "[verify] DES PORTES SONT ROUGES — ne pas déclarer le travail terminé"
fi
exit $fail
