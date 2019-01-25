import sys,time
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
from threading import Thread
url="https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?action=itemlist/BoughtQueryAction&event_submit_do_query=1&tabCode=waitPay"
addrs=[]
def auto_task(p):
    ret = p.ret
    while True:
        if p.flag:
            del ret[0]
            c = len(ret)
            print("开启任务")
            if c % 2 == 0:
                p.btn_a.click()
            else:
                p.btn_b.click()
            p.btn_get.click()
        else:
            print("关闭任务")
        time.sleep(3)
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.flag = False
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件''
        #添加收货地址页面,运行页面js
        #人工校验地址成功后,进入商品页面
        self.btn_a = QPushButton('淘宝')
        self.btn_a.clicked.connect(self.to_a)
        self.btn_b = QPushButton('百度')
        self.btn_b.clicked.connect(self.to_b)
        self.btn_get = QPushButton('get')
        self.btn_get.setVisible(False)
        self.btn_get.clicked.connect(self.get)
        self.btn_start = QPushButton('启动')
        self.btn_start.clicked.connect(self.start)
        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl("https://www.baidu.com"))  # 打开页面
        self.box.addWidget(self.btn_a)
        self.box.addWidget(self.btn_b)
        self.box.addWidget(self.btn_get)
        self.box.addWidget(self.btn_start)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    #进入商品购买页面
    def to_a(self):
        self.web.load(QUrl("http://www.taobao.com"))
        #self.btn_get.click()
    def to_b(self):
        self.web.load(QUrl("http://www.baidu.com"))
        #self.btn_get.click()

    def get(self):
        self.web.page().toHtml(self.sku_html)
    def start(self):
        if self.flag:
            self.flag = False
        else:
            self.flag = True

    #将sku页面信息的内容赋值给窗体对象
    def sku_html(self,html):
        if html.find("www.baidu.com")!=-1:
            print("www.baidu.com")
        else:
            print("www.taobao.com")


if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    Thread(target=auto_task,args=(w,)).start()
    sys.exit(app.exec_())
