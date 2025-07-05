# file:qiqi/grades.py
import json
from typing import List, Dict, Any, Optional
from client import NetworkRequest

def fetch_grades(client: NetworkRequest) -> Optional[List[Dict[str, Any]]]:
    """
    使用已认证的客户端获取成绩信息。

    Args:
        client: 一个已经通过认证的 NetworkRequest 实例。

    Returns:
        一个包含成绩信息的列表，如果失败则返回 None。
    """
    try:
        print("\n正在获取成绩信息...")
        response = client.post("/grade/get", json_data={})

        if response:
            print("成绩获取成功！")
            courses = []
            for item in response:
                course_info = {
                    "ID": item['id'],
                    "学年": item['academicYear'],
                    "学期": item['semester'],
                    "课程名称": item['courseName'],
                    "课程代码": item['courseCode'],
                    "学分": item['credit'],
                    "成绩": item['score'],
                    "绩点": item['gpa'],
                    "课程类型": item['type']
                }
                courses.append(course_info)
        else:
            error_message = response.get("message", "未知错误")
            print(f"获取成绩失败: {error_message}")
        return response

    except Exception as e:
        print(f"获取成绩时发生错误: {e}")
        return None