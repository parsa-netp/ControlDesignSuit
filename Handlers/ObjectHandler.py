from PySide6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsSimpleTextItem
)
from PySide6.QtGui import QColor, QBrush, QFont, QPen, QMouseEvent
from PySide6.QtCore import QPointF


class ObjectHandler(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, name):
        super().__init__(x, y, width, height)

        # Set initial colors and other properties
        self.normal_color = color
        self.highlight_color = QColor(255, 255, 0, 128)  # Highlight color
        self.border_color = QColor(0, 0, 0)  # Border color

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
        """Show the menu below the object on double-click."""
        if self.menu_group:
            # If the menu already exists, remove it first
            if self.scene():
                self.scene().removeItem(self.menu_group)
            self.menu_group = None  # Clear the menu group

        # Create the menu as a QGraphicsItemGroup
        self.menu_group = QGraphicsItemGroup()

        # Menu background (a simple rectangle)
        menu_rect = QGraphicsRectItem(0, 0, 120, 60, self.menu_group)
        menu_rect.setBrush(QBrush(QColor(220, 220, 220)))  # Light gray background
        menu_rect.setPen(QPen(QColor(100, 100, 100), 1))  # Dark gray border

        # Add text options inside the menu
        option1 = QGraphicsSimpleTextItem("Option 1", self.menu_group)
        option2 = QGraphicsSimpleTextItem("Option 2", self.menu_group)
        option1.setPos(10, 10)
        option2.setPos(10, 30)

        # Position the menu below the object
        menu_position = QPointF(self.rect().center().x() - 60, self.rect().bottom() + 10)
        scene_position = self.mapToScene(menu_position)  # Convert local position to scene coordinates
        self.menu_group.setPos(scene_position)

        # Add the menu to the scene
        if self.scene():
            self.scene().addItem(self.menu_group)

        # Debugging output
        print("Menu created at position:", scene_position)

        super().mouseDoubleClickEvent(event)  # Call the base class method

    def mousePressEvent(self, event: QMouseEvent):
        """Remove the menu if the object is clicked."""
        if self.menu_group:
            self.scene.removeItem(self.menu_group)
            self.menu_group = None  # Clear the menu
        super().mousePressEvent(event)
