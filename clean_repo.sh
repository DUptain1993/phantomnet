#!/usr/bin/env bash
# ------------------------------------------------------------
#  PhantomNet repo cleanup – UNIX / macOS / WSL
# ------------------------------------------------------------
set -euo pipefail

OLD_PATHS=(
  "app/controllers"
  "app/models"            # old package
  "app/routes"            # old package
  "app/utils"
  "phantom_client.py"
  "_dynu_updater.py"
  "server.pyc"
  "*.pyc"
  "__pycache__"
  "instance"
  "*.db-journal"
  "DEPLOYMENT_TUTORIAL.md"
  "Features.txt"
)

echo "==> Removing legacy files / directories"
for path in "${OLD_PATHS[@]}"; do
  if compgen -G "$path" > /dev/null; then
    rm -rf $path
    echo "   removed $path"
  fi
done

echo "==> Deleting Python byte-code"
find . -name '__pycache__' -prune -exec rm -rf {} +
find . -name '*.py[co]'   -delete

cat > .gitignore <<'EOF'
# ---- Python ----
__pycache__/
*.py[cod]
*.sqlite3
phantom_c2.db

# ---- React Native / Expo ----
mobile-app/node_modules/
mobile-app/.expo/
mobile-app/dist/

# ---- Docker volumes / logs ----
data/
logs/
ssl/
backups/
*.tar
*.tar.gz

# ---- Misc ----
.DS_Store
.env
EOF

echo "==> Done.  Current tree:"
tree -L 2 -I 'node_modules|__pycache__|data|logs|.git'
echo "==> Commit the cleanup when ready:"
echo "   git add -A && git commit -m 'repo cleanup: remove legacy code & artifacts'"
