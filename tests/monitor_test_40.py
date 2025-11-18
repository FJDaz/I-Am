#!/usr/bin/env python3
"""
Monitoring en temps réel du test des 40 questions
Affiche la progression et les statistiques
"""
import time
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent / "test_40_questions_output.log"
RESULTS_FILE = Path(__file__).parent / "test_results_40_questions.json"
CSV_FILE = Path(__file__).parent / "test_results_40_questions.csv"

def parse_log_line(line: str) -> dict:
    """Parse une ligne du log pour extraire les infos."""
    info = {}
    
    # Chercher le numéro de question [X/45]
    import re
    match = re.search(r'\[(\d+)/(\d+)\]', line)
    if match:
        info['current'] = int(match.group(1))
        info['total'] = int(match.group(2))
    
    # Chercher le statut
    if '✅' in line:
        info['status'] = 'success'
        # Chercher alignment status
        align_match = re.search(r'\[([^\]]+)\]', line)
        if align_match:
            info['alignment'] = align_match.group(1)
    elif '❌' in line:
        info['status'] = 'error'
        if '502' in line:
            info['error'] = '502 Server Error'
        elif 'timeout' in line.lower():
            info['error'] = 'Timeout'
        else:
            info['error'] = 'Unknown error'
    
    return info

def get_progress_from_log() -> dict:
    """Lit le log et extrait la progression."""
    if not LOG_FILE.exists():
        return {"status": "not_started", "current": 0, "total": 45}
    
    try:
        with LOG_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Chercher la dernière ligne de progression
        last_progress = {"current": 0, "total": 45, "status": "running"}
        
        for line in lines:
            if "[ " in line and "/45]" in line:
                info = parse_log_line(line)
                if 'current' in info:
                    last_progress.update(info)
        
        # Vérifier si terminé
        if "FIN DES TESTS" in "".join(lines[-10:]):
            last_progress["status"] = "completed"
        elif last_progress.get("current", 0) > 0:
            last_progress["status"] = "running"
        else:
            last_progress["status"] = "starting"
        
        return last_progress
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_stats_from_results() -> dict:
    """Lit les résultats JSON et calcule les stats."""
    if not RESULTS_FILE.exists():
        return None
    
    try:
        with RESULTS_FILE.open("r", encoding="utf-8") as f:
            results = json.load(f)
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        # Stats par type
        où_tests = [r for r in successful if r.get("type") == "où"]
        quand_tests = [r for r in successful if r.get("type") == "quand"]
        comment_tests = [r for r in successful if r.get("type") == "comment"]
        
        # Stats par niveau
        niveau_stats = {}
        for niveau in [1, 2, 3, 4]:
            niveau_tests = [r for r in successful if r.get("niveau") == niveau]
            total_niveau = len([r for r in results if r.get("niveau") == niveau])
            if total_niveau > 0:
                niveau_stats[niveau] = {
                    "success": len(niveau_tests),
                    "total": total_niveau,
                    "rate": len(niveau_tests) * 100 / total_niveau
                }
        
        # Adresses trouvées
        où_with_address = [r for r in où_tests if r.get("has_address")]
        
        # Alignements
        aligned = [r for r in successful if r.get("alignment_status") in ["aligned", "partial"]]
        
        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) * 100 / len(results) if results else 0,
            "by_type": {
                "où": {"success": len(où_tests), "total": len([r for r in results if r.get("type") == "où"])},
                "quand": {"success": len(quand_tests), "total": len([r for r in results if r.get("type") == "quand"])},
                "comment": {"success": len(comment_tests), "total": len([r for r in results if r.get("type") == "comment"])}
            },
            "by_niveau": niveau_stats,
            "addresses_found": len(où_with_address),
            "addresses_total": len(où_tests),
            "aligned": len(aligned),
            "aligned_rate": len(aligned) * 100 / len(successful) if successful else 0
        }
    except Exception as e:
        return {"error": str(e)}

def display_monitoring():
    """Affiche le monitoring."""
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print("📊 MONITORING TEST 40 QUESTIONS")
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Progression depuis le log
    progress = get_progress_from_log()
    
    if progress["status"] == "not_started":
        print("⏳ Test pas encore démarré")
        return
    elif progress["status"] == "starting":
        print("🚀 Test en cours de démarrage...")
        return
    elif progress["status"] == "error":
        print(f"❌ Erreur: {progress.get('error', 'Unknown')}")
        return
    
    # Barre de progression
    current = progress.get("current", 0)
    total = progress.get("total", 45)
    percentage = (current / total * 100) if total > 0 else 0
    
    bar_width = 50
    filled = int(bar_width * current / total)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    print(f"📈 PROGRESSION: {current}/{total} ({percentage:.1f}%)")
    print(f"   [{bar}]")
    print()
    
    # Statut actuel
    status_emoji = "✅" if progress.get("status") == "completed" else "🔄"
    print(f"{status_emoji} Statut: {progress.get('status', 'running').upper()}")
    
    if progress.get("alignment"):
        print(f"   Dernier alignement: {progress.get('alignment')}")
    if progress.get("error"):
        print(f"   ⚠️  Dernière erreur: {progress.get('error')}")
    print()
    
    # Stats depuis résultats JSON (si disponible)
    stats = get_stats_from_results()
    if stats and not stats.get("error"):
        print("📊 STATISTIQUES ACTUELLES")
        print(f"   ✅ Réussies: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        print(f"   ❌ Échouées: {stats['failed']}")
        print()
        
        print("📊 PAR TYPE")
        for q_type, data in stats['by_type'].items():
            rate = (data['success'] * 100 / data['total']) if data['total'] > 0 else 0
            print(f"   {q_type.upper():8s}: {data['success']}/{data['total']} ({rate:.1f}%)")
        print()
        
        print("📊 PAR NIVEAU")
        for niveau in sorted(stats['by_niveau'].keys()):
            n_stats = stats['by_niveau'][niveau]
            print(f"   Niveau {niveau}: {n_stats['success']}/{n_stats['total']} ({n_stats['rate']:.1f}%)")
        print()
        
        print("📍 ADRESSES")
        addr_rate = (stats['addresses_found'] * 100 / stats['addresses_total']) if stats['addresses_total'] > 0 else 0
        print(f"   Trouvées: {stats['addresses_found']}/{stats['addresses_total']} ({addr_rate:.1f}%)")
        print()
        
        print("🎯 ALIGNEMENTS")
        print(f"   Alignés/Partiels: {stats['aligned']}/{stats['successful']} ({stats['aligned_rate']:.1f}%)")
        print()
    
    # Temps estimé restant
    if current > 0 and current < total and progress.get("status") == "running":
        # Estimation basée sur ~15s par question
        remaining = (total - current) * 15
        minutes = remaining // 60
        seconds = remaining % 60
        print(f"⏱️  Temps estimé restant: ~{minutes}min {seconds}s")
        print()
    
    print("=" * 80)
    print("💡 Appuyez sur Ctrl+C pour arrêter le monitoring")
    print("=" * 80)

def main():
    """Lance le monitoring en boucle."""
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n\n👋 Monitoring arrêté")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            display_monitoring()
            time.sleep(2)  # Rafraîchir toutes les 2 secondes
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring arrêté")

if __name__ == "__main__":
    main()

