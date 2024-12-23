import contextlib
import logging
import threading

from PySide6.QtGui import QDoubleValidator,QAction,QKeyEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel, QMenuBar,QLineEdit
from PySide6.QtCore import Qt

import qtpynodeeditor as nodeeditor
from qtpynodeeditor import (NodeData, NodeDataModel, NodeDataType,NodeValidationState, Port, PortType)
from qtpynodeeditor.type_converter import TypeConverter


class CustomFlowView(nodeeditor.FlowView):
    def __init__(self, scene):
        super().__init__(scene)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scale(1.2, 1.2)  # Zoom in
        elif key == Qt.Key_Minus:
            self.scale(1 / 1.2, 1 / 1.2)  # Zoom out
        elif key == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def delete_selected_items(self):
        # Implement the logic to delete selected items from the scene
        for item in self.scene().selectedItems():
            self.scene().removeItem(item)



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


class AdditionModel(MathOperationDataModel):
    name = "Addition"

    def compute(self):
        self._result = DecimalData(self._number1.number + self._number2.number)


class DivisionModel(MathOperationDataModel):
    name = "Division"
    port_caption = {'input': {0: 'Dividend',
                              1: 'Divisor',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        if self._number2.number == 0.0:
            self._validation_state = NodeValidationState.error
            self._validation_message = "Division by zero error"
            self._result = None
        else:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            self._result = DecimalData(self._number1.number / self._number2.number)


class ModuloModel(MathOperationDataModel):
    name = 'Modulo'
    data_type = IntegerData.data_type
    port_caption = {'input': {0: 'Dividend',
                              1: 'Divisor',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        if self._number2.number == 0.0:
            self._validation_state = NodeValidationState.error
            self._validation_message = "Division by zero error"
            self._result = None
        else:
            self._result = IntegerData(self._number1.number % self._number2.number)


class MultiplicationModel(MathOperationDataModel):
    name = 'Multiplication'
    port_caption = {'input': {0: 'A',
                              1: 'B',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        self._result = DecimalData(self._number1.number * self._number2.number)


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


class SubtractionModel(MathOperationDataModel):
    name = "Subtraction"
    port_caption = {'input': {0: 'Minuend',
                              1: 'Subtrahend'},
                    'output': {0: 'Result'}, }

    def compute(self):
        self._result = DecimalData(self._number1.number - self._number2.number)


def integer_to_decimal_converter(data: IntegerData) -> DecimalData:
    return DecimalData(float(data.number))


def decimal_to_integer_converter(data: DecimalData) -> IntegerData:
    return IntegerData(int(data.number))


def main(app):

    registry = nodeeditor.DataModelRegistry()

    # Register models with style directly
    Operations = (AdditionModel, DivisionModel, ModuloModel,
                  MultiplicationModel,SubtractionModel, NumberDisplayModel)

    input_data = (NumberSourceDataModel,)

    output_data = (NumberDisplayModel,)

    for Operations in Operations:
        registry.register_model(Operations, category='Operations', style=None)

    for input_data in input_data:
        registry.register_model(input_data, category='Input', style=None)

    for output_data in output_data:
        registry.register_model(output_data, category='OutPut', style=None)

    # Register type converters
    dec_converter = TypeConverter(DecimalData.data_type, IntegerData.data_type, decimal_to_integer_converter)
    int_converter = TypeConverter(IntegerData.data_type, DecimalData.data_type, integer_to_decimal_converter)

    registry.register_type_converter(DecimalData.data_type, IntegerData.data_type, dec_converter)
    registry.register_type_converter(IntegerData.data_type, DecimalData.data_type, int_converter)

    # Create scene and view
    scene = nodeeditor.FlowScene(registry=registry)
    view = CustomFlowView(scene)

    # Create the main window
    Main_Window = QMainWindow()
    Main_Window.setWindowTitle("Node Editor with Dockable Menu")

    # Set the view as the central widget
    Main_Window.setCentralWidget(view)

    # Create a dockable menu
    dock_widget = QDockWidget("Dockable Menu", Main_Window)
    dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # Add content to the dockable menu
    dock_content = QWidget()
    dock_layout = QVBoxLayout(dock_content)
    dock_label = QLabel("This is the dockable menu", dock_content)
    dock_layout.addWidget(dock_label)

    dock_widget.setWidget(dock_content)
    Main_Window.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)  # Initially docked on the left side

    # Create a menu bar with an action to toggle the docked widget
    menubar = Main_Window.menuBar()
    view_menu = menubar.addMenu("View")
    toggle_action = QAction("Toggle Dock", Main_Window)
    toggle_action.triggered.connect(lambda: toggle_dock(dock_widget))
    view_menu.addAction(toggle_action)

    # Show the main window
    view.setWindowTitle("Calculator")
    Main_Window.showMaximized()
    Main_Window.show()


    return scene, view, Main_Window


def toggle_dock(dock_widget):
    if dock_widget.isVisible():
        dock_widget.hide()
    else:
        dock_widget.show()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    app = QApplication([])
    scene, view, main_window = main(app)
    app.exec_()