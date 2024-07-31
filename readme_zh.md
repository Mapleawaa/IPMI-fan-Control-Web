# IPMI 调速工具

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=FF4B4B) ![IPMItool](https://img.shields.io/badge/IPMItool-000000?style=for-the-badge&logo=IPMItool&logoColor=FF4B4B) ![github](https://img.shields.io/badge/github-000000?style=for-the-badge&logo=github&logoColor=white)

[English](readme_en.md) | [中文](readme.md) | [项目链接  ](https://github.com/Mapleawaa/IPMI-fan-Control-Web)


本项目是一个基于Python的温度和风扇速度控制脚本，它使用IPMI来监控并根据温度读数调整风扇速度。它包括一个用于手动调整风扇速度和实时监控的网页界面。
* * * 

## 特性

- 根据温度阈值自动调整风扇速度。
- 提供一个用于手动控制风扇速度和实时监控的网页界面。
- 支持Linux和Windows系统。
- 可通过JSON文件进行配置。

## 目录结构
```
IPMI-fan-Control-Web/
├── config.json
├── requirements.txt
├── temp_control.py
└── templates/
    ├── index.html
```


## 开始安装

### 准备环境

- Python 3.x
- Flask
- IPMItool(默认已经存在)

### 步骤指南

1. **克隆仓库**

   ```bash
   git clone https://github.com/Mapleawaa/IPMI-fan-Control-Web.git
   cd temp_control
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **配置脚本**

   编辑`config.json`文件以包含您的IPMI设置和温度到风扇速度的映射。
    

   ```json
   {
       "interval": 60,
       "temp_to_fan_speed": {
           "40": "10",
           "50": "20",
           "60": "30"
       },
       "ipmi": {
           "ip": "192.168.1.100",
           "username": "admin",
           "password": "password"
       }
   }
   ```s

4. **运行脚本**

   ```bash
   python temp_control.py
   ```

### 在Linux上作为Systemd服务运行

*直接运行脚本即可 内有检测环境自动判断系统*

1. **创建systemd服务文件**

   ```ini
   [Unit]
   Description=ipmitempctl
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/your/temp_control.py
   WorkingDirectory=/path/to/your
   StandardOutput=syslog
   StandardError=syslog
   SyslogIdentifier=temp_control
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **重新加载systemd并启动服务**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable temp_control.service
   sudo systemctl start temp_control.service
   ```

3. **检查服务状态**

   ```bash
   sudo systemctl status temp_control.service
   ```

## 使用

### 网页界面

- 通过在您的浏览器中访问`http://<your-server-ip>:500`来访问网页界面。
注:*地址可能发生变动 请查看日志中现实的具体地址*
- 使用界面手动调整风扇速度和查看当前温度。

### API接口

- **开始温度控制**

  ```http
  POST /start_temp_control
  ```

- **设置风扇速度**

  ```http
  POST /set_fan_speed
  {
      "speed": 30
  }
  ```

- **获取当前状态**

  ```http
  GET /status
  ```

## 贡献

欢迎贡献！请参阅我们的[贡献指南](CONTRIBUTING.md)了解更多详情。

## 许可证

本项目采用Apache-2.0许可证 - 详情请参见[LICENSE](LICENSE)文件。

## 致谢

- 本项目灵感来源于[cw1997/dell_fans_controller](https://github.com/cw1997/dell_fans_controller)。