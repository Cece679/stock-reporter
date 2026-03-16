"""数据采集模块 - 使用AkShare获取A股数据"""
import akshare as ak
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from utils import format_number, format_percentage, get_today_str


class DataFetcher:
    """A股数据采集器"""

    def __init__(self):
        self.today = get_today_str()

    def get_index_data(self) -> Dict[str, Dict[str, str]]:
        """获取主要指数数据"""
        # 使用指数代码映射
        indices = {
            '上证指数': '000001',
            '深证成指': '399001',
            '创业板指': '399006',
            '科创50': '000688',
            '北证50': '899050',
        }

        result = {}
        for name, code in indices.items():
            try:
                # 使用stock_zh_index_spot_sina获取指数数据
                df = ak.stock_zh_index_spot_sina()
                if not df.empty:
                    # 查找对应指数
                    idx_data = df[df['代码'] == code]
                    if not idx_data.empty:
                        row = idx_data.iloc[0]
                        result[name] = {
                            'close': format_number(row.get('最新价')),
                            'change': format_percentage(row.get('涨跌幅', 0)),
                            'volume': format_number(row.get('成交量', 0), 0)
                        }
                    else:
                        result[name] = {'close': 'N/A', 'change': 'N/A', 'volume': 'N/A'}
                else:
                    result[name] = {'close': 'N/A', 'change': 'N/A', 'volume': 'N/A'}
            except Exception as e:
                print(f"获取 {name} 数据失败: {e}")
                result[name] = {'close': 'N/A', 'change': 'N/A', 'volume': 'N/A'}

        return result

    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概况数据"""
        try:
            # 获取A股实时数据
            df = ak.stock_zh_a_spot_em()
            if not df.empty:
                up_count = len(df[df['涨跌幅'] > 0])
                down_count = len(df[df['涨跌幅'] < 0])
                flat_count = len(df[df['涨跌幅'] == 0])

                # 涨跌停统计（ST股5%限制，普通股10%）
                limit_up = len(df[df['涨跌幅'] >= 9.8])
                limit_down = len(df[df['涨跌幅'] <= -9.8])

                # 成交额（转换为亿）
                total_amount = df['成交额'].sum() / 100000000

                return {
                    'total_amount': f"{format_number(total_amount)}亿",
                    'up_count': up_count,
                    'down_count': down_count,
                    'flat_count': flat_count,
                    'limit_up': limit_up,
                    'limit_down': limit_down,
                    'prev_amount_change': '需对比前一日数据'
                }
        except Exception as e:
            print(f"获取市场概况失败: {e}")

        return {
            'total_amount': 'N/A',
            'up_count': 'N/A',
            'down_count': 'N/A',
            'flat_count': 'N/A',
            'limit_up': 'N/A',
            'limit_down': 'N/A',
            'prev_amount_change': 'N/A'
        }

    def get_northbound_funds(self) -> Dict[str, str]:
        """获取北向资金数据"""
        try:
            # 使用stock_hsgt_fund_flow_summary_em获取北向资金概要
            df = ak.stock_hsgt_fund_flow_summary_em()
            if not df.empty:
                # 获取最近的数据
                latest = df.iloc[0]
                # 尝试获取净流入字段
                if '当日资金流向' in latest:
                    flow_value = latest['当日资金流向']
                elif '北向资金' in latest:
                    flow_value = latest['北向资金']
                else:
                    flow_value = 0

                return {
                    'net_flow': f"{format_number(flow_value)}亿" if flow_value else '0亿',
                    'direction': '净流入' if flow_value > 0 else ('净流出' if flow_value < 0 else '持平')
                }
        except Exception as e:
            print(f"获取北向资金失败: {e}")

        return {'net_flow': 'N/A', 'direction': 'N/A'}

    def get_sector_data(self, top_n=3, bottom_n=3) -> Dict[str, List[Dict]]:
        """获取板块涨跌幅数据"""
        result = {'up': [], 'down': []}

        try:
            # 获取行业板块数据
            df = ak.stock_board_industry_name_em()
            if not df.empty:
                df = df.sort_values('涨跌幅', ascending=False)

                # 领涨板块
                for _, row in df.head(top_n).iterrows():
                    result['up'].append({
                        'name': row['板块名称'],
                        'change': format_percentage(row['涨跌幅']),
                        'lead_stocks': self._get_sector_leading_stocks(row['板块名称'])
                    })

                # 领跌板块
                for _, row in df.tail(bottom_n).sort_values('涨跌幅', ascending=True).iterrows():
                    result['down'].append({
                        'name': row['板块名称'],
                        'change': format_percentage(row['涨跌幅']),
                        'lead_stocks': self._get_sector_leading_stocks(row['板块名称'])
                    })
        except Exception as e:
            print(f"获取板块数据失败: {e}")

        return result

    def _get_sector_leading_stocks(self, sector_name: str, limit=3) -> List[str]:
        """获取板块内领涨/领跌股票"""
        try:
            df = ak.stock_board_industry_cons_em(symbol=sector_name)
            if not df.empty:
                df = df.sort_values('涨跌幅', ascending=False)
                return df.head(limit)['名称'].tolist()
        except Exception:
            pass
        return []

    def get_stock_data(self, codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """获取个股数据"""
        result = {}

        try:
            # 获取所有A股实时数据
            df = ak.stock_zh_a_spot_em()
            if df.empty:
                return result

            # 转换股票代码格式
            code_map = {self._format_code(code): code for code in codes}

            for code, original_code in code_map.items():
                stock_df = df[df['代码'] == code]
                if not stock_df.empty:
                    row = stock_df.iloc[0]
                    result[original_code] = {
                        'name': row.get('名称', 'N/A'),
                        'close': format_number(row.get('最新价', row.get('收盘价'))),
                        'change': format_percentage(row.get('涨跌幅', 0)),
                        'volume': format_number(row.get('成交量', 0), 0),
                        'amount': format_number(row.get('成交额', 0) / 10000, 2),  # 万
                        'high': format_number(row.get('最高价')),
                        'low': format_number(row.get('最低价')),
                        'open': format_number(row.get('今开')),
                    }
        except Exception as e:
            print(f"获取个股数据失败: {e}")

        return result

    def _format_code(self, code: str) -> str:
        """格式化股票代码"""
        code = str(code).strip()
        # 如果是6位数字，直接返回（stock_zh_a_spot_em不需要前缀）
        if len(code) == 6 and code.isdigit():
            return code
        return code

    def is_trading_day(self, check_date: Optional[date] = None) -> bool:
        """判断是否为交易日"""
        if check_date is None:
            check_date = date.today()

        # 周末不是交易日
        if check_date.weekday() >= 5:  # 5=周六, 6=周日
            return False

        try:
            # 获取交易日历
            trade_days = ak.tool_trade_date_hist_sina()
            if trade_days is not None:
                date_str = check_date.strftime('%Y-%m-%d')
                return date_str in trade_days['trade_date'].values
        except Exception as e:
            print(f"检查交易日失败: {e}")

        # 如果无法获取交易日历，默认工作日为交易日
        return check_date.weekday() < 5

    def fetch_all(self, stock_codes: List[str]) -> Dict[str, Any]:
        """获取所有需要的数据"""
        return {
            'date': get_today_str(),
            'index_data': self.get_index_data(),
            'market_overview': self.get_market_overview(),
            'northbound_funds': self.get_northbound_funds(),
            'sector_data': self.get_sector_data(),
            'stock_data': self.get_stock_data(stock_codes)
        }
