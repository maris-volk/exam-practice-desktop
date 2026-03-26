from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
from services.captcha_service import CaptchaService


class CaptchaWidget(QWidget):
    solved = pyqtSignal()

    def __init__(self, image_paths, captcha_service: CaptchaService, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.captcha_service = captcha_service
        self.current_order = self.captcha_service.shuffle()
        self.was_solved = False

        self.labels = []
        self.selected_index = None

        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_resize)

        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

        self.original_pixmaps = [QPixmap(path) for path in self.image_paths]

        for i in range(4):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setContentsMargins(0, 0, 0, 0)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setStyleSheet("border: 1px solid gray; background: lightgray;")
            label.mousePressEvent = lambda event, idx=i: self.on_label_click(idx)
            self.labels.append(label)
            row, col = divmod(i, 2)
            layout.addWidget(label, row, col)

        self._update_sizes()

    def _update_sizes(self):
        if not self.labels:
            return

        avail_width = self.width()
        avail_height = self.height()
        max_cell_size = min(avail_width // 2, avail_height // 2)

        if max_cell_size <= 0:
            return

        for label in self.labels:
            label.setFixedSize(max_cell_size, max_cell_size)

        self.layout().update()
        self._update_images()

    def _update_images(self):
        if not self.labels:
            return

        for idx, label in enumerate(self.labels):
            img_idx = self.current_order[idx]
            w, h = label.width(), label.height()
            if w > 0 and h > 0:
                pixmap = self.original_pixmaps[img_idx].scaled(
                    w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                label.setPixmap(pixmap)

    def _delayed_resize(self):
        self._update_sizes()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start(10)

    def _perform_swap(self, i: int, j: int):
        self.current_order = self.captcha_service.swap(self.current_order, i, j)
        self._update_images()
        is_solved = self.captcha_service.is_solved(self.current_order)
        if is_solved and not self.was_solved:
            self.solved.emit()
        self.was_solved = is_solved

    def on_label_click(self, clicked_idx):
        if self.selected_index is None:
            self.selected_index = clicked_idx
            self.labels[clicked_idx].setStyleSheet("border: 2px solid blue; background: lightgray;")
        else:
            if self.selected_index != clicked_idx:
                self._perform_swap(self.selected_index, clicked_idx)
            self.labels[self.selected_index].setStyleSheet("border: 1px solid gray; background: lightgray;")
            self.selected_index = None

    def reset(self):
        self.current_order = self.captcha_service.shuffle()
        self.was_solved = False
        self._update_images()
        if self.selected_index is not None:
            self.labels[self.selected_index].setStyleSheet("border: 1px solid gray; background: lightgray;")
            self.selected_index = None

    def is_solved(self):
        return self.captcha_service.is_solved(self.current_order)