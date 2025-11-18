#!/usr/bin/env python3
"""
Point d'entrée principal pour Railway.
Railway détecte automatiquement main.py ou app.py.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

# Importer et exécuter le serveur
if __name__ == "__main__":
    # Railway définit automatiquement PORT
    port = int(os.environ.get("PORT", 8711))
    
    # Importer le module du serveur
    from rag_assistant_server import app
    import uvicorn
    
    # Démarrer le serveur
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        timeout_keep_alive=30,
        limit_concurrency=10
    )

