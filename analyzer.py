"""分析模块 - 使用智谱AI生成市场分析建议"""
from zhipuai import ZhipuAI
from typing import Dict, List, Any
from config import config


class MarketAnalyzer:
    """市场分析器 - 使用智谱AI"""

    def __init__(self):
        self.client = ZhipuAI(api_key=config.zhipuai_api_key)
        self.model = config.zhipuai_model

    def _call_zhipuai(self, prompt: str, max_tokens=2000) -> str:
        """调用智谱AI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"智谱AI API调用失败: {e}")
            return "分析生成失败，请稍后重试"

    def analyze_market_overview(self, market_data: Dict[str, Any]) -> Dict[str, str]:
        """分析市场整体情况"""
        index_data = market_data.get('index_data', {})
        overview = market_data.get('market_overview', {})
        northbound = market_data.get('northbound_funds', {})

        prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。

今日市场数据如下：
指数表现：
- 上证指数: {index_data.get('上证指数', {}).get('close')} ({index_data.get('上证指数', {}).get('change')})
- 深证成指: {index_data.get('深证成指', {}).get('close')} ({index_data.get('深证成指', {}).get('change')})
- 创业板指: {index_data.get('创业板指', {}).get('close')} ({index_data.get('创业板指', {}).get('change')})
- 科创50: {index_data.get('科创50', {}).get('close')} ({index_data.get('科创50', {}).get('change')})

市场概况：
- 两市成交额: {overview.get('total_amount')}
- 上涨家数: {overview.get('up_count')}，下跌家数: {overview.get('down_count')}
- 涨停家数: {overview.get('limit_up')}，跌停家数: {overview.get('limit_down')}
- 北向资金: {northbound.get('direction')} {northbound.get('net_flow')}

请分析并回答以下问题（输出格式：每行一项，直接填写答案）：
1. 市场情绪阶段（冰点/修复/弱修复/分歧/强分歧/高潮/退潮）：
2. 当前市场风格（大盘/小盘 + 成长/价值 + 权重/题材 + 防御/进攻）：
3. 赚钱效应主要集中在哪：
4. 亏钱效应主要集中在哪：
5. 市场波动主因（宏观/政策/行业/资金/情绪）：
6. 原因性质（短期扰动/阶段切换/趋势变化）：
7. 明日市场更可能（延续上涨/冲高回落/分歧震荡/弱修复/延续下跌）：
8. 明日关键观察指标：
9. 一句话市场结论：
"""
        result = self._call_zhipuai(prompt)

        # 解析结果
        return {
            'sentiment': self._extract_line(result, '市场情绪阶段'),
            'style': self._extract_line(result, '当前市场风格'),
            'profit_effect': self._extract_line(result, '赚钱效应'),
            'loss_effect': self._extract_line(result, '亏钱效应'),
            'main_cause': self._extract_line(result, '波动主因'),
            'cause_nature': self._extract_line(result, '原因性质'),
            'tomorrow_trend': self._extract_line(result, '明日市场更可能'),
            'key_indicators': self._extract_line(result, '关键观察'),
            'conclusion': self._extract_line(result, '一句话')
        }

    def analyze_leading_sectors(self, sector_data: Dict[str, List[Dict]]) -> List[Dict[str, str]]:
        """分析领涨板块"""
        up_sectors = sector_data.get('up', [])
        results = []

        for i, sector in enumerate(up_sectors[:3], 1):
            prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。

领涨板块{i}：{sector['name']}
今日涨幅：{sector['change']}
板块内核心个股：{', '.join(sector.get('lead_stocks', []))}

