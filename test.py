import requests

import requests
import json

def test_start_task():
    try:
        # 定义测试数据
        task_id = 'asda231sadasdasdaa'
        command = 'asasdas'
        file_path = './uploads/'
        data = {
            'task_id': task_id,
            'command': command,
            'file_path': file_path
        }

        # 发送 POST 请求到 /start_task 接口
        url = ' http://192.168.5.8:5000/start_task'
        response = requests.post(url, json=data)

        # 打印测试结果
        print(f"start_task 测试结果: {response.json()}")
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
        # 增加详细错误信息
        print(f"详细错误信息: {e.args}")
        # 检查服务端是否启动
        print("请确认 Flask 服务是否已启动，并监听 http://localhost:5000")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        # 增加详细错误信息
        print(f"详细错误信息: {e.args}")
    except Exception as e:
        print(f"未知错误: {e}")
        # 增加详细错误信息
        print(f"详细错误信息: {e.args}")

if __name__ == '__main__':
    test_start_task()