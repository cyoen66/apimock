from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPBasicAuth
import boto3
from botocore.exceptions import NoCredentialsError
import requests
import jwt
import datetime
from functools import wraps
import os
import platform

if platform.system() == 'Windows':
    import msvcrt
else:
    import fcntl


SECRET_KEY = 'aoi_api_secret_key'
app = Flask(__name__)
# 認証オブジェクトを作成
auth = HTTPBasicAuth()
# ユーザー名とパスワードの辞書
users = {
    "username": "password",
    "10001425" : "10001425",
    "400":"400",
    "401":"401",
    "403":"403",
    "500":"500",
    "503":"503"
}

# S3
aws_access_key_id = 'ASIAZQ3DRGRDJ7VTUCRA'
aws_secret_access_key = '/NK/77jJZgJb3Y7M4tS7/0cuIJJQ0RVTCPgzJSR7'
bucket = 'yfc-test-bucket'


# ユーザー名とパスワードの認証関数
@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

# トークンを生成する関数
def generate_token(user):
    payload = {
        'user': user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # トークンの有効期限を1日に設定
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# 署名付きURLの発行
def get_s3_url(file_name = "test.csv"):
    s3_client = boto3.client('s3', 
                             aws_access_key_id=aws_access_key_id, 
                             aws_secret_access_key = aws_secret_access_key) 
    # S3 クライアントを作成
    #s3_client = boto3.client('s3')

    # 署名付きURLを生成
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': file_name},
                                                    ExpiresIn=3600)
        print("署名付きURL: ", response)
        return response
    except NoCredentialsError:
        print("AWS認証情報が見つかりませんでした。")      

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = verify_token(token)
            if data is None:
                return jsonify({'message': 'Token is invalid!'}), 401
            g.current_user = data['user']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated




# token取得API
@app.route('/auth/token/get', methods=['POST'])
@auth.login_required
def get_token():
    # POSTリクエストからJSONデータを取得
    requestData = request.get_json()

    # userを取得する
    user = auth.current_user()
    # userが10001425の場合は、expiresを1日後に設定
    if user == "10001425":
        expires = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return jsonify({
                "user": user,
                "expires": expires,
                "token": generate_token(user),
                "resources": [
                    "v1/login/*",
                    "v1/management/*",
                    "v1/store-management/*",
                    "v1/nsips-upload/*",
                    "v1/picking-inspection/*"
                ]
                }), 200
    elif user == "400":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [
                    {
                    "field": "corpStoreCode",
                    "message": "corpStoreCodeは必須項目です。"
                    }
                ],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 400
    elif user == "401":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "認証に失敗しました。"
                    }
                ]
                }), 401
    elif user == "403":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "アクセスが禁止されています。"
                    }
                ]
                }), 403
    elif user == "500":
        return jsonify({
                "error": "SYSTEM_ERROR",
                "fields": [],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 500
    elif user == "503":
        return jsonify({
                "error": "SYSTEM_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "現在メンテナンス中です。時間をおいて再度アクセスしてください。"
                    }
                ]
                }), 503
    else:
        return jsonify({
                    "message": "想定外のステータスコードです。"
                })

# 店舗情報取得API
@app.route('/store-management/stores/get', methods=['POST'])
@token_required
def get_stores():
    # POSTリクエストからJSONデータを取得
    requestData = request.get_json()

    # userを取得する
    user = g.current_user
    # userが10001425の場合は、expiresを1日後に設定
    if user == "10001425":
        return jsonify({
                "storeInfoResultCd": "1",
                "absStoreCd": "01425",
                "referenceDtStoreNm": "ワテラスモール店",
                "referenceDtStoreKana": "D.ﾜﾃﾗｽﾓｰﾙﾃﾝ",
                "referenceDtCorpCd": "1000",
                "referenceDtStoreCd": "1425"
                }), 200
    elif user == "400":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [
                    {
                    "field": "corpStoreCode",
                    "message": "corpStoreCodeは必須項目です。"
                    }
                ],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 400
    elif user == "401":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "認証に失敗しました。"
                    }
                ]
                }), 401
    elif user == "403":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "アクセスが禁止されています。"
                    }
                ]
                }), 403
    elif user == "500":
        return jsonify({
                "error": "SYSTEM_ERROR",
                "fields": [],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 500
    elif user == "503":
        return jsonify({
                "error": "SYSTEM_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "現在メンテナンス中です。時間をおいて再度アクセスしてください。"
                    }
                ]
                }), 503
    else:
        return jsonify({
                    "message": "想定外のステータスコードです。"
                })



