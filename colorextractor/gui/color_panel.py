from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class ColorRow(QWidget):
    """One row in the color list: swatch, hex + name, and percentage."""

    def __init__(self, color_info, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        swatch = QFrame()
        swatch.setFixedSize(28, 28)
        swatch.setStyleSheet(
            f"background-color: {color_info.hex}; border: 1px solid #1e1e1e; border-radius: 4px;"
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        hex_label = QLabel(color_info.hex.upper())
        hex_label.setStyleSheet(
            "font-family: Menlo, Consolas, monospace; font-weight: 600; color: #f0f0f0;"
        )
        name_label = QLabel(color_info.name)
        name_label.setStyleSheet("color: #999999; font-size: 11px;")
        text_layout.addWidget(hex_label)
        text_layout.addWidget(name_label)

        percent_label = QLabel(f"{color_info.percentage:.1f}%")
        percent_label.setStyleSheet("color: #bbbbbb;")
        percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(swatch)
        layout.addLayout(text_layout, 1)
        layout.addWidget(percent_label)


class ColorPanel(QWidget):
    """Right-hand sidebar: extraction controls plus the sorted color list."""

    settingsChanged = Signal()
    colorCopied = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("colorPanel")
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("COLORS")
        header.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #999999; "
            "padding: 14px 12px 4px 12px;"
        )

        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(12, 4, 12, 10)
        controls_layout.setSpacing(6)

        palette_row = QHBoxLayout()
        palette_row.addWidget(QLabel("Palette size"))
        palette_row.addStretch(1)
        self.palette_spin = QSpinBox()
        self.palette_spin.setRange(2, 256)
        self.palette_spin.setValue(32)
        self.palette_spin.valueChanged.connect(self.settingsChanged)
        palette_row.addWidget(self.palette_spin)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Show top"))
        top_row.addStretch(1)
        self.top_spin = QSpinBox()
        self.top_spin.setRange(0, 256)
        self.top_spin.setSpecialValueText("All")
        self.top_spin.setValue(0)
        self.top_spin.valueChanged.connect(self.settingsChanged)
        top_row.addWidget(self.top_spin)

        self.group_checkbox = QCheckBox("Merge similar colors")
        self.group_checkbox.setChecked(True)
        self.group_checkbox.stateChanged.connect(self.settingsChanged)

        controls_layout.addLayout(palette_row)
        controls_layout.addLayout(top_row)
        controls_layout.addWidget(self.group_checkbox)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(0)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        self.hint_label = QLabel("Click a color to copy its hex code")
        self.hint_label.setStyleSheet("color: #777777; font-size: 10px; padding: 6px 12px;")

        layout.addWidget(header)
        layout.addWidget(controls)
        layout.addWidget(self.list_widget, 1)
        layout.addWidget(self.hint_label)

    def get_settings(self):
        top_n = None if self.top_spin.value() == 0 else self.top_spin.value()
        return {
            "num_colors": self.palette_spin.value(),
            "top_n": top_n,
            "group_similar": self.group_checkbox.isChecked(),
        }

    def set_colors(self, results):
        self.list_widget.clear()
        for color_info in results:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, color_info.hex)
            row_widget = ColorRow(color_info)
            item.setSizeHint(row_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row_widget)

    def _on_item_clicked(self, item):
        hex_code = item.data(Qt.UserRole)
        QGuiApplication.clipboard().setText(hex_code)
        self.colorCopied.emit(hex_code)
