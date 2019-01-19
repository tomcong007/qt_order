import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件
        self.username = None
        self.order = None
        self.skuHtml = ''
        #初始化当前订单数据
        self.btn_b = QPushButton('进入百度')
        self.btn_b.clicked.connect(self.to_b)

        self.btn_b1 = QPushButton('准备进入百度')
        self.btn_b1.clicked.connect(self.to_b1)
        #添加收货地址页面,运行页面js
        self.btn_c = QPushButton('进入京东')  # 创建一个按钮涌来了点击获取cookie
        self.btn_c.clicked.connect(self.to_c)  # 绑定按钮点击事件
        #人工校验地址成功后,进入商品页面
        self.btn_a = QPushButton('进入淘宝')
        self.btn_a.clicked.connect(self.to_a)
        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl("http://www.taobao.com"))  # 打开页面
        self.box.addWidget(self.btn_b)
        self.box.addWidget(self.btn_b1)
        self.box.addWidget(self.btn_c)  # 将组件放到布局内，先在顶部放一个按钮
        self.box.addWidget(self.btn_a)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")

    #初始化订单信息,拿取订单数据
    def to_b(self):
        self.web.page().runJavaScript("window.location='https://www.baidu.com';")
        self.web.page().toHtml(self.sku_html)
        self.btn_b1.click()
    def to_b1(self):
        self.web.page().toHtml(self.sku_html)
    #添加收货地址页面
    def to_c(self):
        self.web.page().runJavaScript("window.location='https://www.jd.com';")
        self.web.page().toHtml(self.sku_html)
    #进入商品购买页面
    def to_a(self):
        self.web.page().runJavaScript("window.location='https://www.taobao.com';")
        self.web.page().toHtml(self.sku_html)
    #将sku页面信息的内容赋值给窗体对象
    def sku_html(self,html):
        self.skuHtml = html
        print(self.skuHtml)
if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    sys.exit(app.exec_())


    #step1_test()
