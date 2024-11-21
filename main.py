

import sys
sys.path.append(r'D:\Develop\Python\Pycharm\ControlDesignSuit\Handlers')

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsScene, QDockWidget, QGroupBox,QWidget, QMenuBar,QMenu,QMessageBox ,QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTransform


from Handlers.PageHandler import PageHandler
from Handlers.ObjectHandler import  ObjectHandler
from Handlers.TarHandler import TarHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Design Suit")
        self.resize(1920 , 1080)

        # Create a central widget with a vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Graphics view and scene for the 2D plane
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.view = PageHandler(self.scene)
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
        rect = ObjectHandler(center.x() - 50, center.y() - 25, 100, 50, QColor("lightblue"), name)
        self.scene.addItem(rect)

    def add_circle(self, item):
        name = item.text(0)

        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a draggable circle (ellipse) to the scene at the center
        ellipse = ObjectHandler(center.x() - 25, center.y() - 25, 50, 50, QColor("lightgreen"), name)
        ellipse.setRect(-25, -25, 50, 50)  # Center the ellipse
        self.scene.addItem(ellipse)



    def add_custom_shape(self, item):
        name = item.text(0)

        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a custom shape (rectangle for now) to the scene at the center
        rect = ObjectHandler(center.x() - 60, center.y() - 30, 120, 60, QColor("lightcoral"), name)
        self.scene.addItem(rect)




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
        line_info = []

        # Iterate over all items in the scene, sorted by their Z-value
        for item in sorted(self.view.scene().items(), key=lambda i: i.zValue()):
            if isinstance(item, ObjectHandler):
                name = item.name
                position = item.scenePos()
                object_info.append(f"{name} at ({position.x():.2f}, {position.y():.2f})")
            elif isinstance(item, TarHandler):
                start = item.start_point
                end = item.end_point
                line_info.append(f"Line from ({start.x():.2f}, {start.y():.2f}) to ({end.x():.2f}, {end.y():.2f})")

        # Combine the information
        info = []
        if object_info:
            info.append("Objects in the scene:")
            info.extend(object_info)
        if line_info:
            info.append("Lines in the scene:")
            info.extend(line_info)

        # Format the message
        message = "\n".join(info) if info else "No objects or lines in the scene."

        # Display the information in a message box
        QMessageBox.information(self, "Scene Items", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())