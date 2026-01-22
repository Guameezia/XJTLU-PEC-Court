# 西浦体育中心场地预订助手

一个半自动预订网球场和羽毛球场的 Python 应用程序，提供图形界面和自动化抢先预订功能。

XJTLUer苦于午夜手速慢已久，我们可以利用一些帮助达到抢场地的目的。

由于作者本人需求极大，repo暂时设置为Private状态，且测试工作并不严谨。如想要下载可以用XJTLU邮箱联系。

## 系统要求

- Python 3.7+
- Microsoft Edge 浏览器
- Edge WebDriver（通常随 Edge 浏览器自动安装）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone https://github.com/Guameezia/PECCourt.git
cd PECcourt
```

### 2. 安装依赖

```bash
pip install selenium
```

### 3. 确保 Edge WebDriver 可用

确保已安装 Microsoft Edge 浏览器，WebDriver 通常会自动安装。如果遇到问题，可以从 [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) 下载。

## 使用方法

### 启动应用程序

```bash
python gui_app.py
```

### 配置预订参数

1. **选择场地类型**：选择"羽毛球场"或"网球场"
2. **选择场地**：从下拉菜单中选择具体场地
3. **预订日期**：输入日期，格式为 `MM/DD`（默认为七日之后，抢场地的普遍需求）
4. **选择时间段**：勾选需要预订的时间段
5. **触发时间**：设置自动触发时间，格式为 `HH:MM:SS`（默认为 `00:00:00`）

### 执行预订

1. 点击"开始预订"按钮，等待自动触发浏览器登录界面
2. 在自动打开的浏览器中完成登录（注意选择正确SIP/TC）

<img src="Login.png" width="300" />

3. 登录完成后，返回GUI界面，点击"我已登录"按钮
4. 程序将等待到设定的触发时间，然后自动执行预订流程
5. 预订完成后，请在浏览器中手动完成支付（五分钟内）

## 项目结构

```
PECcourt/
├── court_reservation.py  # 核心预订逻辑类
├── gui_app.py            # GUI 应用程序
├── README.md             # 项目说明文档
└── ...
```


## 注意事项

- 请确保网络连接稳定
- 在预订开始前提前测试登录流程
- e.g., 大约在23:58提前完成登录操作，程序保持运行，一到00:00就可以触发抢场地的效果
- 触发时间设置要合理，确保在预订开放时间之前
- 预订成功后需要手动完成支付
- 请遵守相关使用条款和规定

## 技术栈

- Python 3
- Selenium WebDriver
- Tkinter (GUI)

<!-- ## 许可证

[在此添加许可证信息] -->

## 贡献

欢迎提交 Issue 和 Pull Request！

<!-- ## 更新日志

[在此添加更新日志] -->
