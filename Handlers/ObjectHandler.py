from PySide6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem
)
from PySide6.QtGui import QColor, QBrush, QFont, QPen, QMouseEvent,QPainter


class ObjectHandler(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, name,main_window):
        super().__init__(x, y, width, height)

        self.main_window = main_window

        # Set initial colors and other properties
        self.normal_color = color
        self.highlight_color = QColor(255, 255, 0, 128)  # Highlight color
        self.border_color = QColor(0, 0, 0)  # Border color
        self.corner_radius = 50  # Radius of the rounded corners

        # Set the appearance
        self.setBrush(QBrush(self.normal_color))  # Set color for the object
        self.setPen(QPen(self.border_color, 2))  # Set the border for the object
        self.setFlag(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)  # Enable hover events


        # Add the name text inside the object
        self.name = name
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(5, 5)  # Position of the text
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))

        # Menu Group initialization
        self.menu_group = None  # Initially, no menu is displayed

    def hoverEnterEvent(self, event):
        """Change the object's appearance when the mouse hovers over it."""
        self.setBrush(QBrush(self.highlight_color))  # Change color to highlight color
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Revert the object's appearance when the mouse leaves it."""
        self.setBrush(QBrush(self.normal_color))  # Revert back to normal color
        super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Show the properties menu in the main window's properties dock."""
        position = self.scenePos()
        properties = {
            "Name": self.name,
            "X": f"{position.x():.2f}",
            "Y": f"{position.y():.2f}",
        }
        self.main_window.show_properties(properties)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Remove the menu if the object is clicked."""
        if self.menu_group:
            self.scene.removeItem(self.menu_group)
            self.menu_group = None  # Clear the menu
        super().mousePressEvent(event)
