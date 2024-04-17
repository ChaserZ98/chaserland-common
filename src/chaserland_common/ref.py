class Ref[T]:
    def __init__(self, current: T = None) -> None:
        self.current = current

    @property
    def current(self) -> T:
        return self._current

    @current.setter
    def current(self, value: T) -> None:
        self._current = value
