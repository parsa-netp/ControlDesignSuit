from PySide6.QtGui import  QKeyEvent
from PySide6.QtCore import Qt

import qtpynodeeditor as nodeeditor


class CustomFlowView(nodeeditor.FlowView):
    def __init__(self, scene):
        super().__init__(scene)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scale(1.2, 1.2)  # Zoom in
        elif key == Qt.Key_Minus:
            self.scale(1 / 1.2, 1 / 1.2)  # Zoom out
        elif key == Qt.Key_Delete:
            self.delete_selected_items()
        elif key == Qt.Key_Control:
            pass
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control:
            pass
        else:
            super().keyReleaseEvent(event)

    def delete_selected_items(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)
