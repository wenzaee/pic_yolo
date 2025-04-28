from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from pathlib import Path
import subprocess
import threading

app = Flask(__name__)

# 配置参数
UPLOAD_FOLDER = './uploads'       # 上传文件保存路径
RESULT_DIR = './results'          # 处理结果保存路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
YOLOV5LITE_PATH = Path('yolov5lite')
DETECT_SCRIPT = YOLOV5LITE_PATH / 'detect.py'
WEIGHTS_PATH = YOLOV5LITE_PATH / 'weights' / 'v5lite-g.pt'

# 创建必要目录
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(RESULT_DIR).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(file_path):
    """调用 YOLO 处理图片"""
    result_filename = f"result_{file_path.name}"
    result_path = Path(RESULT_DIR) / result_filename
    
    try:
        # 执行 YOLO 检测命令
        cmd = [
            'python', str(DETECT_SCRIPT),
            '--source', str(file_path),
            '--weights', str(WEIGHTS_PATH),
            '--project', str(RESULT_DIR),
            '--name', '',
            '--exist-ok'
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # 重命名结果文件
        original_result = Path(RESULT_DIR) / file_path.name
        if original_result.exists():
            original_result.rename(result_path)
            return str(result_path)
        return None
        
    except subprocess.CalledProcessError as e:
        app.logger.error(f"YOLO processing failed: {e.stderr}")
        return None

@app.route('/upload', methods=['POST'])
def upload_image():
    """上传并处理图片的接口"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # 保存上传文件
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    
    # 异步处理（使用线程避免阻塞）
    def async_processing():
        result_path = process_image(Path(save_path))
        app.logger.info(f"Processing completed: {result_path}")
        
    threading.Thread(target=async_processing).start()
    
    return jsonify({
        'status': 'processing',
        'message': 'File uploaded and processing started',
        'upload_path': save_path,
        'result_check_endpoint': f'/results/{filename}'
    }), 202

@app.route('/results/<filename>', methods=['GET'])
def get_result(filename):
    """获取处理结果"""
    result_file = Path(RESULT_DIR) / f"result_{secure_filename(filename)}"
    
    if not result_file.exists():
        return jsonify({'status': 'processing', 'message': 'Result not ready yet'}), 102
    
    return jsonify({
        'status': 'completed',
        'result_path': str(result_file),
        'download_url': f'/download/{result_file.name}'
    })

@app.route('/download/<filename>', methods=['GET'])
def download_result(filename):
    """下载结果文件"""
    return jsonify({'error': 'Not implemented'}), 501  # 需自行实现文件发送逻辑

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
