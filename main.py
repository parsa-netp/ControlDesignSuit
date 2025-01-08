import logging
import inspect

from PySide6.QtGui import QAction,QDrag
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel, QMenuBar,QLineEdit,QPushButton,QGridLayout,QHBoxLayout,QComboBox,QTreeWidget,QTreeWidgetItem
from PySide6.QtCore import Qt,QMimeData

import qtpynodeeditor as nodeeditor
from qtpynodeeditor.type_converter import TypeConverter

from Handlers.FlowView import CustomFlowView

from Data.INPUT.input_number import NumberSourceDataModel
from Data.OUTPUT.output_number import NumberDisplayModel
from Data.Type_Convertors import DecimalData,IntegerData

from Main_Operands import Basic_Arithmetic


def integer_to_decimal_converter(data: IntegerData) -> DecimalData:
    return DecimalData(float(data.number))

def decimal_to_integer_converter(data: DecimalData) -> IntegerData:
    return IntegerData(int(data.number))


def get_classes_from_module(module):

    class_list = []

    for name in dir(module):  # Get all attributes in the module
        model_class = getattr(module, name, None)  # Retrieve the attribute

        # Check if it's a class and belongs to the given module (not inherited)
        if inspect.isclass(model_class) and model_class.__module__ == module.__name__:
            class_list.append(name)

    return class_list


def operation_doc(main_window, custom_flow_view):
    # Retrieve the list of module names from Main_Operands.Basic_Arithmetic
    modules = get_classes_from_module(Basic_Arithmetic)

    # Create a dockable menu
    dock_widget = QDockWidget("Operation Menu", main_window)
    dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # Add content to the dockable menu
    dock_content = QWidget()
    dock_layout = QVBoxLayout(dock_content)

    # Add a tree structure with the main category and clickable subsections
    tree_widget = QTreeWidget(dock_content)
    tree_widget.setHeaderHidden(True)

    main_category_item = QTreeWidgetItem(tree_widget)
    main_category_item.setText(0, "Basic Arithmetic")
    main_category_item.setFlags(Qt.ItemIsEnabled)  # Disable selection & prevent collapsing

    # Subsections (modules) as clickable items
    for module_name in modules:
        module_item = QTreeWidgetItem(main_category_item)
        module_item.setText(0, module_name)

    tree_widget.expandAll()

    # Connect item click to adding nodes
    tree_widget.itemClicked.connect(lambda item, _: handle_item_click(item, custom_flow_view))

    dock_layout.addWidget(tree_widget)
    dock_widget.setWidget(dock_content)
    main_window.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

    return dock_widget

def handle_item_click(item, custom_flow_view):
    if item.parent() is not None:
        class_name = item.text(0)  # Get the clicked class name

    try:
        # Dynamically retrieve the class from the module
        model_class = getattr(Basic_Arithmetic, class_name, None)

        if model_class is not None:
            # Instantiate the class
            node_model = model_class()

            # Create a node in the scene
            node = custom_flow_view.scene.create_node(node_model)

            # Position node in the center of the scene
            center_point = custom_flow_view.mapToScene(custom_flow_view.viewport().rect().center())
            node.graphics_object.setPos(center_point)
        else:
            print(f"Class '{class_name}' not found in Main_Operands.Basic_Arithmetic")

    except ModuleNotFoundError:
        print("Error: Module  not found. Check if it exists and is correctly imported.")



def main(app):

    registry = nodeeditor.DataModelRegistry()

    # Register models with style directly
    operations = (Basic_Arithmetic.AdditionModel, Basic_Arithmetic.DivisionModel, Basic_Arithmetic.ModuloModel,
                  Basic_Arithmetic.MultiplicationModel,Basic_Arithmetic.SubtractionModel,)

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

    dock_widget = operation_doc(Main_Window,view)

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