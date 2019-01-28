import sys,time,csv,pymysql,os,shutil,json
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from datetime import datetime as dt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
url="https://member1.taobao.com/member/fresh/deliver_address.htm"
from threading import Thread
class LoggerUtil():
    @staticmethod
    def get_log_file():
        filename ="淘宝拍单记录%s.txt" % (dt.now().strftime('%Y-%m-%d'))
        if not os.path.exists(filename):
            if not os.path.exists("template.txt"):
                with open("template.txt", "w", encoding="utf-8") as w:
                    w.write("日志记录:\n")
            shutil.copy("template.txt",filename)
        return filename
    @staticmethod
    def write_file_log(info=None):
        if info is None:
            info = "[%s]-[%s]"% (sys.exc_info()[0], sys.exc_info()[1])
        date_str = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LoggerUtil.get_log_file(), "a+", encoding="utf-8") as f:
            f.write("[%s]:%s\n" % (date_str, info))
            print("[%s]:%s\n" % (date_str, info))
def get_conn():
    conn = pymysql.connect(host='mysql-cn-east-2-6f6aafba39094dac.public.jcloud.com', user='Bei_Database', password='Beibeisuper666', db='taobao',
                           charset='utf8')
    return conn
def get_address_json(username,address,phone,addrDetail):
    conn = get_conn()
    cur = conn.cursor()
    addrInfos = address.split("-");
    if addrInfos is None or len(addrInfos)<2:
        LoggerUtil.write_file_log("地址信息不合法:[%s]"%address)
    area = addrInfos[len(addrInfos)-1]
    city = addrInfos[len(addrInfos)-2]
    cur.execute("select city_code from t_city where city_name=%s and parent_code =(select city_code from t_city where city_name=%s)",(area,city))
    areaCode = cur.fetchone()
    if areaCode is None:
        LoggerUtil.write_file_log("找不到区域名:[%s]-[%s]" % (area,city))
        return None
    cur.execute("select city_code,alias_name from t_district where parent_code = %s",(areaCode))
    divisionList = cur.fetchall()
    if divisionList is None or len(divisionList)==0:
        LoggerUtil.write_file_log("区域[%s]-[%s]下街道为空"% (area,city))
    divisionCode = 0
    for division in divisionList:
        alias = division[1]
        if addrDetail.find(alias)!=-1:
            divisionCode = division[0]
            break;
    if divisionCode == 0:
        divisionCode = divisionList[0][0]
    jsonResult ={"mobileCode":"86","addressDetail":addrDetail,"mobile":phone,"phoneAreaCode":"","defaultDeliverAddress":True,"phoneInternationalCode":"86","phoneExtension":"","phoneNumber":"","fullName":username,"divisionCode":divisionCode,"overseaAddress":False}
    return jsonResult


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
                    try:
                        jsonResult = get_address_json(r[0], r[1], r[2], r[3])
                        addr_json = json.dumps(jsonResult)
                        js_string = 'lib.mtop.request({"api":"mtop.taobao.mbis.insertDeliverAddress","v":"1.0","data":%s,"ecode":1,"needLogin":true,"timeout":20000}).then(function(e){alert(JSON.stringify(e));},function(e){alert(JSON.stringify(e))})' % addr_json
                        LoggerUtil.write_file_log("当前添加收货信息为:\n%s\n" % json.dumps(jsonResult, ensure_ascii=False, indent=2))
                        p.web.page().runJavaScript(js_string)
                    except:
                        LoggerUtil.write_file_log()
                p.flag=False
        else:
            print("等待任务")
            time.sleep(10)

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
