import sys,json
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from log_util import LoggerUtil
from order import Order
from sku_util import SkuParser
from urllib.parse import unquote
address_url="https://member1.taobao.com/member/fresh/deliver_address.htm"
# 先来个窗口
class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.box = QVBoxLayout(self)  # 创建一个垂直布局来放控件
        #当前登录用户
        self.username = None
        #当前订单列表
        self.order = None
        #当前真实支付
        self.realPay = None
        #初始化当前订单数据
        self.btn_init_order = QPushButton('进入收货地址添加页面/重新初始化')
        self.btn_init_order.setShortcut("1")
        self.btn_init_order.clicked.connect(self.init_order)
        #添加收货地址页面,运行页面js
        self.btn_add_adress = QPushButton('添加收货地址')  # 创建一个按钮涌来了点击获取cookie
        self.btn_add_adress.setVisible(False)
        self.btn_add_adress.clicked.connect(self.add_address)  # 绑定按钮点击事件
        #人工校验地址成功后,进入商品页面
        self.btn_go_buy_url = QPushButton('进入商品页')
        self.btn_go_buy_url.setVisible(False)
        self.btn_go_buy_url.clicked.connect(self.go_buy_url)
        #计算sku的位置
        self.btn_sku_pos = QPushButton('校验SKU')
        self.btn_sku_pos.setShortcut("3")
        self.btn_sku_pos.setEnabled(False)
        self.btn_sku_pos.clicked.connect(self.sku_pos)
        #进入商品页面后,查询sku信息,若无法查询到,则弹出异常
        self.btn_select_sku = QPushButton('自动选择SKU')
        self.btn_select_sku.setShortcut("4")
        self.btn_select_sku.setEnabled(False)
        self.btn_select_sku.clicked.connect(self.select_sku)
        #校验商品数量
        self.btn_select_count = QPushButton("校验商品数量")
        self.btn_select_count.setShortcut("5")
        self.btn_select_count.setEnabled(False)
        self.btn_select_count.clicked.connect(self.select_count)
        #提交订单信息
        self.btn_commit_order = QPushButton("提交订单")
        self.btn_commit_order.setShortcut("5")
        self.btn_commit_order.setEnabled(False)
        self.btn_commit_order.clicked.connect(self.commit_order)
        #标记处理结果成功
        self.btn_mark_success = QPushButton('成功处理,进入下一个商品或订单')
        self.btn_mark_success.setShortcut("7")
        self.btn_mark_success.setEnabled(False)
        self.btn_mark_success.clicked.connect(self.mark_success)

        self.btn_mark_fail = QPushButton('标记失败,进入下一个商品或订单')
        self.btn_mark_fail.setShortcut("8")
        self.btn_delete = QPushButton('清理收货地址');
        self.btn_delete.setShortcut('Enter')

        self.btn_mark_fail.clicked.connect(self.mark_fail)

        self.btn_delete.clicked.connect(self.delete_address)
        self.web = MyWebEngineView()  # 创建浏览器组件对象
        self.web.resize(1200, 900)  # 设置大小
        self.web.load(QUrl(address_url))  # 打开页面
        self.box.addWidget(self.btn_init_order)
        self.box.addWidget(self.btn_add_adress)  # 将组件放到布局内，先在顶部放一个按钮
        self.box.addWidget(self.btn_go_buy_url)
        self.box.addWidget((self.btn_sku_pos))
        self.box.addWidget(self.btn_select_sku)
        self.box.addWidget(self.btn_select_count)
        self.box.addWidget(self.btn_commit_order)
        #self.box.addWidget(self.btn_buy)
        self.box.addWidget(self.btn_mark_success)
        self.box.addWidget(self.btn_mark_fail)
        self.box.addWidget(self.web)  # 再放浏览器
        self.box.addWidget(self.btn_delete)
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
        self.skuHtml=''
    #初始化订单信息,拿取订单数据
    def init_order(self):
        if self.username is None:
            cookies = self.web.get_cookie()
            pos = cookies.find("lid=")
            if pos==-1:
                self.web.page().runJavaScript("window.alert('请先登录')")
                return;
            else:
                cookies =cookies[pos+4:]
                username =cookies.split(";")[0]
                self.username = unquote(username.strip(),"utf-8")
                LoggerUtil.write_file_log("淘宝拍单用户[%s]登录成功"%self.username)
                self.order = Order(self.username)

        self.order.pop()
        if self.order.current_order is None:
            self.web.page().runJavaScript("window.alert('暂无数据')")
            return;
        print(json.dumps(self.order.current_order, ensure_ascii=False, indent=2))
        self.btn_add_adress.setEnabled(True)
        # self.web.load(QUrl(address_url))
        self.btn_add_adress.click()
    #添加收货地址页面
    def add_address(self):
        if self.username is None:
            self.web.page().runJavaScript("alert('请先登录')")
            return;
        if self.order is None or self.order.current_order is None:
            self.web.page().runJavaScript("alert('暂无数据')")
            return;
        addr_json = self.order.current_addr
        if addr_json is not None:
            js_string = 'lib.mtop.request({"api":"mtop.taobao.mbis.insertDeliverAddress","v":"1.0","data":%s,"ecode":1,"needLogin":true,"timeout":20000}).then(function(e){alert(JSON.stringify(e));},function(e){alert(JSON.stringify(e))})'%addr_json
            LoggerUtil.write_file_log("正在请求页面js\n%s\n"%js_string)
            self.web.page().runJavaScript(js_string)
            self.btn_go_buy_url.click()
            self.btn_sku_pos.setEnabled(True)
        else:
            self.web.page().runJavaScript("alert('暂无数据')")
    #进入商品购买页面
    def go_buy_url(self):
        if self.username is None:
            self.web.page().runJavaScript("alert('请先登录')")
            return;
        if self.order.current_url is not None:
            self.web.load(QUrl(self.order.current_url))
            self.btn_sku_pos.click()
        else:
            self.web.page().runJavaScript("window.alert('暂无数据')")
    def sku_pos(self):
        self.web.page().toHtml(self.sku_html)
        self.btn_select_sku.setEnabled(True)
    #选择sku然后进行购买
    def select_sku(self):
        self.web.page().toHtml(self.sku_html)
        sku_pos = SkuParser.parse(self.skuHtml, self.order.sku_id)
        if sku_pos is not None:
            arr = sku_pos.split(",")
            for prop in arr:
                pos_arry = prop.split("-")
                js_string = "setTimeout(function(){document.getElementsByClassName('J_TSaleProp')[%s].getElementsByTagName('li')[%s].getElementsByTagName('a')[0].click();},1000)"%(pos_arry[0], pos_arry[1])
                self.web.page().runJavaScript(js_string)
            self.web.page().runJavaScript("setTimeout(function(){document.getElementsByClassName('J_LinkBuy')[0].click();},1000)")
        else:
            self.web.page().runJavaScript("window.alert('无法定位sku,请重试')")
            #LoggerUtil.write_file_log("无法定位sku,请标记失败")
        self.btn_select_count.setEnabled(True)
    #选择商品的数量
    def select_count(self):
        self.web.page().toHtml(self.sku_html)
        count = self.order.current_count
        if count is not None:
            count = int(count)
        if count>1:
            for i in range(1,count):
                self.web.page().runJavaScript("document.getElementsByClassName('operate right')[0].click();")
        self.btn_commit_order.setEnabled(True)

    #提交订单,并且确定商品数量
    """
       提交订单信息,包含订单的数量,总价格等信息
       """
    def commit_order(self):
        self.web.page().toHtml(self.sku_html)
        pay = SkuParser.get_total_pay(self.skuHtml)
        print(pay)
        if pay is not None:
            self.realPay = pay
        self.web.page().runJavaScript("setTimeout(function(){document.getElementsByClassName('go-btn')[0].click();},3000)")
        self.btn_mark_success.setEnabled(True)
    def mark_success(self):
        last_order_id = self.order.current_order_id
        self.order.mark_success(self.realPay)
        current_order_id = self.order.current_order_id
        if current_order_id==last_order_id:
            LoggerUtil.write_file_log("订单的商品处理成功,继续处理该订单的下一件商品")
            self.web.load(QUrl(self.order.current_url))
        else:
            LoggerUtil.write_file_log("订单处理成功,继续处理下一个订单")
            self.btn_init_order.click()

    def mark_fail(self):
        if self.username is None:
            self.web.page().runJavaScript("alert('请先登录')")
            return;
        last_order_id = self.order.current_order_id
        self.order.mark_fail()
        current_order_id = self.order.current_order_id
        if current_order_id == last_order_id:
            self.web.load(QUrl(self.order.current_url))
        else:
            self.web.load(QUrl(address_url))


    #将sku页面信息的内容赋值给窗体对象
    def sku_html(self,html):
        self.skuHtml = html

    def order_buy(self):
        if self.username is None:
            self.web.page().runJavaScript("alert('请先登录')")
            return;
        self.web.page().runJavaScript("document.getElementsByClassName('go-btn')[0].click();")

    def delete_address(self):
        js_string='''
           var spans = document.getElementsByClassName("t-delete");
           spans[0].click();
           setTimeout(function(){
              var btn = document.getElementsByClassName("next-dialog-btn")[0].click();
           },2000)
           
        '''
        self.web.page().runJavaScript(js_string)
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
        with open("cookie.txt","w",encoding="utf-8") as w:
            w.write(cookie_str)
        return cookie_str  # 返回拼接好的字符串
if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    w = window()
    w.show()
    sys.exit(app.exec_())


    #step1_test()
