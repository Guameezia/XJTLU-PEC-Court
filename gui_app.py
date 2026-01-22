"""
场地预订GUI应用程序
提供友好的图形界面来配置和运行场地预订脚本
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
import threading
import time
from court_reservation import CourtReservation


class CourtReservationGUI:
    """场地预订GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("场地预订助手")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # 运行状态
        self.is_running = False
        self.reservation_thread = None
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🏸🎾 场地预订助手", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 场地类型选择
        ttk.Label(main_frame, text="场地类型：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.court_type_var = tk.StringVar(value="badminton")
        court_type_frame = ttk.Frame(main_frame)
        court_type_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(court_type_frame, text="羽毛球场", variable=self.court_type_var, 
                       value="badminton", command=self._on_court_type_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(court_type_frame, text="网球场", variable=self.court_type_var, 
                       value="tennis", command=self._on_court_type_change).pack(side=tk.LEFT, padx=5)
        
        # 场地选择
        ttk.Label(main_frame, text="选择场地：").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.court_var = tk.StringVar()
        self.court_combo = ttk.Combobox(main_frame, textvariable=self.court_var, state="readonly", width=20)
        self.court_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self._update_court_options()
        
        # 日期选择
        ttk.Label(main_frame, text="预订日期：").grid(row=3, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 日期输入（MM/DD格式）
        # 计算默认日期：当前日期 + 7天
        default_date = (datetime.now() + timedelta(days=7)).strftime("%m/%d")
        self.date_var = tk.StringVar(value=default_date)
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=10)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="格式：MM/DD").pack(side=tk.LEFT, padx=5)
        
        # 时间段选择
        ttk.Label(main_frame, text="选择时间段：").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.time_frame = ttk.Frame(main_frame)
        self.time_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 时间段复选框
        self.time_vars = {}
        self._update_time_options()
        
        # 触发时间
        ttk.Label(main_frame, text="触发时间：").grid(row=5, column=0, sticky=tk.W, pady=5)
        trigger_frame = ttk.Frame(main_frame)
        trigger_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        self.trigger_time_var = tk.StringVar(value="00:00:00")
        ttk.Entry(trigger_frame, textvariable=self.trigger_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(trigger_frame, text="格式：HH:MM:SS").pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始预订", command=self._start_reservation, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.login_ready_button = ttk.Button(button_frame, text="我已登录", command=self._on_login_ready, 
                                            state=tk.DISABLED, width=15)
        self.login_ready_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self._stop_reservation, 
                                      state=tk.DISABLED, width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 登录等待状态
        self.login_ready = False
        self.login_event = threading.Event()
        
        # 日志输出区域
        ttk.Label(main_frame, text="运行日志：").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70, state=tk.DISABLED)
        self.log_text.grid(row=8, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
    
    def _get_time_options(self):
        """根据场地类型获取可用时间段"""
        # 所有时间段：08:00 到 20:00（排除21:00）
        all_times = [f"{i:02d}:00" for i in range(8, 21)]
        
        # 如果是羽毛球，还要排除08:00, 09:00, 12:00
        if self.court_type_var.get() == "badminton":
            excluded_times = ["08:00", "09:00", "12:00"]
            return [t for t in all_times if t not in excluded_times]
        
        return all_times
    
    def _update_time_options(self):
        """更新时间选项复选框"""
        # 清除现有的复选框
        for widget in self.time_frame.winfo_children():
            widget.destroy()
        self.time_vars.clear()
        
        # 根据场地类型生成新的时间选项
        time_options = self._get_time_options()
        for i, time_option in enumerate(time_options):
            var = tk.BooleanVar()
            self.time_vars[time_option] = var
            ttk.Checkbutton(self.time_frame, text=time_option, variable=var).grid(
                row=i // 7, column=i % 7, sticky=tk.W, padx=2, pady=2
            )
    
    def _on_court_type_change(self):
        """场地类型改变时的回调"""
        self._update_court_options()
        self._update_time_options()
    
    def _update_court_options(self):
        """更新场地选项"""
        court_type = self.court_type_var.get()
        if court_type == "tennis":
            courts = CourtReservation.TENNIS_COURTS
        else:
            courts = CourtReservation.BADMINTON_COURTS
        
        self.court_combo['values'] = courts
        if courts:
            self.court_var.set(courts[0])
    
    def _log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def _validate_inputs(self):
        """验证输入"""
        if not self.court_var.get():
            messagebox.showerror("错误", "请选择场地")
            return False
        
        if not self.date_var.get():
            messagebox.showerror("错误", "请输入预订日期")
            return False
        
        # 验证日期格式
        try:
            date_str = self.date_var.get()
            parts = date_str.split("/")
            if len(parts) != 2:
                raise ValueError
            month, day = int(parts[0]), int(parts[1])
            if not (1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError
        except:
            messagebox.showerror("错误", "日期格式错误，请使用 MM/DD 格式，如 01/22")
            return False
        
        # 检查是否选择了时间段
        selected_times = [time for time, var in self.time_vars.items() if var.get()]
        if not selected_times:
            messagebox.showerror("错误", "请至少选择一个时间段")
            return False
        
        # 验证触发时间格式
        try:
            trigger_time = self.trigger_time_var.get()
            datetime.strptime(trigger_time, "%H:%M:%S")
        except:
            messagebox.showerror("错误", "触发时间格式错误，请使用 HH:MM:SS 格式")
            return False
        
        return True
    
    def _start_reservation(self):
        """开始预订"""
        if not self._validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("警告", "预订任务正在运行中")
            return
        
        # 获取配置
        court_type = self.court_type_var.get()
        court_name = self.court_var.get()
        target_date = self.date_var.get()
        selected_times = sorted([time for time, var in self.time_vars.items() if var.get()])
        trigger_time = self.trigger_time_var.get()
        
        # 更新UI状态
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 显示配置信息
        self._log("=" * 50)
        self._log(f"场地类型：{'网球场' if court_type == 'tennis' else '羽毛球场'}")
        self._log(f"选择场地：{court_name}")
        self._log(f"预订日期：{target_date}")
        self._log(f"时间段：{', '.join(selected_times)}")
        self._log(f"触发时间：{trigger_time}")
        self._log("=" * 50)
        
        # 在新线程中运行预订任务
        def run_reservation():
            try:
                reservation = CourtReservation(
                    court_type=court_type,
                    court_name=court_name,
                    target_date=target_date,
                    target_times=selected_times,
                    trigger_time=trigger_time,
                    status_callback=self._log
                )
                # 初始化驱动并打开页面
                reservation._init_driver()
                reservation.driver.get(reservation.reserve_url)
                self._log("✅ 页面已打开，请手动登录")
                
                # 启用"我已登录"按钮
                self.root.after(0, lambda: self.login_ready_button.config(state=tk.NORMAL))
                
                # 等待用户点击"我已登录"按钮
                self._log("⏳ 等待登录中...（请在浏览器中完成登录后点击'我已登录'按钮）")
                self.login_event.clear()
                self.login_event.wait()  # 等待用户点击按钮
                
                # 继续执行预订流程
                self._log("✅ 继续执行预订流程")
                reservation._wait_for_trigger_time()
                reservation._select_date()
                target_field_box = reservation._find_court()
                reservation._select_times(target_field_box)
                reservation._submit_order()
                self._log("✅ 预订流程完成，请手动完成支付")
                
            except Exception as e:
                self._log(f"❌ 预订过程出错：{str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                # 恢复UI状态
                self.root.after(0, self._on_reservation_finished)
                if hasattr(reservation, 'driver') and reservation.driver:
                    time.sleep(3)
                    reservation.driver.quit()
        
        self.reservation_thread = threading.Thread(target=run_reservation, daemon=True)
        self.reservation_thread.start()
    
    def _on_login_ready(self):
        """用户点击"我已登录"按钮"""
        if not self.is_running:
            return
        
        self.login_ready = True
        self.login_event.set()  # 通知等待线程继续
        self.login_ready_button.config(state=tk.DISABLED)
        self._log("✅ 已确认登录，继续执行预订")
    
    def _stop_reservation(self):
        """停止预订"""
        if not self.is_running:
            return
        
        self._log("⚠️ 用户请求停止预订")
        self.is_running = False
        self.login_event.set()  # 如果正在等待登录，也唤醒线程
        # 注意：Selenium的driver无法直接中断，这里只是标记状态
        self._on_reservation_finished()
    
    def _on_reservation_finished(self):
        """预订完成后的回调"""
        self.is_running = False
        self.login_ready = False
        self.start_button.config(state=tk.NORMAL)
        self.login_ready_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self._log("✅ 预订任务已结束")


def main():
    """主函数"""
    root = tk.Tk()
    app = CourtReservationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
