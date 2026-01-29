from typing import Protocol
from typing import List

class Operation(Protocol):
    def apply(self) -> None: ...


class PanelSession():
    operations: List[Operation]