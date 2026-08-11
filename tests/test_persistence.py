#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core.persistence — save/load/seed/merge.
"""

import json
import os
import tempfile

import pytest

from core.persistence import SkillRegistryPersistence, attach_persistence
from core.auto_skills import AutoSkillEngine


class TestSkillRegistryPersistence:
    def test_save_and_load(self):
        pers = SkillRegistryPersistence(filepath="test_registry.json", autosave=False)
        registry = {
            "Python": {"name": "Python", "category": "Programming", "level": 0.8}
        }
        pers.save(registry)
        loaded = pers.load_registry()
        assert "Python" in loaded
        assert loaded["Python"]["level"] == 0.8
        os.remove("test_registry.json")

    def test_load_nonexistent_returns_empty(self):
        pers = SkillRegistryPersistence(filepath="nonexistent.json", autosave=False)
        loaded = pers.load_registry()
        assert loaded == {}

    def test_load_evolution(self):
        pers = SkillRegistryPersistence(filepath="test_evo.json", autosave=False)
        registry = {"A": {"name": "A"}}
        evolution = {"A": {"level": 0.5, "usage_count": 10}}
        pers.save(registry, evolution)
        loaded_evo = pers.load_evolution()
        assert "A" in loaded_evo
        assert loaded_evo["A"]["level"] == 0.5
        os.remove("test_evo.json")

    def test_load_seed_json(self):
        pers = SkillRegistryPersistence(autosave=False)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"skills": [{"name": "Docker", "category": "DevOps"}]}, f)
            path = f.name
        try:
            seed = pers.load_seed(path)
            assert "Docker" in seed
            assert seed["Docker"]["category"] == "DevOps"
        finally:
            os.remove(path)

    def test_load_seed_csv(self):
        pers = SkillRegistryPersistence(autosave=False)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Python,Programming,5\n")
            f.write("Docker,DevOps,6\n")
            path = f.name
        try:
            seed = pers.load_seed(path)
            assert "Python" in seed
            assert seed["Python"]["category"] == "Programming"
            assert seed["Python"]["complexity"] == 5
            assert "Docker" in seed
        finally:
            os.remove(path)

    def test_merge_seed_no_overwrite(self):
        pers = SkillRegistryPersistence(autosave=False)
        target = {"A": {"level": 0.9}}
        seed = {"A": {"level": 0.1}, "B": {"level": 0.5}}
        merged = pers.merge_seed(seed, target, overwrite=False)
        assert merged["A"]["level"] == 0.9  # kept target
        assert merged["B"]["level"] == 0.5  # added seed

    def test_merge_seed_with_overwrite(self):
        pers = SkillRegistryPersistence(autosave=False)
        target = {"A": {"level": 0.9}}
        seed = {"A": {"level": 0.1}}
        merged = pers.merge_seed(seed, target, overwrite=True)
        assert merged["A"]["level"] == 0.1

    def test_backup_rotation(self):
        pers = SkillRegistryPersistence(filepath="test_bak.json", backup_count=2)
        pers.save({"v1": {}})
        pers.save({"v2": {}})
        pers.save({"v3": {}})
        assert os.path.exists("test_bak.bak1.json")
        os.remove("test_bak.json")
        os.remove("test_bak.bak1.json")
        if os.path.exists("test_bak.bak2.json"):
            os.remove("test_bak.bak2.json")

    def test_get_stats(self):
        pers = SkillRegistryPersistence(filepath="test_stats.json", autosave=False)
        stats = pers.get_stats()
        assert stats["exists"] is False
        pers.save({"A": {}})
        stats = pers.get_stats()
        assert stats["exists"] is True
        assert stats["size_bytes"] > 0
        os.remove("test_stats.json")


class TestAttachPersistence:
    def test_attach_loads_existing(self):
        pers = SkillRegistryPersistence(filepath="test_attach.json", autosave=False)
        pers.save({"Existing": {"name": "Existing", "level": 0.5}})
        engine = AutoSkillEngine(use_llm=False)
        attach_persistence(engine, filepath="test_attach.json", autosave=False)
        assert "Existing" in engine.registry.skills
        os.remove("test_attach.json")

    def test_attach_auto_save(self):
        engine = AutoSkillEngine(use_llm=False)
        pers = attach_persistence(engine, filepath="test_auto.json", autosave=True)
        # Mock: run a task that generates a skill
        engine.registry.skills["TestSkill"] = {"name": "TestSkill", "level": 0.5}
        pers.save(engine.registry.skills)
        loaded = pers.load_registry()
        assert "TestSkill" in loaded
        os.remove("test_auto.json")