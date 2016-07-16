from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import make_response
from flask import abort

import uuid

from models import User
from models import Tweet


app = Flask(__name__)

cookie_dict = {}


# 通过 session 来获取当前登录的用户
def current_user():
    cid = request.cookies.get('cookie_id')
    user = cookie_dict.get(cid, None)
    return user


@app.route('/')
def index():
    return redirect(url_for('login_view'))


# 显示登录界面的函数  GET
@app.route('/login')
def login_view():
    return render_template('login.html')


# 处理登录请求  POST
@app.route('/login', methods=['POST'])
def login():
    u = User(request.form)
    user = User.query.filter_by(username=u.username).first()
    print(user)
    if user.validate(u):
        print("用户登录成功")
        # 用 make_response 生成响应 并且设置 cookie
        r = make_response(redirect(url_for('timeline_view', username=user.username)))
        cookie_id = str(uuid.uuid4())
        cookie_dict[cookie_id] = user
        r.set_cookie('cookie_id', cookie_id)
        return r
    else:
        print("用户登录失败", user)
        return redirect(url_for('login_view'))


# 处理注册的请求  POST
@app.route('/register', methods=['POST'])
def register():
    u = User(request.form)
    if u.valid():
        print("用户注册成功")
        # 保存到数据库
        u.save()
        return redirect(url_for('login_view'))
    else:
        print('注册失败', request.form)
        return redirect(url_for('login_view'))


# 显示某个用户的时间线  GET
@app.route('/timeline/<username>')
def timeline_view(username):
    # 查找 username 对应的用户
    # 对查询对象调用 str 方法，可以知道它执行的 sql 语句
    # str(a) 相当于 a.__str__()
    # sql = str(User.query.filter_by(username=username))
    # print(sql)
    # first() 取第一个数据，其他方法我们以资料的形式提供
    u = User.query.filter_by(username=username).first()
    if u is None:
        # 找不到就返回 404, 这是 flask 的默认 404 用法
        abort(404)
    else:
        # 找到就查找这个用户的所有微博并且逆序排序返回
        # sort 函数的用法 再解释
        # tweets = Tweet.query.filter_by(user_id=u.id).all()
        # 
        # lambda 就是匿名函数的意思
        # lambda t: t.created_time
        # 上面的匿名函数相当于下面这个函数
        # def func(t):
        #     return t.created_time
        tweets = u.tweets
        tweets.sort(key=lambda t: t.created_time, reverse=True)
        return render_template('timeline.html', tweets=tweets, user=current_user())


# 处理 发送 微博的函数  POST
@app.route('/tweet/add', methods=['POST'])
def tweet_add():
    user = current_user()
    if user is None:
        return redirect(url_for('login_view'))
    else:
        t = Tweet(request.form)
        # 设置是谁发的
        t.user = user
        # 保存到数据库
        t.save()
        return redirect(url_for('timeline_view', username=user.username))


# 显示 更新 微博的界面
@app.route('/tweet/update/<tweet_id>')
def tweet_update_view(tweet_id):
    t = Tweet.query.filter_by(id=tweet_id).first()
    if t is None:
        abort(404)
    # 获取当前登录的用户, 如果用户没登录或者用户不是这条微博的主人, 就返回 401 错误
    user = current_user()
    if user is None or user.id != t.user_id:
        abort(401)
    else:
        return render_template('tweet_edit.html', tweet=t)


# 处理 更新 微博的请求
@app.route('/tweet/update/<tweet_id>', methods=['POST'])
def tweet_update(tweet_id):
    t = Tweet.query.filter_by(id=tweet_id).first()
    if t is None:
        abort(404)
    # 获取当前登录的用户, 如果用户没登录或者用户不是这条微博的主人, 就返回 401 错误
    user = current_user()
    if user is None or user.id != t.user_id:
        abort(401)
    else:
        t.content = request.form.get('content', '')
        t.save()
        return redirect(url_for('timeline_view', username=user.username))


# 处理 删除 微博的请求
@app.route('/tweet/delete/<tweet_id>')
def tweet_delete(tweet_id):
    t = Tweet.query.filter_by(id=tweet_id).first()
    if t is None:
        abort(404)
    # 获取当前登录的用户, 如果用户没登录或者用户不是这条微博的主人, 就返回 401 错误
    user = current_user()
    if user is None or user.id != t.user_id:
        abort(401)
    else:
        t.delete()
        return redirect(url_for('timeline_view', username=user.username))


if __name__ == '__main__':
    app.run(debug=True)

# 数据库有个功能叫做索引
# 索引就是一个 字段：id 的字典
# 这样你就能够通过 字段 查找到 id
# 然后实现 O(1) 的快速查询