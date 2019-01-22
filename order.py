import pymysql,json
from log_util import LoggerUtil
def get_conn():
    conn = pymysql.connect(host='localhost', user='Bei_Database', password='Beibeisuper666', db='taobao',
                           charset='utf8')
    return conn
class Order():
    def __init__(self,username):
        self.username = username
        self.current_order = None
        try:
            self.pull()
        except:
            LoggerUtil.write_file_log()
    def pop(self):
        if self.orders is not None and len(self.orders)>0:
            self.current_order = self.orders[0]
            self.current_order_id = self.orders[0]["order_id"]
            self.current_addr = self.orders[0]["address_json"]
            self.current_url = self.orders[0]["list"][0]["url"]
            self.sku_id =  self.orders[0]["list"][0]["sku_id"]
            self.current_count = self.orders[0]["list"][0]["count"]
        else:
            self.current_order_id = None
            self.current_addr = None
            self.current_url = None
            self.sku_id = None
    def mark_success(self,realPay):
        conn = get_conn()
        cur = conn.cursor()
        orders = self.orders
        current_order = self.current_order
        order_details = current_order["list"]
        id = str(order_details[0]["id"])
        cur.execute("update t_shop_order_detail set state =5,pay=%s where id=%s"%(realPay,id))
        l = len(order_details)
        if l==1:
            cur.execute("update t_shop_order set state =3 where id =%s and state!=4"%str(current_order["id"]))
            del orders[0]
            if len(orders)==0:
                self.pull()
            else:
                self.orders = orders
                self.pop()
        else:
            del order_details[0]
            current_order["list"] = order_details
            self.current_order = current_order
            self.pop()
        conn.commit()
        conn.close()
    def mark_fail(self):
        conn = get_conn()
        cur = conn.cursor()
        orders = self.orders
        current_order = self.current_order
        order_details = current_order["list"]
        id = str(order_details[0]["id"])
        cur.execute("update t_shop_order_detail set state =6 where id=%s" % id)
        l = len(order_details)
        if l == 1:
            cur.execute("update t_shop_order set state =4 where id =%s" % str(current_order["id"]))
            del orders[0]
            if len(orders) == 0:
                self.pull()
            else:
                del order_details[0]
                current_order["list"] = order_details
                self.current_order = current_order
                self.pop()
        else:
            del order_details[0]
            current_order["list"] = order_details
            self.current_order = current_order
            self.pop()
        conn.commit()
        conn.close()


    def loop(self):
        self.current_order_id = self.orders[0]["order_id"]
    def pull(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("select id,order_id,address_json from t_shop_order where state = 1 and taobao_user_name=%s limit 0,10",(self.username))
        rows = cur.fetchall()
        if rows is None or len(rows)==0:
            self.orders = None
        orders = []
        for row in rows:
            order ={"id":row[0],"order_id":row[1],"address_json":row[2]}
            details=[]
            cur.execute("select buy_url,sku_id,id,count from t_shop_order_detail where state =3 and order_id=%s",(str(row[1])))
            ds = cur.fetchall()
            if ds is None or len(ds)==0:
                cur.execute(" update t_shop_order set state = -2,error_msg='无合格的商品明细' where id=%d"%row[0])
            else:
                for d in ds:
                    detail={"url":d[0],"sku_id":d[1],"id":d[2],"count":d[3]}
                    details.append(detail)
                order["list"] = details
                orders.append(order)
        conn.commit()
        conn.close()
        self.orders = orders
if __name__ == '__main__':
    order = Order("猫七七021")
    order.pop()
    print(order.current_order["list"][0]["count"])
    print(json.dumps(order.current_order, ensure_ascii=False, indent=2))
