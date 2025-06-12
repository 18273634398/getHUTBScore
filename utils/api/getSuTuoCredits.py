import json
from utils.log_util import logger
from utils.api.base_api import BaseAPI # 导入 BaseAPI

class GetSuTuoCredits(BaseAPI): # 继承 BaseAPI
    def __init__(self,session):
        super().__init__() # 调用父类的 __init__ 方法
        self.session = session
        # self.base_url = "http://jwgl.hutb.edu.cn" # 此行不再需要，已从 BaseAPI 继承

    def get_credits(self):
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

