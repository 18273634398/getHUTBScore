from bs4 import BeautifulSoup
from utils.log_util import logger
from utils.api.base_api import BaseAPI

class GetClassSchedule(BaseAPI):
    def get_class_schedule(self, session):
        """
        获取课程表信息
        :param session: 会话对象
        :return: 课程表数据列表
        """
        url = "http://jwgl.hutb.edu.cn/jsxsd/xskb/xskb_list.do"

        
        # 发送GET请求获取页面内容
        response = session.get(url)
        # 使用BeautifulSoup解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找课程表表格
        table = soup.find('table', id='kbtable')
        logger.info("【课程表数据】")
        
        # 初始化课程表数据列表
        schedule_data = []
        
        if table is None:
            logger.info("未找到课程表表格")
            return schedule_data
        
        # 定义星期映射
        weekdays = ['', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        
        # 定义节次映射
        periods = {
            '0102节': '第1-2节',
            '0304节': '第3-4节', 
            '0506节': '第5-6节',
            '0708节': '第7-8节',
            '0910节': '第9-10节',
            '1112节': '第11-12节'
        }
        
        # 获取所有行（跳过表头）
        rows = table.find_all('tr')[1:]  # 跳过第一行表头
        
        for row_index, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            
            if len(cells) < 8:  # 确保有足够的列
                continue
                
            # 获取节次信息
            period_cell = cells[0].get_text(strip=True)
            period_name = periods.get(period_cell, period_cell)
            
            # 遍历每一天的课程（从第2列开始，共7天）
            for day_index in range(1, 8):
                if day_index < len(cells):
                    cell = cells[day_index]
                    
                    # 查找课程内容div（class="kbcontent1"显示简要信息，class="kbcontent"显示详细信息）
                    course_divs = cell.find_all('div', class_= 'kbcontent')
                    
                    for div in course_divs:
                        course_text = div.get_text(strip=True)
                        
                        # 跳过空课程
                        if not course_text or course_text == '&nbsp;':
                            continue
                            
                        # 解析课程信息
                        course_info = self._parse_course_info(course_text, div)
                        
                        if course_info:
                            course_info.update({
                                '星期': weekdays[day_index],
                                '节次': period_name,
                                '星期索引': day_index,
                                '节次索引': row_index + 1
                            })
                            schedule_data.append(course_info)
        
        # 打印课程表统计信息
        logger.info(f"共解析到 {len(schedule_data)} 门课程")
        
        # 打印课程详细信息
        for course in schedule_data:
            index = course.get('课程名').find(course.get('教师'))
            logger.info(f"课程：{course.get('课程名', 'N/A')[:index]} | {course.get('星期', 'N/A')} {course.get('节次', 'N/A')} | 教室：{course.get('教室', 'N/A')} | 教师：{course.get('教师', 'N/A')}")
        
        return schedule_data

    def _parse_course_info(self, course_text, div_element):
        """
        解析课程信息
        :param course_text: 课程文本内容
        :param div_element: div元素，用于提取更详细的信息
        :return: 课程信息字典
        """
        course_info = {}

        # 按行分割文本
        lines = [line.strip() for line in course_text.split('\n') if line.strip()]

        if not lines:
            return None

        # 第一行通常是课程名称
        course_info['课程名'] = lines[0]

        # 解析其他信息
        for line in lines[1:]:
            if '周' in line and ('(' in line or '（' in line):
                course_info['周次'] = line
            elif any(keyword in line for keyword in ['楼', '室', '厅', '馆']):
                course_info['教室'] = line
            elif any(keyword in line for keyword in ['班', '级']):
                course_info['班级'] = line
            elif '[' in line and ']' in line and '节' in line:
                course_info['具体节次'] = line

        # 尝试从div的font标签中提取更详细信息
        fonts = div_element.find_all('font')
        for font in fonts:
            title = font.get('title', '')
            text = font.get_text(strip=True)

            if title == '老师' or title == '教师':
                course_info['教师'] = text
            elif title == '周次(节次)':
                course_info['周次'] = text
            elif title == '教室':
                course_info['教室'] = text
            elif title == '班级':
                course_info['班级'] = text

        # 如果没有找到教师信息，尝试从文本中提取
        if '教师' not in course_info:
            # 查找可能的教师姓名（通常在课程名后面，用逗号分隔）
            if len(lines) > 1:
                potential_teacher = lines[1]
                # 如果不包含常见的非教师信息关键词，可能是教师姓名
                if not any(keyword in potential_teacher for keyword in ['周', '楼', '室', '班', '级', '节']):
                    course_info['教师'] = potential_teacher

        return course_info if course_info.get('课程名') else None

    
    def get_all_class_schedule(self, session,skyx=None,xqid=None,jzwid=None,xnxqh='2024-2025-2'):
        """
        获取所有课程表信息
        :param session: 会话对象
        :return: 按照['教学楼']['教室'][星期][节次]格式的包含所有课程表数据的数组
        """
        logger.info("【获取所有课程表数据】")
        url = "http://jwgl.hutb.edu.cn/jsxsd/kbcx/kbxx_classroom_ifr"
        payload={
            'xnxqh':xnxqh,
            'skyx':skyx, # 学院ID
            'xqid':xqid, # 校区ID
            'jzwid':jzwid #教学楼ID 
        }
        # 发送POST请求获取页面内容
        response = session.post(url,data=payload)
        logger.info("【所有课程表数据】")
        
        # 使用整合的解析函数
        all_schedule_data = self._parse_course_schedule(response.text)
        
        # 打印统计信息
        total_courses = 0
        for building in all_schedule_data:
            for classroom in all_schedule_data[building]:
                for day in range(7):
                    for period in range(6):
                        if all_schedule_data[building][classroom][day][period] is not None:
                            total_courses += 1
        
        logger.info(f"共解析到 {len(all_schedule_data)} 个教学楼，{total_courses} 门课程")
        
        # 打印详细课程信息
        for building in all_schedule_data:
            for classroom in all_schedule_data[building]:
                for day in range(7):
                    for period in range(6):
                        course = all_schedule_data[building][classroom][day][period]
                        if course:
                            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
                            periods = ['0102节', '0304节', '0506节', '0708节', '0910节', '1112节']
                            logger.info(f"课程：{course.get('课程名', 'N/A')} | 教师：{course.get('教师', 'N/A')} | 教室：{building}{classroom} | 时间：{weekdays[day]} {periods[period]} | 班级：{course.get('上课班级', 'N/A')}")
        
        return all_schedule_data
    
    def _parse_course_schedule(self, html_content):
        """
        解析课程表HTML，提取课程信息。

        Args:
            html_content (str): 包含课程表表格的HTML字符串。

        Returns:
            dict: 按照 {'教学楼': {'教室': [[课程信息_周一], [课程信息_周二], ..., [课程信息_周日]]}} 格式的字典。
                  每个 [课程信息_某天] 是一个列表，包含当天所有节次的课程，
                  节次索引 0 对应 "0102"，1 对应 "0304" 等。
                  课程信息是一个字典: {"课程名": "...", "教师": "...", "上课班级": "..."}
                  如果某时间段无课，则对应值为 None。
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        schedule_data = {}

        table = soup.find('table', id='kbtable')
        if not table:
            return {}

        rows = table.find_all('tr')

        # 每天有6个大节 (0102, 0304, 0506, 0708, 0910, 1112)
        sessions_count_per_day = 6
        days_count = 7 # 星期一到星期日

        # 从第三行开始是课程数据
        for row_idx, row in enumerate(rows[2:]):
            cells = row.find_all('td')
            if not cells:
                continue

            # 第一个单元格是教室信息
            classroom_full_name = cells[0].get_text(strip=True)
            if not classroom_full_name:
                continue

            # 解析教学楼和教室
            # 假设教学楼名称以 "楼" 结尾
            parts = classroom_full_name.split('楼', 1)
            if len(parts) == 2:
                building_name = parts[0] + '楼'
                classroom_name = parts[1]
            else: # 如果没有 "楼" 字，或者格式不符，可以将整个作为教室名，教学楼设为未知
                building_name = "未知教学楼"
                classroom_name = classroom_full_name

            # 为新的教学楼初始化
            if building_name not in schedule_data:
                schedule_data[building_name] = {}

            # 为新的教室初始化，每天的课程列表，默认为None
            # 结构: schedule_data[building_name][classroom_name] = [ [None, None, ... 6 times for Mon], [None, ... for Tue], ... ]
            if classroom_name not in schedule_data[building_name]:
                schedule_data[building_name][classroom_name] = [[None] * sessions_count_per_day for _ in range(days_count)]

            # 后面的单元格是课程信息，每6个单元格对应一天
            course_cells = cells[1:]
            for i, cell in enumerate(course_cells):
                day_index = i // sessions_count_per_day
                session_index = i % sessions_count_per_day

                # 确保不会超出7天的范围
                if day_index >= days_count:
                    continue

                course_div = cell.find('div', class_='kbcontent1')
                if course_div:
                    # 使用 get_text(separator='\n') 来处理 <br> 标签，然后分割
                    content_parts = [part.strip() for part in course_div.get_text(separator='\n').split('\n') if part.strip()]

                    if len(content_parts) >= 3:
                        course_name = content_parts[0]
                        # 教师信息可能包含姓名和周次，周次可能在下一行，也可能与姓名在同一行但由换行符分隔
                        # 简单合并第二行和第三行（如果它们看起来像教师和周次）
                        # 示例: "谭利娜\n(1-16周)" 已经在 content_parts[1] 中了
                        # 但有时原始HTML <br>可能在教师和周次之间，导致它们是 content_parts[1] 和 content_parts[2]
                        # 我们需要更智能地组合

                        teacher_info = content_parts[1]
                        class_info_start_index = 2

                        # 检查第二部分是否是周次信息 (如 "(1-16周)")
                        # 如果不是，并且有更多部分，则尝试将第二和第三部分合并为教师信息
                        if not content_parts[1].startswith('(') and len(content_parts) > 2 and content_parts[2].startswith('('):
                            teacher_info = f"{content_parts[1]} {content_parts[2]}" # 组合 教师姓名 和 (周次)
                            class_info_start_index = 3

                        # 剩余的部分是上课班级，可能有多行，用逗号连接
                        class_info_list = content_parts[class_info_start_index:]
                        class_info_str = ", ".join(filter(None, class_info_list))


                        course_details = {
                            "课程名": course_name,
                            "教师": teacher_info, # 这已经包含了姓名和周次
                            "上课班级": class_info_str
                        }
                        schedule_data[building_name][classroom_name][day_index][session_index] = course_details
                    elif len(content_parts) == 2: # 可能只有课程名和教师（无班级）或者教师和班级（无课程名）等不完整情况
                        # 假设是课程名和教师
                        course_details = {
                            "课程名": content_parts[0],
                            "教师": content_parts[1],
                            "上课班级": "未知班级"
                        }
                        schedule_data[building_name][classroom_name][day_index][session_index] = course_details
                    elif len(content_parts) == 1: # 只有课程名
                        course_details = {
                            "课程名": content_parts[0],
                            "教师": "未知教师",
                            "上课班级": "未知班级"
                        }
                        schedule_data[building_name][classroom_name][day_index][session_index] = course_details

                # else: 单元格为空或只有  ，保持为 None (已初始化)

        return schedule_data
    
    def _parse_all_course_text(self, course_text):
        """
        解析所有课程表中的课程文本信息
        :param course_text: 课程文本，如"数字图像处理及应用<br>谭利娜\n(1-16周)<br>\n物联2201"
        :return: 课程信息字典
        """
        # 替换<br>标签为换行符
        course_text = course_text.replace('<br>', '\n')
        
        # 按行分割
        lines = [line.strip() for line in course_text.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        course_info = {
            "课程名": lines[0],
            "教师": "",
            "上课班级": ""
        }
        
        # 解析教师和班级信息
        for i, line in enumerate(lines[1:], 1):
            # 如果包含周次信息（如"(1-16周)"），通常是教师信息的一部分
            if '周' in line and ('(' in line or '（' in line):
                if i == 1:  # 紧跟课程名的是教师信息
                    course_info["教师"] = lines[1] + line
                continue
            
            # 如果包含班级关键词
            if any(keyword in line for keyword in ['班', '级']):
                course_info["上课班级"] = line
            elif i == 1 and not course_info["教师"]:  # 第二行通常是教师
                course_info["教师"] = line
            elif i > 1 and not course_info["上课班级"] and not any(keyword in line for keyword in ['周']):
                course_info["上课班级"] = line
        
        return course_info if course_info.get('课程名') else None

    def _parse_classroom_info(self, classroom_full):
        """
        解析教室信息，提取教学楼和教室号
        :param classroom_full: 完整的教室信息，如"至诚楼B105*"
        :return: (教学楼, 教室号)
        """
        # 移除特殊字符
        classroom_clean = classroom_full.replace('*', '').replace('(智慧)', '').strip()
        
        # 查找楼字的位置
        building_end = -1
        for i, char in enumerate(classroom_clean):
            if char == '楼':
                building_end = i
                break
        
        if building_end == -1:
            return None, None
        
        building = classroom_clean[:building_end + 1]  # 包含"楼"字
        classroom = classroom_clean[building_end + 1:]  # 楼字后面的部分
        
        return building, classroom
    
    def _parse_course_text(self, course_text):
        """
        解析课程文本信息
        :param course_text: 课程文本，如"中国近现代史纲要<br>曹挹芬\n(1-16周)<br>\n环工2302班,计科2304"
        :return: 课程信息字典
        """
        # 替换<br>标签为换行符
        course_text = course_text.replace('<br>', '\n')
        
        # 按行分割
        lines = [line.strip() for line in course_text.split('\n') if line.strip()]
        
        if len(lines) < 3:
            return None
        
        course_info = {
            "课程名": lines[0],
            "教师": lines[1],
            "上课时间": lines[2] if len(lines) > 2 else "",
            "上课班级": lines[3] if len(lines) > 3 else ""
        }
        
        # 处理上课时间格式，移除括号
        if course_info["上课时间"]:
            course_info["上课时间"] = course_info["上课时间"].replace('(', '').replace(')', '').replace('（', '').replace('）', '')
        
        return course_info
