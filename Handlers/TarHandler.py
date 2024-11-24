from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QPen, QColor, QMouseEvent
from PySide6.QtCore import Qt



class TarHandler(QGraphicsLineItem):
    def __init__(self, start_point, end_point, color=QColor(255, 0, 0), thickness=5):

        super().__init__(start_point.x(), start_point.y(), end_point.x(), end_point.y())
        self.normal_color = color  # Default line color
        self.highlight_color = QColor(255, 255, 0)  # Highlight color (yellow)
        self.thickness = thickness  # Normal thickness
        self.highlight_thickness = thickness + 1  # Highlighted thickness

        self.setPen(QPen(self.normal_color, self.thickness))
        self.start_point = start_point
        self.end_point = end_point

        # Enable selection and movement
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsLineItem.ItemIsMovable, True)

        # Enable hover events for highlighting
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        """Highlight the line when the mouse hovers over it."""
        self.setPen(QPen(self.highlight_color, self.highlight_thickness, Qt.SolidLine))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Revert the line's appearance when the mouse leaves it."""
        self.setPen(QPen(self.normal_color, self.thickness, Qt.SolidLine))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Handle selection and movement by default
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)