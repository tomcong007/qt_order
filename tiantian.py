import sys,time,requests
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
url="https://member1.taobao.com/member/fresh/deliver_address.htm"
#url="https://www.baidu.com"
import csv
from threading import Thread
def auto_task(p):
    while True:
        if p.flag:
            l = None
            with open("order.csv", "r", encoding="utf-8") as r:
                reader = csv.reader(r)
                ret = []
                for line in reader:
                    if l is None:
                        l=line
                    username = line[14]
                    arr = line[15].split(" ")
                    address ="-".join(arr[0:-1])
                    addrDetail = arr[-1]
                    phone = line[18]
                    phone = phone.replace("'", "")
                    ret.append((username,address,phone,addrDetail))
                for r in ret[1:]:
                    resp =requests.get("http://114.67.88.45:8000/system/address",params={"userName":r[0],"address":r[1],"phone":r[2],"addrDetail":r[3]})
                    print(resp.text)
                    resp = resp.json()
                    if resp["code"]==0:
                        addr_json = resp["data"]
                        js_string = 'lib.mtop.request({"api":"mtop.taobao.mbis.insertDeliverAddress","v":"1.0","data":%s,"ecode":1,"needLogin":true,"timeout":20000}).then(function(e){alert(JSON.stringify(e));},function(e){alert(JSON.stringify(e))})' % addr_json
                        print("当前添加收货信息为:\n%s\n" % addr_json)
                        p.web.page().runJavaScript(js_string)
                    time.sleep(3)
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
        #添加收货地址页面,运行页面js
        #人工校验地址成功后,进入商品页面
        self.btn_close = QPushButton('关闭')
        self.btn_close.clicked.connect(self.close)
        self.btn_start = QPushButton('启动')
        self.btn_start.clicked.connect(self.start)

        self.web = QWebEngineView()  # 创建浏览器组件对象
        self.btn_delete = QPushButton('清理收货地址');
        self.btn_delete.clicked.connect(self.delete_address)
        self.btn_delete.setShortcut('Enter')
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(url))  # 打开页面
        self.box.addWidget(self.btn_close)
        self.box.addWidget(self.btn_start)
        self.box.addWidget(self.web)  # 再放浏览器
        self.box.addWidget(self.btn_delete)
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    #进入商品购买页面
    def btn_close(self):
        self.flag=False
    def start(self):
        self.flag = True
    #将sku页面信息的内容赋值给窗体对象
    def delete_address(self):
        js_string = '''
           var spans = document.getElementsByClassName("t-delete");
           spans[0].click();
           setTimeout(function(){
              var btn = document.getElementsByClassName("next-dialog-btn")[0].click();
           },2000)

        '''
        self.web.page().runJavaScript(js_string)


if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    Thread(target=auto_task,args=(w,)).start()
    sys.exit(app.exec_())
