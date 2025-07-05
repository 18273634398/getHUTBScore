## 项目名称
湖南工商大学教务管理系统自助登录

### 项目介绍
该项目实现了基于已有接口的手机短信验证码获取、登录以及成绩信息的查询

### 项目部分接口
- 获取登录手机短信验证码接口
- - url:https://cas.hutb.edu.cn/lyuapServer/login/mobile/generateCode
- - method:post
- - mobile:手机号
- - module:"0"
- - username:手机号

### 分支说明
- master分支使用的是教务网官方接口，因无法确定教务网的前端密码加密逻辑，暂时不支持通过账号密码登录教务网，但是该分支支持更多功能
- GUI分支使用第三方平台提供的接口，目前仅仅支持账号密码登录以及成绩查询功能

### 项目界面
#### master
该分支支持手机验证码登录 使用手机验证码登录后将自动保存cookie，下一次可以使用cookie快速登陆
同时该分支支持调用学校官方的接口来查询登录账号（学号），但是该功能感觉没啥用
![控制台登录方式](https://github.com/user-attachments/assets/033de35b-e459-4eef-84d9-0d4e1e4113fe)
![控制台获取学号](https://github.com/user-attachments/assets/4fb5e890-8b94-44d4-b4b7-50265777361c)
![控制台功能展示](https://github.com/user-attachments/assets/d896d501-dea2-4b07-a3d8-0c3f4a6605fd)


#### GUI
![GUI登录页面](https://github.com/user-attachments/assets/6ce1cef5-e98b-424f-a484-f50629a34716)
![GUI成绩查询页面](https://github.com/user-attachments/assets/790f063c-4674-45d2-8df9-1fef6d9eb12e)





