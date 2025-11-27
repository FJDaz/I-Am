from bs4 import BeautifulSoup
from pathlib import Path

def audit_html_files(folder):
    results = []
    allowed_suffixes = {".html", ".htm", ".txt"}
    for file in Path(folder).rglob("*"):
        if file.suffix.lower() not in allowed_suffixes:
            continue
        html = Path(file).read_text(errors="ignore")
        soup = BeautifulSoup(html, "html.parser")

        has_tables = bool(soup.find_all("table"))
        has_hidden = bool(soup.select('[style*="display:none"], .collapse'))
        has_scripts = bool(soup.find_all("script"))
        has_data_attr = any(attr.startswith("data-") for tag in soup.find_all(True) for attr in tag.attrs)
        has_voir_plus = "voir +" in soup.get_text().lower()

        results.append({
            "file": file.name,
            "tables": has_tables,
            "hidden_blocks": has_hidden,
            "data_attributes": has_data_attr,
            "voir_plus": has_voir_plus,
            "scripts": has_scripts,
        })
    return results

if __name__ == "__main__":
    for r in audit_html_files("download_amiens_enfance"):
        print(r)
