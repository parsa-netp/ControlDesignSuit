from PySide6.QtWidgets import (QApplication,QGraphicsView,QGraphicsEllipseItem)
from PySide6.QtCore import (Qt, QEvent)
from PySide6.QtGui import (QColor, QBrush, QTransform, QKeyEvent)

import ObjectHandler

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
            if isinstance(item, ObjectHandler.ObjectHandler):  # Check if the item is an ObjectHandler
                objects.append(item.name)  # Add the item's name to the list
        return objects
