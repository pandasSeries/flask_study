# request로 POST로 요청된 값 확인
from flask import Blueprint, render_template, request, flash, redirect, url_for
# 회원가입 로직 처리
# 회원가입페이지(signup)에서 전달 받은 값을 db에 저장
# auth.py에서 유효성 검사를 모두 통과하면 가입
from .models import User

# UserMixin, flask_login을 통해 현재 로그인과 관련된 기능(로그인, 로그아웃, 현사용자 정보 접근 사용0)을 구현
# flask-login 모듈 활용으로 로그인 구현
from flask_login import login_user, login_required, logout_user, current_user



# hash 적용한 비밀번호 구현
# 비밀번호 해싱을 위해 import
# user 인스턴스 생성시 password를 해싱
from werkzeug.security import generate_password_hash, check_password_hash
# blueprint를 이용하면 플라스크 App의 모든 url을 한곳에서 관리 하지 않아도 된다
# 이곳저곳에 뿌려진 url의 정의를 수집하여 한곳으로 모아준다
auth = Blueprint('auth', __name__)

# 뷰를 정의하여 보여질 페이지와 경로를 정의
# 클라이언트 요청 > 서버의 응답을 간단히
# 데코레이터로 Blueprint.route가 해줄 예정
# 우리는 동작하기위해 필요한 정보만 입력

# 통신후 데이터가 남는 형태는 POST 통신을 사용
# 회원가입 페이지에 접속 - GET 통신
# 회원가입 신청 - form:POST - POST 통신
@auth.route('/sign-up', methods=['POST', 'GET']) # url 끝부분(end point)를 인자로 입력
def sign_up():
    # 데이터 확인, 클라이언트 요청에 대한 데이터가 담겨있다
    if request.method == 'POST':
        # form - input의 name 속성을 기준으로 가져오기
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 유효성 검사
        # flash 작성후 html에 적용해야함
        if len(email) < 5:
            flash('이메일은 5자 이상입니다.', category='error')
        elif len(nickname) < 2:
            flash('닉네임은 2자 이상입니다.', category='error')
        elif password1 != password2:
            flash('비밀번호와 비밀번호재입력이 서로 다릅니다', category='error')
        elif len(password1) < 7:
            flash('비밀번호가 너무 짧습니다', category='error')
        else:
            flash('회원가입 완료.', category='success') # Create User -> DB
            # Create User > DB
            # 모든 유효성 검사가 끝난 곳에 새로운 user 인스턴스 생성
            
            new_user = User(email=email, nickname=nickname, password=generate_password_hash(password1, method = 'sha256'))
            # 생성한 User 인스턴스를 추가
            db.session.add(new_user)
            # db는 commit하기 전에는 임시상태
            # commit을 해주어서 최종 반영
            db.session.commit()

            # auto login
            login_user(new_user, remember = True)
            flash('회원가입 완료', category = 'success') # create user -> db
            
            return redirect(url_for('views.home'))
    
    return render_template('sign_up.html') # 클라이언트 요청에 응답할 데이터를 return 시키는 함수 생성

# 로그아웃은 logout_user()사용
# 로그아웃도 여러번 안하고 로그인도 안했는데 로그아웃 페이지에 접근할 이유 없다
@auth.route('/logout') # url 끝부분(end point)를 인자로 입력
def logout():
    logout_user()
    # html 아닌 함수로 가려면 redirect
    return redirect(url_for('auth.sign_in')) # 클라이언트 요청에 응답할 데이터를 return 시키는 함수 생성

@auth.route('/sign-in',methods=['GET', 'POST']) # url 끝부분(end point)를 인자로 입력
def sign_in():
    # login
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')

        # Search user in database and compare password
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password1):
                flash('로그인 완료', category='success')
                # 로그인 처리 진행
                # remember는 세션이 만료된후 사용자를 기억할지 여부
                # True일 경우 1 사용자가 인터넷 사용기록이나 세션을 지울때 까지 이사용자가 로그인한것 기억
                # 2 플라스크 세션에 저장
                # 3 플라스크 웹서버를 다시 시작하면 기억된 정보는 사라진다
                login_user(user, remember=True)
                
                # post 통신이니 redirect()한다
                return redirect(url_for('views.home'))
            else:
                flash('비밀번호가 다릅니다', category='error')
        else:
            flash('해당 이메일 정보가 없습니다', category='error')
    return render_template('sign_in.html')
    # 진자로 user변수를 사용할수 있다
    # 변수명은 user로 할필요없이 짓고 싶은대로 지으면 된다
    return render_template('sign_in.html', user = 'Mark') # 클라이언트 요청에 응답할 데이터를 return 시키는 함수 생성