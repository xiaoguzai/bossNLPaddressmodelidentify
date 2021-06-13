import requests
url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html'#请求的方式为get，所以对应选择request的get方法
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
resp = requests.get(url,headers=headers)#resp就是响应结果
#返回的码为200，说明响应结果正常，200表示成功，418表示遇到反爬
print(resp.request.headers)
#返回的头部为一个python-requests表示返回的为一个爬虫

print(resp.encoding)
print(resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0]))
current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0])

import re
kk = re.compile(r'<a href=\'\d+\.html\'>(.*?)<br/>')
current_results = kk.findall(current_data)
#读取所有的省份
kk = re.compile(r'<a href=\'(.*?)\'>.*?<br/>')
current_links = kk.findall(current_data)
#读取下一波链接
#<td><a href='11.html'>北京市<br/>

f = open('国家统计局省份数据.txt','w')
for data in current_results:
    f.write(data+'\n')
f.close()

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
        if len(city_name) < 2:
            continue
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

county_url_data = []
county_name_data = []
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Connection':'close'}
from tqdm import tqdm
break_data = []
for data in tqdm(city_url_data):
    #city_url_data
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    try:
        resp = requests.get(url,headers=headers)
        current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    except:
        break_data.append(data)
        continue
    kk = re.compile(r'<tr class=\'countytr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data2 in  current_results:
    #爬取对应的县的索引以及县的名称
        kk1 = re.compile(r'<td><a href=\'(.*?)\'>\d+</a></td>')
        url_name = re.findall(kk1,data2)
        kk2 = re.compile(r'<td><a href=\'.*?\'>(.*?)</a></td>')
        county_name = re.findall(kk2,data2)
        if len(county_name) < 2:
            continue
        county_url_data.append(data[0:2]+'/'+url_name[0])
        county_name_data.append(county_name[1])
        #<td><a href='11/1101.html'>110100000000</a></td><td><a href='11/1101.html'>市辖区</a></td>

for data in tqdm(break_data):
    #city_url_data
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    resp = requests.get(url,headers=headers)
    current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    kk = re.compile(r'<tr class=\'countytr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data2 in  current_results:
    #爬取对应的县的索引以及县的名称
        kk1 = re.compile(r'<td><a href=\'(.*?)\'>\d+</a></td>')
        url_name = re.findall(kk1,data2)
        kk2 = re.compile(r'<td><a href=\'.*?\'>(.*?)</a></td>')
        county_name = re.findall(kk2,data2)
        if len(county_name) < 2:
            continue
        county_url_data.append(data[0:2]+'/'+url_name[0])
        county_name_data.append(county_name[1])
        #<td><a href='11/1101.html'>110100000000</a></td><td><a href='11/1101.html'>市辖区</a></td>

f = open('county_url_data.txt','w') 
for data in county_url_data:
    f.write(data+'\n')
f.close()
f = open('国家统计局爬取的县名称.txt','w')
for data in county_name_data:
    f.write(data+'\n')
f.close()

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Connection':'close'}
town_url_data = []
town_name_data = []
from tqdm import tqdm
break_data = []
for data in tqdm(county_url_data):
    #data = 11/01/110101.html
    #爬取对应县的数据
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    #county_url_data之中存放的为街道对应的数值
    try:
        resp = requests.get(url,headers=headers)
        current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    except:
        break_data.append(data)
        continue
    #current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0])
    current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    #不加ignore不能够忽视非法字符
    kk = re.compile(r'<tr class=\'towntr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data2 in current_results:
    #爬取对应的县的索引以及县的名称
        kk1 = re.compile(r'<td><a href=\'(.*?)\'>\d+</a></td>')
        url_name = re.findall(kk1,data2)
        kk2 = re.compile(r'<td><a href=\'.*?\'>(.*?)</a></td>')
        town_name = re.findall(kk2,data2)
        if len(county_name) < 2:
            continue
        town_url_data.append(data[0:6]+url_name[0])
        town_name_data.append(town_name[1])

for data in tqdm(break_data):
    #data = 11/01/110101.html
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    #county_url_data之中存放的为街道对应的数值
    resp = requests.get(url,headers=headers)
    current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    #不加ignore不能够忽视非法字符
    kk = re.compile(r'<tr class=\'towntr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data2 in current_results:
    #爬取对应的县的索引以及县的名称
        kk1 = re.compile(r'<td><a href=\'(.*?)\'>\d+</a></td>')
        url_name = re.findall(kk1,data2)
        kk2 = re.compile(r'<td><a href=\'.*?\'>(.*?)</a></td>')
        town_name = re.findall(kk2,data2)
        if len(county_name) < 2:
            continue
        town_url_data.append(data[0:6]+url_name[0])
        town_name_data.append(town_name[1])

f = open('town_url_data.txt','w')
for data in town_url_data:
    f.write(data+'\n')
f.close()
f = open('国家统计局爬取的街道名称.txt','w')
for data in town_name_data:
    f.write(data+'\n')
f.close()

village = []
break_data = []
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Connection':'close'}
for data in tqdm(town_url_data):
#爬取对应街道的数据
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    try:
        resp = requests.get(url,headers=headers)
        current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    except:
        break_data.append(data)
        continue
    #current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0])
    kk = re.compile(r'<tr class=\'villagetr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data in current_results:
        kk = re.compile(r'<td>\d+</td><td>\d+</td><td>(.*?)</td>')
        village_name = re.findall(kk,data)
        if village_name[0][-1] == '区':
        #如果有某某社区，保留
            village.append(village_name[0])
        else:
        #如果有某某居委会，去除
            village.append(village_name[0][:-3])

for data in tqdm(break_data):
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'+data
    resp = requests.get(url,headers=headers)
    current_data = resp.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(resp.text)[0],'ignore')
    #不加ignore不能够忽视非法字符
    kk = re.compile(r'<tr class=\'villagetr\'>(.*?)</tr>')
    current_results = kk.findall(current_data)
    for data in current_results:
        kk = re.compile(r'<td>\d+</td><td>\d+</td><td>(.*?)</td>')
        village_name = re.findall(kk,data)
        if village_name[0][-1] == '区':
            village.append(village_name[0])
        else:
            village.append(village_name[0][:-3])

f = open('国家统计局爬取的社区名称.txt','w')
for data in city_name_data:
    f.write(data+'\n')
f.close()