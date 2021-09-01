#coding=utf-8
#author:whale3070、HHHAMSTER
#link: https://blog.csdn.net/weixin_40502018/article/details/112581719
import configparser
import os
import requests
from requests.utils import add_dict_to_cookiejar
import execjs
import hashlib
import json
import re
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get__jsl_clearance_s(data):
    """
    通过加密对比得到正确cookie参数
    :param data: 参数
    :return: 返回正确cookie参数
    """
    chars = len(data['chars'])
    for i in range(chars):
        for j in range(chars):
            __jsl_clearance_s = data['bts'][0] + data['chars'][i] + data['chars'][j] + data['bts'][1]
            encrypt = None
            if data['ha'] == 'md5':
                encrypt = hashlib.md5()
            elif data['ha'] == 'sha1':
                encrypt = hashlib.sha1()
            elif data['ha'] == 'sha256':
                encrypt = hashlib.sha256()
            encrypt.update(__jsl_clearance_s.encode())
            result = encrypt.hexdigest()
            if result == data['ct']:
                return __jsl_clearance_s

def setCookie(url):
    global session
    session = requests.session()
    header = {
                'Host':'www.cnvd.org.cn',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                'Accept':'*/*',
                'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding':'gzip, deflate',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With':'XMLHttpRequest',
                }
    response1 = session.get(url,headers=header)
    jsl_clearance_s = re.findall(r'cookie=(.*?);location', response1.text)[0]
    jsl_clearance_s = str(execjs.eval(jsl_clearance_s)).split('=')[1].split(';')[0]
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': jsl_clearance_s})

    response2 = session.get(url,headers=header)
    data = json.loads(re.findall(r';go\((.*?)\)', response2.text)[0])
    jsl_clearance_s = get__jsl_clearance_s(data)
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': jsl_clearance_s})

setCookie("https://www.cnvd.org.cn")

