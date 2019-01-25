content =None
with open("tmall.html","r") as r:
    content = r.read()
    start = content.find('"content":[{"text":"')
    content = content[start+len('"content":[{"text":"'):]
    end = content.find('","type":"label"}')
    content= content[0:end]
    print(content)
