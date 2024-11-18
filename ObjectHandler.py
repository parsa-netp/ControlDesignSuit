from PySide6.QtWidgets import ( QGraphicsRectItem, QGraphicsTextItem)
from PySide6.QtGui import QColor, QBrush,QFont

import BorderHandler

class ObjectHandler(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, name):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(color))  # Set the object's color
        self.setFlag(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        # Store the name of the object
        self.name = name

        # Create and position the text label
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(5, 5)  # Position relative to the object
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))

        # Initialize the border (added after the object is added to a scene)
        self.border = None
        self.setZValue(1)  # Ensure the object is in front of the border

    def add_border(self):
        """Create and add the border to the scene after this item is added to the scene."""
        if not self.scene():
            raise RuntimeError("ObjectHandler must be added to a scene before adding a border.")
        self.border = BorderHandler.BorderHandler(self)
        self.scene().addItem(self.border)

    def itemChange(self, change, value):
        """Update the border's geometry when the object is moved or transformed."""
        if change in {QGraphicsRectItem.ItemPositionChange, QGraphicsRectItem.ItemTransformChange}:
            if self.border:
                self.border.update_geometry()
        return super().itemChange(change, value)
