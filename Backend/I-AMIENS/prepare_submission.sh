#!/bin/bash
# Script pour préparer le package de soumission Chrome Web Store - Version I-AMIENS

set -e

EXTENSION_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$EXTENSION_DIR")"
OUTPUT_ZIP="$PARENT_DIR/I-Amiens-extension.zip"

echo "📦 Préparation du package I-Amiens pour Chrome Web Store (Version Production)"
echo "============================================================================"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "$EXTENSION_DIR/manifest.json" ]; then
    echo "❌ Erreur: manifest.json non trouvé dans $EXTENSION_DIR"
    exit 1
fi

echo "✅ Répertoire extension: $EXTENSION_DIR"
echo ""

# Vérifier les fichiers requis
echo "🔍 Vérification des fichiers requis..."
REQUIRED_FILES=(
    "manifest.json"
    "content.js"
    "data/corpus_segments.json"
    "data/lexique_enfance.json"
    "data/questions_usager.json"
    "statics/img/IAM_logo.png"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$EXTENSION_DIR/$file" ]; then
        MISSING_FILES+=("$file")
        echo "  ❌ $file - MANQUANT"
    else
        SIZE=$(du -h "$EXTENSION_DIR/$file" | cut -f1)
        echo "  ✅ $file ($SIZE)"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Fichiers manquants détectés. Veuillez les ajouter avant de continuer."
    exit 1
fi

echo ""
echo "📋 Vérification du manifest.json..."

# Vérifier que le nom est bien "I-Amiens"
if grep -q '"name": "I-Amiens"' "$EXTENSION_DIR/manifest.json"; then
    echo "  ✅ Nom: I-Amiens"
else
    echo "  ⚠️  Le nom dans manifest.json n'est pas 'I-Amiens'"
fi

# Vérifier les icônes
if grep -q '"icons"' "$EXTENSION_DIR/manifest.json"; then
    echo "  ✅ Icônes définies"
else
    echo "  ⚠️  Icônes non définies dans manifest.json"
fi

# Vérifier les permissions Railway
if grep -q "i-am-production.up.railway.app" "$EXTENSION_DIR/manifest.json"; then
    echo "  ✅ Permissions Railway configurées"
else
    echo "  ⚠️  Permissions Railway non trouvées"
fi

# Vérifier qu'il n'y a PAS de permissions localhost
if grep -q "localhost:8711" "$EXTENSION_DIR/manifest.json"; then
    echo "  ❌ ATTENTION: Permissions localhost détectées (ne devraient pas être présentes)"
    echo "     Ces permissions seront rejetées par le Chrome Web Store"
else
    echo "  ✅ Aucune permission localhost (conforme Chrome Web Store)"
fi

# Vérifier content.js
echo ""
echo "📜 Vérification content.js..."
if grep -q "i-am-production.up.railway.app" "$EXTENSION_DIR/content.js"; then
    echo "  ✅ Endpoint Railway configuré"
else
    echo "  ⚠️  Endpoint Railway non trouvé dans content.js"
fi

if grep -q "localhost:8711" "$EXTENSION_DIR/content.js"; then
    echo "  ⚠️  Référence localhost trouvée dans content.js (peut être dans les messages d'erreur)"
else
    echo "  ✅ Aucune référence localhost dans content.js"
fi

echo ""
echo "🗜️  Création du package ZIP..."

# Supprimer l'ancien ZIP s'il existe
if [ -f "$OUTPUT_ZIP" ]; then
    rm "$OUTPUT_ZIP"
    echo "  🗑️  Ancien ZIP supprimé"
fi

# Créer le ZIP en excluant les fichiers non nécessaires
cd "$EXTENSION_DIR"
zip -r "$OUTPUT_ZIP" . \
    -x "*.md" \
    -x "*.sh" \
    -x ".DS_Store" \
    -x "*.log" \
    -x ".git/*" \
    -x "*.bak" \
    -x "*~" \
    > /dev/null

ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)
echo "  ✅ ZIP créé: $OUTPUT_ZIP ($ZIP_SIZE)"
echo ""

# Vérifier le contenu du ZIP
echo "📦 Contenu du package:"
unzip -l "$OUTPUT_ZIP" | tail -n +4 | awk 'NR>1 && !/^Archive:/ && !/^[[:space:]]*$/ {print "  " $4}' | head -20
echo ""

echo "✅ Package prêt pour soumission!"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Vérifier que le ZIP contient tous les fichiers nécessaires"
echo "  2. Tester l'extension en la chargeant dans Chrome (chrome://extensions)"
echo "  3. Préparer les captures d'écran"
echo "  4. Créer une politique de confidentialité"
echo "  5. Soumettre sur https://chrome.google.com/webstore/devconsole"
echo ""
echo "📚 Consultez README.md pour plus de détails sur cette version"
