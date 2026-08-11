#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistence v1 — JSON-based skill registry with auto-save/load.
Molecular AI remembers skills between sessions.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class SkillRegistryPersistence:
    """
    Save/load skill registry to JSON. Supports:
    - Full registry snapshot
    - Seed loading (initial skills)
    - Auto-save on change (optional)
    - Backup rotation
    """

    def __init__(self, filepath: str = "data/skills_registry.json",
                 autosave: bool = False, backup_count: int = 3):
        self.filepath = Path(filepath)
        self.autosave = autosave
        self.backup_count = backup_count
        self._dirty = False

        # Ensure directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def save(self, registry: Dict[str, Any], evolution: Optional[Dict[str, Any]] = None) -> str:
        """
        Save registry + evolution to JSON. Returns saved filepath.
        """
        # Convert evolution records to dicts for JSON serialization
        evo_serializable = {}
        if evolution:
            for name, rec in evolution.items():
                if hasattr(rec, "__dataclass_fields__"):
                    evo_serializable[name] = asdict(rec)
                else:
                    evo_serializable[name] = rec

        payload = {
            "version": "1.0",
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "registry": registry,
            "evolution": evo_serializable,
        }

        # Backup rotation
        self._rotate_backup()

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

        self._dirty = False
        return str(self.filepath)

    def load(self) -> Dict[str, Any]:
        """
        Load registry from JSON. Returns dict with 'registry' and 'evolution' keys.
        """
        if not self.filepath.exists():
            return {"registry": {}, "evolution": {}}

        with open(self.filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        return payload

    def load_registry(self) -> Dict[str, Any]:
        """Convenience: load only registry dict."""
        return self.load().get("registry", {})

    def load_evolution(self) -> Dict[str, Any]:
        """Convenience: load only evolution dict."""
        return self.load().get("evolution", {})

    def load_seed(self, seed_path: str) -> Dict[str, Any]:
        """
        Load seed skills from JSON/CSV. Returns registry dict.
        """
        path = Path(seed_path)
        if not path.exists():
            raise FileNotFoundError(f"Seed file not found: {seed_path}")

        ext = path.suffix.lower()
        if ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Support both flat dict and nested "skills" list
            if isinstance(data, dict) and "skills" in data:
                return {s["name"]: s for s in data["skills"]}
            return data
        elif ext in (".csv", ".txt"):
            return self._parse_csv_seed(path)
        else:
            raise ValueError(f"Unsupported seed format: {ext}")

    def _parse_csv_seed(self, path: Path) -> Dict[str, Any]:
        """Parse simple CSV/TXT seed format."""
        registry = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    category = parts[1].strip() if len(parts) > 1 else "General"
                    complexity = int(parts[2].strip()) if len(parts) > 2 and parts[2].strip().isdigit() else 5
                    registry[name] = {
                        "name": name,
                        "category": category,
                        "description": f"Seed skill: {name}",
                        "complexity": complexity,
                        "code": "",
                        "tests": "",
                        "keywords": [name.lower()],
                        "level": 0.5,
                        "seed": True,
                    }
        return registry

    def merge_seed(self, seed_registry: Dict[str, Any], target_registry: Dict[str, Any],
                   overwrite: bool = False) -> Dict[str, Any]:
        """
        Merge seed into target registry. If overwrite=False, skip existing keys.
        """
        merged = dict(target_registry)
        for name, info in seed_registry.items():
            if name in merged and not overwrite:
                continue
            merged[name] = info
        return merged

    def _rotate_backup(self):
        """Keep last N backups as .bak1, .bak2, ..."""
        if not self.filepath.exists():
            return
        for i in range(self.backup_count - 1, 0, -1):
            src = self.filepath.parent / (self.filepath.stem + f".bak{i}" + self.filepath.suffix)
            dst = self.filepath.parent / (self.filepath.stem + f".bak{i + 1}" + self.filepath.suffix)
            if src.exists():
                src.replace(dst)
        self.filepath.replace(self.filepath.parent / (self.filepath.stem + ".bak1" + self.filepath.suffix))

    def mark_dirty(self):
        """Call after registry change to trigger auto-save."""
        self._dirty = True
        if self.autosave:
            # Note: caller must provide registry to save
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Return file stats."""
        if not self.filepath.exists():
            return {"exists": False, "size": 0}
        stat = self.filepath.stat()
        return {
            "exists": True,
            "path": str(self.filepath),
            "size_bytes": stat.st_size,
            "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        }


def attach_persistence(engine, filepath: str = "data/skills_registry.json",
                        autosave: bool = True) -> SkillRegistryPersistence:
    """
    Attach persistence to AutoSkillEngine.
    Loads existing registry on attach, auto-saves after lifecycle.
    """
    pers = SkillRegistryPersistence(filepath=filepath, autosave=autosave)

    # Load existing
    existing = pers.load_registry()
    if existing:
        engine.registry.skills.update(existing)
        print(f"    [Persist] Loaded {len(existing)} skills from {filepath}")

    # Monkey-patch lifecycle to auto-save
    original_run = engine.run_lifecycle

    def run_with_save(task: str, required_keywords=None):
        candidate = original_run(task, required_keywords)
        if candidate and pers.autosave:
            pers.save(engine.registry.skills, engine.registry.evolution)
            print(f"    [Persist] Auto-saved {len(engine.registry.skills)} skills")
        return candidate

    engine.run_lifecycle = run_with_save
    engine.persistence = pers
    return pers