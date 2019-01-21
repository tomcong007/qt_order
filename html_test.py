import sys,time
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import threading
def auto_task(w):
    while True:
        w.btn_a.click()
        time.sleep(10)
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件''
        #添加收货地址页面,运行页面js
        #人工校验地址成功后,进入商品页面
        self.btn_a = QPushButton('进入淘宝')
        self.btn_a.clicked.connect(self.to_a)
        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl("http://www.taobao.com"))  # 打开页面
        self.box.addWidget(self.btn_a)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    #进入商品购买页面
    def to_a(self):
        self.web.page().runJavaScript("window.alert('我加载了1次');")
        self.web.reload()

    #将sku页面信息的内容赋值给窗体对象
    def sku_html(self,html):
        self.skuHtml = html
        print(self.skuHtml)
if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    t1 = threading.Thread(target=auto_task, args=(w,))
    t1.start()
    sys.exit(app.exec_())


    #step1_test()
