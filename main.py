import logging
import inspect

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel, QMenuBar,QLineEdit,QPushButton,QGridLayout,QHBoxLayout
from PySide6.QtCore import Qt

import qtpynodeeditor as nodeeditor
from qtpynodeeditor.type_converter import TypeConverter

from Handlers.FlowView import CustomFlowView
from Data.INPUT.input_number import NumberSourceDataModel
from Data.OUTPUT.output_number import NumberDisplayModel
from Data.Type_Convertors import DecimalData,IntegerData
from Main_Operands.Basic_Arithmetic import AdditionModel,DivisionModel,ModuloModel,MultiplicationModel,SubtractionModel


def integer_to_decimal_converter(data: IntegerData) -> DecimalData:
    return DecimalData(float(data.number))

def decimal_to_integer_converter(data: DecimalData) -> IntegerData:
    return IntegerData(int(data.number))

def find_classes(module: str)->list :
    listofclass = []
    for name, obj in globals().items():
        if inspect.isclass(obj) and obj.__module__ == module:
            listofclass.append(name)
    return listofclass

def operation_doc(main_window):

    modules = find_classes("Main_Operands.Basic_Arithmetic")
    # Create a dockable menu
    dock_widget = QDockWidget("Operation Menu", main_window)
    dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # Add content to the dockable menu
    dock_content = QWidget()
    dock_layout = QGridLayout(dock_content)


    for modules in modules:
        button = QPushButton(modules, dock_content)
        button.clicked.connect(lambda checked, name=modules: print(f"Button {name} clicked!"))  # Example action
        dock_layout.addWidget(button)


    dock_widget.setWidget(dock_content)
    main_window.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)  # Initially docked on the left side
    return dock_widget

def main(app):

    registry = nodeeditor.DataModelRegistry()

    # Register models with style directly
    operations = (AdditionModel, DivisionModel, ModuloModel,
                  MultiplicationModel,SubtractionModel, NumberDisplayModel)

    input_data = (NumberSourceDataModel,)

    output_data = (NumberDisplayModel,)


    for operations in operations:
        registry.register_model(operations, category='Operations', style=None)

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
    Main_Window.setWindowTitle("Control Design Systems")

    # Set the view as the central widget
    Main_Window.setCentralWidget(view)

    dock_widget = operation_doc(Main_Window)

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