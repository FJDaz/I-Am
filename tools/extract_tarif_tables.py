#!/usr/bin/env python3
"""
Extrait les tableaux de tarifs depuis le PDF syn+tarif+2024+2025+pour+contrat (1).pdf
Version améliorée avec meilleure détection des colonnes
"""
import json
import re
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    raise SystemExit("❌ Installe pdfplumber: pip install pdfplumber")

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "data" / "raw" / "syn+tarif+2024+2025+pour+contrat (1).pdf"
OUTPUT_PATH = ROOT / "data" / "tarifs_2024_2025.json"

def split_mixed_cell(cell_text: str) -> list:
    """Sépare une cellule contenant plusieurs valeurs (ex: "24,77 € 45,15 €")."""
    if not cell_text or len(cell_text) < 5:
        return [cell_text]
    
    # Nettoyer d'abord : remplacer les espaces multiples par un seul espace
    cell_text = re.sub(r'\s+', ' ', cell_text.strip())
    
    # Pattern amélioré pour détecter des montants avec nombres séparés par espaces
    # Ex: "2 4,77 €" -> "24,77 €"
    # Pattern: (chiffres séparés par espaces) + (virgule/point) + (chiffres) + " €"
    def fix_spaced_numbers(text: str) -> str:
        # Pattern pour "2 4,77 €" -> "24,77 €"
        pattern = r'(\d+)\s+(\d+[,\.]\d+)\s*€'
        while re.search(pattern, text):
            text = re.sub(pattern, r'\1\2 €', text)
        return text
    
    cell_text = fix_spaced_numbers(cell_text)
    
    # Maintenant chercher plusieurs montants séparés
    # Pattern pour montants complets: "24,77 €" ou "24.77 €"
    amounts = re.findall(r'\d+[,\.]\d+\s*€', cell_text)
    if len(amounts) > 1:
        # Plusieurs montants trouvés, les séparer
        return amounts
    
    # Si un seul montant mais avec du texte avant/après, garder le texte aussi
    if '\n' in cell_text:
        parts = [p.strip() for p in cell_text.split('\n') if p.strip()]
        if len(parts) > 1:
            return parts
    
    # Si la cellule contient plusieurs valeurs séparées par des espaces multiples
    # (mais pas des montants), essayer de séparer
    if '  ' in cell_text or len(cell_text) > 50:
        # Essayer de détecter des séparations logiques
        # Chercher des patterns comme "mot1 mot2   mot3 mot4" (2+ espaces = séparation)
        parts = re.split(r'\s{2,}', cell_text)
        if len(parts) > 1 and all(len(p.strip()) > 3 for p in parts):
            return [p.strip() for p in parts if p.strip()]
    
    return [cell_text]

def improve_table_structure(table: list) -> list:
    """Améliore la structure d'un tableau en séparant les colonnes mélangées."""
    if not table or len(table) == 0:
        return table
    
    improved = []
    max_cols = max(len(row) for row in table if row) if table else 0
    
    for row in table:
        if not row:
            continue
        
        improved_row = []
        for cell in row:
            cell_text = str(cell).strip() if cell else ""
            if not cell_text:
                improved_row.append("")
                continue
            
            # Si la cellule contient plusieurs valeurs, essayer de les séparer
            split_values = split_mixed_cell(cell_text)
            if len(split_values) > 1:
                # Ajouter chaque valeur comme une colonne séparée
                improved_row.extend(split_values)
            else:
                improved_row.append(cell_text)
        
        # Normaliser le nombre de colonnes
        while len(improved_row) < max_cols:
            improved_row.append("")
        
        improved.append(improved_row[:max_cols])
    
    return improved

