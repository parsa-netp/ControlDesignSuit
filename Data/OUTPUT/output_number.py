
import contextlib
import logging

from PySide6.QtGui import QAction

from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel, QMenuBar,QLineEdit
from PySide6.QtCore import Qt

import qtpynodeeditor as nodeeditor
from qtpynodeeditor import NodeData, NodeDataModel, NodeDataType,NodeValidationState, Port, PortType
from qtpynodeeditor.type_converter import TypeConverter

from Handlers.FlowView import CustomFlowView

from Data.Type_Convertors import DecimalData,IntegerData

class NumberDisplayModel(NodeDataModel):
    name = "NumberDisplay"
    data_type = DecimalData.data_type
    caption_visible = False
    num_ports = {PortType.input: 1,
                 PortType.output: 0,
                 }
    port_caption = {'input': {0: 'Number'}}

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        self._label.setMargin(3)
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

    def set_in_data(self, data: NodeData, port: Port):
        self._number = data
        number_ok = (self._number is not None and
                     self._number.data_type.id in ('decimal', 'integer'))

        if number_ok:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            self._label.setText(self._number.number_as_text())
        else:
            self._validation_state = NodeValidationState.warning
            self._validation_message = "Missing or incorrect inputs"
            self._label.clear()

        self._label.adjustSize()

    def embedded_widget(self) -> QWidget:
        return self._label
