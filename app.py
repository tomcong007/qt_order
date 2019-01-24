import sys,json
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton,QPlainTextEdit
from log_util import LoggerUtil
from order import Order
from sku_util import SkuParser
from urllib.parse import unquote
from datetime import datetime as dt
address_url="https://member1.taobao.com/member/fresh/deliver_address.htm"
class TextArea(QWidget):
    def __init__(self):
        super().__init__()
        self.box = QVBoxLayout(self)
        self.b = QPlainTextEdit()
        self.b.setWindowTitle("当前订单")
        self.b.setStyleSheet("background-color:lightYellow;")
        self.b.resize(1200, 900)
        self.box.addWidget(self.b)
        self.setWindowTitle("拍单日志")

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
        #当前的淘宝订单号
        self.orderId = None
        #当前的淘宝实际拍单数量
        self.skuCount = None
        #子窗体
        self.dialog = TextArea()
        self.dialog.show()
        #初始化当前订单数据
        self.btn_init_order = QPushButton('进入收货地址添加页面/重新初始化')
        self.btn_init_order.clicked.connect(self.init_order)
        #添加收货地址页面,运行页面js
        self.btn_add_adress = QPushButton('添加收货地址')  # 创建一个按钮涌来了点击获取cookie
        self.btn_add_adress.setVisible(False)
        self.btn_add_adress.clicked.connect(self.add_address)  # 绑定按钮点击事件
        #校验地址是否成功添加
        self.btn_validate_adress = QPushButton('校验收货地址')
        self.btn_validate_adress.setVisible(False)
        self.btn_validate_adress.clicked.connect(self.validate_address)
        #人工校验地址成功后,进入商品页面
        self.btn_go_buy_url = QPushButton('进入商品页')
        self.btn_go_buy_url.setEnabled(False)
        self.btn_go_buy_url.clicked.connect(self.go_buy_url)
        #计算sku的位置
        self.btn_sku_pos = QPushButton('校验SKU')
        self.btn_sku_pos.setEnabled(False)
        self.btn_sku_pos.clicked.connect(self.sku_pos)
        #进入商品页面后,查询sku信息,若无法查询到,则弹出异常
        self.btn_select_sku = QPushButton('自动选择SKU')
        self.btn_select_sku.setEnabled(False)
        self.btn_select_sku.clicked.connect(self.select_sku)
        #校验商品数量
        self.btn_select_count = QPushButton("校验商品数量")
        self.btn_select_count.setEnabled(False)
        self.btn_select_count.clicked.connect(self.select_count)
        #提交订单信息
        self.btn_commit_order = QPushButton("提交订单")
        self.btn_commit_order.setEnabled(False)
        self.btn_commit_order.clicked.connect(self.commit_order)
        #计算淘宝订单号,进入订单
        self.btn_go_order_page = QPushButton("进入我的订单列表")
        self.btn_go_order_page.setEnabled(False)
        self.btn_go_order_page.clicked.connect(self.go_order_page)
        #计算当前订单的skuId对应的淘宝订单号
        self.btn_get_order_id = QPushButton("获取订单号(点击2次)")
        self.btn_get_order_id.setEnabled(False)
        self.btn_get_order_id.clicked.connect(self.get_order_id)
        #标记处理结果成功
        self.btn_mark_success = QPushButton('成功处理,进入下一个商品或订单')
        self.btn_mark_success.setEnabled(False)
        self.btn_mark_success.clicked.connect(self.mark_success)

        self.btn_mark_fail = QPushButton('标记失败,进入下一个商品或订单')
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
        self.box.addWidget(self.btn_go_order_page)
        self.box.addWidget(self.btn_get_order_id)
        #self.b = QPlainTextEdit()
        #self.b.setWindowTitle("当前订单")
        #self.b.setStyleSheet("background-color:lightYellow;")
        #self.b.resize(1200, 400)
        self.box.addWidget(self.btn_mark_success)
        self.box.addWidget(self.btn_mark_fail)
        self.box.addWidget(self.web)  # 再放浏览器
        #self.box.addWidget(self.b)
        self.box.addWidget(self.btn_delete)
        self.web.show()  # 最后让页面显示出来
        self.setWindowTitle("贝贝拍单工具")
        self.skuHtml=''
    def insertPlain(self,info):
        date_str = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dialog.b.insertPlainText("[%s]:%s\n"%(date_str,info))
    #初始化订单信息,拿取订单数据
    def init_order(self):
        self.insertPlain("正在点击初始化按钮...")
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
            self.insertPlain("暂无数据")
            self.web.page().runJavaScript("window.alert('暂无数据')")
            return;
        LoggerUtil.write_file_log("当前订单商品信息为:")
        info = json.dumps(self.order.current_order, ensure_ascii=False, indent=2)
        LoggerUtil.write_file_log(info)
        self.insertPlain("当前订单商品贝贝订单号为:%s" % self.order.current_order_id)
        self.insertPlain("当前订单商品链接为:%s" % self.order.current_url)
        self.insertPlain("当前订单商品skuId:%s"%self.order.sku_id)
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
            LoggerUtil.write_file_log("正在添加收货地址:\n%s\n"%addr_json)
            self.insertPlain("当前添加收货信息为:\n%s\n"%addr_json)
            self.web.page().runJavaScript(js_string)
            self.btn_go_buy_url.setEnabled(True)
        else:
            self.web.page().runJavaScript("alert('暂无数据')")
    def validate_address(self):
        pass

    #进入商品购买页面
    def go_buy_url(self):
        self.insertPlain("正在进入商品购买页...")
        if self.order.current_url is not None:
            self.web.load(QUrl(self.order.current_url))
            self.btn_sku_pos.setEnabled(True)
            self.btn_sku_pos.click()
        else:
            self.web.page().runJavaScript("window.alert('暂无数据')")
    def sku_pos(self):
        self.insertPlain("正在获取商品sku属性数据...")
        self.web.page().toHtml(self.sku_html)
        self.btn_select_sku.setEnabled(True)
    #选择sku然后进行购买
    def select_sku(self):
        self.insertPlain("正在校验商品属性...")
        self.web.page().toHtml(self.sku_html)
        sku_pos = SkuParser.parse(self.skuHtml, self.order.sku_id)
        if sku_pos is None:
            self.web.page().runJavaScript("window.alert('无法定位sku,请重试')")
            LoggerUtil.write_file_log("无法定位sku,请标记失败")
            self.insertPlain("无法定位sku,请标记失败")
        elif sku_pos == 0:
            self.web.page().runJavaScript("window.alert('属性无法完全匹配,请标记或手动选择')")
            LoggerUtil.write_file_log("无法定位sku,请标记失败")
            self.insertPlain("无法定位sku,请标记失败")
        else:
            for prop in sku_pos:
                LoggerUtil.write_file_log("选择属性%s"%(str(prop)))
                self.insertPlain("选择属性%s"%(str(prop)))
                i,j,prop_name =prop
                js_string = "setTimeout(function(){var lis = document.getElementsByClassName('J_TSaleProp')[%s].getElementsByTagName('li');if(lis.length>1){lis[%s].getElementsByTagName('a')[0].click()};},1000)"%(i, j)
                self.web.page().runJavaScript(js_string)
                self.insertPlain("选择SKU属性:%s"%prop_name)
            self.web.page().runJavaScript("setTimeout(function(){document.getElementsByClassName('J_LinkBuy')[0].click();},1000)")
        self.btn_select_count.setEnabled(True)

    #选择商品的数量
    def select_count(self):
        self.insertPlain("正在同步商品数量...")
        self.web.page().toHtml(self.sku_html)
        count = self.order.current_count
        if count is not None:
            count = int(count)
        if count>1:
            self.insertPlain("商品数量为%d,正在模拟点击"%count)
            for i in range(1,count):
                self.web.page().runJavaScript("document.getElementsByClassName('operate right')[0].click();")
        else:
            self.insertPlain("商品数量为1,无需校验数量")
        self.btn_commit_order.setEnabled(True)

    #提交订单,并且确定商品数量
    """
       提交订单信息,包含订单的数量,总价格等信息
       """
    def commit_order(self):
        self.insertPlain("1秒后提交订单...")
        self.web.page().runJavaScript("setTimeout(function(){document.getElementsByClassName('go-btn')[0].click();},1000)")
        self.btn_go_order_page.setEnabled(True)
    def go_order_page(self):
        self.insertPlain("正在跳转我的订单列表页")
        self.web.load(QUrl("https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?action=itemlist/BoughtQueryAction&event_submit_do_query=1&tabCode=waitPay"))
        self.btn_get_order_id.setEnabled(True)
    def get_order_id(self):
        self.insertPlain("准备获取我的淘宝订单号")
        self.web.page().toHtml(self.sku_html)
        self.get_orders(self.skuHtml)
        self.btn_mark_success.setEnabled(True)
        if self.orderId is not None:
            self.insertPlain("获取淘宝订单号成功,订单单号为:%s,拍单数量为:%s"%(self.orderId,str(self.skuCount)))
            LoggerUtil.write_file_log("获取淘宝订单号成功,订单单号为:%s,拍单数量为:%s"%(self.orderId,str(self.skuCount)))
        else:
            self.insertPlain("获取淘宝订单单号失败,可手动标记为成功或失败...")
            LoggerUtil.write_file_log("获取淘宝订单单号失败,可手动标记为成功或失败...")
    def mark_success(self):
        self.insertPlain("点击标记成功")
        order = self.order
        last_order_id = order.current_order["order_id"]
        self.insertPlain("正在处理订单单号[%s]的贝贝数据"%str(last_order_id))
        LoggerUtil.write_file_log("正在处理订单单号[%s]的贝贝数据"%str(last_order_id))
        order.mark_success(self.realPay,self.orderId,self.skuCount)
        current_order_id = order.current_order["order_id"]
        self.insertPlain("处理完毕,当前单号为[%s]" % str(current_order_id))
        LoggerUtil.write_file_log("处理完毕,当前单号为[%s]" % str(current_order_id))
        self.order = order
        if current_order_id==last_order_id:
            self.insertPlain("订单的商品处理成功,继续处理该订单的下一件商品")
            LoggerUtil.write_file_log("订单的商品处理成功,继续处理该订单的下一件商品")
            self.web.load(QUrl(self.order.current_url))
        else:
            self.insertPlain("订单处理成功,继续处理下一个订单")
            LoggerUtil.write_file_log("订单处理成功,继续处理下一个订单")
            self.web.load(QUrl(address_url))

    def mark_fail(self):
        self.insertPlain("点击标记失败")
        order = self.order
        last_order_id = order.current_order["order_id"]
        self.insertPlain("正在标记失败订单单号[%s]的贝贝数据" % str(last_order_id))
        LoggerUtil.write_file_log("正在标记失败订单单号[%s]的贝贝数据" % str(last_order_id))
        order.mark_fail()
        current_order_id = order.current_order["order_id"]
        self.order = order
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
    def get_orders(self,content):
        self.orderId = None
        self.skuCount = None
        try:
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

            for c in cr:
                skuId = c["subOrders"][0]["itemInfo"]["skuId"]
                skuCount = c["subOrders"][0]["quantity"]
                realPay = c["subOrders"][0]["priceInfo"]["realTotal"]
                if skuId == self.order.sku_id:
                    orderId = str(c["id"])
                    self.insertPlain("获取淘宝订单单号:%s" % orderId)
                    LoggerUtil.write_file_log("获取淘宝订单单号:%s" % orderId)
                    self.orderId = orderId
                    self.skuCount = skuCount
                    self.realPay = realPay
                    self.insertPlain("获取淘宝订单单号总金额,数量:%s,%s" % realPay,str(skuCount))
                    LoggerUtil.write_file_log("获取淘宝订单单号总金额,数量:%s,%s" % realPay,str(skuCount))
                    break
            if self.orderId is None:
                self.insertPlain("获取淘宝订单号失败")
        except:
            pass

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
