"""
场地预订GUI应用程序（框架版本）
提供友好的图形界面来配置和运行场地预订脚本

注意：这是展示版本，完整实现请通过 XJTLU 邮箱联系获取。
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
import threading
import time
# from court_reservation_public import CourtReservation


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
        
        # 提示信息
        info_label = ttk.Label(main_frame, 
                              text="⚠️ 这是展示版本，完整实现请通过 XJTLU 邮箱联系获取", 
                              foreground="orange")
        info_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 场地类型选择
        ttk.Label(main_frame, text="场地类型：").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.court_type_var = tk.StringVar(value="badminton")
        court_type_frame = ttk.Frame(main_frame)
        court_type_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(court_type_frame, text="羽毛球场", variable=self.court_type_var, 
                       value="badminton", command=self._on_court_type_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(court_type_frame, text="网球场", variable=self.court_type_var, 
                       value="tennis", command=self._on_court_type_change).pack(side=tk.LEFT, padx=5)
        
        # 场地选择
        ttk.Label(main_frame, text="选择场地：").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.court_var = tk.StringVar()
        self.court_combo = ttk.Combobox(main_frame, textvariable=self.court_var, state="readonly", width=20)
        self.court_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        self._update_court_options()
        
        # 日期选择
        ttk.Label(main_frame, text="预订日期：").grid(row=4, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 日期输入（MM/DD格式）
        default_date = (datetime.now() + timedelta(days=7)).strftime("%m/%d")
        self.date_var = tk.StringVar(value=default_date)
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=10)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="格式：MM/DD").pack(side=tk.LEFT, padx=5)
        
        # 时间段选择
        ttk.Label(main_frame, text="选择时间段：").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.time_frame = ttk.Frame(main_frame)
        self.time_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 时间段复选框
        self.time_vars = {}
        self._update_time_options()
        
        # 触发时间
        ttk.Label(main_frame, text="触发时间：").grid(row=6, column=0, sticky=tk.W, pady=5)
        trigger_frame = ttk.Frame(main_frame)
        trigger_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        self.trigger_time_var = tk.StringVar(value="00:00:00")
        ttk.Entry(trigger_frame, textvariable=self.trigger_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(trigger_frame, text="格式：HH:MM:SS").pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始预订", command=self._start_reservation, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 日志输出区域
        ttk.Label(main_frame, text="运行日志：").grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70, state=tk.DISABLED)
        self.log_text.grid(row=9, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
    
    def _get_time_options(self):
        """根据场地类型获取可用时间段"""
        all_times = [f"{i:02d}:00" for i in range(8, 21)]
        if self.court_type_var.get() == "badminton":
            excluded_times = ["08:00", "09:00", "12:00"]
            return [t for t in all_times if t not in excluded_times]
        return all_times
    
    def _update_time_options(self):
        """更新时间选项复选框"""
        for widget in self.time_frame.winfo_children():
            widget.destroy()
        self.time_vars.clear()
        
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
        # 完整实现请通过 XJTLU 邮箱联系获取
        pass
    
    def _log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def _start_reservation(self):
        """开始预订"""
        messagebox.showinfo("提示", "这是展示版本，完整实现请通过 XJTLU 邮箱联系获取")


def main():
    """主函数"""
    root = tk.Tk()
    app = CourtReservationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