def extract_tables_from_pdf(pdf_path: Path) -> list:
    """Extrait tous les tableaux du PDF avec amélioration de la détection."""
    tables_data = []
    
    print(f"📄 Extraction depuis {pdf_path.name}...")
    
    # Stratégies d'extraction à essayer
    table_settings = [
        {},  # Par défaut
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "text"},
    ]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Essayer différentes stratégies
            tables_found = False
            for strategy_num, settings in enumerate(table_settings):
                try:
                    tables = page.extract_tables(table_settings=settings)
                    if tables:
                        print(f"   Page {page_num}: {len(tables)} tableau(x) trouvé(s) (stratégie {strategy_num+1})")
                        tables_found = True
                        
                        for table_num, table in enumerate(tables, 1):
                            if table and len(table) > 1:  # Au moins header + 1 ligne
                                # Nettoyer le tableau
                                cleaned_table = []
                                for row in table:
                                    if row and any(cell for cell in row if cell and str(cell).strip()):
                                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                                        cleaned_table.append(cleaned_row)
                                
                                if cleaned_table:
                                    # Améliorer la structure
                                    improved_table = improve_table_structure(cleaned_table)
                                    
                                    tables_data.append({
                                        "page": page_num,
                                        "table_num": table_num,
                                        "strategy": strategy_num,
                                        "rows": improved_table,
                                        "header": improved_table[0] if improved_table else [],
                                        "data_rows": improved_table[1:] if len(improved_table) > 1 else []
                                    })
                        break  # Si on a trouvé des tableaux, on arrête
                except Exception as e:
                    continue  # Essayer la stratégie suivante
            
            if not tables_found:
                print(f"   Page {page_num}: Aucun tableau détecté")
    
    return tables_data

def identify_tarif_tables(tables_data: list) -> dict:
    """Identifie les types de tableaux tarifaires."""
    tarifs = {
        "cantine": [],
        "periscolaire": [],
        "mercredi": [],
        "alsh": [],
        "autres": []
    }
    
    keywords = {
        "cantine": ["cantine", "restauration", "scolaire", "repas"],
        "periscolaire": ["périscolaire", "avant", "après", "école"],
        "mercredi": ["mercredi", "accueil"],
        "alsh": ["alsh", "accueil", "loisirs", "centre"]
    }
    
    for table in tables_data:
        # Analyser header pour identifier le type
        header_text = " ".join(table["header"]).lower()
        table_text = " ".join([" ".join(row) for row in table["data_rows"][:3]]).lower()
        full_text = header_text + " " + table_text
        
        identified = False
        for tarif_type, kws in keywords.items():
            if any(kw in full_text for kw in kws):
                tarifs[tarif_type].append(table)
                identified = True
                break
        
        if not identified:
            tarifs["autres"].append(table)
    
    return tarifs

def format_table_html(table: dict) -> str:
    """Formate un tableau en HTML avec meilleure structure."""
    rows = table["rows"]
    if not rows:
        return ""
    
    # Déterminer le nombre de colonnes (prendre le max)
    max_cols = max(len(row) for row in rows if row) if rows else 0
    if max_cols == 0:
        return ""
    
    html = "<table border='1' style='border-collapse: collapse;'>\n"
    
    # Header
    if rows:
        html += "  <thead>\n    <tr>\n"
        header_row = rows[0]
        # Normaliser le header pour avoir le bon nombre de colonnes
        while len(header_row) < max_cols:
            header_row.append("")
        for cell in header_row[:max_cols]:
            cell_text = str(cell).replace('\n', ' ').strip() if cell else ""
            html += f"      <th style='padding: 4px;'>{cell_text}</th>\n"
        html += "    </tr>\n  </thead>\n"
    
    # Body
    html += "  <tbody>\n"
    for row in rows[1:]:
        html += "    <tr>\n"
        # Normaliser la ligne pour avoir le bon nombre de colonnes
        normalized_row = list(row) if row else []
        while len(normalized_row) < max_cols:
            normalized_row.append("")
        for cell in normalized_row[:max_cols]:
            cell_text = str(cell).replace('\n', '<br>').strip() if cell else ""
            html += f"      <td style='padding: 4px;'>{cell_text}</td>\n"
        html += "    </tr>\n"
    html += "  </tbody>\n</table>"
    
    return html

def main():
    if not PDF_PATH.exists():
        print(f"❌ PDF introuvable: {PDF_PATH}")
        return
    
    # Extraire tableaux
    tables_data = extract_tables_from_pdf(PDF_PATH)
    print(f"\n✅ {len(tables_data)} tableau(x) extrait(s)")
    
    if not tables_data:
        print("⚠️ Aucun tableau trouvé")
        return
    
    # Identifier types
    tarifs = identify_tarif_tables(tables_data)
    print("\n📊 Répartition:")
    for tarif_type, tables in tarifs.items():
        if tables:
            print(f"   - {tarif_type}: {len(tables)} tableau(x)")
    
    # Sauvegarder
    output_data = {
        "source": PDF_PATH.name,
        "total_tables": len(tables_data),
        "tarifs_by_type": {
            k: [format_table_html(t) for t in v] for k, v in tarifs.items() if v
        },
        "raw_tables": tables_data  # Garder aussi les données brutes
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Données sauvegardées: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