请分析并回答（输出格式：每行一项，直接填写答案）：
1. 领涨原因（消息催化/政策刺激/基本面变化/资金推动/情绪扩散）：
2. 原因性质判断（短期事件驱动/中期产业趋势/资金轮动/超跌反弹）：
3. 持续性判断（强/中/弱）：
4. 明日重点观察：
5. 可能带动的相关板块：
6. 一句话判断：
"""
            result = self._call_zhipuai(prompt, max_tokens=500)
            results.append({
                'name': sector['name'],
                'change': sector['change'],
                'lead_stocks': ', '.join(sector.get('lead_stocks', [])),
                'reason': self._extract_line(result, '领涨原因'),
                'nature': self._extract_line(result, '原因性质'),
                'continuity': self._extract_line(result, '持续性'),
                'observe': self._extract_line(result, '明日重点观察'),
                'related_sectors': self._extract_line(result, '相关板块'),
                'conclusion': self._extract_line(result, '一句话')
            })

        return results

    def analyze_falling_sectors(self, sector_data: Dict[str, List[Dict]]) -> List[Dict[str, str]]:
        """分析领跌板块"""
        down_sectors = sector_data.get('down', [])
        results = []

        for i, sector in enumerate(down_sectors[:3], 1):
            prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。

领跌板块{i}：{sector['name']}
今日跌幅：{sector['change']}
板块内核心个股：{', '.join(sector.get('lead_stocks', []))}

请分析并回答（输出格式：每行一项，直接填写答案）：
1. 领跌原因（利空消息/业绩压力/估值压缩/资金撤退/高位兑现/情绪退潮）：
2. 原因性质判断（趋势转弱/短期回调/高位补跌/板块切换）：
3. 是否可能继续拖累（是/否/需观察）：
4. 可能影响的相关板块：
5. 一句话判断：
"""
            result = self._call_zhipuai(prompt, max_tokens=500)
            results.append({
                'name': sector['name'],
                'change': sector['change'],
                'lead_stocks': ', '.join(sector.get('lead_stocks', [])),
                'reason': self._extract_line(result, '领跌原因'),
                'nature': self._extract_line(result, '原因性质'),
                'will_drag': self._extract_line(result, '继续拖累'),
                'related_sectors': self._extract_line(result, '相关板块'),
                'conclusion': self._extract_line(result, '一句话')
            })

        return results

    def analyze_position_stocks(self, positions: List[Dict], stock_data: Dict) -> List[Dict[str, str]]:
        """分析持仓股票"""
        results = []

        for position in positions:
            code = position['code']
            stock_info = stock_data.get(code, {})

            prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。

持仓股票：{position.get('name', code)}
持仓成本：{position.get('cost', 'N/A')}
当前价格：{stock_info.get('close', 'N/A')}
当日涨跌幅：{stock_info.get('change', 'N/A')}
当前仓位等级：{position.get('position_level', 'N/A')}
原买入逻辑：{position.get('buy_logic', 'N/A')}

