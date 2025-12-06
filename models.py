# models.py - 存放所有数据模型
from datetime import datetime
from extensions import db

# --- 定义数据模型 (Model) ---
# 定义用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # 字段名改为 password_hash 更语义化，表示存储的是“哈希值”而非明文
    password_hash = db.Column(db.String(128), nullable=False)
    # 建立与Post的关系（一个用户可有多篇文章）
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# 定义文章表
class Post(db.Model):
    # 定义表中的列
    id = db.Column(db.Integer, primary_key=True)  # 主键，唯一标识
    title = db.Column(db.String(100), nullable=False)  # 标题，非空，最大100个字符
    content = db.Column(db.Text, nullable=False)  # 内容，非空，长文本
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)  # 创建时间，自动设为当前时间
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=1)

    # 可选：定义对象打印格式，方便调试
    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"


# 定义天气表
class WeatherData(db.Model):
    """天气数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)  # 温度
    condition = db.Column(db.String(50), nullable=False)  # 天气状况
    humidity = db.Column(db.Integer)  # 湿度
    wind_speed = db.Column(db.Float)  # 风速
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"WeatherData('{self.city}', {self.temperature}°C, '{self.condition}')"