import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDockWidget, QGroupBox,
    QWidget, QGraphicsEllipseItem, QMenuBar, QMenu, QGraphicsTextItem,
    QMessageBox
)
from PySide6.QtCore import Qt, QPointF, QEvent,Signal
from PySide6.QtGui import QColor, QBrush, QTransform, QKeyEvent,QFont


class ObjectHandler(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, name):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(color))
        self.setFlag(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        # Create the text on object
        self.name = name
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(x + 5, y + 5)
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))

        # Add a border around the rectangle
        self.border = QGraphicsRectItem(self)
        self.border.setPen(Qt.SolidLine)
        self.border.setBrush(Qt.NoBrush)
        self.update_border()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange or change == QGraphicsRectItem.ItemTransformChange:
            self.update_border()
        return super().itemChange(change, value)

    def update_border(self):
        # Update the border to match the rectangle's geometry
        margin = 1  # Border width
        self.border.setRect(
            self.rect().x() - margin,
            self.rect().y() - margin,
            self.rect().width() + 2 * margin,
            self.rect().height() + 2 * margin
        )



class PageHandler(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(self.renderHints())
        self.setDragMode(QGraphicsView.NoDrag)
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure the view can receive keyboard focus
        self.setInteractive(True)  # Ensure the scene responds to mouse clicks
        self.create_dot_grid(spacing=20, dot_size=2, color=QColor(100, 100, 100))

        # Initial scale factor
        self.scale_factor = 1.0
        self.viewport().installEventFilter(self)  # Enable mouse wheel zooming

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            selected_items = self.scene().selectedItems()
            if selected_items:
                for item in selected_items:
                    self.scene().removeItem(item)
        else:
            super().keyPressEvent(event)

    def create_dot_grid(self, spacing, dot_size, color):
        for x in range(int(self.scene().sceneRect().left()), int(self.scene().sceneRect().right()), spacing):
            for y in range(int(self.scene().sceneRect().top()), int(self.scene().sceneRect().bottom()), spacing):
                if (y // spacing) % 2 == 0:
                    adjusted_color = QColor(
                        color.red() // 2,
                        color.green() // 2,
                        color.blue() // 2
                    )
                    current_dot_size = dot_size
                else:
                    adjusted_color = color
                    current_dot_size = dot_size * 2

                circle = QGraphicsEllipseItem(
                    x - current_dot_size / 2,
                    y - current_dot_size / 2,
                    current_dot_size,
                    current_dot_size
                )
                circle.setBrush(QBrush(adjusted_color))
                circle.setPen(Qt.NoPen)
                circle.setZValue(-1)
                self.scene().addItem(circle)

    def get_viewport_scene_rect(self):
        view_rect = self.viewport().rect()
        return self.mapToScene(view_rect).boundingRect()

    def scale_view(self, scale_increment):
        self.scale_factor += scale_increment
        self.scale_factor = max(0.1, self.scale_factor)  # Prevent too much scaling in or out
        transform = QTransform()
        transform.scale(self.scale_factor, self.scale_factor)
        center = self.mapToScene(self.viewport().rect().center())
        self.setTransform(transform)
        self.centerOn(center)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and obj is self.viewport():
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier:
                # Zoom when Control is pressed
                delta = event.angleDelta().y() / 120
                self.scale_view(delta * 0.1)
            else:
                # Allow normal vertical scrolling when Control is not pressed
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - event.angleDelta().y()
                )
            return True
        return super().eventFilter(obj, event)

    def get_objects_in_scene(self):
        """Returns a list of names of all ObjectHandler items in the scene."""
        objects = []
        for item in self.scene().items():  # Iterate over all items in the scene
            if isinstance(item, ObjectHandler):  # Check if the item is an ObjectHandler
                objects.append(item.name)  # Add the item's name to the list
        return objects

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         # Store the starting point of the drag
    #         self.is_dragging = True
    #         self.last_pos = event.position()
    #     super().mousePressEvent(event)
    #
    # def mouseMoveEvent(self, event):
    #     if self.is_dragging:
    #         # Calculate the distance moved and translate the scene
    #         delta = event.position() - self.last_pos
    #         self.last_pos = event.position()
    #
    #         # Move the view (pan the scene)
    #         self.translate_scene(delta)
    #     super().mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.is_dragging = False
    #     super().mouseReleaseEvent(event)
    #
    # def translate_scene(self, delta):
    #     # Move the scene based on the mouse movement
    #     self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
    #     self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

    class SceneItemManager:
        def __init__(self, scene):
            self.scene = scene

        def get_items(self):
            """Return all items in the scene."""
            return self.scene.items()

        def get_object_handlers(self):
            """Return all items that are instances of ObjectHandler."""
            return [item for item in self.get_items() if isinstance(item, ObjectHandler)]

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
        for item in self.view.scene().items():  # Iterate over all items in the scene
            if isinstance(item, ObjectHandler):  # Check if the item is an ObjectHandler
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