# ベースイメージとしてPythonを使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# Gunicornを使用してアプリケーションを起動
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "aoiapi:app"]
#python .\aoiapi.py