请分析并回答（输出格式：每行一项，直接填写答案）：
1. 今日走势表现（高开低走/低开高走/冲高回落/缩量震荡/放量上涨/放量下跌）：
2. 波动原因分析（大盘影响/板块影响/个股消息面/资金面/技术面）：
3. 当前走势性质（正常震荡/强势延续/转弱信号/破位风险/洗盘/出货嫌疑）：
4. 当前逻辑状态（未变化/部分削弱/明显变化/已证伪）：
5. 若继续持有，主要博弈点：
6. 若继续持有，最大风险：
7. 明日重点观察信号：
8. 一句话结论：
"""
            result = self._call_zhipuai(prompt, max_tokens=500)
            results.append({
                'code': code,
                'name': position.get('name', code),
                'cost': position.get('cost', 'N/A'),
                'close': stock_info.get('close', 'N/A'),
                'change': stock_info.get('change', 'N/A'),
                'position_level': position.get('position_level', 'N/A'),
                'trend': self._extract_line(result, '今日走势表现'),
                'reason': self._extract_line(result, '波动原因分析'),
                'nature': self._extract_line(result, '走势性质'),
                'logic_status': self._extract_line(result, '逻辑状态'),
                'hold_reason': self._extract_line(result, '主要博弈点'),
                'risk': self._extract_line(result, '最大风险'),
                'observe': self._extract_line(result, '重点观察'),
                'conclusion': self._extract_line(result, '一句话')
            })

        return results

    def analyze_watchlist_stocks(self, watchlist: List[Dict], stock_data: Dict) -> List[Dict[str, str]]:
        """分析关注股票"""
        results = []

        for watch in watchlist:
            code = watch['code']
            stock_info = stock_data.get(code, {})

            prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。

关注股票：{watch.get('name', code)}
今日涨跌幅：{stock_info.get('change', 'N/A')}
所属板块：{watch.get('sector', 'N/A')}
关注原因：{watch.get('watch_reason', 'N/A')}
适合周期：{watch.get('cycle', 'N/A')}

请分析并回答（输出格式：每行一项，直接填写答案）：
1. 今日表现强弱（强/中/弱）：
2. 今日波动原因分析：
3. 当前是否进入可操作区间（是/否/继续观察）：
4. 若买入，主要逻辑：
5. 若不买入，主要顾虑：
6. 明日重点观察条件：
7. 一句话结论：
"""
            result = self._call_zhipuai(prompt, max_tokens=500)
            results.append({
                'code': code,
                'name': watch.get('name', code),
                'change': stock_info.get('change', 'N/A'),
                'sector': watch.get('sector', 'N/A'),
                'strength': self._extract_line(result, '表现强弱'),
                'reason': self._extract_line(result, '波动原因'),
                'operable': self._extract_line(result, '可操作区间'),
                'buy_logic': self._extract_line(result, '买入逻辑'),
                'concern': self._extract_line(result, '主要顾虑'),
                'observe': self._extract_line(result, '重点观察'),
                'conclusion': self._extract_line(result, '一句话')
            })

        return results

    def generate_operation_strategy(self, all_data: Dict, positions: List, watchlist: List) -> Dict[str, str]:
        """生成明日操作策略"""
        prompt = f"""你是一个专业的A股市场分析师，擅长短线交易，主要从技术面和情绪面分析。
投资偏好：优先短线，其次中线；不信长线；量化主导，轮动快。

基于以下数据，生成明日操作策略：

市场概况：{all_data.get('market_overview', {})}
北向资金：{all_data.get('northbound_funds', {})}
领涨板块：{', '.join([s['name'] for s in all_data.get('sector_data', {}).get('up', [])])}
领跌板块：{', '.join([s['name'] for s in all_data.get('sector_data', {}).get('down', [])])}

请回答（输出格式：每行一项，直接填写答案）：
1. 明日总仓位建议（降至2-3成/降至4-5成/维持当前/小幅提升）：
2. 最值得新增跟踪的板块/方向：
3. 短线机会（1-3个交易日）重点关注：
4. 中短期机会（1-4周）重点关注：
5. 需要规避的风险方向：
6. 明日最重要的操作指令：
7. 一句话操作总结：
"""
        result = self._call_zhipuai(prompt, max_tokens=800)

        return {
            'position_suggestion': self._extract_line(result, '总仓位建议'),
            'focus_direction': self._extract_line(result, '值得新增跟踪'),
            'short_term': self._extract_line(result, '短线机会'),
            'medium_term': self._extract_line(result, '中短期机会'),
            'risk_avoid': self._extract_line(result, '规避风险'),
            'key_instruction': self._extract_line(result, '重要指令'),
            'summary': self._extract_line(result, '一句话总结')
        }

    def _extract_line(self, text: str, keyword: str) -> str:
        """从文本中提取包含关键词的行"""
        for line in text.split('\n'):
            if keyword in line:
                # 提取冒号后面的内容
                if '：' in line:
                    return line.split('：')[-1].strip()
                elif ':' in line:
                    return line.split(':')[-1].strip()
        return text.strip()[:100] if text else '暂无分析'
