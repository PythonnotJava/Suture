from typing import Optional

import json5
import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from MapPipeProxy import PipeProxy
from MapProxyItemWidget import MapProxyItemWidget
# from MapScene import MapScene

class _ExportThread(QThread):
    def __init__(self, all_pipes : list[PipeProxy], all_nodes : list[MapProxyItemWidget], fp : str, parent : 'MapReaderObj'):
        super().__init__()
        self.all_pipes = all_pipes
        self.all_nodes = all_nodes
        self.parent = parent
        self.fp = fp

    def run(self) -> None:
        data = {
            'version': '1.0.0',
            'nodes': [self.parent.explain_node(node) for node in self.all_nodes],
            'pipes': [self.parent.explain_pipe_path(pipe) for pipe in self.all_pipes]
        }
        json5.dump(data, open(self.fp, 'w', encoding='utf-8'), indent=4)

class _LoadThread(QThread):
    copeOver = pyqtSignal(list)
    def __init__(self, fp : str, bind_scene : 'MapScene'):
        super().__init__()

        self.fp = fp
        self.bind_scene = bind_scene

    def run(self) -> None:
        l = []
        with open(self.fp, 'r', encoding='utf-8') as f:
            data = json5.load(f)
        nodes = data['nodes']
        pipes = data['pipes']
        for node in nodes:
            l.append(self.bind_scene.addProxyItemWidget(
                node['category'],
                QPointF(node['x'], node['y']),
                current=node['current'],
                errorp=node.get('errorp', None)
            ))
        for pipe in pipes:
            s = self.bind_scene.itemAt(QPointF(pipe['ax'], pipe['ay']), QTransform())
            e = self.bind_scene.itemAt(QPointF(pipe['bx'], pipe['by']), QTransform())
            l.append(self.bind_scene.addPipeAndLink(
                s,
                e,
                pipe.get('distance', None),
                pipe['errorp']
            ))
        self.copeOver.emit(l)

class MapReaderObj(QObject):
    send = pyqtSignal(str)
    def __init__(self, bind_scene : 'MapScene', parent : QWidget):
        super().__init__()

        self.bind_scene = bind_scene
        self.parent = parent
        self.export_thread: Optional[_ExportThread] = None
        self.load_thread : Optional[_LoadThread] = None

    # 解析图元必要数据
    # 解析气源
    @staticmethod
    def explain_gas_node(node : MapProxyItemWidget) -> dict:
        return {
            'x' : node.timing_pos.x(),
            'y' : node.timing_pos.y(),
            'category' : 'Gas',
            'current' : node.currentGasSource,
            'errorp' : node.errorp
        }
    # 解析用户
    @staticmethod
    def explain_user_node(node : MapProxyItemWidget) -> dict:
        return {
            'x': node.timing_pos.x(),
            'y': node.timing_pos.y(),
            'category': 'User',
            'current': node.currentGasUser
        }
    def explain_node(self, node : MapProxyItemWidget) -> dict:
        return self.explain_gas_node(node) if  node.category == 'Gas' else self.explain_user_node(node)

    # 解析管线
    # 管线和节点不直接绑定，而是通过端口，要记录在图元的哪个端口或者端口位置也行
    @staticmethod
    def explain_pipe_path(pipe : PipeProxy) -> dict:
        nodeA = pipe.startPort.bind_node.timing_pos
        nodeB = pipe.endPort.bind_node.timing_pos
        return {
            'bindIds' : pipe.mapToPortIds(),
            'ax' : nodeA.x(),
            'ay' : nodeA.y(),
            'bx': nodeB.x(),
            'by': nodeB.y(),
            'distance' : pipe.distance,
            'errorp' : pipe.errorp
        }

    # 纯导出功能的逻辑
    def exporter_func(self):
        # 通过管道找两端
        all_pipes : list[PipeProxy] = self.bind_scene.findAllItems(PipeProxy)
        all_nodes : list[MapProxyItemWidget] = self.bind_scene.findAllItems(MapProxyItemWidget)  # 这个要是空，管道肯定不存在
        if not all_nodes:
            QMessageBox.warning(self.parent, '不可行警告', '场景中无任何节点')
        else:
            fileName, _ = QFileDialog.getSaveFileName(
                self.parent,
                '地图保存',
                os.path.join(os.path.expanduser("~"), "Desktop"),
                "mj5 文件 (*.mj5)"
                ""
            )
            if not fileName:
                self.send.emit('取消选择！')
            else:
                self.export_thread = _ExportThread(all_pipes, all_nodes, fileName, self)
                self.export_thread.start()
                self.export_thread.finished.connect(lambda : self.export_finish(fileName))

    def export_finish(self, f : str) -> None:
        QMessageBox.information(
            self.parent,
            '成功导出地图',
            f'地图成功写入至：{f}'
        )
        self.export_thread = None

    def load_finish(self, f : str) -> None:
        QMessageBox.information(
            self.parent,
            '成功导入地图',
            f'地图读取文件：{f}'
        )
        self.load_thread = None

    # 载入地图文件
    def loader_func(self) -> None:
        fileName, _ = QFileDialog.getOpenFileName(
            self.parent,
            '选择地图文件',
            os.path.join(os.path.expanduser("~"), "Desktop"),
            "mj5 文件 (*.mj5)"
        )
        if not fileName:
            self.send.emit('取消选择！')
        elif not fileName.upper().endswith('.MJ5'):
            QMessageBox.critical(self.parent, '不支持读取', '你必须选择mj5格式的文件')
        else:
            with open(fileName, 'r', encoding='utf-8') as f:
                data = json5.load(f)
            nodes = data['nodes']
            for node in nodes:
                self.bind_scene.addProxyItemWidget(
                    node['category'],
                    QPointF(node['x'], node['y']),
                    current=node['current'],
                    errorp=node.get('errorp', None)
                )
            pipes = data['pipes']
            self.bind_scene.pipe_project(pipes)

