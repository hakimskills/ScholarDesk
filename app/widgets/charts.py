# -*- coding: utf-8 -*-
"""
app/widgets/charts.py

Lightweight, dependency-free charts drawn with QPainter so the
dashboard doesn't require a third-party charting library. Two charts
are provided:

- BarChartWidget: simple vertical bar chart (e.g. monthly revenue).
- DonutChartWidget: donut/ring chart with a centered label
  (e.g. today's attendance breakdown).
"""

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient

from app.theme import Colors


class BarChartWidget(QWidget):
    """values: list[tuple[str label, float value]]"""

    def __init__(self, values, bar_color=Colors.PRIMARY, parent=None):
        super().__init__(parent)
        self.values = values
        self.bar_color = QColor(bar_color)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_values(self, values):
        self.values = values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.values:
            painter.end()
            return

        w = self.width()
        h = self.height()
        label_h = 22
        top_pad = 14
        chart_h = h - label_h - top_pad
        max_val = max(v for _, v in self.values) or 1

        n = len(self.values)
        gap = 18
        total_gap = gap * (n + 1)
        bar_w = max(18, (w - total_gap) / n)

        font = QFont(self.font())
        font.setPointSize(9)
        painter.setFont(font)

        x = gap
        for label, value in self.values:
            bar_h = (value / max_val) * chart_h
            y = top_pad + (chart_h - bar_h)

            gradient = QLinearGradient(QPointF(x, y), QPointF(x, top_pad + chart_h))
            top_color = QColor(self.bar_color)
            bottom_color = QColor(self.bar_color)
            bottom_color.setAlpha(140)
            gradient.setColorAt(0, top_color)
            gradient.setColorAt(1, bottom_color)

            rect = QRectF(x, y, bar_w, bar_h)
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(rect, 6, 6)

            painter.setPen(QPen(QColor(Colors.TEXT_MUTED)))
            painter.drawText(
                QRectF(x - gap / 2, top_pad + chart_h + 4, bar_w + gap, label_h),
                Qt.AlignHCenter | Qt.AlignTop,
                label,
            )

            x += bar_w + gap

        painter.end()


class DonutChartWidget(QWidget):
    """
    segments: list[tuple[str label, float value, str color_hex]]
    center_value / center_label are drawn in the middle of the ring.
    """

    def __init__(self, segments, center_value="", center_label="", parent=None):
        super().__init__(parent)
        self.segments = segments
        self.center_value = center_value
        self.center_label = center_label
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_data(self, segments, center_value="", center_label=""):
        self.segments = segments
        self.center_value = center_value
        self.center_label = center_label
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height()) - 20
        if side <= 0:
            painter.end()
            return

        rect = QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side,
        )

        thickness = max(12, side * 0.16)
        inner_rect = rect.adjusted(thickness, thickness, -thickness, -thickness)

        total = sum(v for _, v, _ in self.segments) or 1
        start_angle = 90 * 16  # start at 12 o'clock, Qt angles are in 1/16th degrees

        pen_track = QPen(QColor(Colors.SURFACE_ALT), thickness)
        pen_track.setCapStyle(Qt.FlatCap)
        painter.setPen(pen_track)
        painter.drawArc(rect.adjusted(thickness / 2, thickness / 2, -thickness / 2, -thickness / 2), 0, 360 * 16)

        for label, value, color in self.segments:
            span_angle = -int((value / total) * 360 * 16)
            pen = QPen(QColor(color), thickness)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            painter.drawArc(
                rect.adjusted(thickness / 2, thickness / 2, -thickness / 2, -thickness / 2),
                start_angle,
                span_angle,
            )
            start_angle += span_angle

        # Center text
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        value_font = QFont(self.font())
        value_font.setPointSize(int(side * 0.11))
        value_font.setBold(True)
        painter.setFont(value_font)
        value_rect = QRectF(inner_rect.x(), inner_rect.y() + inner_rect.height() * 0.28, inner_rect.width(), inner_rect.height() * 0.4)
        painter.drawText(value_rect, Qt.AlignHCenter | Qt.AlignVCenter, self.center_value)

        label_font = QFont(self.font())
        label_font.setPointSize(int(side * 0.055))
        painter.setFont(label_font)
        painter.setPen(QColor(Colors.TEXT_MUTED))
        label_rect = QRectF(inner_rect.x(), inner_rect.y() + inner_rect.height() * 0.52, inner_rect.width(), inner_rect.height() * 0.3)
        painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignVCenter, self.center_label)

        painter.end()