import re
import datetime
from dateutil import parser as date_parser

def parse_date(date_str):
    """解析日期字符串为日期对象"""
    if not date_str:
        return None
    
    # 清理日期字符串
    date_str = re.sub(r'[\u4e00-\u9fa5]+', '', date_str).strip()
    date_str = re.sub(r'[年月]', '-', date_str)
    date_str = re.sub(r'[日号]', '', date_str)
    
    try:
        return date_parser.parse(date_str).date()
    except Exception as e:
        print(f"解析日期 '{date_str}' 失败: {str(e)}")
        return None

def get_today():
    """获取今天的日期"""
    return datetime.date.today()

def format_date(date_obj, fmt='%Y-%m-%d'):
    """格式化日期对象为字符串"""
    if not date_obj:
        return None
    return date_obj.strftime(fmt)

def get_date_range(start_date, end_date=None):
    """获取日期范围内的所有日期"""
    if not end_date:
        end_date = get_today()
    
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    return dates

def is_valid_date(date_str):
    """检查是否为有效的日期字符串"""
    return parse_date(date_str) is not None