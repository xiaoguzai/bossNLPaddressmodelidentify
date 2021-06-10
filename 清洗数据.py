from os import curdir
import re
f = open('D:\webproject\location_data.txt')
datas = f.readlines()
text1 = re.compile(r'.*[0-9]$')
text2 = re.compile(r'^[0-9].*')
text3 = re.compile(r'.*(与|自治区|和).*')
text4 = re.compile(r'.*[0-9]\)$')
text5 = re.compile(r'.*(，|、|\+|（|）|电话|【|“|@|#|/).*')
result_str = []
for i in range(len(datas)):
    datas[i] = datas[i].strip('\n')
    current = datas[i].split(' ')
    if len(current) == 5:
        continue
    if text1.match(current[3]) or text2.match(current[3]) or text3.match(current[3]) or text4.match(current[3]) or text5.match(current[3]):
        continue
    if current[1] != current[2]:
        if current[2][-1] == '州' and current[2][-2] == '治':
            result_str.append(current[1]+'省'+current[2]+current[3])
        else:
            result_str.append(current[1]+'省'+current[2]+'市'+current[3])
    else:
        result_str.append(current[2]+'市'+current[3])
print('result_str = ')
print(result_str)

categories_to_id = {0:'redundant',1:'prov',2:'city',3:'district',4:'devzone',5:'town',
             6:'community',7:'village_group',8:'road',9:'roadno',10:'poi',11:'subpoi',
             12:'houseno',13:'cellno',14:'floorno',15:'roomno',16:'detail',17:'assist',
             18:'distance',19:'intersection',20:'others'}
id_to_categories = {categories_to_id[data]:data for data in categories_to_id}

def split_data(currentdata,label,principle,category):
    #data1 = re.match(r'(.*)省(.*)',currentstr)
    data1 = re.match(principle,currentdata)
    number = len(principle)-8
    if data1 == None:
        return '',currentdata,label
    else:
        string1 = data1.group(1)
        string2 = data1.group(2)
        if principle == '(.*?)[^东西南北新发小街]区[^域](.*)':
            label.append([category]*(len(string1)+1))
        elif principle == '(.*?)[^超]市[^场](.*)':
            current_list = []
            for _ in range(len(string1)+1):
                current_list.append(category)
            label.append(current_list)
        else:
            current_list = []
            for _ in range(len(string1)+number-1):
                current_list.append(category)
            label.append(current_list)
    return string1,string2,label

