from bs4 import BeautifulSoup
from utils.log_util import logger
from utils.api.base_api import BaseAPI

class GetScore(BaseAPI):
    def __init__(self,session):
        super().__init__() # 调用父类的 __init__ 方法
        self.session = session

    # 获取期末成绩
    def get_score_final_exam(self,sj="2024-2025-2"):
        # 进入成绩查询页面
        url = f'{self.base_url}/jsxsd/kscj/cjcx_list' # 使用 self.base_url
        payload = {
            'kksj': sj,
            'kcxz': None,
            'kcmc': None,
            'xsfs': 'all'
        }
        response = self.session.get(url,data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含成绩数据的表格
        table = soup.find('table', id='dataList')
        logger.info("【成绩数据】")

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
            logger.info(f"课程名：{grade['课程名']}, 成绩：{grade['成绩']}, 绩点：{grade['绩点']}")

        # 打印科目总数
        total_courses = len(grades)
        logger.info(f"科目总数：{total_courses}")

        # 返回成绩数据
        return grades

    # 获取等级考试成绩
    def get_score_level_exam(self):
        url = f"{self.base_url}/jsxsd/kscj/djkscj_list" # 使用 self.base_url
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含等级考试成绩数据的表格
        table = soup.find('table', id='dataList')
        logger.info("【等级考试成绩数据】")
        
        # 初始化一个列表来存储等级考试成绩数据
        level_grades = []
        
        if table is None:
            logger.info("未找到等级考试成绩表格")
            return level_grades
            
        if "未查询到数据" in table.text:
            logger.info("未查询到等级考试成绩数据")
            return level_grades
        
        # 遍历表格中的每一行（跳过前两行表头）
        for row in table.find_all('tr')[2:]:  # 跳过两行表头
            cols = row.find_all('td')
            if len(cols) >= 9:  # 确保有足够的列
                exam_name = cols[1].text.strip()  # 考级课程(等级)
                written_score = cols[2].text.strip()  # 笔试分数
                computer_score = cols[3].text.strip()  # 机试分数
                total_score = cols[4].text.strip()  # 总成绩分数
                written_grade = cols[5].text.strip()  # 笔试等级
                computer_grade = cols[6].text.strip()  # 机试等级
                total_grade = cols[7].text.strip()  # 总成绩等级
                exam_time = cols[8].text.strip()  # 考级时间
                
                level_grades.append({
                    '考级课程': exam_name,
                    '笔试分数': written_score if written_score else None,
                    '机试分数': computer_score if computer_score else None,
                    '总分数': total_score if total_score else None,
                    '笔试等级': written_grade if written_grade else None,
                    '机试等级': computer_grade if computer_grade else None,
                    '总等级': total_grade if total_grade else None,
                    '考试时间': exam_time
                })
        
        # 打印等级考试成绩数据
        for grade in level_grades:
            logger.info(f"考级课程：{grade['考级课程']}, 总分数：{grade['总分数']}, 总等级：{grade['总等级']}, 考试时间：{grade['考试时间']}")
        
        # 打印等级考试总数
        total_exams = len(level_grades)
        logger.info(f"等级考试总数：{total_exams}")
        
        # 返回等级考试成绩数据
        return level_grades