class CNVD(object):
    def __init__(self):


        self.companys = self.company()
        self.vul_url = self.vul_address()
        self.docxs_path = self.doc_path()
        self.config = self.config_ini()

        self.options=webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        self.driver = webdriver.Chrome(chrome_options=self.options)
        # self.driver.maximize_window()

    #读配置文件
    def config_ini(self):
        config = configparser.ConfigParser()
        config.read("CNVD_UPLOAD.ini",encoding="UTF-8")
        return config.items("ini")

    #获取报告的绝对路径
    def doc_path(self):
        cwd = str(os.getcwd()) + "\\docxs"
        docxs_path = []
        for file in os.listdir(cwd):
            file_path = os.path.join(cwd,file)
            docxs_path.append(file_path)
        # docxs_path = os.listdir(cwd)
        return docxs_path

    #获取公司名称
    def company(self):
        list = []
        company_file = open("company.txt", "r", encoding='utf-8')
        for eachCompany in company_file.readlines():
            list.append(eachCompany.strip("\n"))
        company_file.close()
        return list

    #获取漏洞地址
    def vul_address(self):
        list = []
        vul_add = open("pwned.txt", "r", encoding='utf-8')
        for each in vul_add.readlines():
            mysplit = each.strip("\n").split(",")
            #print(mysplit)
            list.append(mysplit[0])
        vul_add.close()
        return list

    def login(self):
        
        #headers设置，缺少会导致session实效
        headers = {
                    'Host':'www.cnvd.org.cn',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                    'Accept':'*/*',
                    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding':'gzip, deflate',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With':'XMLHttpRequest',
                    'Origin':'https://www.cnvd.org.cn',
                    'Referer':'https://www.cnvd.org.cn/user/login'
                    }

        data = 'password=xxxx'
        response = session.post(url="https://www.cnvd.org.cn/user/doLogin/loginForm",data=data,headers=headers)
        response.encoding='utf-8'

        self.driver.get("https://www.cnvd.org.cn")
        self.driver.add_cookie({'name':'__jsl_clearance_s','value':session.cookies.get_dict()['__jsl_clearance_s']})
        self.driver.add_cookie({'name':'JSESSIONID','value':session.cookies.get_dict()['JSESSIONID']})
        self.driver.add_cookie({'name':'__jsluid_s','value':session.cookies.get_dict()['__jsluid_s']})

        #登录阶段
        while(1):
            try:
                self.driver.get("https://www.cnvd.org.cn/user/doLogin/loginForm")
                self.driver.find_element_by_id('email').send_keys("xxxx")
                self.driver.find_element_by_id('password').send_keys("xxxx")
                code = input("登录验证码：")
                self.driver.find_element_by_id('myCode').send_keys(code)
                self.driver.find_element_by_class_name('b_28_1').click()
                WebDriverWait(self.driver,2).until(EC.presence_of_element_located((By.XPATH,"//dt[contains(text(),'账号设置')]")))
                break
            except TimeoutException:
                print("验证码输入错误,请重新登录!")
                continue


    def submit(self,i):
        
        print("正在提交第{num}个报告".format(num=i+1))

        #进入提交页面
        self.driver.find_element_by_class_name('b_28_1').click()

        #填写数据
        self.driver.execute_script('window.scrollBy(0,400)')
        self.driver.find_element_by_name('unitName').send_keys(self.companys[i])
        self.driver.find_element(By.XPATH,"//label[contains(text(),'所在省份')]").click()
        self.driver.find_element_by_id('select2-param_province-container').click()
        province = self.driver.find_element(By.XPATH,"//body/span[1]/span[1]/span[1]/input[1]")
        province.send_keys("未知")
        province.send_keys(Keys.ENTER)
        self.driver.find_element(By.XPATH,"//input[@id='title']").send_keys(self.companys[i])

        self.driver.find_element(By.XPATH,"//select[@id='titlel']").click()

        #设置配置    
        ini_vul_type = self.config[0][1]    #漏洞类型
        sql_type = self.config[1][1]   #sql注入类型(get/post)
        extra = self.config[2][1]    #写入额外输入框中的内容
        usr_name = self.config[3][1]  #弱口令账号密码
        usr_pwd = self.config[4][1]

        #漏洞类型判断
        if ini_vul_type == "sql注入":
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[12]/p[1]/select[1]/option[1]").click()
            if sql_type == "post":
                self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[13]/div[1]/p[1]/span[1]/input[2]").click()
            self.driver.execute_script('window.scrollBy(0,600)')
            self.driver.find_element(By.XPATH,"//textarea[@id='sqlInjectionVulnerabilitySqlMap']").send_keys(extra)

        elif ini_vul_type == "xss":
            self.driver.execute_script('window.scrollBy(0,600)')
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[12]/p[1]/select[1]/option[3]").click()
            self.driver.find_element(By.XPATH,"//textarea[@id='xssVulnerabilityPayload']").send_keys(extra)

        elif ini_vul_type == "弱口令":
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[12]/p[1]/select[1]/option[5]").click()
            self.driver.execute_script('window.scrollBy(0,600)')
            self.driver.find_element(By.XPATH,"//input[@id='weakPasswordAccountNumber']").send_keys(usr_name)
            self.driver.find_element(By.XPATH,"//input[@id='weakPasswordPwd']").send_keys(usr_pwd)

        elif ini_vul_type == "命令执行":
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[12]/p[1]/select[1]/option[11]").click()
            self.driver.execute_script('window.scrollBy(0,600)')
            self.driver.find_element(By.XPATH,"//select[@id='remoteCommandExecutionType']").click()
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[13]/div[11]/p[1]/select[1]/option[5]").click()
            self.driver.find_element(By.XPATH,"//select[@id='remoteCommandExecutionMiddleware']").click()
            self.driver.find_element(By.XPATH,"//body/div[3]/div[1]/div[1]/form[1]/div[2]/div[13]/div[11]/p[2]/select[1]/option[7]").click()
            self.driver.find_element(By.XPATH,"//textarea[@id='remoteCommandExecutionTool']").send_keys(extra)

        else:
            1==1

        self.driver.find_element(By.XPATH,"//textarea[@id='url']").send_keys(self.vul_url[i])  
        self.driver.find_element(By.XPATH,"//input[@id='flawAttFile']").send_keys(self.docxs_path[i])
        self.driver.execute_script('window.scrollBy(0,300)')
        while(1):
            try:
                upload_code = input("请输入上传报告阶段的验证码：")
                self.driver.find_element(By.XPATH,"//input[@id='myCode']").send_keys(upload_code)
                self.driver.find_element(By.XPATH,"//span[contains(text(),'提交')]").click()
                WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.XPATH,"//dt[contains(text(),'账号设置')]")))
                break
            except TimeoutException:
                print("验证码输入错误,请重新输入!")
                self.driver.find_element(By.XPATH,"//input[@id='myCode']").clear()
                continue

        if i != len(self.docxs_path)-1 :
            try:
                WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.XPATH,"//dt[contains(text(),'账号设置')]")))
            except TimeoutException:
                print("跳转用户页面失败!")
                self.driver.quit()
                sys.exit(2)  
        else:
            print("所有报告提交完成")

    def start(self):
        offset = self.config[5][1]
        if offset == '':
            try:
                self.login()
                for i in range(len(self.docxs_path)):
                    self.submit(i)
            except KeyboardInterrupt:
                print("用户退出！")
                # self.driver.quit()
                sys.exit(2)
        else:
            try:
                self.login()
                for i in range((offset-1),len(self.docxs_path)):
                    self.submit(i)
            except KeyboardInterrupt:
                print("用户退出！")
                # self.driver.quit()
                sys.exit(2)
cnvd = CNVD()
cnvd.start()
