import json
def get_content():
    with open("html.txt", "r", encoding="utf-8-sig") as r:
        content = r.read()
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
        pos=content.find(",'page':")
        content = content[0:pos]+"}"
        print(json.dumps(content, ensure_ascii=False, indent=5))
        with open("content.txt", "w", encoding="utf-8") as w:
            w.write(content)
def explain():
    with open("content.txt","r",encoding="utf-8") as r:
        content = r.read()
        content = content.replace("'","\"")
        cr = json.loads(content)
        cr = cr["mainOrders"]
        print(cr)
        result = []
        print(json.dumps(cr[0], ensure_ascii=False, indent=2))
        for c in cr:
            order ={}
            order["id"] = c["id"]
            order["skuId"] = c["subOrders"][0]["itemInfo"]["skuId"]
            order["buy_url_id"] = c["subOrders"][0]["itemInfo"]["id"]
            result.append(str(json.dumps(order, ensure_ascii=False, indent=5)))
        with open("order.txt","w",encoding="utf-8") as w:
            w.write("\n\n*******************************************************************\n\n".join(result))


if __name__ == '__main__':
    #get_content()
    explain()




