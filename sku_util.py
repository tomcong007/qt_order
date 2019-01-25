from bs4 import BeautifulSoup
import  requests
class SkuParser():
    @staticmethod
    def parse(html, skuId):
        skuStr = '"skuId":"%d"' % skuId
        pos = html.find(skuStr)
        if pos == -1:
            return None
        desc = html[0:pos]
        arr = desc.split("},")
        if len(arr) == 0:
            return None
        desc = arr[-1]
        pos = desc.find(':{"price"')
        if pos == -1:
            return None
        desc = desc[0:pos]
        pvs = desc.replace('"', '')
        result = []
        for a in pvs.split(";"):
            a = a.strip()
            if len(a) > 0:
                result.append(a)
        sku_pos = []
        soup = BeautifulSoup(html, 'html.parser')
        uls = soup.find_all('ul', class_='J_TSaleProp')
        if uls is None or len(uls) == 0:
            return None
        for i in range(len(uls)):
            ul = uls[i]
            lis = ul.find_all('li')
            if lis is None or len(lis) == 0:
                continue
            for j in range(len(lis)):
                li = lis[j]
                pv = li.attrs['data-value']
                pv = pv.replace("'","")
                pv = pv.strip()
                if pv in result:
                    sku_pos.append((i,j,li.find_all("span")[0].get_text()))
                    break;
        if len(sku_pos)==0:
            return None
        if len(sku_pos)!=len(uls):
            return 0
        return sku_pos
    @staticmethod
    def get_sku_price(html):
        soup = BeautifulSoup(html, 'html.parser')
        spans =soup.find_all('span',class_='simple-price')
        if spans is None or len(spans)==0:
            return None
        return spans[0].get_text()
    @staticmethod
    def get_total_pay(html):
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find_all('span', class_='realPay-price')
        if div is None or len(div) == 0:
            return None
        pay = div[0].get_text()
        return pay




