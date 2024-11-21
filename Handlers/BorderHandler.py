from PySide6.QtWidgets import ( QGraphicsRectItem,QGraphicsItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class BorderHandler(QGraphicsRectItem):
    def __init__(self, parent_item):
        super().__init__(parent_item.rect())  # Initialize with the parent item's geometry
        self.parent_item = parent_item
        self.setPen(QColor(0, 0, 0))  # Black border
        self.setBrush(Qt.NoBrush)  # Transparent fill
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)  # Make the border selectable
        self.setZValue(parent_item.zValue() - 1)  # Ensure the border is drawn behind the parent item

    def update_geometry(self):
        """Update the border geometry to match the parent item's geometry."""
        self.setRect(self.parent_item.rect())  # Update size and position
        self.setPos(self.parent_item.pos())  # Sync position with parent item

    def itemChange(self, change, value):
        """Respond to changes in selection."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:  # Border is selected
                print(f"Border of {self.parent_item.name} selected.")
        return super().itemChange(change, value)


