import sys,json
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
import threading
url="https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?action=itemlist/BoughtQueryAction&event_submit_do_query=1&tabCode=waitPay"
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件''
        #添加收货地址页面,运行页面js
        #人工校验地址成功后,进入商品页面
        self.btn_a = QPushButton('获取页面信息')
        self.btn_a.clicked.connect(self.to_a)
        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.b = QPlainTextEdit()
        self.b.setWindowTitle("当前订单")
        self.b.insertPlainText("测试订单数据")
        self.b.resize(1200,400)
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(url))  # 打开页面
        self.box.addWidget(self.btn_a)
        self.box.addWidget(self.web)  # 再放浏览器
        self.box.addWidget(self.b)
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    #进入商品购买页面
    def to_a(self):
        self.web.load(QUrl(url))
        #self.web.loadFinished(self.xxx)
        self.xxx()
    def xxx(self):
        self.web.page().toHtml(self.sku_html)

    #将sku页面信息的内容赋值给窗体对象
    def sku_html(self,html):
        self.skuHtml = html
        content = self.skuHtml
        pos = content.find("JSON.parse('")
        content = content[pos + len("JSON.parse('"):]
        pos = content.find("');")
        content = content[0:pos]
        content = content.replace('\\"', "'")
        content = content.replace("\\u", 'u')
        content = content.replace("\\\\", "")
        pos = content.find("mainOrders")
        content = "{'" + content[pos:]
        content = content.replace('"', '')
        # content=unquote(content,'unicode')
        pos = content.find(",'page':")
        content = content[0:pos] + "}"
        content = content.replace("'", "\"")
        cr = json.loads(content)
        cr = cr["mainOrders"]
        print(cr)
        result = []
        print(json.dumps(cr[0], ensure_ascii=False, indent=2))
        for c in cr:
            order = {}
            order["id"] = c["id"]
            order["skuId"] = c["subOrders"][0]["itemInfo"]["skuId"]
            order["buy_url_id"] = c["subOrders"][0]["itemInfo"]["id"]
            result.append(str(json.dumps(order, ensure_ascii=False, indent=5)))
        with open("order.txt", "w", encoding="utf-8") as w:
            w.write("\n\n*******************************************************************\n\n".join(result))
if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    sys.exit(app.exec_())
