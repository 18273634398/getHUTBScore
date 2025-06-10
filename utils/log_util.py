import logging
import os
from logging.handlers import RotatingFileHandler
# 绑定绑定句柄到logger对象
logger = logging.getLogger(__name__)
# 获取当前⼯具⽂件所在的路径
root_path = os.path.dirname(os.path.abspath(__file__))
# 拼接当前要输出⽇志的路径
log_dir_path = os.sep.join([root_path, '..', f'/logs'])
if not os.path.isdir(log_dir_path):
    os.mkdir(log_dir_path)
# 创建⽇志记录器，指明⽇志保存路径,每个⽇志的⼤⼩，保存⽇志的上限
file_log_handler = RotatingFileHandler(os.sep.join([log_dir_path, 'log.txt']),
                                       maxBytes=1024 * 1024, backupCount=10 , encoding="utf-8")
# 设置⽇志的格式
date_string = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s]/[line: %(lineno)d]/[%(funcName)s] %(message)s ', date_string)
# ⽇志输出到控制台的句柄
stream_handler = logging.StreamHandler()
# 将⽇志记录器指定⽇志的格式
file_log_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
# 为全局的⽇志⼯具对象添加⽇志记录器
# 绑定绑定句柄到logger对象
logger.addHandler(stream_handler)
logger.addHandler(file_log_handler)
# 设置⽇志输出级别
logger.setLevel(level=logging.INFO)