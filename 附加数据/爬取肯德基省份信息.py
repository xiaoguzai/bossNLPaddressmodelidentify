import  requests
#第一句：导入requests模块
import  re
#第二局：发送请求
from tqdm import tqdm

url = 'http://www.kfc.com.cn/kfccda/storelist/index.aspx'
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Connection': 'close',
    }
reap = requests.get(url,headers = headers)
provinces = re.findall(r'<li id=\".\">(.*?)</li>',reap.text)
resultdata = []
for data in tqdm(provinces):
    province = re.findall(r'<strong>(.*?)</strong>',data)
    province = province[0]
    info = re.findall(r'<a href=\"javascript:void\(0\);".*?>(.*?)</a>',data)
    for data1 in info:
        result = province+' '+data1
        resultdata.append(result)
#.为任意字符，*为任意个，小括号的意思是只要小括号里面的内容
#此时没有拿到任意东西
#print(reap.text)    #响应结果显示输出
fp = open('省份数据.txt','w',encoding='utf-8')
for data in resultdata:
    fp.write(data+'\n')
fp.close()
#strs = '<a href="javascript:void(0);" title="" cityid="6616" rel="明光">明光</a>'
#info = re.findall(r'<a href=\"javascript:void\(0\);".*?>(.*?)</a>',strs)
