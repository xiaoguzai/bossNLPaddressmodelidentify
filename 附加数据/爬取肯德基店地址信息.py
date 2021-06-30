import  requests
import  json
from tqdm import tqdm
url = 'http://www.kfc.com.cn/kfccda/ashx/GetStoreList.ashx'
#原先url = https://movie.douban.com/j/chart/top_list?type=24&interval_id=100%3A90&action=&start=20&limit=20
#将？后面的数据都封装到相应的字典之中
with open('省份数据.txt','r',encoding='utf-8') as f1:
    cities = f1.readlines()
#将Query String Parameters中对应的5个参数粘贴过来
#浏览器最下面一栏的Query String Parameters能够查看到相应的5个参数
f1.close()
totalnumber = 1
f1 = open('已处理过的省份数据.txt','w')
for city in tqdm(cities):
    city = city[:-1]
    city = city.split(' ')
    province = city[0]
    city = city[1]
    param = {
        'op':'cname'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'Connection': 'close',
    }
    #注意headers之中需要加入'Connection':'close',否则一直requests.post并且不关闭会报错
    #failed to establish a new connection
    pageIndex = 1
    total = 0
    address = []
    f1.write(str(city)+'\n')
    fp = open('./location.txt','a+')
    while True:
        data = {
            'cname':city,
            'pid':'',
            'pageIndex':str(pageIndex),
            'pageSize':'10'
        }
        response = requests.post(url=url,params=param,data=data,headers=headers)
        response_text = response.text
        response_json = json.loads(response_text)
        rowcount = response_json["Table"][0]["rowcount"]
        if rowcount == 0:
            break
        currentaddress = response_json["Table1"]
        for currentdata in currentaddress:
            address.append(currentdata["addressDetail"]+'\n')
            fp.write(str(totalnumber)+' '+province+' '+city+' '+currentdata["addressDetail"]+'\n')
            totalnumber = totalnumber+1
        if  currentdata["rownum"] == rowcount:
            break
        pageIndex = pageIndex+1

print('over!!!')
