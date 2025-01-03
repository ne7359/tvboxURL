import requests,re,json,os,time
from datetime import datetime
import notify
import warnings 
warnings.filterwarnings("ignore")


def respon_out(respon): #输入respond,判断线路、单仓和多仓
    mcang=re.search("storeHouse",respon,re.M|re.I)
    scang = re.search("urls",respon,re.M|re.I)
    xlu = re.search("sites",respon,re.M|re.I)
    if xlu is not None :
        return 0 #"H线路"
    elif xlu is  None and scang is not None and mcang is None:
        return 1 #"H单仓"
    elif xlu is  None and scang is  None and mcang is not None:
        return 2 #"H多仓"
    else :
        return "other"
def addlink(url): #增加代理链接
    agentlink="http://fly.lyin.cf/?url=" #失效
    agentlink1="http://lige.unaux.com/?url=" 
    agentlink2="https://xn--sss604efuw.com/jm/jiemi.php?url="
    urll=agentlink1+url
    url2=agentlink2+url
    return url2

def fetch_url_info(url):
    try:
        
        start_time = time.time() # 记录开始时间
        response = requests.get(url) # 发送GET请求
        end_time = time.time() # 记录结束时间
        response_time = end_time - start_time # 计算响应时间
        content_length_kb = len(response.content) / 1024 # 获取内容长度并转换为KB
        print(f"响应时间: {response_time:.4f} 秒")
        print(f"内容长度: {content_length_kb:.2f} KB")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

def process_json(url): # 判断url路线有效性，并在本地生成tvbox_json文件
    response = requests.get(url,verify=False)
    headers={"User-Agent":"okhttp/4.1.0"}
    if response.status_code == 200:
        jsondata = json.loads(response.text)
        datas=jsondata['urls']
        x=len(datas)
        print('总线路条数：',x)
        for data in datas:
            testurl=data['url']
            start_time = time.time()
            try:
                rnse = requests.get(testurl,verify=False,timeout =60)
                if rnse.status_code==200:
                    if respon_out(rnse.text)==0 and len(rnse.text) / 1024 > 2:
                        print(data['name'],data['url'],"线路成功")
                    else:
                        # rnse1= requests.get(addlink(testurl),verify=False,timeout =60)
                        rnse1= requests.get(testurl,headers=headers,verify=False,timeout =60)
                        if rnse1.status_code==200 and respon_out(rnse1.text)==0 and len(rnse1.text) / 1024 > 2:
                            print(data['name'],data['url'],"线路成功")
                        else:
                            datas.remove(data)
                            print('已删除当前失败',data['name'],data['url'])
                else:
                    datas.remove(data)
                    print('已删除当前失败',data['name'],data['url'])
            except Exception:
                datas.remove(data)
                print('已删除当前error',data['name'],data['url'])
            else:
                pass
            finally:
                content_length_kb = len(rnse.text) / 1024
                end_time = time.time()
                response_time = end_time - start_time
                print(f"响应时间: {response_time:.4f} 秒; ",f"内容长度: {content_length_kb:.2f} KB")
                print("-"*100)
                # pass
        y=len(datas) #成功路线
    print('成功路线条数：',y)

    def DelRepeat(data,key):
        new_data = [] # 用于存储去重后的list
        values = []   # 用于存储当前已有的值
        for d in data:
            if d[key] not in values:
                new_data.append(d)
                values.append(d[key])
        z=len(data)-len(new_data) #去重路线条数
        return new_data,z

    dict2={}
    dict2['urls']=DelRepeat(datas,'url')[0]
    print('去除线路：',DelRepeat(datas,'url')[1])
    print('总成功路线：',y-DelRepeat(datas,'url')[1])
    savejson2=json.dumps(dict2, indent=4, ensure_ascii=False)
    
    # print(type(savejson2))
    with open(filename, "w", encoding="utf-8") as file:
        file.write(savejson2)
        file.close()
    return savejson2,y-DelRepeat(datas,'url')[1]


def check_file_exist():
    folder_path = os.getcwd()
    file_list = os.listdir(folder_path)
    if filename in file_list:
        # print(file_list)
        file_path = os.path.join(folder_path,filename)
        # 获取tvboxjson文件的修改时间
        filelast_modified=os.path.getmtime(file_path)
        last_modified_time = datetime.fromtimestamp(filelast_modified)
        formatted_time = last_modified_time.strftime('%Y-%m-%d %H:%M:%S')
        print('文件存在，文件修改时间是：',formatted_time,"文件路径是：",file_path)
        return file_path
    else:
        print('文件不存在')
        # print(file_list)

def main():
    # url = "https://gitee.com/jiangnandao/tvboxshare/raw/master/Tvtest"
    url="https://gitee.com/jiangnandao/tvboxshare/raw/master/TVLineTestTew.json"
    tvjson=process_json(url)
    notify.send("tvbox路线失效验证", "最后成功的线路条数有："+str(tvjson[1]))
    check_file_exist()
    
if __name__ == '__main__':
    filename='tvbox.json'
    main()
