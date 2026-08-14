from typing import Callable, Dict, Optional, Any

class State:
    """Base class for game states."""
    def __init__(self, name: str) -> None:
        self.name = name

    def enter(self, **kwargs: Any) -> None:
        """Called when entering the state."""
        pass

    def exit(self) -> None:
        """Called when exiting the state."""
        pass

    def update(self, dt: float) -> None:
        """Update logic for the state."""
        pass

    def render(self, screen: Any) -> None:
        """Render the state."""
        pass

class StateManager:
    """Manages states and transitions for a Pong game."""
    def __init__(self) -> None:
        self._states: Dict[str, State] = {}
        self._current: Optional[State] = None
        self._transitions: Dict[str, Dict[str, Callable[[], bool]]] = {}

    def add_state(self, state: State) -> None:
        """Register a state."""
        if state.name in self._states:
            raise ValueError(f"State '{state.name}' already exists")
        self._states[state.name] = state

    def add_transition(self, from_state: str, to_state: str, condition: Callable[[], bool]) -> None:
        """Add a transition condition from one state to another."""
        if from_state not in self._states or to_state not in self._states:
            raise ValueError("Both states must exist")
        if from_state not in self._transitions:
            self._transitions[from_state] = {}
        self._transitions[from_state][to_state] = condition

    def set_state(self, name: str, **kwargs: Any) -> None:
        """Change to a new state, calling exit/enter hooks."""
        if name not in self._states:
            raise ValueError(f"Unknown state '{name}'")
        if self._current is not None:
            self._current.exit()
        self._current = self._states[name]
        self._current.enter(**kwargs)

    def update(self, dt: float) -> None:
        """Update current state and check transitions."""
        if self._current is None:
            return
        # Check transitions from current state
        if self._current.name in self._transitions:
            for to_state, condition in self._transitions[self._current.name].items():
                if condition():
                    self.set_state(to_state)
                    break
        self._current.update(dt)

    def render(self, screen: Any) -> None:
        """Render current state."""
        if self._current is not None:
            self._current.render(screen)

    @property
    def current_state(self) -> Optional[str]:
        """Return the name of the current state, or None."""
        return self._current.name if self._current else None