# 署名付きURL取得API
@app.route('/nsips-upload/presigned-url/get', methods=['POST'])
@token_required
def get_presigned_url():
    # POSTリクエストからJSONデータを取得
    data = request.get_json()
    filename = data.get('fileNm') 
    corpStoreCd = data.get('corpStoreCd')
    s3_url = get_s3_url(filename)
     # userを取得する
    user = g.current_user
    # userが10001425の場合は、expiresを1日後に設定
    if user == "10001425" and corpStoreCd == "20002260" and filename == "A00200501010000100000.txt":
        return jsonify({
                "corpStoreCd": "10001425",
                "fileNm": "A00200501010000100000.txt",
                "url": s3_url
                }), 200
    elif user == "400":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [
                    {
                    "field": "corpStoreCode",
                    "message": "corpStoreCodeは必須項目です。"
                    }
                ],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 400
    elif user == "401":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "認証に失敗しました。"
                    }
                ]
                }), 401
    elif user == "403":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "アクセスが禁止されています。"
                    }
                ]
                }), 403
    elif user == "500":
        return jsonify({
                "error": "SYSTEM_ERROR",
                "fields": [],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 500
    elif user == "503":
        return jsonify({
                "error": "SYSTEM_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "現在メンテナンス中です。時間をおいて再度アクセスしてください。"
                    }
                ]
                }), 503
    else:
        return jsonify({
                    "message": "想定外のステータスコードです。"
                })

# 端末ログ送信API
@app.route('/management/logs/submit', methods=['POST'])
@token_required
def submit_logs():
    # POSTリクエストからJSONデータを取得
    data = request.get_json()
    deviceName = data.get('deviceName') 

     # userを取得する
    user = g.current_user
    # userが10001425の場合は、expiresを1日後に設定
    if user == "10001425" and deviceName == "FZ-N1":
        return jsonify({}), 200
    elif user == "400":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [
                    {
                    "field": "corpStoreCode",
                    "message": "corpStoreCodeは必須項目です。"
                    }
                ],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 400
    elif user == "401":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "認証に失敗しました。"
                    }
                ]
                }), 401
    elif user == "403":
        return jsonify({
                "error": "VALIDATION_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "アクセスが禁止されています。"
                    }
                ]
                }), 403
    elif user == "500":
        return jsonify({
                "error": "SYSTEM_ERROR",
                "fields": [],
                "global": [
                    {
                    "message": "予期しないエラーが発生しました。"
                    }
                ]
                }), 500
    elif user == "503":
        return jsonify({
                "error": "SYSTEM_FAILURE",
                "fields": [],
                "global": [
                    {
                    "message": "現在メンテナンス中です。時間をおいて再度アクセスしてください。"
                    }
                ]
                }), 503
    else:
        return jsonify({
                    "message": "想定外のステータスコードです。"
                })    

# S3へアップロード
@app.route('/api/upload', methods=['get'])
def upload_s3():
    # 署名付きURL
    url = "https://yfc-test-bucket.s3.amazonaws.com/test.csv?AWSAccessKeyId=ASIAZQ3DRGRDJ7VTUCRA&Signature=f0elW3rsYJ1EO5aQqzFdjDYsYyU%3D&Expires=1724148326"

    # アップロードするファイルのパス
    file_path = 'test.csv'

    # ファイルを開いてPUTリクエストを送信
    with open(file_path, 'rb') as f:
        response = requests.put(url, data=f)

    # レスポンスのステータスコードを確認
    response1 = {
        'received_param1': response.status_code,
        'received_param2': url
    }
    if response.status_code == 200:
        print("ファイルが正常にアップロードされました。")
    else:
        print(f"ファイルのアップロードに失敗しました。ステータスコード: {response.status_code}")
    return jsonify(response1)




if __name__ == '__main__':
    app.run(debug=True)