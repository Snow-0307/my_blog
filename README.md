个人全栈博客系统

一个使用Python Flask构建的功能完整的全栈个人博客，包含用户认证、文章管理、实时天气面板，并已部署至云端。
在线访问：[https://my_blog.onrender.com](https://my-blog-wg11.onrender.com)

核心功能：
用户系统
注册与登录：安全的密码哈希存储与验证。
会话管理：基于Flask Session的登录状态保持。
权限控制：用户只能编辑和删除自己发布的文章。

博客系统
文章CRUD：完整的文章创建、读取、更新、删除功能。
Markdown支持：支持使用Markdown语法编写文章（如果已实现）。
文章归档：按时间倒序展示所有文章。

天气数据面板
实时数据：集成Open-Meteo API，展示当前城市的天气状况。
历史记录：查看最近的天气数据变化。
多城市支持：可轻松配置扩展多个城市。

其他特性
干净的代码架构：模块化设计，避免循环依赖。

技术栈
后端框架：Flask, Flask-SQLAlchemy, Flask-Migrate
前端模板：Jinja2, HTML5, CSS3, 少量JavaScript
数据库：SQLite / PostgreSQL
身份验证：Werkzeug Security, Flask-Login模式
API集成：Requests, JSON解析
部署平台：Render (也可一键部署至Railway, Heroku等)
代码质量：Git版本控制， PEP8风格

项目结构
my_blog/
├── app.py # Flask应用主入口
├── requirements.txt # Python依赖
├── extensions.py # Flask扩展初始化 (SQLAlchemy等)
├── models.py # 数据模型 (User, Post, WeatherData)
├── weather_fetcher.py # 天气数据抓取模块
├── migrations/ # 数据库迁移目录 (Flask-Migrate生成)
└── templates/ # Jinja2 HTML模板
  ├── base.html # 基础模板
  ├── index.html # 首页
  ├── login.html # 登录页
  ├── register.html # 注册页
  ├── create.html # 创建文章
  ├── weather.html # 天气面板
  ├── about.html # 关于我
  ├── edit.html # 编辑文章
  
致谢
感谢Flask及其生态的所有开发者。
感谢Open-Meteo提供免费的天气API。
感谢Render等平台提供便捷的部署服务。

README最后更新于：2025年12月
