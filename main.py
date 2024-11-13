import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDockWidget, QGroupBox, QWidget, QGraphicsEllipseItem
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush, QWheelEvent, QTransform


class DraggableRect(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(color))
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemSendsGeometryChanges
        )


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
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)  # Set the scene size
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        main_layout.addWidget(self.view)
        self.create_dot_grid(spacing=20, dot_size=2, color=QColor(100, 100, 100))
        self.view.setTransform(QTransform().scale(0.5, 0.5))

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

    def on_item_clicked(self, item, column):
        # When a subsection is clicked, add a new shape to the scene
        text = item.text(0)
        if "Rectangle" in text:
            self.add_rectangle()
        elif "Circle" in text:
            self.add_circle()
        elif "Custom Shape" in text:
            self.add_custom_shape()

    def add_rectangle(self):
        # Add a draggable rectangle to the scene at a default position
        rect = DraggableRect(0, 0, 100, 50, QColor("lightblue"))
        self.scene.addItem(rect)

    def add_circle(self):
        # Add a draggable circle (ellipse) to the scene
        ellipse = DraggableRect(0, 0, 50, 50, QColor("lightgreen"))
        ellipse.setRect(-25, -25, 50, 50)  # Center the ellipse at the origin
        self.scene.addItem(ellipse)

    def add_custom_shape(self):
        # You could define and add more complex custom shapes here
        rect = DraggableRect(0, 0, 120, 60, QColor("lightcoral"))
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

    def create_dot_grid(self, spacing, dot_size, color):
        # Draw circles across the scene
        for x in range(int(self.scene.sceneRect().left()), int(self.scene.sceneRect().right()), spacing):
            for y in range(int(self.scene.sceneRect().top()), int(self.scene.sceneRect().bottom()), spacing):
                # Alternate circle size based on the row (y coordinate)
                current_dot_size = dot_size if (y // spacing) % 2 == 0 else dot_size * 2
                # Create the circle, ensuring the size changes but the position stays the same
                circle = QGraphicsEllipseItem(x - current_dot_size / 2,
                                              y - current_dot_size / 2,
                                              current_dot_size,
                                              current_dot_size)
                circle.setBrush(QBrush(color))
                circle.setPen(Qt.NoPen)  # Remove outline
                circle.setZValue(-1)  # Keep circles in the background
                self.scene.addItem(circle)

    def wheelEvent(self, event: QWheelEvent):
        # Check if Ctrl key is held down for zooming
        if event.modifiers() == Qt.ControlModifier:
            angle = event.angleDelta().y()
            scale_factor = 1.2 if angle > 0 else 1 / 1.2
            current_transform = self.view.transform()
            new_transform = current_transform.scale(scale_factor, scale_factor)
            self.view.setTransform(new_transform)
        else:
            # Default behavior, scroll up/down
            super().wheelEvent(event)


# Main application setup
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
