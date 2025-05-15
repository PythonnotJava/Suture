from dataclasses import dataclass
from typing import Optional, Callable, Self

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from MapProxyItemWidget import MixinPort

@dataclass
class PipeAttr:
    ax : float
    bx : float
    ay : float
    by : float
    distance : float
    errorp : float

class PipeProxyObject(QObject):
    attr = pyqtSignal(PipeAttr)

class PipeProxy(QGraphicsPathItem):
    def __init__(self, eventPos : QPointF, startPort : MixinPort, endPort : Optional[MixinPort]=None):
        super().__init__()
        self.pipeProxyObject = PipeProxyObject()
        self.eventPos = eventPos
        self.startPort = startPort
        self.endPort = endPort
        self.width = 5
        # 每次都是先找到Port然后开始画线，因此Port的起点即Pipe的起点
        # 后续更新的时候，变成绑定的两个Port的位置
        self.pos_src = [self.eventPos.x(), self.eventPos.y()]
        self.pos_dst = [self.eventPos.x(), self.eventPos.y()]

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)
        # 模拟管道长度，默认是两端点之间的欧几里得距离，可以手动设置新的长度
        self.distance = 0.0
        # 失效率
        self.errorp = 0.05
        # 自定义路径样子的函数
        self.customPathFunc : Optional[Callable[[QPointF, QPointF], QPainterPath]] = None

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self) -> QPainterPath:
        start_pos = QPointF(self.pos_src[0], self.pos_src[1])
        end_pos = QPointF(self.pos_dst[0], self.pos_dst[1])
        self.distance = QLineF(start_pos, end_pos).length()
        if self.customPathFunc is None:
            buffer = 20  # 适当增加 buffer 让曲线更自然
            path = QPainterPath(start_pos)

            # 计算控制点
            distance = (end_pos.x() - start_pos.x()) / 2
            control1 = QPointF(start_pos.x() + distance, start_pos.y() + buffer)
            control2 = QPointF(end_pos.x() - distance, end_pos.y() + buffer)

            path.cubicTo(control1, control2, end_pos)  # 绘制贝塞尔曲线
            return path
        else:
            return self.customPathFunc(start_pos, end_pos)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        path = self.calc_path()
        stroker = QPainterPathStroker()
        stroker.setWidth(self.width + 5)  # 增加额外宽度，提高选中范围
        return stroker.createStroke(path)  # 返回更宽的形状

    def paint(self, painter : QPainter, option : QStyleOptionGraphicsItem, widget : Optional[QWidget] = None):
        self.setPath(self.calc_path())
        path = self.path()
        if self.endPort is None:
            painter.setPen(QPen(Qt.red, self.width))
            painter.drawPath(path)
        else:
            painter.setPen(QPen(Qt.black, self.width))
            painter.drawPath(path)

        # 被选中效果
        if self.isSelected():
            painter.setPen(QPen(QColor('orange'), self.width))
            painter.drawPath(path)

    # 管道跟着端口移动事件
    def update_pipe_path(self) -> None:
        # 这时候两端点都存在，先更新两端点的位置
        p1, p2 = self.startPort.getPosInScene(), self.endPort.getPosInScene()
        self.pos_src = [p1.x(), p1.y()]
        self.pos_dst = [p2.x(), p2.y()]
        self.setPath(self.calc_path())
        self.update()  # 强制重新绘制管道路径

    # 手动删除管线
    # 先要删除两端点的对这条边的记录，再删除本身
    def del_self(self) -> None:
        self.startPort.bind_node.records.inverse.pop(self)
        self.endPort.bind_node.records.inverse.pop(self)
        # print(self.startPort.bind_node.records)
        # print(self.endPort.bind_node.records)
        self.scene().removeItem(self)

    # 拉成直线路径
    @staticmethod
    def convertToLine(s, e) -> QPainterPath:
        path = QPainterPath(s)
        path.lineTo(e)
        return path

    # 右键管线
    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):
        menu = QMenu()
        attrAct = menu.addAction("属性")
        delAct = menu.addAction("删除")
        toLine = menu.addAction('拉直')
        selected_action = menu.exec_(event.screenPos())

        if selected_action == attrAct:
            self.pipeProxyObject.attr.emit(PipeAttr(
                ax=self.startPort.bind_node.x(),
                bx=self.endPort.bind_node.x(),
                ay=self.startPort.bind_node.y(),
                by=self.endPort.bind_node.y(),
                distance=self.distance,
                errorp=self.errorp
            ))
        elif selected_action == delAct:
            self.del_self()
        elif selected_action == toLine:
            self.customPathFunc = self.convertToLine
            self.setPath(self.calc_path())
            self.update()

    # 定位到绑定到两个端点的哪一个端口（分上下左右 --map--> 0123）
    def mapToPortIds(self) -> tuple[int, int]:
        return self.startPort.bind_node.bindPorts.index(self.startPort), self.endPort.bind_node.bindPorts.index(self.endPort)