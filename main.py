import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsScene, QDockWidget, QGroupBox,QWidget, QMenuBar,QMenu,QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTransform

import PageHandler
import ObjectHandler



class SceneItemManager:
    def __init__(self, scene):
        self.scene = scene

    def get_items(self):
        """Return all items in the scene."""
        return self.scene.items()

    def get_object_handlers(self):
        """Return all items that are instances of ObjectHandler."""
        return [item for item in self.get_items() if isinstance(item, ObjectHandler.ObjectHandler)]

    def get_object_positions(self):
        """
        Return a list of tuples containing the names and positions of all ObjectHandler items.
        Each tuple contains (name, x, y).
        """
        positions = []
        for item in self.get_object_handlers():
            name = item.name
            position = item.pos()  # Get the position of the object
            positions.append((name, position.x(), position.y()))
        return positions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Design Suit")
        self.resize(1080, 720)

        # Create a central widget with a vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Graphics view and scene for the 2D plane
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.view = PageHandler.PageHandler(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        main_layout.addWidget(self.view)
        self.view.setTransform(QTransform().scale(0.5, 0.5))
        self.view.setFocus()

        # Create the top menu bar
        self.create_menu_bar()

        # Create dock widget for the left sidebar
        dock_widget = QDockWidget("Options", self)
        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

        # Create a sidebar widget with layout
        sidebar_widget = QGroupBox()
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Search bar at the top
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_tree)
        sidebar_layout.addWidget(self.search_bar)

        # Tree widget for sections and subsections
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        sidebar_layout.addWidget(self.tree_widget)

        # Add sections and subsections
        self.add_sections_to_tree()

        # Set sidebar as dock widget's main content
        dock_widget.setWidget(sidebar_widget)

        # Connect tree item clicks to add items to the 2D plane
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def add_sections_to_tree(self):
        # Create sections and subsections
        section1 = QTreeWidgetItem(["Section 1"])
        section2 = QTreeWidgetItem(["Section 2"])
        section3 = QTreeWidgetItem(["Section 3"])

        for i in range(1, 4):
            subsection = QTreeWidgetItem([f"Add Rectangle {i}"])
            section1.addChild(subsection)

        for i in range(1, 3):
            subsection = QTreeWidgetItem([f"Add Circle {i}"])
            section2.addChild(subsection)

        for i in range(1, 5):
            subsection = QTreeWidgetItem([f"Add Custom Shape {i}"])
            section3.addChild(subsection)

        self.tree_widget.addTopLevelItem(section1)
        self.tree_widget.addTopLevelItem(section2)
        self.tree_widget.addTopLevelItem(section3)

        # Expand all sections by default
        self.tree_widget.expandAll()

    def on_item_clicked(self, item):
        # When a subsection is clicked, add a new shape to the scene
        text = item.text(0)
        if "Rectangle" in text:
            self.add_rectangle(item)
        elif "Circle" in text:
            self.add_circle(item)
        elif "Custom Shape" in text:
            self.add_custom_shape(item)

    def add_rectangle(self, item):
        name = item.text(0)
        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a draggable rectangle to the scene at the center
        rect = ObjectHandler.ObjectHandler(center.x() - 50, center.y() - 25, 100, 50, QColor("lightblue"), name)
        self.scene.addItem(rect)

        # Add its border
        rect.add_border()

    def add_circle(self, item):
        name = item.text(0)

        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a draggable circle (ellipse) to the scene at the center
        ellipse = ObjectHandler.ObjectHandler(center.x() - 25, center.y() - 25, 50, 50, QColor("lightgreen"), name)
        ellipse.setRect(-25, -25, 50, 50)  # Center the ellipse
        self.scene.addItem(ellipse)

        ellipse.add_border()




    def add_custom_shape(self, item):
        name = item.text(0)

        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a custom shape (rectangle for now) to the scene at the center
        rect = ObjectHandler.ObjectHandler(center.x() - 60, center.y() - 30, 120, 60, QColor("lightcoral"), name)
        self.scene.addItem(rect)

        rect.add_border()



    def filter_tree(self, text):
        # Filter tree items based on the search bar input
        text = text.lower()
        for i in range(self.tree_widget.topLevelItemCount()):
            section = self.tree_widget.topLevelItem(i)
            section.setHidden(True)
            match = False

            if text in section.text(0).lower():
                section.setHidden(False)
                match = True

            for j in range(section.childCount()):
                subsection = section.child(j)
                subsection.setHidden(True)

                if text in subsection.text(0).lower():
                    subsection.setHidden(False)
                    section.setHidden(False)
                    match = True

            section.setExpanded(match)

    def get_viewport_scene_rect(self):
        # Map the view's visible rectangle to the scene coordinates
        view_rect = self.view.viewport().rect()
        scene_rect = self.view.mapToScene(view_rect).boundingRect()
        return scene_rect

    def create_menu_bar(self):
        # Create a top menu bar with options
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        edit_menu = QMenu("Edit", self)
        menu_bar.addMenu(edit_menu)

        view_menu = QMenu("View", self)
        menu_bar.addMenu(view_menu)

        object_menu = QMenu("Objects", self)
        menu_bar.addMenu(object_menu)

        show_objects_action = object_menu.addAction("Show Objects Info")
        show_objects_action.triggered.connect(self.show_objects_info)

    def show_objects_info(self):
        # Retrieve object information from the scene
        object_info = []
        for item in self.view.scene().items():  # Iterate over all items in the scene
            if isinstance(item, ObjectHandler.ObjectHandler):  # Check if the item is an ObjectHandler
                name = item.name
                position = item.pos()  # Get the position of the object in the scene
                object_info.append(f"{name} at ({position.x():.2f}, {position.y():.2f})")

        # Format the object information
        if object_info:
            message = "Objects in the scene:\n" + "\n".join(object_info)
        else:
            message = "No objects in the scene."

        # Display the information in a message box
        QMessageBox.information(self, "Scene Objects", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())