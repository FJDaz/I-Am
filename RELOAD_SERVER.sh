#!/bin/bash
# Script pour relancer le serveur avec les dernières corrections

cd "$(dirname "$0")"

echo "🛑 Arrêt du serveur actuel..."
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
echo "🚀 Démarrage du serveur avec les corrections..."
python3 rag_assistant_server.py

