#!/bin/bash
# Script pour relancer le serveur en HTTP (sans SSL)
# Pour que l'extension Chrome fonctionne

# Se placer dans le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Arrêt du serveur actuel..."
# Trouver et arrêter le processus sur le port 8711
PID=$(lsof -ti :8711)
if [ ! -z "$PID" ]; then
    echo "   Processus trouvé: $PID"
    kill $PID
    sleep 2
    echo "   ✅ Serveur arrêté"
else
    echo "   ℹ️  Aucun serveur trouvé sur le port 8711"
fi

echo ""
echo "📦 Sauvegarde des certificats SSL..."
if [ -f "localhost-key.pem" ]; then
    mv localhost-key.pem localhost-key.pem.bak 2>/dev/null || true
    echo "   ✅ localhost-key.pem sauvegardé"
fi
if [ -f "localhost-cert.pem" ]; then
    mv localhost-cert.pem localhost-cert.pem.bak 2>/dev/null || true
    echo "   ✅ localhost-cert.pem sauvegardé"
fi

echo ""
echo "🚀 Démarrage du serveur en HTTP..."
python3 rag_assistant_server.py

