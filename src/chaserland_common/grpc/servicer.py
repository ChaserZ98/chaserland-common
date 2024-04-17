from ..ref import Ref
from .aio import AbstractContext


class BaseServicer:
    def __init__(self, server_context_ref: Ref[AbstractContext] = Ref()):
        self.server_context_ref = server_context_ref

    @property
    def server_context(self) -> AbstractContext:
        if self.server_context_ref.current is None:
            raise AttributeError("Server context is not set")
        return self.server_context_ref.current
