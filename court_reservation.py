"""
场地预订核心逻辑类
封装了网球场和羽毛球场的预订功能
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime, timedelta


class CourtReservation:
    """场地预订类"""
    
    # 场地配置
    TENNIS_COURTS = ["EB东网球场", "EB西网球场", "FB北网球场", "FB南网球场"]
    BADMINTON_COURTS = ["1号场", "2号场", "3号场", "4号场", "5号场", "6号场"]
    
    # URL配置
    TENNIS_URL = "https://sportscentre.xipueduinno.cn/website/court?serviceId=1003"
    BADMINTON_URL = "https://sportscentre.xipueduinno.cn/website/court?serviceId=1002"
    
    def __init__(self, court_type, court_name, target_date, target_times, trigger_time, status_callback=None):
        """
        初始化预订参数
        
        Args:
            court_type: "tennis" 或 "badminton"
            court_name: 场地名称
            target_date: 目标日期，格式 "MM/DD"
            target_times: 时间段列表，如 ["19:00", "20:00"]
            trigger_time: 触发时间，格式 "HH:MM:SS"
            status_callback: 状态回调函数，用于更新GUI状态
        """
        self.court_type = court_type
        self.court_name = court_name
        self.target_date = target_date
        self.target_times = target_times
        self.trigger_time = trigger_time
        self.status_callback = status_callback
        self.driver = None
        
        # 根据类型选择URL
        if court_type == "tennis":
            self.reserve_url = self.TENNIS_URL
        elif court_type == "badminton":
            self.reserve_url = self.BADMINTON_URL
        else:
            raise ValueError(f"不支持的场地类型: {court_type}")
    
    def _log(self, message):
        """记录日志，如果有回调函数则调用"""
        print(message)
        if self.status_callback:
            self.status_callback(message)
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument("--start-maximized")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Edge(options=edge_options)
        self.driver.implicitly_wait(3)
    
    def _wait_for_trigger_time(self):
        """等待触发时间"""
        self._log(f"⏰ 等待触发时间 {self.trigger_time}")
        
        # 解析触发时间
        trigger_hour, trigger_minute, trigger_second = map(int, self.trigger_time.split(":"))
        
        # 获取当前时间
        now = datetime.now()
        
        # 计算今天的触发时间
        target_time = now.replace(hour=trigger_hour, minute=trigger_minute, second=trigger_second, microsecond=0)
        
        # 如果今天的触发时间已经过了，就等到明天
        if target_time <= now:
            target_time += timedelta(days=1)
            self._log(f"⏰ 今天的触发时间已过，将等到明天 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self._log(f"⏰ 将等到今天 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 计算需要等待的秒数
        wait_seconds = (target_time - now).total_seconds()
        self._log(f"⏰ 需要等待 {wait_seconds:.1f} 秒（约 {wait_seconds/60:.1f} 分钟）")
        
        # 等待到目标时间
        time.sleep(wait_seconds)
        
        self.driver.refresh()
        self._log("✅ 页面已刷新")
    
    def _select_date(self):
        """选择日期"""
        date_elem = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//*[text()="{self.target_date}"]'))
        )
        self.driver.execute_script("arguments[0].click();", date_elem)
        self._log(f"✅ 已选择日期 {self.target_date}")
    
    def _find_court(self):
        """查找目标场地"""
        field_boxes = self.driver.find_elements(By.CLASS_NAME, "field-box")
        target_field_box = None
        for field_box in field_boxes:
            field_name = field_box.find_element(By.CLASS_NAME, "item-name").text
            if self.court_name in field_name:
                target_field_box = field_box
                self._log(f"✅ 找到场地：{field_name}")
                break
        
        if not target_field_box:
            raise Exception(f"❌ 未找到场地：{self.court_name}")
        
        return target_field_box
    
    def _select_times(self, target_field_box):
        """选择时间段"""
        # 获取时间索引映射
        time_items = self.driver.find_elements(By.XPATH, '//div[@class="time-line"]/div[@class="item"]')
        time_index_map = {item.text.strip(): i for i, item in enumerate(time_items)}
        self._log(f"📝 时间索引映射：{time_index_map}")
        
        # 批量点击目标时间段
        for target_time in self.target_times:
            if target_time not in time_index_map:
                raise Exception(f"❌ 时间 {target_time} 不在可用时间列表中")
            
            time_index = time_index_map[target_time]
            self._log(f"\n🎯 处理时间段：{target_time}（索引：{time_index}）")
            
            # 找到对应时间的格子
            court_items = target_field_box.find_elements(By.CLASS_NAME, "item")
            target_item = court_items[time_index]
            
            # 检查是否可用
            if "disabled" in target_item.get_attribute("class"):
                self._log(f"⚠️ {target_time} 时段不可用（已被占用）")
                continue
            
            # 滚动到元素并点击
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_item)
            self.driver.execute_script("arguments[0].click();", target_item)
            
            # 验证是否选中
            if "checked" in target_item.get_attribute("class") or target_item.find_elements(By.CLASS_NAME, "iconzhengque"):
                self._log(f"✅ 成功选择 {target_time}-{self.court_name}")
            else:
                self._log(f"⚠️ {target_time} 点击可能未生效，但继续执行")
    
    def _submit_order(self):
        """提交订单"""
        # 滚动到顶部
        self.driver.execute_script("window.scrollTo(0, 0);")
        
        # 勾选协议
        agreement_elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//label[@class="el-checkbox"]//input[@type="checkbox"]'))
        )
        if not agreement_elem.is_selected():
            agreement_label = self.driver.find_element(By.XPATH, '//label[@class="el-checkbox"]')
            self.driver.execute_script("arguments[0].click();", agreement_label)
        self._log("✅ 协议已勾选")
        
        # 提交订单
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn-primary") and contains(text(), "提交订单")]'))
        )
        
        if submit_btn.get_attribute("disabled"):
            raise Exception("❌ 提交订单按钮不可用，请检查是否已选择场地")
        
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self._log("✅ 订单已提交")
        time.sleep(5)
    
    def run(self, wait_for_login=True):
        """执行预订流程"""
        try:
            # 初始化驱动
            self._init_driver()
            
            # 打开页面并等待登录
            self.driver.get(self.reserve_url)
            self._log("✅ 页面已打开，请手动登录")
            
            # 等待用户登录（GUI版本中通过回调函数控制）
            if wait_for_login:
                self._log("⏳ 等待登录中...（请在浏览器中完成登录）")
                # 等待30秒让用户有时间登录，或者通过GUI按钮控制
                time.sleep(30)
                self._log("✅ 继续执行预订流程")
            
            # 等待触发时间
            self._wait_for_trigger_time()
            
            # 选择日期
            self._select_date()
            
            # 查找并选择场地和时间
            target_field_box = self._find_court()
            self._select_times(target_field_box)
            
            # 提交订单
            self._submit_order()
            
            self._log("✅ 预订流程完成，请手动完成支付")
            return True
            
        except Exception as e:
            self._log(f"❌ 错误：{str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                time.sleep(3)
                self.driver.quit()
