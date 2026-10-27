"""Single-use, single-thread in-memory fixture shadows. No durable root journal."""

from collections.abc import Callable
from types import TracebackType

from dgca_next.graph.network import FixtureBuilder, MutationStage, SparseNetwork, _Editor


class InjectedFailure(RuntimeError):
    """Synthetic fault after an internal shadow write, before publication."""


class FixtureTransaction(FixtureBuilder):
    def __init__(self, network: SparseNetwork, *, fail_at: MutationStage | None = None) -> None:
        super().__init__(network)
        if fail_at is not None and type(fail_at) is not MutationStage:
            raise ValueError("fail_at must be MutationStage")
        self._fail_at = fail_at
        self._closed = False
        self._visited: list[MutationStage] = []
        self._shadow = _Editor(network, self._checkpoint)

    @property
    def visited_stages(self) -> tuple[MutationStage, ...]:
        return tuple(self._visited)

    def _checkpoint(self, stage: MutationStage) -> None:
        self._visited.append(stage)
        if stage is self._fail_at:
            raise InjectedFailure(f"INJECTED_FAILURE: {stage.value}")

    def _require_open(self) -> None:
        if self._closed:
            raise ValueError("CLOSED_FIXTURE_TRANSACTION")

    def _apply(self, operation: Callable[[_Editor], None]) -> None:
        self._require_open()
        try:
            operation(self._shadow)
        except BaseException:
            self._closed = True
            raise

    def commit(self) -> None:
        self._require_open()
        try:
            self._shadow.publish()
        finally:
            self._closed = True

    def rollback(self) -> None:
        self._closed = True

    def transaction(self, *, fail_at: MutationStage | None = None) -> FixtureTransaction:
        raise ValueError("NESTED_FIXTURE_TRANSACTION_UNSUPPORTED")

    def __enter__(self) -> FixtureTransaction:
        self._require_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
