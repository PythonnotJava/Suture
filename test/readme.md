# 这是Develop-Action的测试记录

## 场景中图元读入添加和管线连接模拟(Success!)
```text
s = self.addProxyItemWidget('Gas', QPointF(0, 0), 1000, 0.5)
e = self.addProxyItemWidget('User', QPointF(100, 300), 1000)
self.addPipeAndLink(s.topPort, e.leftPort, 100, 0.05)
```

