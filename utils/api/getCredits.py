import json
import requests
from bs4 import BeautifulSoup
from utils.log_util import logger
from utils.api.base_api import BaseAPI

class GetCredits(BaseAPI):
    def __init__(self,session):
        super().__init__()
        self.session = session

    def get_study_credits(self):
        credits_url = f"{self.base_url}/sxsd/xxwcqk/xxwcqkOnkclb.do"
        payload = {
            'ndzydm':'BE870C388E8C435282C66AB5C0A4C301'
        }
        try:
            res = self.session.post(credits_url, data=payload)
            logger.info(res.text)
            res.raise_for_status() # 如果请求失败则引发HTTPError
            soup = BeautifulSoup(res.text, 'html.parser')
            
            study_data = {
                'category_summary': [],  # 课程类别汇总
                'course_details': []     # 课程详细信息
            }
            
            # 查找所有表格
            tables = soup.find_all('table', class_='Nsb_r_list Nsb_table')
            
            if len(tables) >= 1:
                # 解析第一个表格：课程类别汇总
                summary_table = tables[0]
                for row in summary_table.find_all('tr')[1:]:  # 跳过表头
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        category = cols[0].text.strip()
                        completed_credits = cols[1].text.strip()
                        current_credits = cols[2].text.strip()
                        
                        # 跳过总计行和空行
                        if category and category != '总计' and not category.startswith('&nbsp;'):
                            completed_credits_val = 0.0
                            current_credits_val = 0.0
                            try:
                                if completed_credits:
                                    completed_credits_val = float(completed_credits)
                            except ValueError:
                                logger.warning(f"类别 '{category}' 的已修学分 '{completed_credits}' 不是有效数字，将使用0.0。")
                            
                            try:
                                if current_credits:
                                    current_credits_val = float(current_credits)
                            except ValueError:
                                logger.warning(f"类别 '{category}' 的正修读学分 '{current_credits}' 不是有效数字，将使用0.0。")

                            category_info = {
                                'category': category,
                                'completed_credits': completed_credits_val,
                                'current_credits': current_credits_val
                            }
                            study_data['category_summary'].append(category_info)
            
            if len(tables) >= 2:
                # 解析第二个表格：课程详细信息
                detail_table = tables[1]
                current_category = None
                
                for row in detail_table.find_all('tr')[1:]:  # 跳过表头
                    cols = row.find_all('td')
                    
                    # 检查是否是类别标题行
                    # 一个类别标题行通常有一个td，colspan="7"，并且包含一个<b>标签
                    if len(cols) == 1 and cols[0].get('colspan') == '7':
                        b_tag = cols[0].find('b')
                        if b_tag:
                            category_text = b_tag.text.strip()
                            if category_text and not category_text.startswith('&nbsp;'):
                                current_category = category_text
                            continue # 处理完类别标题行后，跳到下一行
                    
                    # 解析课程详细信息行 (如果不是类别标题行)
                    
                    # 解析课程详细信息行
                    if len(cols) >= 7 and current_category:
                        course_code = cols[0].text.strip()
                        course_name = cols[1].text.strip()
                        credits = cols[2].text.strip()
                        category = cols[3].text.strip()
                        nature = cols[4].text.strip()
                        grade = cols[5].text.strip()
                        remarks = cols[6].text.strip() if len(cols) > 6 else ''
                        
                        # 跳过空行
                        if course_code and course_name and not course_code.startswith('&nbsp;'):
                            credits_val = 0.0
                            try:
                                if credits: # 确保credits非空
                                    credits_val = float(credits)
                            except ValueError:
                                logger.warning(f"课程 '{course_name}' (代码: {course_code}) 的学分 '{credits}' 不是有效的数字，将使用0.0。")
                            
                            course_info = {
                                'course_code': course_code,
                                'course_name': course_name,
                                'credits': credits_val,
                                'category': category, # 这是 cols[3].text.strip()
                                'nature': nature,
                                'grade': grade,
                                'remarks': remarks
                            }
                            study_data['course_details'].append(course_info)
            
            if not study_data['category_summary'] and not study_data['course_details']:
                logger.info("未查询到学习完成情况数据。")
            else:
                logger.info(f"成功获取到 {len(study_data['category_summary'])} 个课程类别汇总信息。")
                logger.info(f"成功获取到 {len(study_data['course_details'])} 个课程详细信息。")
                
                # 打印部分信息以供调试
                for category in study_data['category_summary']:
                    logger.info(f"课程类别: {category['category']}, 已修学分: {category['completed_credits']}, 正修读学分: {category['current_credits']}")
            
            return study_data

        except requests.exceptions.RequestException as e:
            logger.error(f"请求学习完成情况数据时发生错误: {e}")
            return {'category_summary': [], 'course_details': []}
        except Exception as e:
            logger.error(f"处理学习完成情况数据时发生未知错误: {e}")
            return {'category_summary': [], 'course_details': []}


    def get_sutuo_credits(self):
        credits_url = f"{self.base_url}/jsxsd/syjx/getJsonList.do"
        payload = {
            'id': ''
        }
        try:
            res = self.session.post(credits_url, data=payload)
            res.raise_for_status() # 如果请求失败则引发HTTPError
            data = res.json() # 解析JSON响应

            projects = []
            if 'datZ' in data and data['datZ']:
                # 跳过第一个 'start' 元素
                for item_data in data['datZ']:
                    if isinstance(item_data, list) and len(item_data) >= 10:
                        if item_data[0] == 'start': # 有时 'start' 可能不是第一个元素
                            continue
                        project = {
                            'id': item_data[0],
                            'content_level': item_data[2],  # 内容/等级
                            'credits': item_data[3],        # 学分
                            'class': item_data[5],          # 班级
                            'project_name': item_data[7],   # 项目名称
                            'audit_status': item_data[6],   # 审核状态
                            'audit_remarks': item_data[8] if item_data[8] is not None else '', # 审核备注
                            'audit_status_id': item_data[9]
                        }
                        projects.append(project)
            
            if not projects:
                logger.info("未查询到素质拓展学分项目数据。")
            else:
                logger.info(f"成功获取到 {len(projects)} 个素质拓展项目信息。")
                # 打印部分信息以供调试
                # for p in projects:
                #     logger.info(f"项目名称: {p['project_name']}, 学分: {p['credits']}, 状态: {p['audit_status']}")
            return projects

        except requests.exceptions.RequestException as e: # requests 需要导入
            logger.error(f"请求素质拓展学分数据时发生错误: {e}")
            return []
        except json.JSONDecodeError:
            logger.error("解析素质拓展学分JSON数据失败。收到的内容非JSON格式或已损坏。")
            # logger.debug(f"原始响应文本: {res.text[:500]}...") # res 可能未定义，如果json解析失败
            return []
        except Exception as e:
            logger.error(f"处理素质拓展学分数据时发生未知错误: {e}")
            return []

