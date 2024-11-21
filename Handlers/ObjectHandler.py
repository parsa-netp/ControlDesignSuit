from PySide6.QtWidgets import ( QGraphicsRectItem, QGraphicsTextItem)
from PySide6.QtGui import QColor, QBrush,QFont,QPen


class ObjectHandler(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, name):
        super().__init__(x, y, width, height)

        self.normal_color = color  # Store the normal color
        self.highlight_color = QColor(255, 255, 0, 128)  # Highlight color (semi-transparent yellow)
        self.border_color = QColor(0, 0, 0)  # Default border color
        self.highlight_border_color = QColor(0, 0, 255)  # Highlighted border color (blue)

        self.setBrush(QBrush(self.normal_color))  # Set the object's initial color
        self.setPen(QPen(self.border_color, 2))  # Set the initial border
        self.setFlag(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        self.setPen(QPen(self.border_color, 2))  # Revert to the normal border
        self.setPen(QPen(self.highlight_border_color, 3))  # Change border to highlighted

        self.setAcceptHoverEvents(True)  # Enable hover events

        self.name = name
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(5, 5)  # Position relative to the object
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))

    def hoverEnterEvent(self, event):
        """Change the object's appearance when the mouse hovers over it."""
        self.setBrush(QBrush(self.highlight_color))  # Apply the highlight color
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Revert the object's appearance when the mouse leaves it."""
        self.setBrush(QBrush(self.normal_color))  # Revert to the normal color
        super().hoverLeaveEvent(event)