from __future__ import annotations

from typing import Optional, Sequence

from PySide6.QtWidgets import QHBoxLayout, QWidget


class DetailMixin:
    """Helpers for managing the detail widget area."""

    def _init_detail_layout(self) -> None:
        detail_layout = self.ui.DetailWidget.layout()
        if detail_layout is None:
            detail_layout = QHBoxLayout(self.ui.DetailWidget)
            detail_layout.setContentsMargins(0, 0, 0, 0)
            detail_layout.setSpacing(0)
        self._detail_layout = detail_layout
        self._current_detail_widget: Optional[QWidget] = None

    def _apply_custom_widgets(self, widgets: Sequence[QWidget]) -> None:
        container = self.ui.widget_custom_show
        layout = container.layout()
        if layout is None:
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)

        self._clear_custom_widget(layout)

        for widget in widgets:
            if widget.parent() is not container:
                widget.setParent(container)
            layout.addWidget(widget)
            widget.show()

        container.setVisible(bool(widgets))

    def _clear_custom_widget(self, layout: QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _show_detail_widget(self, widget: QWidget) -> None:
        if self._current_detail_widget is widget:
            widget.show()
            return

        if self._current_detail_widget is not None and self._current_detail_widget is not widget:
            self._detail_layout.removeWidget(self._current_detail_widget)
            self._current_detail_widget.setParent(None)

        if widget.parent() is not self.ui.DetailWidget:
            widget.setParent(self.ui.DetailWidget)
        if self._detail_layout.indexOf(widget) == -1:
            self._detail_layout.addWidget(widget)
        widget.show()
        self._current_detail_widget = widget

    def _clear_detail_widget(self) -> None:
        if self._current_detail_widget is None:
            return
        self._detail_layout.removeWidget(self._current_detail_widget)
        self._current_detail_widget.hide()
        self._current_detail_widget.setParent(None)
        self._current_detail_widget = None
