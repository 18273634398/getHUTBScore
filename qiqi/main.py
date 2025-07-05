# file: main.py

from client import NetworkRequest
from auth import perform_login,get_captcha
from grades import fetch_grades

use_history = True

def main():
    """主执行函数"""
    base_url = "http://122.152.213.95:9893"

    # 这是一个初始的、可能已过期的或用于公共接口的 token
    initial_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTg4LCJpYXQiOjE3NTE3MDU4NDYsImV4cCI6MTc1MjMxMDY0Nn0.gPafpz3MVZpVJDtvlqrie4UBm4Ygjc9BLq04RsIh9fQ"

    common_headers = {
        "authorization": f"Bearer {initial_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Origin": "http://jw.qiqi.pro",
        "Referer": "http://jw.qiqi.pro/"
    }

    # 1. 创建一个通用的客户端实例 (这是将被共享的 session 对象)
    api_client = NetworkRequest(base_url=base_url, headers=common_headers)

    # 2. 获取用户凭据
    if not use_history:
        account = input("请输入账号: ")
        password = input("请输入密码: ")
    else:
        account = "2209030006"
        password = "lushangwu;2004"
    # 3. 将客户端实例传递给登录模块进行认证
    if(get_captcha(api_client)):
        print("获取验证码成功！")
    else:
        print("获取验证码失败！")
        return
    print("请输入验证码：")
    login_successful = perform_login(api_client, account, password, input())

    # 4. 如果登录成功，将同一个客户端实例传递给成绩模块
    if login_successful:
        grades = fetch_grades(api_client)

        if grades is not None:
            if grades:
                print("\n---------- 成绩单 ----------")
                for course in grades:
                    course_name = course.get("courseName", "N/A")
                    score = course.get("score", "N/A")
                    credit = course.get("credit", "N/A")
                    gpa = course.get("gpa", "N/A")
                    print(f"课程: {course_name:<20} 学分: {credit:<5} 成绩: {score} GPA: {gpa}")
                print("--------------------------")
            else:
                print("未查询到成绩信息。")
    else:
        print("\n由于登录失败，无法获取成绩。")

if __name__ == "__main__":
    main()