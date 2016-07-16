# encoding: utf-8
import json
import uuid

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

app = Flask(__name__)


# 用户类
class User(object):
    def __init__(self, form):
        super(User, self).__init__()
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.qq = form.get('qq', '')
        self.email = form.get('email', '')

    def __repr__(self):
        d = {
            'username': self.username,
            'password': self.password,
            'email'   : self.email,
            'qq'      : self.qq,
        }
        return json.dumps(d)

    def validate(self, user):
        if isinstance(user, User):
            username_equals = self.username == user.username
            password_equals = self.password == user.password
            return username_equals and password_equals
        else:
            return False


def save_users():
    with open('users.txt', 'w') as f:
        # u = json.dumps(user_list)
        u = str(user_list)
        f.write(u)


def load_users():
    try:
        with open('users.txt', 'r') as f:
            users = json.loads(f.read())
            print(users)
            return [User(u) for u in users]
    except:
        return []


def user_by_name(username):
    for u in user_list:
        if username == u.username:
            return u


user_list = load_users()


@app.route('/')
def index():
    return redirect(url_for('login_view'))


# 登录页面 包括了 注册表单
@app.route('/login')
def login_view():
    return render_template('login.html')


cookie_dict = {}


@app.route('/logout')
def logout():
    cookie_dict.clear()
    r = make_response(redirect(url_for('login_view')))
    r.set_cookie('cookie_id', '')
    return r


# 处理登录请求的路由
# 路由设计
@app.route('/login', methods=['POST'])
def login():
    user = User(request.form)
    u = user_by_name(user.username)
    print(user_list)
    if user.validate(u):
        print("用户登录成功")
        # 用 make_response 生成响应 并且设置 cookie
        r = make_response(redirect(url_for('message_view')))
        cookie_id = str(uuid.uuid4())
        cookie_dict[cookie_id] = u.username
        r.set_cookie('cookie_id', cookie_id)
        return r
    else:
        print("用户登录失败", user)
        return redirect(url_for('login_view'))


@app.route('/register', methods=['POST'])
def register():
    u = User(request.form)
    if len(u.username) >= 3 and len(u.password) >= 3:
        print("用户注册成功")
        # user_dict[u.username] = u
        user_list.append(u)
        save_users()
        return redirect(url_for('login_view'))
    else:
        print('注册失败', len(u.username))
        return redirect(url_for('login_view'))


messages = []


@app.route('/message', methods=['GET', 'POST'])
def message_view():
    username = request.cookies.get('username')
    print('username is', username)

    print('request, query 参数', request.args)
    args = request.args

    name = args.get('name', '')
    content = args.get('content', '')
    msg = {
        'name'   : name,
        'content': content,
    }
    messages.append(msg)

    print('request POST 的 form 表单数据\n', request.form)

    return render_template('message.html', msgs=messages)


@app.route('/profile')
def profile_view():
    cookie_id = request.cookies.get('cookie_id')
    if cookie_id in cookie_dict:
        username = cookie_dict.get(cookie_id, None)
        return json.dumps({'username': username, 'cookie_id': cookie_id})
    else:
        return redirect(url_for('login_view'))


@app.route('/user/<username>')
def profile(username):
    cookie_id = request.cookies.get('cookie_id')
    if cookie_id in cookie_dict:
        msgs = []
        _username = cookie_dict.get(cookie_id, None)
        if username == _username:
            for item in messages:
                if item['name'] == username:
                    msgs.append(item)
                else:
                    pass
        else:
            pass
        return render_template('message.html', msgs=msgs)
    else:
        return redirect(url_for('login_view'))


if __name__ == '__main__':
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    debug = True
    app.run(debug=debug)
