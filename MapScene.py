# 场景编辑器

import sys

from typing import Optional, Tuple, Union, Type
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MapAttributeWidget import MapAttributeWidget
from MapProxyItemWidget import MapProxyItemWidget, MixinPort
from MapPipeProxy import PipeProxy
from MapReaderObj import MapReaderObj

class MapScene(QGraphicsScene):

    interfaceRequest = pyqtSignal()  # 底层调用测试请求
    callStatus = pyqtSignal(str)  # 信息反馈给状态栏

    def __init__(self, dock : MapAttributeWidget, view : QWidget):
        super().__init__(-10000, -10000, 20000, 20000)

        # 创建 QGraphicsScene（无限扩展）
        self.dock = dock
        self.view = view

        # 设置锁A
        self.is_gas_edit = False
        self.is_user_edit = False
        self.is_pipe_edit = False

        # 实时同步scene中鼠标的位置
        self.mouse_scene = QPointF(0, 0)

        # 是否已经在进行管道工程
        self.start_port = None
        self.current_pipe : Optional[PipeProxy] = None

    def addItems(self, items : list):
        for i in items:
            self.addItem(i)

    # 场景中添加一个节点
    def addProxyItemWidget(self, name: str, init_pos: QPointF, current : Optional[float] = None, errorp : Optional[float] = None)\
            -> MapProxyItemWidget:
        iconName = 'fa5s.gas-pump' if name == 'Gas' else 'fa5.user-circle'
        proxy = MapProxyItemWidget(iconName, init_pos, self)
        proxy.setPos(init_pos)
        proxy.attr.connect(self.dock.setCurrentNodeAttr)
        self.addItem(proxy)
        if name == 'Gas':
            if current:
                proxy.currentGasSource = current
            if errorp:
                proxy.errorp = errorp
        else:
            if current:
                proxy.currentGasUser = current
        self.update()
        return proxy

    # 场景中根据位置预先添加一个管线但是不连接（没添加到场景并且没绘制）
    def addPipeProxy(self, start_pos: QPointF, end_pos: QPointF, distance : Optional[float] = None, errorp : Optional[float] = None) \
            -> PipeProxy:
        s : MixinPort | QGraphicsItem = self.itemAt(start_pos, QTransform())
        e : MixinPort | QGraphicsItem = self.itemAt(end_pos, QTransform())
        p = PipeProxy(start_pos, s, e)
        if errorp:
            p.errorp = errorp
        p.distance = distance if distance else QLineF(start_pos, end_pos).length()
        return p

    # 场景中根据端口预先添加一个管线但是不连接（没添加到场景并且没绘制）
    @staticmethod
    def addPipeProxyByPort(startPort : MixinPort, endPort : MixinPort, distance : Optional[float] = None, errorp : Optional[float] = None) \
        -> PipeProxy:
        p = PipeProxy(startPort.pos(), startPort, endPort)
        if errorp:
            p.errorp = errorp
        p.distance = distance if distance else QLineF(startPort.pos(), endPort.pos()).length()
        return p

    # 添加管线并且连接，通过端口
    def addPipeAndLink(self, startPort : MixinPort, endPort : MixinPort, distance : Optional[float] = None, errorp : Optional[float] = None)\
            -> PipeProxy:
        p = self.addPipeProxyByPort(startPort, endPort, distance, errorp)
        self.addItem(p)
        print(f"连接了两个端口的位置：{p.mapToPortIds()}")
        # 绑定管线自身事件
        p.pipeProxyObject.attr.connect(self.dock.setCurrentPipeAttr)
        nodeA = startPort.bind_node
        nodeB = endPort.bind_node
        # 记录节点和管线，便于查询，而且只需要查询两次即可
        nodeA.records[nodeB] = p
        nodeB.records[nodeA] = p
        # 完成管道绘制后，此时管道存在两个端点，可以传入管道事件响应了，必须是双向绑定
        nodeA.pipePathUpdate.connect(p.update_pipe_path)
        nodeB.pipePathUpdate.connect(p.update_pipe_path)
        p.update_pipe_path()
        return p

    # 添加管线并且连接，通过端口位置
    def addPipeAndLinkByLocal(
        self,
        startPortPos : QPointF,
        endPortPos : QPointF,
        distance : Optional[float] = None,
        errorp : Optional[float] = None
    ) -> PipeProxy:
        print(f'检测端口：{startPortPos, endPortPos}')
        startPort : MixinPort | QGraphicsItem = self.itemAt(startPortPos, QTransform())
        endPort: MixinPort | QGraphicsItem = self.itemAt(endPortPos, QTransform())
        print(f'startPort, endPort : {startPort, endPort}')
        nodeA = startPort.bind_node
        nodeB = endPort.bind_node
        print(f'search A & B : {nodeA, nodeB}')
        p = self.addPipeProxyByPort(startPort, endPort, distance, errorp)
        self.addItem(p)
        print(f"连接了两个端口的位置：{p.mapToPortIds()}")
        # 绑定管线自身事件
        p.pipeProxyObject.attr.connect(self.dock.setCurrentPipeAttr)
        # 记录节点和管线，便于查询，而且只需要查询两次即可
        nodeA.records[nodeB] = p
        nodeB.records[nodeA] = p
        # 完成管道绘制后，此时管道存在两个端点，可以传入管道事件响应了，必须是双向绑定
        nodeA.pipePathUpdate.connect(p.update_pipe_path)
        nodeB.pipePathUpdate.connect(p.update_pipe_path)
        p.update_pipe_path()
        return p

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.mouse_scene = event.scenePos()
        # 管道铺设
        if self.current_pipe and self.is_pipe_edit:
            # 更新管道的目标位置
            self.current_pipe.set_dst(self.mouse_scene.x(), self.mouse_scene.y())
            self.current_pipe.update()  # 刷新管道显示
        super().mouseMoveEvent(event)

    # 点击工具图标进行鼠标变换，变成Cross Cursor。
    # 如果用户点击Esc，则取消变回原来的图标。
    # 如果Cross Cursor点击在MapEditor的某个位置，则在该位置生成a.png的Icon并且打印在MapEditor的位置
    def mousePressEvent(self, event : QGraphicsSceneMouseEvent) -> None:
        pos = event.scenePos()
        if event.button() == Qt.LeftButton and self.is_gas_edit:
            self.addItem(self.addProxyItemWidget('Gas', pos))
            # 解锁A
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.is_gas_edit = False

        elif event.button() == Qt.LeftButton and self.is_user_edit:
            self.addItem(self.addProxyItemWidget('User', pos))
            # 解锁A
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.is_user_edit = False

        elif event.button() == Qt.LeftButton and isinstance(self.itemAt(pos, QTransform()), MixinPort) and self.is_pipe_edit:
            # 选中起点端口
            self.start_port : MixinPort | QGraphicsItem = self.itemAt(pos, QTransform())
            self.current_pipe = PipeProxy(pos, self.start_port, None)  # 创建管道对象
            self.addItem(self.current_pipe)  # 添加管道到场景
            self.view.setCursor(Qt.CrossCursor)  # 设置鼠标为十字

        elif event.button() == Qt.RightButton:
            print(f"右键位置: {event.scenePos()}")

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pos = event.scenePos()
        if self.current_pipe and self.is_pipe_edit:
            # 检查释放的地方是否点击了目标端口
            end_port = self.itemAt(pos, QTransform())
            if isinstance(end_port, MixinPort) and end_port != self.start_port:
                nodeA = self.start_port.bind_node
                nodeB = end_port.bind_node
                # 约束：
                # 1. 同一个图元上的端口不能互联
                # 2. 两个不同图元只能有一条管线
                if nodeA == nodeB:
                    print("⚠️ 不能连接同一个图元上的端口！")
                    self.removeItem(self.current_pipe)  # 移除非法管道
                else:
                    print(f"✅ 选中了目标端口: {end_port}")
                    self.current_pipe.endPort = end_port  # 绑定目标端口
                    if nodeA.records.get(self.current_pipe.endPort.bind_node):
                        print("⚠️ 两个不同图元只能有一条管线！")
                        self.removeItem(self.current_pipe)
                        return
                    # 这时候才成功地创建一条管道，这部分由于更早出现，防止逻辑错误，先不用addPipeAndLink方法代替
                    self.current_pipe.set_dst(pos.x(), pos.y())  # 更新终点坐标
                    self.current_pipe.update()
                    print(f"连接了两个端口的位置：{self.current_pipe.mapToPortIds()}")
                    # 绑定管线自身事件
                    self.current_pipe.pipeProxyObject.attr.connect(self.dock.setCurrentPipeAttr)
                    # 记录节点和管线，便于查询，而且只需要查询两次即可
                    nodeA.records[nodeB] = self.current_pipe
                    nodeB.records[nodeA] = self.current_pipe
                    # 完成管道绘制后，此时管道存在两个端点，可以传入管道事件响应了，必须是双向绑定
                    nodeA.pipePathUpdate.connect(self.current_pipe.update_pipe_path)
                    nodeB.pipePathUpdate.connect(self.current_pipe.update_pipe_path)
            else:
                print("目标端口无效")
                self.removeItem(self.current_pipe)

            # 完成管道编辑，重置状态
            self.is_pipe_edit = False
            self.start_port = None
            self.current_pipe = None
            self.view.setCursor(Qt.ArrowCursor)  # 恢复箭头光标

        super().mouseReleaseEvent(event)

    # 按下生成图标
    def keyPressEvent(self, event : QKeyEvent) -> None:
        # 解锁A
        if event.key() == Qt.Key_Escape and self.is_gas_edit:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.is_gas_edit = False
        elif event.key() == Qt.Key_Escape and self.is_user_edit:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.is_user_edit = False
        elif event.key() == Qt.Key_Escape and self.is_pipe_edit:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.is_pipe_edit = False
        super().keyPressEvent(event)

    # 连接工具栏和场景交互的类
    def handle_toolbar_scene(self, msg : str) -> None:
        # 加锁A
        if msg == 'gas':
            self.is_gas_edit = True
            self.view.setCursor(Qt.CrossCursor)
        elif msg == 'user':
            self.is_user_edit = True
            self.view.setCursor(Qt.CrossCursor)
        elif msg == 'pipe':
            self.is_pipe_edit = True
            self.view.setCursor(Qt.CrossCursor)
        elif msg == 'load':
            rObj = MapReaderObj(self, self.views()[0])
            rObj.send.connect(lambda t : self.callStatus.emit(t))
            rObj.loader_func()
        elif msg == 'export':
            rObj = MapReaderObj(self, self.views()[0])
            rObj.send.connect(lambda t : self.callStatus.emit(t))
            rObj.exporter_func()
        elif msg == 'inject':
            self.interfaceRequest.emit()
        elif msg == 'clear':
            btn = QMessageBox.warning(self.view, '警告', '确认要清理全部？', QMessageBox.Yes | QMessageBox.No)
            if btn == QMessageBox.Yes:
                self.clearScene()
                self.callStatus.emit('已清理完毕！')
            else:
                print('取消了清场操作')
        elif msg == 'update':
            self.update()
            self.view.update()
            self.callStatus.emit('已刷新场景！')
        elif msg == 'dev':
            s = self.addProxyItemWidget('Gas', QPointF(0, 0), 1000, 0.5)
            e = self.addProxyItemWidget('User', QPointF(100, 300), 1000)
            self.addPipeAndLink(s.topPort, e.leftPort, 100, 0.05)

    # 从场景中筛选全部的XXX类型的图元
    def findAllItems(self, target : Type[Union[MixinPort, MapProxyItemWidget, PipeProxy]])\
            -> list[Union[MixinPort, MapProxyItemWidget, PipeProxy]]:
        its = self.items()
        return list(filter(lambda item: isinstance(item, target), its)) if its else []

    # 清理场景
    # 先清理管线再清理节点，最后清理场景中没考虑的图元
    def clearScene(self) -> None:
        all_pipes = self.findAllItems(PipeProxy)
        for pipe in all_pipes:
            self.removeItem(pipe)
        self.clear()

    def pipe_project(self, pipes : list) -> None:
        for pipe in pipes:

            pa = QPointF(pipe['ax'], pipe['ay'])
            pb = QPointF(pipe['bx'], pipe['by'])

            nodeA : MapProxyItemWidget = self.itemAt(pa, QTransform()).parentItem()
            nodeB : MapProxyItemWidget = self.itemAt(pb, QTransform()).parentItem()
            a, b = pipe['bindIds']
            self.addPipeAndLink(
                nodeA.bindPorts[a],
                nodeB.bindPorts[b],
                pipe.get('distance', None),
                pipe['errorp']
            )