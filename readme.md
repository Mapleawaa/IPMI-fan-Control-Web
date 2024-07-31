
# Temperature and Fan Speed Control

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=FF4B4B) ![IPMItool](https://img.shields.io/badge/IPMItool-000000?style=for-the-badge&logo=IPMItool&logoColor=FF4B4B) ![github](https://img.shields.io/badge/github-000000?style=for-the-badge&logo=github&logoColor=white)


[English](readme.md) | [中文](readme_zh.md) | [Project link ](https://github.com/Mapleawaa/IPMI-fan-Control-Web)
## Features

This project is a Python-based temperature and fan speed control script that uses IPMI to monitor and adjust fan speeds based on temperature readings. It includes a web interface for manual fan speed adjustments and real-time monitoring.

## Features

- Automatically adjusts fan speeds based on temperature thresholds.
- Provides a web interface for manual control of fan speeds and real-time monitoring.
- Supports both Linux and Windows systems.
- Configurable through a JSON file.

## File Tree
```
IPMI-fan-Control-Web/
├── config.json
├── requirements.txt
├── temp_control.py
└── templates/
    ├── index.html
```

## Installation

### Prerequisites

- Python 3.x
- Flask
- IPMItool

### Step-by-Step Guide

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Mapleawaa/IPMI-fan-Control-Web.git
   cd temp_control
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Script**

   Update the `config.json` file with your IPMI settings and temperature-to-fan speed mappings.
    example :
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
   ```

4. **Run the Script**

   ```bash
   python temp_control.py
   ```

### Running as a Systemd Service on Linux

1. **Create a systemd Service File**

   ```ini
   [Unit]
   Description=Temperature Control Service
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

2. **Reload systemd and Start the Service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable temp_control.service
   sudo systemctl start temp_control.service
   ```

3. **Check Service Status**

   ```bash
   sudo systemctl status temp_control.service
   ```

## Usage

### Web Interface

- Access the web interface by navigating to `http://<your-server-ip>:5000` in your web browser.
- Use the interface to manually adjust fan speeds and view current temperatures.

### API Endpoints

- **Start Temperature Control**

  ```http
  POST /start_temp_control
  ```

- **Set Fan Speed**

  ```http
  POST /set_fan_speed
  {
      "speed": 30
  }
  ```

- **Get Current Status**

  ```http
  GET /status
  ```

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the Apache-2.0 license - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project was inspired by [cw1997/dell_fans_controller](https://github.com/cw1997/dell_fans_controller).
