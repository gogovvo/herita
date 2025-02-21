from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
import requests
from functools import wraps
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/kakao-login', methods=['POST'])
def kakao_login():
    data = request.json
    kakao_id = data.get('kakao_id')
    nickname = data.get('nickname')
    email = data.get('email')

    if kakao_id:
        # 세션에 사용자 정보 저장
        session['kakao_id'] = kakao_id
        session['nickname'] = nickname
        session['email'] = email
        return jsonify(success=True)
    return jsonify(success=False)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'kakao_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/mypage')
@login_required
def mypage():
    # 세션에서 사용자 정보 가져오기
    user = {
        'name': session.get('nickname', '사용자'),
        'email': session.get('email', '')
    }
    # 나중에 DB에서 saved_flowers 데이터를 가져오는 로직 추가
    saved_flowers = []
    return render_template('mypage.html', user=user, saved_flowers=saved_flowers)


# 로그아웃 기능 추가
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


#####업로더 테스트
# 허용할 이미지 확장자 목록
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# 업로드 테스트로 잠시 주석
# # Routes
# @app.route('/')
# def index():
#     return redirect(url_for('write'))

# Load flower data
def load_flower_data():
    try:
        # 먼저 cp949로 시도
        df = pd.read_csv('static/flower_date_honest.csv', encoding='cp949')
    except:
        try:
            # cp949가 실패하면 euc-kr로 시도
            df = pd.read_csv('static/flower_date_honest.csv', encoding='euc-kr')
        except:
            # 모두 실패하면 utf-8 with BOM 시도
            df = pd.read_csv('static/flower_date_honest.csv', encoding='utf-8-sig')

    # NaN 값을 빈 문자열로 대체
    df = df.fillna('')

    # 모든 문자열 컬럼의 값을 문자열로 변환
    for col in ['name_kr', 'name_en', 'mean', 'color']:
        df[col] = df[col].astype(str)

    return df.to_dict('records')


@app.route('/api/flowers', methods=['GET'])
def get_flowers():
    flowers = load_flower_data()
    return jsonify(flowers)


@app.route('/api/search/<query>')
def search_flowers(query):
    flowers = load_flower_data()

    # Filter flowers based on Korean or English name
    filtered_flowers = []
    query = query.lower()

    for flower in flowers:
        name_kr = str(flower['name_kr']).lower() if flower['name_kr'] is not None else '-'
        name_en = str(flower['name_en']).lower() if flower['name_en'] is not None else '-'

        if query in name_kr or query in name_en:
            filtered_flowers.append(flower)

    return jsonify(filtered_flowers)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Store the file path in session for result page
            session['uploaded_image'] = filepath
            return redirect(url_for('result'))

    return render_template('write.html')

#이미지 패스 없는지 체크하는 코드가 필요할까해서 저장
# @app.route('/result')
# def result():
#     image_path = session.get('uploaded_image', None)
#     if not image_path:
#         return redirect(url_for('write'))
#     return render_template('result.html', image_path=image_path)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # 세션에 업로드된 이미지 경로 저장
        session['uploaded_image'] = f'/static/uploads/{filename}'
        return jsonify({"success": True})

    return jsonify({"error": "Invalid file type"}), 400

@app.route('/result')
def result():
    # 세션에서 이미지 경로 가져오기
    image_path = session.get('uploaded_image', '/static/flowers/default.png')  # 기본 이미지 경로 설정
    selected_flowers = session.get('selected_flowers', [])
    return render_template('result.html', image_path=image_path, selected_flowers=selected_flowers)
@app.route('/api/selected-flowers', methods=['POST'])
def save_selected_flowers():
    selected_flowers = request.json
    # 세션에 선택된 꽃 정보 저장
    session['selected_flowers'] = selected_flowers
    return jsonify({"status": "success"})

@app.route('/api/selected-flowers', methods=['GET'])
def get_selected_flowers():
    selected_flowers = session.get('selected_flowers', [])
    return jsonify(selected_flowers)





@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/GEJ')
def GEJ():
    return render_template('은지.html')

@app.route('/GYE')
def GYE():
    return render_template('GYE.html')

@app.route('/HSJ')
def HSJ():
    return render_template('HSJ.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
