from bs4 import BeautifulSoup

from utils.api.base_api import BaseAPI

class GetScore(BaseAPI):
    def get_score(self,session):
        # 进入成绩查询页面
        url = 'http://jwgl.hutb.edu.cn/jsxsd/kscj/cjcx_list'
        payload = {
            'kksj': '2024-2025-2',
            'kcxz': None,
            'kcmc': None,
            'xsfs': 'all'
        }
        response = session.post(url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含成绩数据的表格
        table = soup.find('table', id='dataList')
        print("【成绩数据】")
        print(table)

        # 初始化一个列表来存储成绩数据
        grades = []

        if "未查询到数据" in table.text:
            return grades

            # 遍历表格中的每一行
        for row in table.find_all('tr')[1:]:  # 跳过表头行
            cols = row.find_all('td')
            course_name = cols[3].text.strip()
            grade = cols[4].text.strip()
            credit_point = cols[7].text.strip()
            grades.append({
                '课程名': course_name,
                '成绩': grade,
                '绩点': credit_point
            })

        # 打印成绩数据
        for grade in grades:
            print(f"课程名：{grade['课程名']}, 成绩：{grade['成绩']}, 绩点：{grade['绩点']}")

        # 打印科目总数
        total_courses = len(grades)
        print(f"科目总数：{total_courses}")

        # 返回成绩数据
        return grades
