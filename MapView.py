# 场景容器

import sys
from typing import Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MapView(QGraphicsView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 缩放控制
        self.zoom_level = 1.0
        self.zoom_min = 0.2
        self.zoom_max = 5.0

        self.setUI()

    def setUI(self) -> None:
        # 场景拖拽
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # 渲染模式
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高品质抗锯齿
                            QPainter.TextAntialiasing |  # 文字抗锯齿
                            QPainter.SmoothPixmapTransform |  # 使图元变换更加平滑
                            QPainter.LosslessImageRendering)  # 不失真的图片渲染
        # 视窗更新模式
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def drawBackground(self, painter : QPainter, rect : QRectF) -> None:
        """优化绘制网格的方法，避免重复创建 QGraphicsItem"""
        grid_size = 50
        pen = QPen(Qt.lightGray)
        pen.setWidth(1)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())
        # 绘制竖直线
        for x in range(left, right, grid_size):
            painter.drawLine(x, top, x, bottom)

        # 绘制水平线
        for y in range(top, bottom, grid_size):
            painter.drawLine(left, y, right, y)

        super().drawBackground(painter, rect)

    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放，区域受限"""
        zoom_factor = 1.2
        # 放大
        if event.angleDelta().y() > 0:
            if self.zoom_level < self.zoom_max:
                self.scale(zoom_factor, zoom_factor)
                self.zoom_level *= zoom_factor
        # 缩小
        else:
            if self.zoom_level > self.zoom_min:
                self.scale(1 / zoom_factor, 1 / zoom_factor)
                self.zoom_level /= zoom_factor

