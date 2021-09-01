# 山石网科CNVD自动提交工具
## 安装依赖环境

```shell
pip install -r requirement.txt
```

报告放在docxs文件夹下
## 配置文件

CNVD_UPLOAD.ini为程序配置，具体写法里面有详细写法  
company.txt存放公司名称  
pwned.txt存放'存在漏洞的url'  
 
## CNVD_AUTO.py
注意修改里面和账号相关的东西,具体如下  
+ login()里的data
+ self.driver.find_element_by_id('email').send_keys("xxxx")
+ self.driver.find_element_by_id('password').send_keys("xxxx")

## 运行 
在当前文件夹下打开cmd运行exe文件  
(还不是完全自动，验证码还是要手动输，以后有能力可以看看用图像识别解决
