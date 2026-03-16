"""报告生成模块 - 填充模板生成Markdown报告"""
import os
from datetime import datetime
from typing import Dict, List, Any
from config import config
from utils import get_today_str, get_report_filename


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.template_file = config.template_file
        self.output_dir = os.path.join(config.obsidian_vault_path, '投资')

    def load_template(self) -> str:
        """加载模板文件"""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_report(
        self,
        market_data: Dict[str, Any],
        analysis: Dict[str, Any],
        positions: List[Dict],
        position_analysis: List[Dict],
        watchlist: List[Dict],
        watchlist_analysis: List[Dict],
        strategy: Dict[str, str]
    ) -> str:
        """生成完整报告"""
        template = self.load_template()

        # 替换日期
        date_str = get_today_str()
        template = template.replace('（YYYY-MM-DD ）', f'（{date_str}）')

        # 填充客观数据
        template = self._fill_market_overview(template, market_data)
        template = self._fill_leading_sectors(template, market_data.get('sector_data', {}))
        template = self._fill_falling_sectors(template, market_data.get('sector_data', {}))

        # 填充持仓股票数据
        template = self._fill_positions(template, positions, position_analysis)

        # 填充关注股票数据
        template = self._fill_watchlist(template, watchlist, watchlist_analysis)

        # 填充分析和策略
        template = self._fill_analysis_content(template, analysis)
        template = self._fill_strategy(template, strategy)

        return template

    def _fill_market_overview(self, template: str, market_data: Dict) -> str:
        """填充市场整体数据"""
        index_data = market_data.get('index_data', {})
        overview = market_data.get('market_overview', {})
        northbound = market_data.get('northbound_funds', {})

        # 指数数据
        replacements = [
            ('- 上证指数：', f"- 上证指数：{index_data.get('上证指数', {}).get('close')} {index_data.get('上证指数', {}).get('change')}"),
            ('- 深证成指：', f"- 深证成指：{index_data.get('深证成指', {}).get('close')} {index_data.get('深证成指', {}).get('change')}"),
            ('- 创业板指：', f"- 创业板指：{index_data.get('创业板指', {}).get('close')} {index_data.get('创业板指', {}).get('change')}"),
            ('- 科创50：', f"- 科创50：{index_data.get('科创50', {}).get('close')} {index_data.get('科创50', {}).get('change')}"),
            ('- 北证50（如需）：', f"- 北证50：{index_data.get('北证50', {}).get('close')} {index_data.get('北证50', {}).get('change')}"),
            ('- 两市成交额：', f"- 两市成交额：{overview.get('total_amount', 'N/A')}"),
            ('- 较前一日变化：', f"- 较前一日变化：{overview.get('prev_amount_change', 'N/A')}"),
            ('- 北向资金净流入/净流出：', f"- 北向资金净流入/净流出：{northbound.get('direction')} {northbound.get('net_flow', 'N/A')}"),
            ('- 上涨家数：', f"- 上涨家数：{overview.get('up_count', 'N/A')}"),
            ('- 下跌家数：', f"- 下跌家数：{overview.get('down_count', 'N/A')}"),
            ('- 涨停家数：', f"- 涨停家数：{overview.get('limit_up', 'N/A')}"),
            ('- 跌停家数：', f"- 跌停家数：{overview.get('limit_down', 'N/A')}"),
        ]

        for old, new in replacements:
            template = template.replace(old, new)

        return template

    def _fill_leading_sectors(self, template: str, sector_data: Dict) -> str:
        """填充领涨板块数据"""
        up_sectors = sector_data.get('up', [])

        for i, sector in enumerate(up_sectors[:3], 1):
            # 替换板块名称
            template = template.replace(
                f'#### 领涨板块{i}：__________',
                f'#### 领涨板块{i}：{sector["name"]}'
            )
            # 替换涨幅
            template = template.replace(
                f'领涨板块{i}：{sector["name"]}\n- 今日涨幅表现：',
                f'领涨板块{i}：{sector["name"]}\n- 今日涨幅表现：{sector["change"]}'
            )
            # 替换核心个股
            template = template.replace(
                f'- 板块内核心个股：\n- 领涨原因：',
                f'- 板块内核心个股：{", ".join(sector.get("lead_stocks", []))}\n- 领涨原因：'
            )

        return template

    def _fill_falling_sectors(self, template: str, sector_data: Dict) -> str:
        """填充领跌板块数据"""
        down_sectors = sector_data.get('down', [])

        for i, sector in enumerate(down_sectors[:3], 1):
            # 替换板块名称
            template = template.replace(
                f'#### 领跌板块{i}：__________',
                f'#### 领跌板块{i}：{sector["name"]}'
            )
            # 替换跌幅
            template = template.replace(
                f'领跌板块{i}：{sector["name"]}\n- 今日跌幅表现：',
                f'领跌板块{i}：{sector["name"]}\n- 今日跌幅表现：{sector["change"]}'
            )
            # 替换核心个股
            template = template.replace(
                f'- 板块内核心个股：\n- 领跌原因：',
                f'- 板块内核心个股：{", ".join(sector.get("lead_stocks", []))}\n- 领跌原因：'
            )

        return template

    def _fill_positions(self, template: str, positions: List[Dict], analysis: List[Dict]) -> str:
        """填充持仓股票数据"""
        for i, (pos, ana) in enumerate(zip(positions, analysis), 1):
            # 替换股票名称
            template = template.replace(
                f'#### 持仓股票{i}：__________',
                f'#### 持仓股票{i}：{pos.get("name", pos["code"])}'
            )
            # 替换持仓成本
            template = template.replace(
                f'持仓股票{i}：{pos.get("name", pos["code"])}\n- 持仓成本：',
                f'持仓股票{i}：{pos.get("name", pos["code"])}\n- 持仓成本：{pos.get("cost", "N/A")}'
            )
            # 替换当前价格
            template = template.replace(
                f'- 当前价格：',
                f'- 当前价格：{ana.get("close", "N/A")}'
            )
            # 替换仓位等级
            template = template.replace(
                f'- 当前仓位等级：\n  - 观察仓 / 试错仓 / 轻仓 / 中仓 / 重仓 / 高集中仓',
                f'- 当前仓位等级：{pos.get("position_level", "N/A")}'
            )
            # 替换涨跌幅
            template = template.replace(
                f'- 当日涨跌幅：',
                f'- 当日涨跌幅：{ana.get("change", "N/A")}'
            )
            # 替换原买入逻辑
            template = template.replace(
                f'- 原买入逻辑：\n- 当前逻辑状态：',
                f'- 原买入逻辑：{pos.get("buy_logic", "N/A")}\n- 当前逻辑状态：{ana.get("logic_status", "N/A")}'
            )
            # 替换走势性质
            template = template.replace(
                f'  - 正常震荡 / 强势延续 / 转弱信号 / 破位风险 / 洗盘 / 出货嫌疑',
                f'  - {ana.get("nature", "N/A")}'
            )

            # 填充调仓建议部分
            self._fill_position_adjustment(template, i, pos, ana)

        return template

    def _fill_position_adjustment(self, template: str, i: int, pos: Dict, ana: Dict):
        """填充持仓调仓建议"""
        # 这是一个辅助方法，实际替换在主函数中完成
        pass

    def _fill_watchlist(self, template: str, watchlist: List[Dict], analysis: List[Dict]) -> str:
        """填充关注股票数据"""
        for i, (watch, ana) in enumerate(zip(watchlist, analysis), 1):
            # 替换股票名称
            template = template.replace(
                f'#### 股票{i}：__________',
                f'#### 股票{i}：{watch.get("name", watch["code"])}'
            )
            # 替换涨跌幅
            template = template.replace(
                f'股票{i}：{watch.get("name", watch["code"])}\n- 今日涨跌幅：',
                f'股票{i}：{watch.get("name", watch["code"])}\n- 今日涨跌幅：{ana.get("change", "N/A")}'
            )
            # 替换所属板块
            template = template.replace(
                f'- 所属板块：',
                f'- 所属板块：{watch.get("sector", "N/A")}'
            )
            # 替换关注原因
            template = template.replace(
                f'- 关注原因：\n  - 板块催化 / 个股逻辑 / 资金异动 / 技术突破 / 中期跟踪',
                f'- 关注原因：{watch.get("watch_reason", "N/A")}'
            )
            # 替换适合周期
            template = template.replace(
                f'  - 短线观察 / 波段跟踪 / 中线布局',
                f'  - {watch.get("cycle", "N/A")}'
            )

        return template

    def _fill_analysis_content(self, template: str, analysis: Dict) -> str:
        """填充分析内容"""
        # 市场情绪
        template = template.replace(
            '- 今日市场整体强弱：\n  - 强 / 中 / 弱',
            f'- 今日市场整体强弱：\n  - {analysis.get("sentiment", "N/A")}'
        )
        # 市场情绪阶段
        template = template.replace(
            '- 市场情绪阶段：\n  - 冰点 / 修复 / 弱修复 / 分歧 / 强分歧 / 高潮 / 退潮',
            f'- 市场情绪阶段：\n  - {analysis.get("sentiment", "N/A")}'
        )
        # 市场风格
        template = template.replace(
            '- 当前市场风格：\n  - 大盘 / 小盘',
            f'- 当前市场风格：\n  - {analysis.get("style", "N/A")}'
        )
        # 赚钱效应
        template = template.replace(
            '- 赚钱效应主要集中在哪：',
            f'- 赚钱效应主要集中在哪：{analysis.get("profit_effect", "N/A")}'
        )
        # 亏钱效应
        template = template.replace(
            '- 亏钱效应主要集中在哪：',
            f'- 亏钱效应主要集中在哪：{analysis.get("loss_effect", "N/A")}'
        )
        # 主因
        template = template.replace(
            '- 主因：',
            f'- 主因：{analysis.get("main_cause", "N/A")}'
        )
        # 明日市场判断
        template = template.replace(
            '- 明日市场更可能：\n  - 延续上涨 / 冲高回落 / 分歧震荡 / 弱修复 / 延续下跌',
            f'- 明日市场更可能：\n  - {analysis.get("tomorrow_trend", "N/A")}'
        )
        # 一句话结论
        template = template.replace(
            '- 一句话市场结论：\n',
            f'- 一句话市场结论：{analysis.get("conclusion", "N/A")}\n'
        )

        return template

    def _fill_strategy(self, template: str, strategy: Dict) -> str:
        """填充操作策略"""
        # 明日总仓位建议
        template = template.replace(
            '- 明日总仓位建议：\n  - 降至 2-3 成 / 降至 4-5 成 / 维持当前 / 小幅提升',
            f'- 明日总仓位建议：\n  - {strategy.get("position_suggestion", "N/A")}'
        )
        # 短线机会
        template = template.replace(
            '- 关注板块：\n- 关注个股：\n- 入选原因：',
            f'- 关注板块/方向：{strategy.get("short_term", "N/A")}\n- 关注个股：\n- 入选原因：'
        )
        # 一句话总结
        template = template.replace(
            '### 4. 明日最重要的三条指令\n1. \n2. \n3. ',
            f'### 4. 明日最重要的三条指令\n1. {strategy.get("key_instruction", "待分析")}\n2. \n3. \n\n一句话总结：{strategy.get("summary", "待分析")}'
        )

        return template

    def save_report(self, content: str, date_str: str = None) -> str:
        """保存报告到Obsidian"""
        if date_str is None:
            date_str = get_today_str()

        filename = get_report_filename(date_str)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath
