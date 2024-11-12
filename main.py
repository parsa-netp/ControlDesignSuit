import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QWidget, QGroupBox, QDockWidget, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QColor


class DotGridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(2000, 2000)  # Large size to allow scrolling

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(200, 200, 200))  # Light grey dots
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw dots in a grid pattern
        spacing = 20  # Distance between dots
        for x in range(0, self.width(), spacing):
            for y in range(0, self.height(), spacing):
                painter.drawPoint(QPoint(x, y))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Searchable Sidebar with Dropdown Sections")

        # Central widget layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Scroll area for the dot grid in main content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        dot_grid = DotGridWidget()
        scroll_area.setWidget(dot_grid)
        main_layout.addWidget(scroll_area)

        # Create dock widget for left sidebar
        dock_widget = QDockWidget("Options", self)
        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

        # Create a sidebar widget with a border and margin
        sidebar_widget = QGroupBox()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Add margin around the sidebar
        sidebar_widget.setLayout(sidebar_layout)

        # Search bar at the top
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_tree)  # Connect search function
        sidebar_layout.addWidget(self.search_bar)

        # Tree widget for dropdown-style sections and subsections
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        sidebar_layout.addWidget(self.tree_widget)

        # Add sections and subsections
        self.add_sections_to_tree()

        # Set the styled sidebar as the dock widget's main content
        dock_widget.setWidget(sidebar_widget)

    def add_sections_to_tree(self):
        # Create sections
        section1 = QTreeWidgetItem(["Section 1"])
        section2 = QTreeWidgetItem(["Section 2"])
        section3 = QTreeWidgetItem(["Section 3"])

        # Add subsections to each section
        for i in range(1, 4):
            subsection = QTreeWidgetItem([f"Subsection {i} in Section 1"])
            section1.addChild(subsection)

        for i in range(1, 3):
            subsection = QTreeWidgetItem([f"Subsection {i} in Section 2"])
            section2.addChild(subsection)

        for i in range(1, 5):
            subsection = QTreeWidgetItem([f"Subsection {i} in Section 3"])
            section3.addChild(subsection)

        # Add sections to the tree widget
        self.tree_widget.addTopLevelItem(section1)
        self.tree_widget.addTopLevelItem(section2)
        self.tree_widget.addTopLevelItem(section3)

        # Expand all sections by default
        self.tree_widget.expandAll()

    def filter_tree(self, text):
        # Traverse and filter the tree based on the search bar input
        text = text.lower()
        for i in range(self.tree_widget.topLevelItemCount()):
            section = self.tree_widget.topLevelItem(i)
            section.setHidden(True)  # Hide section initially
            match = False

            # Check if the section itself matches the text
            if text in section.text(0).lower():
                section.setHidden(False)
                match = True

            # Check subsections for matches
            for j in range(section.childCount()):
                subsection = section.child(j)
                subsection.setHidden(True)  # Hide subsection initially

                if text in subsection.text(0).lower():
                    subsection.setHidden(False)
                    section.setHidden(False)  # Unhide section if a match is found
                    match = True

            # Expand the section if it or any subsection matches
            section.setExpanded(match)


# Main application setup
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
