import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDockWidget, QGroupBox, QWidget, QGraphicsEllipseItem , QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QColor, QBrush, QTransform, QKeyEvent



class DraggableRect(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(color))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange:
            # Update the scene with new position if needed
            return value
        return super().itemChange(change, value)


class DraggableGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(self.renderHints())
        self.setDragMode(QGraphicsView.NoDrag)
        self.is_dragging = False
        self.last_pos = QPointF()

        # Create the dot grid
        self.create_dot_grid(spacing=20, dot_size=2, color=QColor(100, 100, 100))

    def create_dot_grid(self, spacing, dot_size, color):
        # Draw circles across the scene
        for x in range(int(self.scene().sceneRect().left()), int(self.scene().sceneRect().right()), spacing):
            for y in range(int(self.scene().sceneRect().top()), int(self.scene().sceneRect().bottom()), spacing):

                if (y // spacing) % 2 == 0:
                    # Halve the color intensity and use original dot size
                    adjusted_color = QColor(
                        color.red() // 2,
                        color.green() // 2,
                        color.blue() // 2
                    )
                    current_dot_size = dot_size
                else:
                    # Use the original color and double the dot size
                    adjusted_color = color
                    current_dot_size = dot_size * 2

                # Create the circle, ensuring the size changes but the position stays the same
                circle = QGraphicsEllipseItem(
                    x - current_dot_size / 2,
                    y - current_dot_size / 2,
                    current_dot_size,
                    current_dot_size
                )

                # Apply the modified or original color
                circle.setBrush(QBrush(adjusted_color))
                circle.setPen(Qt.NoPen)  # Remove outline
                circle.setZValue(-1)  # Keep circles in the background
                self.scene().addItem(circle)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Store the starting point of the drag
            self.is_dragging = True
            self.last_pos = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Calculate the distance moved and translate the scene
            delta = event.position() - self.last_pos
            self.last_pos = event.position()

            # Move the view (pan the scene)
            self.translate_scene(delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        super().mouseReleaseEvent(event)

    def translate_scene(self, delta):
        # Move the scene based on the mouse movement
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())



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
        self.view = DraggableGraphicsView(self.scene)  # Use DraggableGraphicsView for panning
        self.view.setRenderHint(self.view.renderHints())
        main_layout.addWidget(self.view)
        self.view.setTransform(QTransform().scale(0.5, 0.5))

        # Initial scale factor
        self.scale_factor = 1.0

        # Enable mouse wheel event for scaling
        self.view.viewport().installEventFilter(self)

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
        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a draggable rectangle to the scene at the center
        rect = DraggableRect(center.x() - 50, center.y() - 25, 100, 50, QColor("lightblue"))
        self.scene.addItem(rect)

    def add_circle(self):
        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a draggable circle (ellipse) to the scene at the center
        ellipse = DraggableRect(center.x() - 25, center.y() - 25, 50, 50, QColor("lightgreen"))
        ellipse.setRect(-25, -25, 50, 50)  # Center the ellipse
        self.scene.addItem(ellipse)

    def add_custom_shape(self):
        # Get the center of the visible area
        visible_area = self.get_viewport_scene_rect()
        center = visible_area.center()

        # Add a custom shape (rectangle for now) to the scene at the center
        rect = DraggableRect(center.x() - 60, center.y() - 30, 120, 60, QColor("lightcoral"))
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

    def scale_view(self, scale_increment):
        # Adjust the scale of the view
        self.scale_factor += scale_increment
        self.scale_factor = max(0.1, self.scale_factor)  # Prevent too much scaling in or out
        transform = QTransform()
        transform.scale(self.scale_factor, self.scale_factor)

        # Get the center of the view and zoom towards it
        center = self.view.mapToScene(self.view.viewport().rect().center())
        transform.translate(center.x(), center.y())
        transform.scale(self.scale_factor, self.scale_factor)
        transform.translate(-center.x(), -center.y())

        # Apply the new transform to the view
        self.view.setTransform(transform)

    def eventFilter(self, source, event):
        # Check if the event is a wheel event
        if event.type() == QEvent.Wheel and source is self.view.viewport():
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                # Zoom in/out when Control is held
                delta = event.angleDelta().y()
                scale_increment = 0.1 if delta > 0 else -0.1
                self.scale_view(scale_increment)
                return True
        return super().eventFilter(source, event)

    def keyPressEvent(self, event: QKeyEvent):
        # Delete selected items when the Delete key is pressed
        if event.key() == Qt.Key_Delete:
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)

    def create_menu_bar(self):
        # Create the menu bar
        menu_bar = QMenuBar(self)

        # File menu
        file_menu = QMenu("File", self)
        file_menu.addAction("New", self.new_project)
        file_menu.addAction("Open", self.open_project)
        file_menu.addAction("Save", self.save_project)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = QMenu("Edit", self)
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Preferences")

        # Help menu
        help_menu = QMenu("Help", self)
        help_menu.addAction("About", self.show_about_dialog)

        # Add menus to the menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(help_menu)

        # Set the menu bar for the main window
        self.setMenuBar(menu_bar)

    def new_project(self):
        print("New project created!")

    def open_project(self):
        print("Open project dialog!")

    def save_project(self):
        print("Save project dialog!")

    def show_about_dialog(self):
        print("About dialog opened!")


# Main application setup
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
