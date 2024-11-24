import sys
sys.path.append(r'D:\Develop\Python\Pycharm\ControlDesignSuit\Handlers')

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QTreeWidget, QTreeWidgetItem
  , QDockWidget, QGroupBox,QWidget, QMenuBar,QMenu,QMessageBox,QLabel,QGridLayout,QPushButton,QWidgetAction
,QToolBar
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
        self.resize(1920, 1080)  # or any custom size you prefer

        # Optionally maximize the window after resizing
        self.showMaximized()        # Create a central widget with a vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Graphics view and scene for the 2D plane
        self.view = PageHandler()

        main_layout.addWidget(self.view)
        self.view.setTransform(QTransform().scale(0.5, 0.5))
        self.view.setFocus()

        # Create the top menu bar
        self.create_menu_bar()

        self.create_tool_bar()
        # Create dock widget for the left sidebar
        self.function_dock = QDockWidget("Options", self)
        self.function_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.function_dock)
        self.function_dock.setMinimumSize(300, 400)
        self.function_dock.setMaximumSize(800, 1200)

        # Create dock widget for the right sidebar
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.properties_dock.setMinimumSize(300, 400)
        self.properties_dock.setMaximumSize(800, 1200)

        # Create a sidebar widget with layout
        sidebar_widget = QGroupBox()
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Tree widget for sections and subsections
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        sidebar_layout.addWidget(self.tree_widget)

        # Add sections and subsections
        self.add_sections_to_tree()

        # Set sidebar as dock widget's main content
        self.function_dock.setWidget(sidebar_widget)

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
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        rect = ObjectHandler(center.x() - 50, center.y() - 25, 100, 50, QColor("lightblue"), name,self)
        self.view.scene.addItem(rect)

    def add_circle(self, item):
        name = item.text(0)

        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        ellipse = ObjectHandler(center.x() - 25, center.y() - 25, 50, 50, QColor("lightgreen"), name,self)
        ellipse.setRect(-25, -25, 50, 50)  # Center the ellipse
        self.view.scene.addItem(ellipse)

    def add_custom_shape(self, item):
        name = item.text(0)

        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        rect = ObjectHandler(center.x() - 60, center.y() - 30, 120, 60, QColor("lightcoral"), name,self)
        self.view.scene.addItem(rect)

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

    def toggle_properties(self):
        """Toggle the visibility of the Properties dock widget."""
        if self.properties_dock.isVisible():
            self.properties_dock.hide()
        else:
            self.properties_dock.show()

    def toggle_options(self):
        """Toggle the visibility of the Options dock widget."""
        if self.function_dock.isVisible():
            self.function_dock.hide()
        else:
            self.function_dock.show()

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

    def show_properties(self, properties):
        """Update the properties dock with the given properties."""
        # Clear the existing content in the properties dock
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(10)  # Add some spacing between rows
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins for better visuals

        # Add headers for "Property" and "Value"
        header_property = QLabel("<b>Property</b>")
        header_value = QLabel("<b>Value</b>")
        layout.addWidget(header_property, 0, 0)
        layout.addWidget(header_value, 0, 1)

        # Add properties in a grid layout
        for row, (key, value) in enumerate(properties.items(), start=1):
            property_label = QLabel(f"{key}:")
            value_label = QLabel(f"{value}")

            # Use bold for property names
            property_label.setStyleSheet("font-weight: bold;")
            value_label.setStyleSheet("color: #333;")  # Subtle color for values

            layout.addWidget(property_label, row, 0)
            layout.addWidget(value_label, row, 1)

        # Set the layout and apply it to the dock widget
        widget.setLayout(layout)
        self.properties_dock.setWidget(widget)

    def create_tool_bar(self):
          # Create a toolbar
          toolbar = QToolBar("Main Toolbar", self)

          # Add actions or widgets to the toolbar
          self.add_toolbar_buttons(toolbar)

          # Add the toolbar to the main window
          self.addToolBar(Qt.TopToolBarArea, toolbar)  # Place at the top of the window

    def add_toolbar_buttons(self, toolbar):
        # Create buttons and add them to the toolbar
        button1 = QPushButton("Button 1")
        button1.clicked.connect(self.on_button1_clicked)
        toolbar.addWidget(button1)

        button2 = QPushButton("Button 2")
        button2.clicked.connect(self.on_button2_clicked)
        toolbar.addWidget(button2)

    def on_button1_clicked(self):
        print("Button 1 clicked")

    def on_button2_clicked(self):
        print("Button 2 clicked")


if   __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())