# app.py - 你的第一个Flask应用
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from weather_fetcher import fetch_weather, save_weather_to_db, get_latest_weather, get_weather_history
from extensions import db, init_extensions
from models import User, Post, WeatherData
import hashlib
import secrets


# 1. 创建Flask应用实例，这是所有操作的起点
app = Flask(__name__)

app.config['SECRET_KEY'] = '8fe4219caa373407cef5ebda249667be'  # 生产环境要用更安全的方式生成

# --- 数据库配置 ---
# 设置SQLite数据库的路径。数据库文件将位于项目根目录下，名为 site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告

# 创建数据库对象
init_extensions(app)


def generate_password_hash(password):
    """生成密码的哈希值（使用SHA256 + 随机盐）"""
    # 生成一个随机盐（16个字节，32位十六进制字符）
    salt = secrets.token_hex(16)
    # 将盐和密码组合后哈希
    hash_obj = hashlib.sha256((salt + password).encode())
    hash_value = hash_obj.hexdigest()
    # 存储格式：算法$盐$哈希值 (类似werkzeug格式)
    return f"sha256${salt}${hash_value}"

def check_password_hash(stored_hash, password):
    """验证密码是否与存储的哈希匹配"""
    try:
        # 解析存储的哈希值
        algorithm, salt, hash_value = stored_hash.split("$")
        if algorithm != "sha256":
            return False
        # 用相同的盐和算法计算输入密码的哈希
        hash_obj = hashlib.sha256((salt + password).encode())
        return secrets.compare_digest(hash_obj.hexdigest(), hash_value)
    except (ValueError, AttributeError):
        return False


def get_current_user():
    """获取当前登录的用户对象，如果未登录返回None"""
    if 'user_id' in session:
        user_id = session['user_id']
        return User.query.get(user_id)
    return None


@app.context_processor
def inject_current_user():
    """让 current_user 在所有模板中自动可用"""
    return dict(current_user=get_current_user())


# --- 创建数据库表（在首次运行时） ---
# 这段代码会检查所有定义好的模型，并在数据库中创建对应的表
# with app.app_context():
    # db.create_all()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. 获取表单数据
        username = request.form['username']
        password = request.form['password']

        # 2. 检查用户名或邮箱是否已存在（简单的验证）
        existing_user = User.query.filter_by(username = username).first()
        if existing_user:
            # 这里先简单处理，后续可以优化提示
            return "用户名已被注册，请更换后重试 <a href='/'>返回首页</a>"

        # 3. 创建新用户（密码需要加密存储！）
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)

        # 4. 保存到数据库
        db.session.add(new_user)
        db.session.commit()

        # 5. 注册成功后跳转到登录页
        return redirect(url_for('login'))

    # GET请求：显示注册表单
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 1. 根据邮箱查找用户
        user = User.query.filter_by(username=username).first()

        # 2. 验证用户存在且密码正确
        if user and check_password_hash(user.password_hash, password):
            # 登录成功！将用户ID存入session
            session['user_id'] = user.id
            session['username'] = user.username
            return f"登录成功！欢迎，{user.username}! <a href='/'>返回首页</a>"
        else:
            return "用户名或密码错误，请重试 <a href='/'>返回首页</a>"

    return render_template('login.html')


@app.route('/logout')
def logout():
    # 清除session中的所有数据
    session.clear()
    return redirect(url_for('home'))


# 2. 定义路由和视图函数：当用户访问'/'时，执行home函数
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    current_user = get_current_user()
    post_count = len(posts)
    print(f"从数据库查询到 {post_count} 篇文章")
    return render_template('index.html', posts = posts, post_count = post_count, current_user=current_user)


@app.route('/create', methods=['GET', 'POST'])  # 允许GET（访问页面）和POST（提交表单）两种请求
def create_post():
    # 1. 权限检查：未登录用户重定向到登录页
    if 'user_id' not in session:
        flash('请先登录后再发布文章', 'warning')
        return redirect(url_for('login'))

    # 获取当前用户对象（因为后面会用到）
    current_user_obj = User.query.get(session['user_id'])

    if request.method == 'POST':
        # 1. 从表单获取用户输入的数据
        title = request.form['title']
        content = request.form['content']

        # 2. 创建新的Post对象（此时created_at会自动设为当前时间）
        new_post = Post(title=title, content=content, user_id=current_user_obj.id)

        # 3. 保存到数据库（熟悉的流程）
        db.session.add(new_post)
        db.session.commit()

        # 4. 发布成功后，跳转回首页查看新文章
        return redirect(url_for('home'))

        # 如果请求方法是‘GET‘，则渲染表单页面
    return render_template('create.html')


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):  # 接收URL中的 post_id 参数
    # 1. 先检查用户是否登录
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))

    # 2. 获取要编辑的文章
    post = Post.query.get_or_404(post_id)

    # 3. 权限验证：检查当前用户是否是文章作者
    if post.user_id != session['user_id']:
        flash('您没有权限编辑此文章', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # 处理表单提交：更新文章对象
        post.title = request.form['title']
        post.content = request.form['content']
        # 可以加一个‘修改时间‘字段，这里用created_at代替
        db.session.commit()  # 提交修改到数据库

        return redirect(url_for('home'))

        # GET请求：渲染编辑表单，并传递当前文章对象
    return render_template('edit.html', post = post)


@app.route('/post/<int:post_id>/delete', methods=['POST'])  # 注意：只允许POST
def delete_post(post_id):
    # 1. 先检查用户是否登录
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))

    # 2. 获取要编辑的文章
    post = Post.query.get_or_404(post_id)

    # 3. 权限验证：检查当前用户是否是文章作者
    if post.user_id != session['user_id']:
        flash('您没有权限删除此文章', 'error')
        return redirect(url_for('home'))

    db.session.delete(post)  # 标记对象为待删除
    db.session.commit()      # 执行删除
    # 删除后可以加个闪现消息（下次学），这里先简单跳回首页
    return redirect(url_for('home'))


# 3. 定义“about”页面
@app.route('/about')
def about():
    # 我们可以直接渲染一个简单的模板，也可以创建一个 about.html
    # 这里先直接渲染一个模板并传递变量
    return render_template('about.html', username ='Snow')


@app.route('/weather')
def weather_dashboard():
    """天气数据面板"""
    # 获取最新天气
    latest = get_latest_weather()

    # 获取历史记录（最近10条）
    history = get_weather_history(limit=10)

    return render_template(
        'weather.html',
        latest_weather=latest,
        weather_history=history,
        current_user=get_current_user()
    )


@app.route('/weather/fetch', methods=['POST'])
def fetch_weather_now():
    """手动触发获取天气数据"""
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))

    weather_data = fetch_weather()
    if weather_data and save_weather_to_db(weather_data):
        flash('天气数据获取成功！', 'success')
    else:
        flash('获取天气数据失败，请稍后重试', 'error')

    return redirect(url_for('weather_dashboard'))

# 4. 运行应用的代码块
if __name__ == '__main__':
    # debug=True 表示调试模式开启，代码改动后服务器会自动重启
    app.run(debug=True)