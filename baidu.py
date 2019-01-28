import sys,time,json,requests,random
from log_util import LoggerUtil
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from redis import StrictRedis
from PyQt5.QtWebEngineCore import *
rs = StrictRedis(host="114.67.85.93", port=10000, db=120,password="Summer001")
class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
    def interceptRequest(self, info):
        requestUrl = str(info.requestUrl())
        if requestUrl.find("mdskip.taobao.com/core/initItemDetail.htm")!=-1:
            print(type(info))
            print(info.requestUrl(), info.requestMethod(), info.resourceType(), info.firstPartyUrl())

def randHeader(referer=None):
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    head_user_agent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                       'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']
    header = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]
    }
    if referer is not None:
        header["referer"] = referer
    return header
from threading import Thread
def auto_task(p):
    while True:
        if p.flag:
            with open("url.txt", "r", encoding="utf-8") as r:
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
        #当前页面是否加载完成
        self.has_load_finished = False
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
        #人工校验地址成功后,进入商品页面
        self.btn_close = QPushButton('关闭')
        self.btn_close.clicked.connect(self.close)
        self.btn_start = QPushButton('启动')
        self.btn_start.clicked.connect(self.start)
        self.web = MyWebEngineView()  # 创建浏览器组件对象
        t = WebEngineUrlRequestInterceptor()
        self.web.page().profile().setRequestInterceptor(t)
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(self.current_url))  # 打开页面
        self.box.addWidget(self.btn_close)
        self.box.addWidget(self.btn_start)
        self.box.addWidget(self.btn_load)
        self.box.addWidget(self.btn_save)
        self.box.addWidget(self.web)  # 再放浏览器
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
    def load(self):
        self.web.load(QUrl(self.current_url))
    def has_finished(self):
        print("load finished...")
        self.has_load_finished = True
    def save(self):
        #self.web.reload()
        self.web.page().runJavaScript("window.scrollTo(100,1200);")
        #self.web.page().toHtml(self.sku_html)
        """
        while self.has_load_finished==False:
            time.sleep(1)
            LoggerUtil.write_file_log("等待页面加载完毕...")
        """
        self.web.page().toHtml(self.sku_html)



    #进入商品购买页面
    def btn_close(self):
        self.flag=False
    def start(self):
        self.flag = True
    def sku_html(self,html):
        current_url = self.current_url
        if self.current_url.find(".tmall.")!=-1:
            result = self.fill_detail(html)
            buy_url_id = current_url.replace("https://detail.tmall.com/item.htm?id=", "")
            if result is not None:
                with open("tmall-detail-%s.txt" % buy_url_id, "w", encoding="utf-8") as w:
                    w.write(result)
                    rs.set("tmall-detail-%s" % buy_url_id, result)
            with open("tmall-%s.txt" % buy_url_id, "w", encoding="utf-8") as w:
                w.write(html)
                rs.set("tmall-%s.txt" % buy_url_id, html)
        else:
            buy_url_id = current_url.replace("https://item.taobao.com/item.htm?id=", "")
            with open("targets/%s.txt"% buy_url_id, "w", encoding="utf-8") as w:
                w.write(html)
                rs.set("taobao-%s" % buy_url_id, html)
    def fill_detail(self,html):
        start = html.find('{"valItemInfo"')
        if start==-1:
            return None
        desc = html[start:].split(");")
        desc = desc[0]
        desc = desc.strip()
        with open("desc.txt","w",encoding="utf-8") as w:
            w.write(desc)
        jsonObject = json.loads(desc)
        descUrl = jsonObject["api"]["descUrl"]
        if descUrl.find("http:")==-1:
            descUrl = "http:%s"%descUrl
        LoggerUtil.write_file_log("请求详情接口地址:%s"%descUrl)
        resp = requests.get(descUrl,headers=randHeader(self.current_url),
            cookies={"cookie": self.web.get_cookie()})
        if resp.status_code!=200:
            print(resp.text)
            return None
        result = resp.text
        if result.find("var desc")!=-1:
            result = result.replace("var desc='","")
        if result.endswith("';"):
            result = result[0:-2]
        return result


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
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    Thread(target=auto_task,args=(w,)).start()
    sys.exit(app.exec_())

    #print(rs.get("tmall-549036569931"))
