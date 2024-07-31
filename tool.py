import json
import logging
import os
import subprocess
import time
import platform
from flask import Flask, request, jsonify, render_template
from threading import Thread

# 检测操作系统类型
is_windows = platform.system() == 'Windows'

# 配置路径和IPMI工具路径
if is_windows:
    CONFIG_PATH = 'config.json'
    LOG_PATH = 'temp_control.log'
    IPMI_TOOL_PATH = 'ipmitool.exe'
else:
    CONFIG_PATH = '/etc/temp_control/config.json'
    LOG_PATH = '/var/log/temp_control.log'
    IPMI_TOOL_PATH = '/usr/local/bin/ipmitool'

# 配置日志
logging.basicConfig(level=logging.INFO, filename=LOG_PATH, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 添加日志处理器，将日志输出到终端
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# 加载配置
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

interval = config['interval']
temp_to_fan_speed = config['temp_to_fan_speed']
ipmi_config = config['ipmi']
ipmi_ip = ipmi_config['ip']
ipmi_user = ipmi_config['username']
ipmi_pass = ipmi_config['password']

# 创建Flask应用
app = Flask(__name__)

# 获取温度信息
def get_temperature():
    try:
        result = subprocess.run([IPMI_TOOL_PATH, '-I', 'lanplus', '-H', ipmi_ip, '-U', ipmi_user, '-P', ipmi_pass, 'sdr', 'type', 'temperature'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        temp_lines = result.stdout.strip().split('\n')
        temps = []
        for line in temp_lines:
            if 'Temp' in line:  # 获取所有温度信息
                temp_info = line.split('|')
                temps.append({
                    "sensor": temp_info[0].strip(),
                    "status": temp_info[2].strip(),
                    "temperature": temp_info[3].strip()
                })
        return temps
    except Exception as e:
        logging.error(f"获取温度信息失败: {e}")
    return []

# 获取当前风扇转速
def get_fan_speed():
    try:
        result = subprocess.run([IPMI_TOOL_PATH, '-I', 'lanplus', '-H', ipmi_ip, '-U', ipmi_user, '-P', ipmi_pass, 'sdr', 'type', 'fan'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        fan_lines = result.stdout.strip().split('\n')
        for line in fan_lines:
            if 'Fan' in line:
                fan_info = line.split('|')
                return fan_info[3].strip()
    except Exception as e:
        logging.error(f"获取风扇转速失败: {e}")
    return None

# 设置手动模式
def set_manual_mode():
    try:
        result = subprocess.run([IPMI_TOOL_PATH, '-I', 'lanplus', '-H', ipmi_ip, '-U', ipmi_user, '-P', ipmi_pass, 'raw', '0x30', '0x30', '0x01', '0x00'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.info("成功设置为手动模式")
        else:
            logging.error(f"设置手动模式失败: {result.stderr}")
    except Exception as e:
        logging.error(f"设置手动模式失败: {e}")

# 预设风扇速度
fan_speed_preset = {
    "10": "0x0a",
    "15": "0x0f",
    "20": "0x14",
    "25": "0x19",
    "30": "0x1e",
    "35": "0x23",
    "40": "0x28",
    "45": "0x2d",
    "50": "0x32",
    "55": "0x37",
    "60": "0x3c",
    "65": "0x41",
    "70": "0x46",
    "75": "0x4b",
    "80": "0x50",
    "85": "0x55",
    "90": "0x5a",
    "95": "0x5f",
    "100": "0x64"
}


# 调整风扇转速
def set_fan_speed(speed):
    hex_speed = fan_speed_preset.get(str(speed))
    if not hex_speed:
        logging.error(f"无效的风扇转速: {speed}%")
        return
    try:
        set_manual_mode()
        result = subprocess.run([IPMI_TOOL_PATH, '-I', 'lanplus', '-H', ipmi_ip, '-U', ipmi_user, '-P', ipmi_pass, 'raw', '0x30', '0x30', '0x02', '0xff', hex_speed], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.info(f"成功将风扇转速设置为 {speed}% ({hex_speed})")
        else:
            logging.error(f"设置风扇转速失败: {result.stderr}")
    except Exception as e:
        logging.error(f"设置风扇转速失败: {e}")

# 温控逻辑
def temp_control():
    while True:
        temps = get_temperature()
        if temps:
            for temp_data in temps:
                if temp_data["sensor"] == "Temp":
                    temp = int(temp_data["temperature"].split(' ')[0])
                    for temp_threshold in sorted(temp_to_fan_speed.keys()):
                        if temp < int(temp_threshold):
                            set_fan_speed(temp_to_fan_speed[temp_threshold])
                            break
        else:
            logging.error("无法获取温度信息，跳过此次调整")
        time.sleep(interval)

# 启动温控脚本
@app.route('/start_temp_control', methods=['POST'])
def start_temp_control():
    try:
        thread = Thread(target=temp_control)
        thread.start()
        logging.info("温控脚本已启动")
        return jsonify({"status": "success", "message": "温控脚本已启动"}), 200
    except Exception as e:
        logging.error(f"启动温控脚本失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 设置风扇转速
@app.route('/set_fan_speed', methods=['POST'])
def set_fan_speed_endpoint():
    try:
        speed = request.json.get('speed')
        if not speed:
            return jsonify({"status": "error", "message": "风扇转速不能为空"}), 400
        set_fan_speed(speed)
        return jsonify({"status": "success", "message": f"风扇转速已设置为 {speed}%"}), 200
    except Exception as e:
        logging.error(f"设置风扇转速失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 获取当前状态
@app.route('/status', methods=['GET'])
def status():
    try:
        temps = get_temperature()
        fan_speed = get_fan_speed()
        return jsonify({"status": "success", "temperatures": temps, "fan_speed": fan_speed}), 200
    except Exception as e:
        logging.error(f"获取状态失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 网页界面
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500)
