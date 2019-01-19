from urllib.parse import unquote
s='%E7%8C%AB%E4%B8%83%E4%B8%83021'
s = unquote(s,'utf-8')
print(s)