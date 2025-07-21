from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


class DynamicSeparatorTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.separator_row_indices = []

    def set_separator_rows(self, indices):
        self.separator_row_indices = indices
        self.update_separator_rows()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_separator_rows()

    def update_separator_rows(self):
        font = self.font()
        metrics = QFontMetrics(font)
        for sep_row in self.separator_row_indices:
            for col in range(self.columnCount()):
                col_width = self.columnWidth(col)
                eq_width = metrics.horizontalAdvance("=")
                num_eq = max(1, col_width // eq_width)
                self.setItem(sep_row, col, QTableWidgetItem("=" * num_eq))
