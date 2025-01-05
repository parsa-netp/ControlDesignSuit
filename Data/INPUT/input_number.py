from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import  QWidget,QLineEdit

from qtpynodeeditor import NodeData, NodeDataModel ,PortType

from Data.Type_Convertors import DecimalData,IntegerData


class NumberSourceDataModel(NodeDataModel):
    name = "NumberSource"
    caption_visible = False
    num_ports = {PortType.input: 0,
                 PortType.output: 1,
                 }
    port_caption = {'output': {0: 'Result'}}
    data_type = DecimalData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._line_edit = QLineEdit()
        self._line_edit.setValidator(QDoubleValidator())
        self._line_edit.setMaximumSize(self._line_edit.sizeHint())
        self._line_edit.textChanged.connect(self.on_text_edited)
        self._line_edit.setText("0.0")

    @property
    def number(self):
        return self._number

    def save(self) -> dict:
        doc = super().save()
        if self._number:
            doc['number'] = self._number.number
        return doc

    def restore(self, state: dict):
        try:
            value = float(state["number"])
        except Exception:
            ...
        else:
            self._number = DecimalData(value)
            self._line_edit.setText(self._number.number_as_text())

    def out_data(self, port: int) -> NodeData:
        return self._number

    def embedded_widget(self) -> QWidget:
        return self._line_edit

    def on_text_edited(self, string: str):
        try:
            number = float(self._line_edit.text())
        except ValueError:
            self._data_invalidated.emit(0)
        else:
            self._number = DecimalData(number)
            self.data_updated.emit(0)
