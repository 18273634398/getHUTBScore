# file: main.py

# 假设这些模块是你已有的，保持不变
from client import NetworkRequest
from auth import perform_login,get_captcha
from grades import fetch_grades

use_history = True

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw # ### MODIFIED ###: 增加了 ImageDraw 用于创建默认图片
import os
from tkinter import ttk
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from tkinter import font as tkFont # ### NEW ###: 导入字体模块

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

CONFIG_FILE = "config.json"

# ### NEW ###: 函数用于创建占位图片，如果图片文件不存在
def create_placeholder_images():
    # 创建背景图
    if not os.path.exists("./img/background.png"):
        try:
            img = Image.new('RGB', (800, 600), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            d.rectangle([(200, 150), (600, 450)], fill=(10, 50, 80), outline=None)
            img = img.resize((480, 350), Image.LANCZOS)
            img.save("./img/background.png")
            print("Created placeholder background.png")
        except Exception as e:
            print(f"无法创建背景图片: {e}")

    # 创建头像
    if not os.path.exists("./img/avatar.png"):
        try:
            img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            # 在白色背景上画一个简单的logo
            draw.ellipse((0, 0, 99, 99), fill='white', outline='lightgray', width=2)
            draw.text((30, 35), "hutb", fill="cornflowerblue", font=ImageFont.load_default(size=24))
            img.save("./img/avatar.png")
            print("Created placeholder avatar.png")
        except Exception as e:
            # 如果Pillow字体失败，则使用更简单的方法
            try:
                img = Image.new('RGB', (100, 100), color = 'white')
                draw = ImageDraw.Draw(img)
                draw.ellipse((5, 5, 95, 95), fill='cornflowerblue')
                img.save("./img/avatar.png")
                print("Created simple placeholder avatar.png")
            except Exception as e2:
                print(f"无法创建头像图片: {e2}")

# ### CLASS MODIFIED ###: 下面是重构后的 LoginWindow 类
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("登录 - HUTB 成绩查询系统")
        # 调整窗口大小以适应新布局
        master.geometry("1280x840") 
        master.resizable(False, False)

        # --- 样式定义 ---
        self.font_normal = tkFont.Font(family="Microsoft YaHei", size=10)
        self.font_button = tkFont.Font(family="Microsoft YaHei", size=11, weight="bold")
        self.login_button_bg = "#0078D7"
        self.login_button_fg = "white"

        self.api_client = None

        # --- 背景图片 ---
        try:
            self.bg_image = Image.open("./img/background.png")
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(master, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            master.config(bg="#E0E0E0") # 如果图片不存在，设置一个备用背景色
            print("警告: background.png 未找到。")
        except Exception as e:
            master.config(bg="#E0E0E0")
            print(f"加载背景图时出错: {e}")

        # --- 中心登录框架 ---
        # 使用 place 将此框架居中
        login_frame = tk.Frame(master, bg="white", bd=2, relief=tk.GROOVE)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=320, height=380)

        # 在中心框架内部使用 grid 布局
        # --- 头像 ---
        try:
            self.avatar_image = Image.open("./img/avatar.png").resize((80, 80), Image.LANCZOS)
            self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)
            avatar_label = tk.Label(login_frame, image=self.avatar_photo, bg="white")
            avatar_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))
        except FileNotFoundError:
            print("警告: avatar.png 未找到。")
        except Exception as e:
            print(f"加载头像时出错: {e}")

        # --- 账号 ---
        tk.Label(login_frame, text="账号:", font=self.font_normal, bg="white").grid(row=1, column=0, columnspan=2, sticky="w", padx=30)
        self.entry_account = ttk.Entry(login_frame, font=self.font_normal, width=30)
        self.entry_account.grid(row=2, column=0, columnspan=2, padx=30, pady=(0, 10), ipady=4)

        # --- 密码 ---
        tk.Label(login_frame, text="密码:", font=self.font_normal, bg="white").grid(row=3, column=0, columnspan=2, sticky="w", padx=30)
        self.entry_password = ttk.Entry(login_frame, show="*", font=self.font_normal, width=30)
        self.entry_password.grid(row=4, column=0, columnspan=2, padx=30, pady=(0, 5), ipady=4)

        # --- 保存密码 & 刷新验证码 ---
        # 使用一个新的框架来容纳复选框和刷新按钮，使它们在同一行
        options_frame = tk.Frame(login_frame, bg="white")
        options_frame.grid(row=5, column=0, columnspan=2, padx=30, pady=0, sticky="ew")

        self.save_password_var = tk.BooleanVar()
        self.check_save_password = tk.Checkbutton(options_frame, text="保存密码", variable=self.save_password_var, font=self.font_normal, bg="white")
        self.check_save_password.pack(side=tk.LEFT)
        
        # 将刷新按钮放在这里，看起来更像一个链接
        self.btn_get_captcha = tk.Button(options_frame, text="刷新验证码", command=self.get_captcha_gui, 
                                         relief=tk.FLAT, fg="gray", font=self.font_normal, bg="white", cursor="hand2")
        self.btn_get_captcha.pack(side=tk.RIGHT)

        # --- 验证码 ---
        captcha_frame = tk.Frame(login_frame, bg="white")
        captcha_frame.grid(row=6, column=0, columnspan=2, padx=30, pady=5)
        
        self.captcha_image_label = tk.Label(captcha_frame, bg="white")
        self.captcha_image_label.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_captcha = ttk.Entry(captcha_frame, font=self.font_normal, width=12)
        self.entry_captcha.pack(side=tk.LEFT, ipady=4)
        # 绑定回车键进行登录
        self.entry_captcha.bind("<Return>", self.login_gui)

        # --- 登录按钮 ---
        self.btn_login = tk.Button(login_frame, text="登 录", command=self.login_gui,
                                   font=self.font_button, bg=self.login_button_bg, fg=self.login_button_fg,
                                   relief=tk.FLAT, cursor="hand2")
        self.btn_login.grid(row=7, column=0, columnspan=2, sticky="ew", padx=30, pady=(10, 15), ipady=5)

        self.load_saved_credentials()
        self.initialize_client()

    def load_saved_credentials(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.entry_account.insert(0, config.get("account", ""))
                    self.entry_password.insert(0, config.get("password", ""))
                    self.save_password_var.set(config.get("save_password", False))
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def save_credentials(self):
        if self.save_password_var.get():
            config = {
                "account": self.entry_account.get(),
                "password": self.entry_password.get(),
                "save_password": True
            }
            try:
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
            except Exception as e:
                print(f"保存配置文件失败: {e}")
        else:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

    def initialize_client(self):
        base_url = "http://122.152.213.95:9893"
        initial_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTg4LCJpYXQiOjE3NTE3MDU4NDYsImV4cCI6MTc1MjMxMDY0Nn0.gPafpz3MVZpVJDtvlqrie4UBm4Ygjc9BLq04RsIh9fQ"
        common_headers = {
            "authorization": f"Bearer {initial_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Origin": "http://jw.qiqi.pro",
            "Referer": "http://jw.qiqi.pro/"
        }
        self.api_client = NetworkRequest(base_url=base_url, headers=common_headers)
        self.get_captcha_gui()

    def get_captcha_gui(self):
        if get_captcha(self.api_client):
            captcha_path = "./captcha.png" # 请确保这个路径是正确的
            if os.path.exists(captcha_path):
                try:
                    img = Image.open(captcha_path)
                    img = img.resize((120, 40), Image.LANCZOS) # ### MODIFIED ### 调整尺寸以适应新布局
                    self.captcha_photo = ImageTk.PhotoImage(img)
                    self.captcha_image_label.config(image=self.captcha_photo)
                except Exception as e:
                    messagebox.showerror("错误", f"加载验证码图片失败: {e}")
            else:
                messagebox.showerror("错误", "验证码图片未找到！")
        else:
            messagebox.showerror("错误", "获取验证码失败！")

    # ### MODIFIED ###: 接受一个可选的 event 参数，以支持回车键登录
    def login_gui(self, event=None): 
        account = self.entry_account.get()
        password = self.entry_password.get()
        captcha_code = self.entry_captcha.get()

        if not account or not password or not captcha_code:
            messagebox.showwarning("警告", "账号、密码和验证码不能为空！")
            return

        login_successful = perform_login(self.api_client, account, password, captcha_code)

        if login_successful:
            self.save_credentials()
            self.master.destroy()
            grades_root = tk.Tk()
            GradesWindow(grades_root, self.api_client)
            grades_root.mainloop()
        else:
            messagebox.showerror("失败", "登录失败，请检查账号、密码或验证码！")
            self.get_captcha_gui()
            # 清空验证码输入框并使其获得焦点
            self.entry_captcha.delete(0, tk.END)
            self.entry_captcha.focus_set()


# GradesWindow 类保持不变
class GradesWindow:
    def __init__(self, master, api_client):
        self.master = master
        self.api_client = api_client
        master.title("成绩单 - HUTB 成绩查询系统")
        master.geometry("800x600")

        self.all_grades = []
        self.current_grades = []
        self.semester_grades = []

        # Top frame for controls
        top_frame = tk.Frame(master)
        top_frame.pack(pady=10, padx=10, fill=tk.X)

        # Semester selection
        self.semester_label = tk.Label(top_frame, text="选择学期:")
        self.semester_label.pack(side=tk.LEFT, padx=(0, 5))
        self.semester_combobox = ttk.Combobox(top_frame, state="readonly")
        self.semester_combobox.pack(side=tk.LEFT, padx=5)
        self.semester_combobox.bind("<<ComboboxSelected>>", self.filter_by_semester)

        # Search box
        self.search_label = tk.Label(top_frame, text="搜索课程:")
        self.search_label.pack(side=tk.LEFT, padx=(20, 5))
        self.search_entry = tk.Entry(top_frame)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind("<Return>", self.search_courses)

        # Grades table
        self.tree = ttk.Treeview(master, columns=("courseName", "score", "credit", "gpa", "academicYear", "semester"), show="headings")
        self.tree.heading("courseName", text="课程名称", command=lambda: self.sort_column("courseName", False))
        self.tree.heading("score", text="成绩", command=lambda: self.sort_column("score", False))
        self.tree.heading("credit", text="学分", command=lambda: self.sort_column("credit", False))
        self.tree.heading("gpa", text="绩点", command=lambda: self.sort_column("gpa", False))
        self.tree.heading("academicYear", text="学年", command=lambda: self.sort_column("academicYear", False))
        self.tree.heading("semester", text="学期", command=lambda: self.sort_column("semester", False))
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Stats and Chart
        bottom_frame = tk.Frame(master)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.stats_label = tk.Label(bottom_frame, text="统计信息:")
        self.stats_label.pack(anchor='w')

        self.chart_frame = tk.Frame(bottom_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fetch_grades()

    def fetch_grades(self):
        raw_grades = fetch_grades(self.api_client)
        if raw_grades is not None:
            self.all_grades = raw_grades
            self.semester_grades = self.all_grades
            self.current_grades = self.all_grades
            self.populate_semester_filter()
            self.update_grades_display()
            self.update_stats_and_chart()
        else:
            messagebox.showerror("错误", "获取成绩失败！")
            self.master.destroy()

    def populate_semester_filter(self):
        unique_semesters = sorted(list(set((g['academicYear'], g['semester']) for g in self.all_grades)))
        self.semester_map = {}
        display_semesters = ["所有学期"]
        for i, (year, sem) in enumerate(unique_semesters):
            semester_number = i + 1
            self.semester_map[str(semester_number)] = (year, sem)
            display_semesters.append(f"第{semester_number}学期")
        self.semester_combobox['values'] = display_semesters
        self.semester_combobox.current(0)

    def filter_by_semester(self, event=None):
        selection = self.semester_combobox.get()
        if selection == "所有学期":
            self.semester_grades = self.all_grades
        else:
            semester_num_str = selection.replace('第', '').replace('学期', '')
            year, sem = self.semester_map.get(semester_num_str, (None, None))
            if year and sem:
                self.semester_grades = [g for g in self.all_grades if g['academicYear'] == year and g['semester'] == sem]
            else:
                self.semester_grades = []
        self.search_courses()

    def update_grades_display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for course in self.current_grades:
            self.tree.insert("", "end", values=(
                course.get("courseName", "N/A"),
                course.get("score", "N/A"),
                course.get("credit", "N/A"),
                course.get("gpa", "N/A"),
                course.get("academicYear", "N/A"),
                course.get("semester", "N/A")
            ))

    def sort_column(self, col, reverse):
        def sort_key(item):
            val = item[0]
            try:
                return float(val)
            except (ValueError, TypeError):
                return -1
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        data.sort(key=sort_key, reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def search_courses(self, event=None):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.current_grades = self.semester_grades
        else:
            self.current_grades = [c for c in self.semester_grades if search_term in c.get("courseName", "").lower()]
        self.update_grades_display()
        self.update_stats_and_chart()

    def update_stats_and_chart(self):
        if not self.current_grades:
            self.stats_label.config(text="统计信息: 无数据")
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            return

        total_credits = sum(float(c.get('credit', 0)) for c in self.current_grades)
        weighted_sum = 0
        valid_credits_for_avg = 0
        for c in self.current_grades:
            try:
                score = float(c.get('score'))
                credit = float(c.get('credit'))
                weighted_sum += score * credit
                valid_credits_for_avg += credit
            except (ValueError, TypeError):
                continue
        average_score = weighted_sum / valid_credits_for_avg if valid_credits_for_avg > 0 else 0
        self.stats_label.config(text=f"总学分: {total_credits:.2f}  |  加权平均分: {average_score:.2f}")

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        scores = []
        for c in self.current_grades:
            try:
                scores.append(float(c.get('score')))
            except (ValueError, TypeError):
                continue
        if scores:
            ax.hist(scores, bins=10, edgecolor='black')
            ax.set_title('成绩分布')
            ax.set_xlabel('分数')
            ax.set_ylabel('课程数')
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    # ### NEW ###: 在启动主窗口前创建占位图
    # 注意: 如果你已经有这些图片，可以注释掉这行
    try:
        from PIL import ImageFont # 尝试导入ImageFont
    except ImportError:
        print("Pillow ImageFont not found. Using basic image creation.")
        ImageFont = None
    create_placeholder_images()

    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()