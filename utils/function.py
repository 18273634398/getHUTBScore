from utils.log_util import logger
from utils.api.getScore import GetScore
from utils.api.getClassSchedule import GetClassSchedule
from utils.api.getExamSchedule import GetExamSchedule
from utils.api.autoJudge import AutoJudge
from utils.api.getCredits import GetCredits
class Function:
    function_list = [
        "1. 查询期末成绩",
        "2. 查询等级考试成绩",
        "3. 查询个人课表",
        "4. 查询所有教室上课信息",
        "5. 查询考试安排",
        "6. 自动评教",
        "7. 查询素拓学分",
        "8. 查询课程学分",
        "9. 退出"
    ]
    def get_functions(self):
        logger.info("""功能菜单:""")
        for i in self.function_list:
            logger.info(f"{i}")

    def function(self, function_id, session=None):
        try:
            function_id = int(function_id)
        except ValueError:
            logger.error(f"输入的功能编号 '{function_id}' 无效，请输入一个数字。")
            return None

        while function_id in range(1,self.function_list.__len__()+1):
            if function_id == 1:
                GetScore(session).get_score_final_exam()
            elif function_id == 2:
                GetScore(session).get_score_level_exam()
            elif function_id == 3:
                GetClassSchedule(session).get_class_schedule()
            elif function_id == 4:
                GetClassSchedule(session).get_all_class_schedule()
            elif function_id == 5:
                GetExamSchedule(session).get_exam_schedule()
            elif function_id == 6:
                AutoJudge(session).get_judge_status()
            elif function_id == 7:
                GetCredits(session).get_sutuo_credits()
            elif function_id == 8:
                GetCredits(session).get_study_credits()
            elif function_id == self.function_list.__len__():
                logger.info("欢迎下次使用！")
                return None
            try:
                function_id = int(input("请输入功能编号："))
            except ValueError:
                logger.error(f"输入的功能编号 '{function_id}' 无效，请输入一个数字。")
                return None
        else:
            logger.error(f"输入的功能编号 {function_id} 不存在！")
            return None



