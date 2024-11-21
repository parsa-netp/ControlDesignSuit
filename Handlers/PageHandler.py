from PySide6.QtWidgets import (QApplication,QGraphicsView,QGraphicsEllipseItem,QGraphicsLineItem)
from PySide6.QtCore import (Qt, QEvent)
from PySide6.QtGui import (QColor, QBrush, QTransform, QKeyEvent,QMouseEvent,QPen)

from Handlers.ObjectHandler import  ObjectHandler
from Handlers.TarHandler import TarHandler

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

        # Variables for line drawing
        self.start_point = None
        self.temp_line = None  # Temporary line displayed during mouse movement

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

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            selected_items = self.scene().selectedItems()
            if selected_items:
                for item in selected_items:
                    self.scene().removeItem(item)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Get the position in scene coordinates
            scene_pos = self.mapToScene(event.pos())

            # Check if there is an item at the clicked position
            clicked_item = self.scene().itemAt(scene_pos, self.transform())
            if isinstance(clicked_item, (ObjectHandler, TarHandler)):
                # Let the clicked object handle its interaction
                super().mousePressEvent(event)
                return

            # Start the line-drawing process
            self.start_point = scene_pos
            self.temp_line = QGraphicsLineItem()
            self.temp_line.setPen(QPen(QColor(0, 0, 255), 2, Qt.DashLine))  # Dashed blue line
            self.scene().addItem(self.temp_line)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_point and self.temp_line:
            # Update the temporary line to follow the mouse position
            current_point = self.mapToScene(event.pos())
            self.temp_line.setLine(
                self.start_point.x(),
                self.start_point.y(),
                current_point.x(),
                current_point.y(),
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.start_point:
            # Get the ending position in scene coordinates
            end_point = self.mapToScene(event.pos())

            # Check if the release point is on an existing item; if so, skip creating a new line
            released_item = self.scene().itemAt(end_point, self.transform())
            if isinstance(released_item, (ObjectHandler, TarHandler)):
                # Remove the temporary line if it exists
                if self.temp_line:
                    self.scene().removeItem(self.temp_line)
                    self.temp_line = None
                self.start_point = None
                return

            # Add a permanent line to the scene
            permanent_line = TarHandler(self.start_point, end_point)
            self.scene().addItem(permanent_line)

            # Clean up the temporary line and starting point
            if self.temp_line:
                self.scene().removeItem(self.temp_line)
                self.temp_line = None
            self.start_point = None
        else:
            super().mouseReleaseEvent(event)
