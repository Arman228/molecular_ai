import pytest
from typing import Any, List

# Assume the StateManager code is in a module named 'state_manager'
from state_manager import State, StateManager

class DummyState(State):
    def __init__(self, name: str, log: List[str]):
        super().__init__(name)
        self.log = log
        self.update_called = 0
        self.render_called = 0

    def enter(self, **kwargs: Any) -> None:
        self.log.append(f"enter:{self.name}")

    def exit(self) -> None:
        self.log.append(f"exit:{self.name}")

    def update(self, dt: float) -> None:
        self.update_called += 1
        self.log.append(f"update:{self.name}:{dt}")

    def render(self, screen: Any) -> None:
        self.render_called += 1
        self.log.append(f"render:{self.name}")

def test_initial_state_none():
    sm = StateManager()
    assert sm.current_state is None

def test_add_state_and_set_state():
    sm = StateManager()
    log = []
    state = DummyState("menu", log)
    sm.add_state(state)
    sm.set_state("menu")
    assert sm.current_state == "menu"
    assert log == ["enter:menu"]

def test_set_state_exits_previous():
    sm = StateManager()
    log = []
    sm.add_state(DummyState("a", log))
    sm.add_state(DummyState("b", log))
    sm.set_state("a")
    sm.set_state("b")
    assert log == ["enter:a", "exit:a", "enter:b"]

def test_duplicate_state_raises():
    sm = StateManager()
    sm.add_state(DummyState("a", []))
    with pytest.raises(ValueError):
        sm.add_state(DummyState("a", []))

def test_set_unknown_state_raises():
    sm = StateManager()
    with pytest.raises(ValueError):
        sm.set_state("nonexistent")

def test_update_calls_current_state():
    sm = StateManager()
    log = []
    state = DummyState("play", log)
    sm.add_state(state)
    sm.set_state("play")
    sm.update(0.5)
    assert state.update_called == 1
    assert log[-1] == "update:play:0.5"

def test_render_calls_current_state():
    sm = StateManager()
    log = []
    state = DummyState("play", log)
    sm.add_state(state)
    sm.set_state("play")
    sm.render("screen")
    assert state.render_called == 1
    assert log[-1] == "render:play"

def test_transition_condition_true():
    sm = StateManager()
    log = []
    sm.add_state(DummyState("menu", log))
    sm.add_state(DummyState("play", log))
    sm.set_state("menu")
    sm.add_transition("menu", "play", lambda: True)
    sm.update(0.1)
    assert sm.current_state == "play"
    assert "exit:menu" in log
    assert "enter:play" in log

def test_transition_condition_false():
    sm = StateManager()
    log = []
    sm.add_state(DummyState("menu", log))
    sm.add_state(DummyState("play", log))
    sm.set_state("menu")
    sm.add_transition("menu", "play", lambda: False)
    sm.update(0.1)
    assert sm.current_state == "menu"
    assert "exit:menu" not in log

def test_transition_requires_existing_states():
    sm = StateManager()
    sm.add_state(DummyState("a", []))
    with pytest.raises(ValueError):
        sm.add_transition("a", "b", lambda: True)

def test_update_with_no_state_does_nothing():
    sm = StateManager()
    sm.update(0.1)  # should not raise

def test_render_with_no_state_does_nothing():
    sm = StateManager()
    sm.render("screen")  # should not raise
