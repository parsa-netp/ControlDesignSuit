import threading
from qtpynodeeditor import (NodeData, NodeDataModel, NodeDataType,NodeValidationState, Port, PortType)

class DecimalData(NodeData):
    data_type = NodeDataType("decimal", "Decimal")

    def __init__(self, number: float = 0.0):
        self._number = number
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def number(self) -> float:
        return self._number

    def number_as_text(self) -> str:
        return '%g' % self._number


class IntegerData(NodeData):
    data_type = NodeDataType("integer", "Integer")

    def __init__(self, number: int = 0):
        self._number = number
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def number(self) -> int:
        return self._number

    def number_as_text(self) -> str:
        return str(self._number)
