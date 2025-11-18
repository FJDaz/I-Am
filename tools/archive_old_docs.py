#!/usr/bin/env python3
"""
Script pour archiver les fichiers de documentation de plus de 1 jour.
Déplace les fichiers dans docs/tests/archives/ et renomme avec la date.
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def archive_old_docs(docs_dir: str = "docs/tests", days: int = 1):
    """
    Archive les fichiers .md de plus de N jours dans un sous-dossier archives/.
    Renomme les fichiers avec la date de dernière modification devant.
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"❌ Le dossier {docs_dir} n'existe pas")
        return
    
    archives_dir = docs_path / "archives"
    archives_dir.mkdir(exist_ok=True)
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Fichiers à ne jamais archiver
    exclude_files = {"RESUME_CONTEXTE.md", "README.md"}
    
    files_archived = []
    files_kept = []
    
    for md_file in docs_path.glob("*.md"):
        if md_file.name in exclude_files:
            files_kept.append(md_file.name)
            continue
        
        # Vérifier la date de modification
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        
        if mtime < cutoff_date:
            # Lire le contenu pour mettre à jour le titre
            content = md_file.read_text(encoding="utf-8")
            
            # Extraire le titre actuel (première ligne après #)
            lines = content.split("\n")
            title_line_idx = None
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    title_line_idx = i
                    break
            
            # Formater la date
            date_str = mtime.strftime("%Y-%m-%d")
            
            # Nouveau nom de fichier avec date
            new_name = f"{date_str}_{md_file.name}"
            new_path = archives_dir / new_name
            
            # Mettre à jour le titre dans le contenu si trouvé
            if title_line_idx is not None:
                old_title = lines[title_line_idx]
                new_title = f"# {date_str} - {old_title[2:].lstrip()}"  # Enlever le # initial
                lines[title_line_idx] = new_title
                content = "\n".join(lines)
            
            # Écrire le fichier archivé
            new_path.write_text(content, encoding="utf-8")
            
            # Supprimer l'original
            md_file.unlink()
            
            files_archived.append((md_file.name, new_name, date_str))
        else:
            files_kept.append(md_file.name)
    
    # Résumé
    print(f"📁 Archivage des fichiers de documentation (> {days} jours)")
    print(f"   Dossier: {docs_dir}")
    print(f"   Date limite: {cutoff_date.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    if files_archived:
        print(f"✅ {len(files_archived)} fichier(s) archivé(s):")
        for old_name, new_name, date_str in files_archived:
            print(f"   {old_name} → archives/{new_name}")
    else:
        print("ℹ️  Aucun fichier à archiver (tous récents)")
    
    print()
    print(f"📄 {len(files_kept)} fichier(s) conservé(s) dans {docs_dir}/")
    
    return len(files_archived)


if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    archive_old_docs(days=days)

