#!/usr/bin/env python3
"""
天气数据抓取模块
使用 Open-Meteo 免费API：https://open-meteo.com
无需注册，无需API密钥
"""
import requests
from datetime import datetime
from models import WeatherData
from extensions import db


def fetch_weather(city='重庆', latitude=29.563, longitude=106.551):
    """
    获取指定城市的天气数据

    参数：
        city: 城市名称
        latitude: 纬度
        longitude: 经度
    """
    # Open-Meteo API 端点
    url = f"https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m"

    # 请求参数
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
        'timezone': 'auto'
    }

    try:
        print(f"正在获取 {city} 的天气数据...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()
        current = data.get('current', {})

        # 解析数据
        weather_info = {
            'city': city,
            'temperature': current.get('temperature_2m', 0),
            'humidity': current.get('relative_humidity_2m', 0),
            'wind_speed': current.get('wind_speed_10m', 0),
            'condition': _parse_weather_code(current.get('weather_code', 0))
        }

        print(f"获取成功: {weather_info}")
        return weather_info

    except requests.exceptions.RequestException as e:
        print(f"获取天气数据失败: {e}")
        return None


def _parse_weather_code(code):
    """将天气代码转换为中文描述"""
    weather_codes = {
        0: '晴天', 1: '主要晴朗', 2: '局部多云', 3: '阴天',
        45: '雾', 48: '雾凇',
        51: '小雨', 53: '中雨', 55: '大雨',
        61: '小雨', 63: '中雨', 65: '大雨',
        71: '小雪', 73: '中雪', 75: '大雪',
        80: '阵雨', 81: '强阵雨', 82: '强阵雨',
        85: '阵雪', 86: '强阵雪',
        95: '雷暴', 96: '雷暴伴有冰雹', 99: '强雷暴伴有冰雹'
    }
    return weather_codes.get(code, '未知')


def save_weather_to_db(weather_data):
    """将天气数据保存到数据库"""
    if not weather_data:
        return False

    try:
        new_record = WeatherData(
            city=weather_data['city'],
            temperature=weather_data['temperature'],
            condition=weather_data['condition'],
            humidity=weather_data['humidity'],
            wind_speed=weather_data['wind_speed']
        )

        db.session.add(new_record)
        db.session.commit()
        print(f"天气数据已保存到数据库: {new_record}")
        return True

    except Exception as e:
        print(f"保存天气数据失败: {e}")
        db.session.rollback()
        return False


def get_latest_weather(city='重庆'):
    """从数据库获取指定城市的最新天气记录"""
    return WeatherData.query.filter_by(city=city) \
        .order_by(WeatherData.recorded_at.desc()) \
        .first()


def get_weather_history(city='重庆', limit=10):
    """获取天气历史记录"""
    return WeatherData.query.filter_by(city=city) \
        .order_by(WeatherData.recorded_at.desc()) \
        .limit(limit).all()