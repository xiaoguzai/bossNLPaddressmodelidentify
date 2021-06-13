import requests
url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html'#请求的方式为get，所以对应选择request的get方法
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
resp = requests.get(url,headers=headers)#resp就是响应结果
print(resp)
#返回的码为200，说明响应结果正常，200表示成功，418表示遇到反爬
print(resp.request.headers)
#返回的头部为一个python-requests表示返回的为一个爬虫
print(resp.text)

current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0])
#当前数据需要由ISO-8859-1进行转换

import re
kk = re.compile(r'<a href=\'\d+\.html\'>(.*?)<br/>')
current_results = kk.findall(current_data)
#current_data = re.findall(r'<a .*?(.*)<br/>',current_data)
#<a href='35.html'>福建省<br/></a>
kk = re.compile(r'<a href=\'(.*?)\'>.*?<br/>')
current_links = kk.findall(current_data)

city_url_data = []
city_name_data = []
for current_link in current_links:
    #range(11,66)
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+current_link
    resp = requests.get(url,headers=headers)#resp就是响应结果
    current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0])
    #kk = re.compile(r'<tr class=\"citytr\">(.*)</tr>')
    kk = re.compile(r'<tr class=\'citytr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    r"""
    这里提取出来的数据
    <tr class='citytr'><td><a href='13/1301.html'>130100000000</a></td><td><a href='13/1301.html'>石家庄市</a></td></tr>
    <tr class='citytr'><td><a href='13/1310.html'>131000000000</a></td><td><a href='13/1310.html'>廊坊市</a></td></tr>
    <tr class='citytr'><td><a href='13/1311.html'>131100000000</a></td><td><a href='13/1311.html'>衡水市</a></td></tr>
    """
    for data in  current_results:
    #爬取对应的市的索引以及市的名称
        kk1 = re.compile(r'<td><a href=\'(.*?)\'>\d+</a></td>')
        url_name = re.findall(kk1,data)
        kk2 = re.compile(r'<td><a href=\'.*?\'>(.*?)</a></td>')
        city_name = re.findall(kk2,data)
        city_url_data.append(url_name[0])
        city_name_data.append(city_name[1])
        #<td><a href='11/1101.html'>110100000000</a></td><td><a href='11/1101.html'>市辖区</a></td>

f = open('city_url_data.txt','w') 
for data in city_url_data:
    f.write(data+'\n')
f.close()
f = open('国家统计局爬取的市名称.txt','w')
for data in city_name_data:
    f.write(data+'\n')
f.close()