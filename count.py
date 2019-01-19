import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from sku_util import SkuParser
url = "https://item.taobao.com/item.htm?id=577604003839"
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件
        # 人工校验地址成功后,进入商品页面
        self.btn_go_test = QPushButton('添加商品数量测试')
        self.btn_go_test.setShortcut("3")
        self.btn_go_test.clicked.connect(self.go_test)

        self.btn_go_back = QPushButton('回归初始化')
        self.btn_go_back.clicked.connect(self.go_back)

        self.btn_get_pay = QPushButton('获取订单总计')
        self.btn_get_pay.setShortcut("Enter")
        self.btn_get_pay.clicked.connect(self.get_pay)

        self.web = MyWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(url))  # 打开页面
        self.box.addWidget(self.btn_go_test)
        self.box.addWidget(self.btn_go_back)
        self.box.addWidget(self.btn_get_pay)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单测试")
        self.skuHtml = ''

    # 进入商品购买页面
    def go_test(self):
        self.web.page().toHtml(self.sku_html)
        sku_price = SkuParser.get_sku_price(self.skuHtml)
        print(sku_price)
        if sku_price is None:
            self.web.page().runJavaScript("alert('未采集到单价,请重新点击购买订单按钮');")
            return
        for i in range(3):
            self.web.page().runJavaScript("document.getElementsByClassName('operate right')[0].click();")
        self.web.page().runJavaScript("setTimeout(function(){document.getElementsByClassName('go-btn')[0].click();},3000)")
    def go_back(self):
        self.web.load(QUrl(url))

    def get_pay(self):
        self.web.page().toHtml(self.sku_html)
        pay = SkuParser.get_total_pay(self.skuHtml)
        if pay is None:
            self.web.page().runJavaScript("alert('未采集到总价格信息,请重新点击');")
            #self.btn_get_pay.click()
            return
        else:
            self.web.page().runJavaScript("alert('总采集价格为["+pay+"]');")
            self.btn_go_back.click()

    # 将sku页面信息的内容赋值给窗体对象
    def sku_html(self, html):
        self.skuHtml = html

# 创建自己的浏览器控件，继承自QWebEngineView
class MyWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(MyWebEngineView, self).__init__(*args, **kwargs)
        # 绑定cookie被添加的信号槽
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.cookies = {}  # 存放cookie字典

    def onCookieAdd(self, cookie):  # 处理cookie添加的事件
        name = cookie.name().data().decode('utf-8')  # 先获取cookie的名字，再把编码处理一下
        value = cookie.value().data().decode('utf-8')  # 先获取cookie值，再把编码处理一下
        self.cookies[name] = value  # 将cookie保存到字典里

    # 获取cookie
    def get_cookie(self):
        cookie_str = ''
        for key, value in self.cookies.items():  # 遍历字典
            cookie_str += (key + '=' + value + ';')  # 将键值对拿出来拼接一下
        return cookie_str  # 返回拼接好的字符串


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = window()
    w.show()
    sys.exit(app.exec_())
