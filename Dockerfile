FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0
COPY . /app
# 卸载 opencv-python 并安装 opencv-python-headless
#RUN pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["python", "worker.py"]
