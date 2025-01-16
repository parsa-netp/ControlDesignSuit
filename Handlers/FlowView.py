from PySide6.QtGui import QKeyEvent, QMouseEvent ,QWheelEvent,QContextMenuEvent,QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView,QMenu
import qtpynodeeditor as nodeeditor

class CustomFlowView(nodeeditor.FlowView):
    def __init__(self, scene):
        super().__init__(scene)
        self.space_pressed = False  # Track if spacebar is pressed
        self.drag_enabled = False   # Disable node dragging
        self.setDragMode(QGraphicsView.NoDrag)  # Initially no dragging

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scale(1.2, 1.2)  # Zoom in
        elif key == Qt.Key_Minus:
            self.scale(1 / 1.2, 1 / 1.2)  # Zoom out
        elif key == Qt.Key_Delete:
            self.delete_selected_items()
        elif key == Qt.Key_Space:
            self.space_pressed = True
            self.setCursor(Qt.ClosedHandCursor)  # Show panning cursor
            self.setDragMode(QGraphicsView.ScrollHandDrag)  # Enable dragging
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.space_pressed = False
            self.setCursor(Qt.ArrowCursor)  # Restore normal cursor
            self.setDragMode(QGraphicsView.NoDrag)  # Disable dragging
        else:
            super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if self.space_pressed :
            self.setCursor(Qt.ClosedHandCursor)  # Show grabbing cursor
            self.setDragMode(QGraphicsView.ScrollHandDrag)  # Enable dragging
        elif event.button() == Qt.LeftButton:
            event.accept()  # Prevent left-click dragging
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.space_pressed:
            event.accept()  # Prevent default dragging behavior
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.space_pressed:
            self.setCursor(Qt.OpenHandCursor)  # Restore panning cursor
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Pans the scene vertically with the mouse wheel."""
        delta = event.angleDelta().y()  # Get the vertical wheel movement
        pan_speed = 1.0  # Adjust this value to control the panning speed

        # Calculate the amount to translate the view
        vertical_movement = -delta * pan_speed

        # Apply the translation to the view
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + vertical_movement)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ Show a custom context menu when right-clicking. """
        menu = QMenu(self)

        # Example actions
        action1 = QAction("Zoom In", self)
        action1.triggered.connect(lambda: self.scale(1.2, 1.2))

        action2 = QAction("Zoom Out", self)
        action2.triggered.connect(lambda: self.scale(1 / 1.2, 1 / 1.2))

        action3 = QAction("Reset View", self)
        action3.triggered.connect(lambda: self.resetTransform())

        action4 = QAction("Delete Selected", self)
        action4.triggered.connect(lambda: self.delete_selected_items())

        # Add actions to the menu
        menu.addAction(action1)
        menu.addAction(action2)
        menu.addSeparator()
        menu.addAction(action3)
        menu.addSeparator()
        menu.addAction(action4)

        # Show menu at cursor position
        menu.exec_(event.globalPos())

    def delete_selected_items(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

