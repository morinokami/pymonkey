from typing import Dict, Tuple, Union

from .object import Object


class Environment:

    def __init__(self, store: Dict[str, Object] = None, outer=None):
        if store is None:
            store = {}
        self.store = store
        self.outer = outer

    def get(self, name: str) -> Union[Tuple[Object, bool], Tuple[None, bool]]:
        if name in self.store:
            return self.store[name], True
        elif self.outer is not None and name in self.outer.store:
            return self.outer.get(name)
        return None, False

    def set(self, name: str, val: Object) -> Object:
        self.store[name] = val
        return val


def new_enclosed_environment(outer: Environment) -> Environment:
    env = new_environment()
    env.outer = outer
    return env


def new_environment() -> Environment:
    s: Dict[str, Object] = {}
    return Environment(s)
