FROM python:3.10-slim
# 设置 HTTP/HTTPS 代理
ENV http_proxy=http://192.168.3.7:17890
ENV https_proxy=http://192.168.3.7:17890

WORKDIR /app

# 复制所需文件到容器中
COPY ./requirements.txt /app
COPY ./VERSION /app

RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
# 最后建议取消代理（可选，避免影响镜像中运行环境）
ENV http_proxy=""
ENV https_proxy=""
