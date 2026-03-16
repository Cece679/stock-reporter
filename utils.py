"""工具函数模块"""
from datetime import datetime, date, timedelta
import time


def format_number(num, decimals=2):
    """格式化数字"""
    if num is None:
        return 'N/A'
    try:
        return f"{float(num):.{decimals}f}"
    except (ValueError, TypeError):
        return str(num)


def format_percentage(num, decimals=2):
    """格式化百分比"""
    if num is None:
        return 'N/A'
    try:
        return f"{float(num)*100:+.2f}%"
    except (ValueError, TypeError):
        return str(num)


def get_today_str():
    """获取今日日期字符串"""
    return datetime.now().strftime('%Y-%m-%d')


def get_report_filename(date_str=None):
    """生成报告文件名"""
    if date_str is None:
        date_str = get_today_str()
    return f"股票市场复盘及操作策略建议（{date_str}）.md"


def retry_on_failure(func, max_retries=3, delay=2):
    """失败重试装饰器"""
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
        raise last_exception
    return wrapper