import random
final_label = []
final_str = []
for data in result_str:
    current_string_list = []
    current_label = []
    currentstring1 = data

    currentstring1,currentstring2,current_label = split_data(currentstring1,current_label,'(.*?)省(.*)',id_to_categories['prov'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'省')
    #prov:省、自治区、直辖市
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)市(.*)',id_to_categories['city'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'市')

    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)自治州(.*)',id_to_categories['city'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'自治州')
    #city:地级市、自治州

    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)县(.*)',id_to_categories['district'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'县')

    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)[^东西南北新发小街]区[^域](.*)',id_to_categories['district'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'区')

    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)[^超]市[^场](.*)',id_to_categories['district'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'市')
    #district:行政区划，县级市、县等
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)开发区(.*)',id_to_categories['devzone'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'开发区')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)高新区(.*)',id_to_categories['devzone'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'高新区')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)园区(.*)',id_to_categories['devzone'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'园区')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)假区(.*)',id_to_categories['devzone'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'假区')
    #devzone:开发区，高新区，产业园区，度假区
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)镇(.*)',id_to_categories['town'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'镇')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)街道(.*)',id_to_categories['town'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'街道')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)乡(.*)',id_to_categories['town'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'乡')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)庄(.*)',id_to_categories['town'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'庄')
    #town:镇、街道、乡
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)社区(.*)',id_to_categories['community'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'社区')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)村(.*)',id_to_categories['community'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'村')
    #community:社区、村
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)组(.*)',id_to_categories['village_group'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'组')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)队(.*)',id_to_categories['village_group'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'队')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)社区(.*)',id_to_categories['village_group'])
    if currentstring1 != '':
        current_string_list.append(currentstring1+'社')
    #village_group = 组、队、社
    
    flag = False
    #标记有无路，有路才有路号
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)道(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'道')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)高架(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'高架')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)街(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'街')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)弄(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'弄')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)巷(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'巷')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路东侧(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路东侧')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路西侧(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路西侧')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路南侧(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路南侧')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路北侧(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路北侧')
    
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路')
        
    currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)路段(.*)',id_to_categories['road'])
    if currentstring1 != '':
        flag = True
        current_string_list.append(currentstring1+'路段')
    #road = 隧道、高架、街、弄、巷、路东侧、路西侧、路南侧、路北侧、路
    
    if flag == True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)号(.*)',id_to_categories['roadno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'号')
    #roadno = 路号
    
    flag = False
    
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)场(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'场')
    
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)餐厅(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'餐厅')
            
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)中心(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'中心') 
    
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)超市(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'超市')
            
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)商厦(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'商厦')
        
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)站(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'站')
        
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)服务区(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'服务区')
        
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)高铁(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'高铁')
            
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)公司(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'公司')
            
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)市场(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'市场')
            
    if flag != True:
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)小区(.*)',id_to_categories['poi'])
        if currentstring1 != '':
            flag = True
            current_string_list.append(currentstring1+'小区')
    #poi:餐厅、中心、场、超市、商厦、站、服务区、高铁、公司、市场、小区、花园
    
    if flag == True:
    #subpoi 期,幢/楼,区/侧,单元,层,号
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)期(.*)',id_to_categories['subpoi'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'期')
    
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)幢(.*)',id_to_categories['houseno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'幢')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)楼(.*)',id_to_categories['houseno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'楼')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)区(.*)',id_to_categories['assist'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'边')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)侧(.*)',id_to_categories['assist'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'侧')
        
        #!!!这里带不带单元可以两试!!!
        current_string_list.append(str(random.randint(0,9))+'单元')
        current_label.append([id_to_categories['cellno'],id_to_categories['cellno'],id_to_categories['cellno']])
        
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)层(.*)',id_to_categories['floorno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'层')
            
        result = re.match(r'([0-9A-Za-z]+-[0-9A-Za-z]+)(.*)',currentstring2)
        if result != None:
            data1 = result.group(1)
            data2 = result.group(2)
            if data1 != '':
                current_string_list.append(data1)
                data_list = []
                for _ in range(len(data1)):
                    data_list.append(id_to_categories['detail'])
                current_label.append(data_list)
                current_string_list.append(data1)
                currentstring2 = data2

        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)号(.*)',id_to_categories['roomno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'号')

    if flag == True:
        flag = False
        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)餐厅(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'餐厅')
            
        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)中心(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'中心') 

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)场(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'场')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)超市(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'超市')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)商厦(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'商厦')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)站(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'站')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)服务区(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'服务区')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)高铁(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'高铁')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)公司(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'公司')

        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)市场(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'市场')
                
        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)小区(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'小区')
                
        if flag != True:
            currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)花园(.*)',id_to_categories['poi'])
            if currentstring1 != '':
                flag = True
                current_string_list.append(currentstring1+'花园')
    #subpoi 餐厅、中心、场、超市、商厦、站、服务区、高铁、公司、市场、小区、花园
    
    if flag == True:
    #subpoi 期,幢/楼,区/侧,单元,层,号
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)期(.*)',id_to_categories['subpoi'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'期')
    
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)幢(.*)',id_to_categories['houseno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'幢')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)楼(.*)',id_to_categories['houseno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'楼')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)区(.*)',id_to_categories['assist'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'边')
            
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)侧(.*)',id_to_categories['assist'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'侧')
        
        current_string_list.append(str(random.randint(0,9))+'单元')
        current_label.append([id_to_categories['cellno']*3])
        
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)层(.*)',id_to_categories['floorno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'层')
            
        result = re.match(r'([0-9A-Za-z]+-[0-9A-Za-z]+)(.*)',currentstring2)
        if result != None:
            data1 = result.group(1)
            data2 = result.group(2)
            if data1 != '':
                current_string_list.append(data1)
                data_list = []
                for _ in range(len(data1)):
                    data_list.append(id_to_categories['detail'])
                current_label.append(data_list)
                current_string_list.append(data1)
                currentstring2 = data2
        
        currentstring1,currentstring2,current_label = split_data(currentstring2,current_label,'(.*?)号(.*)',id_to_categories['roomno'])
        if currentstring1 != '':
            current_string_list.append(currentstring1+'号')
            
    final_str.append(current_string_list)
    final_label.append(current_label)

