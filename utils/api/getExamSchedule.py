from bs4 import BeautifulSoup
from utils.log_util import logger
from utils.api.base_api import BaseAPI

class GetExamSchedule(BaseAPI):
    # 获取考试安排信息
    # params:
    #     xnxqid: 学年学期id，默认为2024-2025-2
    def get_exam_schedule(self, session,xnxqid="2024-2025-2"):
        """
        获取考试安排信息
        :param session: 会话对象
        :return: 考试安排数据列表
        """
        url = "http://jwgl.hutb.edu.cn/jsxsd/xsks/xsksap_list"
        
        # 发送POST请求获取页面内容
        payload={
            "xnxqid":f"{xnxqid}"
        }
        response = session.post(url,data=payload)
        
        # 使用BeautifulSoup解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找考试安排表格
        table = soup.find('table', id='dataList')
        logger.info("【考试安排数据】")
        
        # 初始化考试安排数据列表
        exam_data = []
        
        if table is None:
            logger.info("未找到考试安排表格")
            return exam_data
        
        # 获取所有行（跳过表头）
        rows = table.find_all('tr')[1:]  # 跳过第一行表头
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            
            if len(cells) < 10:  # 确保有足够的列
                continue
            
            # 获取原始课程名称文本
            course_name_cell = cells[3]
            course_name_text = course_name_cell.get_text(strip=True)
            
            # 跳过空行或无效数据
            if not course_name_text or course_name_text == '&nbsp;':
                continue
            
            # 解析课程名称和教师信息
            course_info = self._parse_exam_course_info(course_name_text, course_name_cell)
            
            # 解析考试信息
            exam_info = {
                '序号': cells[0].get_text(strip=True),
                '考试场次': cells[1].get_text(strip=True),
                '课程编号': cells[2].get_text(strip=True),
                '课程名称': course_info.get('课程名', course_name_text),
                '教师': course_info.get('教师', ''),
                '考试时间': cells[4].get_text(strip=True),
                '考场': cells[5].get_text(strip=True),
                '座位号': cells[6].get_text(strip=True),
                '准考证号': cells[7].get_text(strip=True),
                '备注': cells[8].get_text(strip=True)
            }
            
            exam_data.append(exam_info)
        
        # 打印考试安排统计信息
        logger.info(f"共解析到 {len(exam_data)} 门考试")
        
        # 打印考试详细信息
        for exam in exam_data:
            teacher_info = f" | 教师：{exam.get('教师', 'N/A')}" if exam.get('教师') else ""
            logger.info(f"考试：{exam.get('课程名称', 'N/A')}{teacher_info} | 时间：{exam.get('考试时间', 'N/A')} | 考场：{exam.get('考场', 'N/A')} | 座位号：{exam.get('座位号', 'N/A')}")
        
        return exam_data
    
    def _parse_exam_course_info(self, course_text, cell_element):
        """
        解析考试课程信息，提取课程名称和教师信息
        :param course_text: 课程文本内容
        :param cell_element: 单元格元素，用于提取更详细的信息
        :return: 课程信息字典
        """
        course_info = {}
        
        # 按行分割文本
        lines = [line.strip() for line in course_text.split('\n') if line.strip()]
        
        if not lines:
            return {'课程名': course_text, '教师': ''}
        
        # 第一行通常是课程名称
        course_info['课程名'] = lines[0]
        
        # 解析其他信息
        for line in lines[1:]:
            # 如果不包含常见的非教师信息关键词，可能是教师姓名
            if not any(keyword in line for keyword in ['周', '楼', '室', '班', '级', '节', '考试', '时间', '地点']):
                course_info['教师'] = line
                break
        
        # 尝试从cell的font标签中提取更详细信息
        fonts = cell_element.find_all('font')
        for font in fonts:
            title = font.get('title', '')
            text = font.get_text(strip=True)
            
            if title == '老师' or title == '教师':
                course_info['教师'] = text
                break
        
        # 如果仍然没有找到教师信息，尝试其他方法
        if '教师' not in course_info and len(lines) > 1:
            # 查找可能的教师姓名（通常在课程名后面）
            potential_teacher = lines[1]
            # 如果不包含常见的非教师信息关键词，可能是教师姓名
            if not any(keyword in potential_teacher for keyword in ['考试', '时间', '地点', '周', '楼', '室', '班', '级', '节']):
                course_info['教师'] = potential_teacher
        
        # 确保返回的课程名不为空
        if not course_info.get('课程名'):
            course_info['课程名'] = course_text
        
        # 确保教师字段存在
        if '教师' not in course_info:
            course_info['教师'] = ''
        
        return course_info