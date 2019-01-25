import sys,time
from log_util import LoggerUtil
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
from redis import StrictRedis
rs = StrictRedis(host="114.67.85.93", port=10000, db=120,password="Summer001")
print(rs.get("taobao-522830258527"))
with open("taobao-522830258527.txt","w",encoding="utf-8") as w:
    w.write(rs.get("taobao-522830258527").decode())
#url="https://www.baidu.com"
import csv
from threading import Thread
def auto_task(p):
    while True:
        if p.flag:
            with open("urls.txt", "r", encoding="utf-8") as r:
                urls = r.read().split("\n")
                for r in urls:
                    p.current_url = r
                    p.btn_load.click()
                    LoggerUtil.write_file_log("正在采集页面[%s]数据"%r)
                    time.sleep(3)
                    p.btn_save.click()
                    LoggerUtil.write_file_log("采集完毕,准备下1条数据")
                    time.sleep(2)
                p.flag=False
        else:
            print("等待任务")
            time.sleep(5)

# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.flag = False
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件''
        #当前链接请求
        self.current_url = "https://www.taobao.com"
        #当前页面信息
        self.skuHtml = None
        #加载某个页面,但是该按钮不显示
        self.btn_load = QPushButton('加载')
        self.btn_load.setVisible(False)
        self.btn_load.clicked.connect(self.load)
        #保存页面信息
        self.btn_save = QPushButton('保存')
        self.btn_save.setVisible(False)
        self.btn_save.clicked.connect(self.save)
        # 保存页面信息
        self.btn_download = QPushButton('下载')
        self.btn_download.setVisible(False)
        self.btn_download.clicked.connect(self.download)
        #人工校验地址成功后,进入商品页面
        self.btn_close = QPushButton('关闭')
        self.btn_close.clicked.connect(self.close)
        self.btn_start = QPushButton('启动')
        self.btn_start.clicked.connect(self.start)
        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(self.current_url))  # 打开页面
        self.box.addWidget(self.btn_close)
        self.box.addWidget(self.btn_start)
        self.box.addWidget(self.btn_load)
        self.box.addWidget(self.btn_save)
        self.box.addWidget(self.btn_download)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    def load(self):
        self.web.load(QUrl(self.current_url))

    def save(self):
        #self.web.reload()
        #self.web.page().runJavaScript("console.log('hello world');")
        self.web.page().toHtml(self.sku_html)

    def download(self):
        self.web.page().toHtml(self.sku_html)
        current_url = self.current_url
        buy_url_id = current_url.replace("https://item.taobao.com/item.htm?id=","")
        html = self.skuHtml
        if self.current_url.find(".tmall.")!=-1:
            with open("targets/%s.txt"% buy_url_id, "w", encoding="utf-8") as w:
            #with open("targets/tamll-%s.txt"%buy_url_id,"w",encoding="utf-8") as w:
                w.write(html)
            #rs.set("tamll-%s"%buy_url_id,html)
        else:
            with open("targets/%s.txt"% buy_url_id, "w", encoding="utf-8") as w:
                w.write(html)
            #with open("targets/taobao-%s.txt"%buy_url_id,"w",encoding="utf-8") as w:
            #rs.set("taobao-%s"%buy_url_id,html)


    #进入商品购买页面
    def btn_close(self):
        self.flag=False
    def start(self):
        self.flag = True
    def sku_html(self,html):
        print(html)
        current_url = self.current_url
        buy_url_id = current_url.replace("https://item.taobao.com/item.htm?id=", "")
        if self.current_url.find(".tmall.") != -1:
            with open("targets/%s.txt" % buy_url_id, "w", encoding="utf-8") as w:
                # with open("targets/tamll-%s.txt"%buy_url_id,"w",encoding="utf-8") as w:
                w.write(html)
                # rs.set("tamll-%s"%buy_url_id,html)
        else:
            with open("targets/%s.txt" % buy_url_id, "w", encoding="utf-8") as w:
                w.write(html)
                # with open("targets/taobao-%s.txt"%buy_url_id,"w",encoding="utf-8") as w:
if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    Thread(target=auto_task,args=(w,)).start()
    sys.exit(app.exec_())
