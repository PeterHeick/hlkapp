#!/usr/bin/env bash
# Bump version i pyproject.toml og KlinikPortal.iss
# Brug: ./bump.sh patch|minor|major
set -e

if [[ $# -ne 1 ]] || [[ ! "$1" =~ ^(patch|minor|major)$ ]]; then
  echo "Brug: $0 patch|minor|major"
  exit 1
fi

BUMP=$1

# Læs nuværende version fra pyproject.toml
CURRENT=$(grep -m1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case $BUMP in
  patch) PATCH=$((PATCH + 1)) ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
esac

NEW="$MAJOR.$MINOR.$PATCH"

echo "Version: $CURRENT → $NEW"

# Opdater pyproject.toml
sed -i "s/^version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml

# Opdater KlinikPortal.iss
sed -i "s/#define AppVersion \"$CURRENT\"/#define AppVersion \"$NEW\"/" KlinikPortal.iss

echo "Opdateret pyproject.toml og KlinikPortal.iss"
echo "Frontend henter version fra pyproject.toml ved næste build."
