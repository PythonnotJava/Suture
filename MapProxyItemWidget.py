# 图元
from typing import Optional, Literal, Any, Self
from dataclasses import dataclass

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtawesome import icon as QAwesomeIcon
from bidict import bidict

# 节点属性传参
@dataclass
class NodeAttr:
    x : float
    y : float
    category : Optional[Literal['Gas', 'User']] = None
    errorp : Optional[float] = None
    currentGasSource : Optional[float] = None
    currentGasUser : Optional[float] = None

# 连接点
class MixinPort(QGraphicsEllipseItem):
    def __init__(self, pos : QPointF, bind_scene, bind_node : 'MapProxyItemWidget'):  # pos是起始位置
        super().__init__(pos.x(), pos.y(), 10, 10)  # 圆形端口的直径为 10，中心为给定位置

        self.initPos = pos
        self.bind_scene = bind_scene  # 场景
        self.bind_node = bind_node  # 绑定的图元
        self.setParentItem(self.bind_node)

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.blue, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(self.rect())  # 绘制一个圆形端口

        super().paint(painter, option, widget)

    # 有关于线宽的偏差，不影响
    def getPosInScene(self) -> QPointF:
        return self.mapToScene(self.initPos)

class MapProxyItemWidget(QGraphicsWidget):
    attr = pyqtSignal(NodeAttr)  # 属性右键反馈
    pipePathUpdate = pyqtSignal()  # 更新管道位置
    def __init__(self, iconName: str, init_pos: QPointF, bind_scene):
        super().__init__()

        self.bind_scene = bind_scene
        self.category: Literal['Gas', 'User'] | None = 'User' if iconName == 'fa5.user-circle' else 'Gas'

        # 实时追踪位置
        self.timing_pos = init_pos

        # 创建图标
        pixmap = QAwesomeIcon(iconName).pixmap(50, 50)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_proxy = QGraphicsProxyWidget(self)
        icon_proxy.setWidget(icon_label)

        # 创建文本
        self.text_label = QLabel(f"x: {round(init_pos.x(), 1)}\ny: {round(init_pos.y(), 1)}")
        self.text_label.setFixedWidth(50)
        text_proxy = QGraphicsProxyWidget(self)
        text_proxy.setWidget(self.text_label)

        # 使用布局管理
        layout = QGraphicsLinearLayout(Qt.Horizontal)
        layout.addItem(icon_proxy)
        layout.addItem(text_proxy)
        self.setLayout(layout)

        # 设置节点可以移动和选择
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

        # 绑定的接口
        # 设置接口的位置偏移量
        self.topPortOffset = QPointF(57.5, -10)
        self.bottomPortOffset = QPointF(57.5, 67.5)
        self.leftPortOffset = QPointF(-10, 30)
        self.rightPortOffset = QPointF(125, 30)
        # 创建接口端口并添加到场景
        self.topPort = MixinPort(init_pos + self.topPortOffset, self.bind_scene, self)
        self.bottomPort = MixinPort(init_pos + self.bottomPortOffset, self.bind_scene, self)
        self.leftPort = MixinPort(init_pos + self.leftPortOffset, self.bind_scene, self)
        self.rightPort = MixinPort(init_pos + self.rightPortOffset, self.bind_scene, self)
        # Z来设置层级关系
        self.topPort.setZValue(1)
        self.bottomPort.setZValue(1)
        self.leftPort.setZValue(1)
        self.rightPort.setZValue(1)
        self.bind_scene.addItem(self.topPort)
        self.bind_scene.addItem(self.bottomPort)
        self.bind_scene.addItem(self.leftPort)
        self.bind_scene.addItem(self.rightPort)
        # 绑定的四个接口，可以用于验证任意两个接口连接时，是否属于同一个图元
        self.bindPorts = [self.topPort, self.bottomPort, self.leftPort, self.rightPort]
        # 记录MapProxyItemWidget绑定的图元与对应的管线
        # 由于值（管线）是唯一的，为了支持反向快速查询，这类采用bidict
        from MapPipeProxy import PipeProxy
        self.records : bidict['MapProxyItemWidget', PipeProxy] = bidict()

        # 气源时的属性
        self.errorp = 0.05  # 失效率
        self.currentGasSource = 10000
        # 用户源的属性
        self.currentGasUser = 10

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.darkBlue, 10)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.white))
        painter.drawRoundedRect(self.rect(), 15, 15)

        # 被选中效果
        if self.isSelected():
            pen = QPen(Qt.red, 10)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect(), 15, 15)  # 绘制边框

        super().paint(painter, option, widget)

    # 实时更新位置但是暂先不做无限拖动（即一直往边缘滑动进行场景更换）
    def moveEvent(self, event: QGraphicsSceneMoveEvent):
        new_pos = event.newPos()
        delta_pos = new_pos - self.timing_pos
        self.timing_pos = new_pos

        # 更新文本
        self.text_label.setText(f"x: {round(new_pos.x(), 1)}\ny: {round(new_pos.y(), 1)}")
        # 更新四个接口
        self.topPort.moveBy(delta_pos.x(), delta_pos.y())
        self.bottomPort.moveBy(delta_pos.x(), delta_pos.y())
        self.leftPort.moveBy(delta_pos.x(), delta_pos.y())
        self.rightPort.moveBy(delta_pos.x(), delta_pos.y())

        # 发出信号，通知管道更新
        self.pipePathUpdate.emit()
        super().moveEvent(event)

    # 右键菜单
    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):
        menu = QMenu()
        attrAct = menu.addAction("属性")
        delAct = menu.addAction("删除")
        selected_action = menu.exec_(event.screenPos())

        if selected_action == attrAct:
            # 先不实现实时更新坐标
            if self.category == 'Gas':
                print('View Gas')
                self.attr.emit(NodeAttr(x=self.x(), y=self.y(), category='Gas', errorp=self.errorp, currentGasSource=self.currentGasSource))
            elif self.category == 'User':
                print('View User')
                self.attr.emit(NodeAttr(x=self.x(), y=self.y(), category='User', currentGasUser=self.currentGasUser))
            print(f'四个端口位置：\n\t上：{self.topPort.getPosInScene()}\n\t下：{self.bottomPort.getPosInScene()}\n\t左：{self.leftPort.getPosInScene()}\n\t右：{self.rightPort.getPosInScene()}')
        elif selected_action == delAct:
            # 删除要考虑：端口删掉、删除场景连接记录，如果有绑定管线也要跟着删掉，最后自身删掉
            for it in self.bindPorts:
                self.scene().removeItem(it)
            self.bindPorts.clear()

            for key_node in self.records.keys():
                # key_node : 'MapProxyItemWidget'
                bindPipe = key_node.records[self]
                # print(bindPipe)
                self.scene().removeItem(bindPipe)

            self.scene().removeItem(self)
