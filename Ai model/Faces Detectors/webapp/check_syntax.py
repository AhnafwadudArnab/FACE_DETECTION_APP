s=open('app.py','r',encoding='utf8').read()
try:
    compile(s,'app.py','exec')
    print('syntax ok')
except Exception as e:
    print('syntax error:',e)
