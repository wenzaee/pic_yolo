FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0
COPY . /app
# 卸载 opencv-python 并安装 opencv-python-headless
#RUN pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install  -r requirements.txt
EXPOSE 6001
CMD ["python", "yolo.py"]
