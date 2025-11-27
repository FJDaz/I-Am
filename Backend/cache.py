"""
Cache mémoire pour questions fréquentes dans le système RAG.
Utilise un dictionnaire Python simple avec TTL (Time To Live).
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional, Tuple


class SimpleCache:
    """
    Cache simple en mémoire avec TTL.
    
    Structure:
    {
        cache_key: {
            "value": ...,
            "expires_at": timestamp
        }
    }
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Args:
            default_ttl: TTL par défaut en secondes (1h = 3600)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, question: str) -> str:
        """Crée une clé de cache à partir d'une question normalisée"""
        # Normaliser la question (minuscules, strip)
        normalized = question.lower().strip()
        # Hash pour clé unique
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()
    
    def get(self, question: str) -> Optional[Any]:
        """
        Récupère une valeur du cache si elle existe et n'est pas expirée.
        
        Args:
            question: Question normalisée
            
        Returns:
            Valeur en cache ou None si absente/expirée
        """
        key = self._make_key(question)
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        expires_at = entry.get("expires_at", 0)
        
        # Vérifier expiration
        if time.time() > expires_at:
            # Expiré, supprimer
            del self._cache[key]
            return None
        
        return entry.get("value")
    
    def set(self, question: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Stocke une valeur dans le cache.
        
        Args:
            question: Question normalisée
            value: Valeur à stocker
            ttl: TTL en secondes (None = utiliser default_ttl)
        """
        key = self._make_key(question)
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
    
    def clear(self) -> None:
        """Vide tout le cache"""
        self._cache.clear()
    
    def clear_expired(self) -> int:
        """
        Supprime toutes les entrées expirées.
        
        Returns:
            Nombre d'entrées supprimées
        """
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.get("expires_at", 0) < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Retourne le nombre d'entrées dans le cache"""
        return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache"""
        now = time.time()
        expired = sum(
            1 for entry in self._cache.values()
            if entry.get("expires_at", 0) < now
        )
        
        return {
            "total_entries": len(self._cache),
            "expired_entries": expired,
            "active_entries": len(self._cache) - expired,
            "default_ttl": self.default_ttl
        }


# Instance globale du cache (singleton)
_global_cache: Optional[SimpleCache] = None


def get_cache(ttl: int = 3600) -> SimpleCache:
    """
    Récupère l'instance globale du cache (singleton).
    
    Args:
        ttl: TTL par défaut si cache n'existe pas encore
        
    Returns:
        Instance SimpleCache
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = SimpleCache(default_ttl=ttl)
    return _global_cache


def clear_cache() -> None:
    """Vide le cache global"""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()


def cache_stats() -> Dict[str, Any]:
    """Retourne les statistiques du cache global"""
    global _global_cache
    if _global_cache is None:
        return {"total_entries": 0, "active_entries": 0}
    return _global_cache.stats()

