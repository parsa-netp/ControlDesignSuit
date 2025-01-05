import contextlib

from qtpynodeeditor import NodeData, NodeDataModel,NodeValidationState, Port

from Data.Type_Convertors import DecimalData,IntegerData


class MathOperationDataModel(NodeDataModel):
    caption_visible = True
    num_ports = {
        'input': 2,
        'output': 1,
    }
    port_caption_visible = True
    data_type = DecimalData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number1 = None
        self._number2 = None
        self._result = None
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

    @property
    def caption(self):
        return self.name

    def _check_inputs(self):
        number1_ok = (self._number1 is not None and
                      self._number1.data_type.id in ('decimal', 'integer'))
        number2_ok = (self._number2 is not None and
                      self._number2.data_type.id in ('decimal', 'integer'))

        if not number1_ok or not number2_ok:
            self._validation_state = NodeValidationState.warning
            self._validation_message = "Missing or incorrect inputs"
            self._result = None
            self.data_updated.emit(0)
            return False

        self._validation_state = NodeValidationState.valid
        self._validation_message = ''
        return True

    @contextlib.contextmanager
    def _compute_lock(self):
        if not self._number1 or not self._number2:
            raise RuntimeError('inputs unset')

        with self._number1.lock:
            with self._number2.lock:
                yield

        self.data_updated.emit(0)

    def out_data(self, port: int) -> NodeData:
        return self._result

    def set_in_data(self, data: NodeData, port: Port):
        if port.index == 0:
            self._number1 = data
        elif port.index == 1:
            self._number2 = data

        if self._check_inputs():
            with self._compute_lock():
                self.compute()

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message

    def compute(self):
        pass
