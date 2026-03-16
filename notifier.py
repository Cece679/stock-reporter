"""飞书推送模块"""
import requests
import json
from typing import Dict, Any
from config import config
from utils import get_today_str


class FeishuNotifier:
    """飞书机器人通知器"""

    def __init__(self):
        self.webhook_url = config.feishu_webhook_url
        self.max_length = 2000  # 飞书消息长度限制

    def send_notification(
        self,
        title: str,
        market_summary: Dict[str, str],
        strategy: Dict[str, str],
        report_path: str = None
    ) -> bool:
        """发送飞书通知"""
        if not self.webhook_url:
            print("飞书Webhook未配置，跳过通知")
            return False

        content = self._format_message(title, market_summary, strategy, report_path)

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "msg_type": "text",
                    "content": {"text": content}
                }),
                timeout=10
            )
            response.raise_for_status()
            print("飞书通知发送成功")
            return True
        except Exception as e:
            print(f"飞书通知发送失败: {e}")
            return False

    def _format_message(
        self,
        title: str,
        market_summary: Dict[str, str],
        strategy: Dict[str, str],
        report_path: str = None
    ) -> str:
        """格式化飞书消息"""
        date_str = get_today_str()

        message = f"📊 {title} ({date_str})\n\n"
        message += "【市场概览】\n"
        message += f"市场情绪: {market_summary.get('sentiment', 'N/A')}\n"
        message += f"市场风格: {market_summary.get('style', 'N/A')}\n"
        message += f"明日趋势: {market_summary.get('tomorrow_trend', 'N/A')}\n"
        message += f"一句话: {market_summary.get('conclusion', 'N/A')}\n\n"

        message += "【操作建议】\n"
        message += f"总仓位: {strategy.get('position_suggestion', 'N/A')}\n"
        message += f"关注方向: {strategy.get('focus_direction', 'N/A')}\n"
        message += f"短线机会: {strategy.get('short_term', 'N/A')}\n"
        message += f"规避风险: {strategy.get('risk_avoid', 'N/A')}\n"
        message += f"关键指令: {strategy.get('key_instruction', 'N/A')}\n"

        if report_path:
            message += f"\n完整报告已保存到Obsidian"

        # 截断超长消息
        if len(message) > self.max_length:
            message = message[:self.max_length - 10] + "..."

        return message

    def send_error_notification(self, error_msg: str) -> bool:
        """发送错误通知"""
        if not self.webhook_url:
            return False

        message = f"⚠️ 股票报告生成失败 ({get_today_str()})\n{error_msg}"

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "msg_type": "text",
                    "content": {"text": message}
                }),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"错误通知发送失败: {e}")
            return False

    def send_card_notification(
        self,
        title: str,
        market_summary: Dict[str, str],
        strategy: Dict[str, str]
    ) -> bool:
        """发送飞书卡片消息（更美观）"""
        if not self.webhook_url:
            print("飞书Webhook未配置，跳过通知")
            return False

        card_content = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"{title} ({get_today_str()})",
                    "tag": "plain_text"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**市场情绪**\n{market_summary.get('sentiment', 'N/A')}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**市场风格**\n{market_summary.get('style', 'N/A')}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**明日趋势**\n{market_summary.get('tomorrow_trend', 'N/A')}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**总仓位建议**\n{strategy.get('position_suggestion', 'N/A')}",
                                "tag": "lark_md"
                            }
                        }
                    ]
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"**一句话总结**: {strategy.get('summary', 'N/A')}",
                        "tag": "lark_md"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "msg_type": "interactive",
                    "card": card_content
                }),
                timeout=10
            )
            response.raise_for_status()
            print("飞书卡片通知发送成功")
            return True
        except Exception as e:
            print(f"飞书卡片通知发送失败: {e}")
            # 降级到文本消息
            return self.send_notification(title, market_summary, strategy)


    def send_full_report(self, report_content: str, date_str: str = None) -> bool:
        """发送完整报告到飞书"""
        if not self.webhook_url:
            print("飞书Webhook未配置，跳过通知")
            return False

        if date_str is None:
            date_str = get_today_str()

        # 由于飞书消息长度限制，将报告分段发送
        # 使用富文本格式发送完整报告
        sections = self._split_report(report_content)

        for i, section in enumerate(sections, 1):
            title = f"📊 股票复盘报告 ({date_str}) - 第{i}部分" if len(sections) > 1 else f"📊 股票复盘报告 ({date_str})"
            success = self._send_text_message(title, section)
            if not success:
                return False

        print(f"完整报告已分{len(sections)}部分发送")
        return True

    def _split_report(self, report: str, max_length=15000) -> list:
        """将报告分成多个部分"""
        # 飞书富文本消息限制较长，我们按章节分割
        lines = report.split('\n')
        sections = []
        current_section = ""
        current_length = 0

        for line in lines:
            line_length = len(line)
            if current_length + line_length > max_length and current_section:
                sections.append(current_section)
                current_section = line + '\n'
                current_length = line_length + 1
            else:
                current_section += line + '\n'
                current_length += line_length + 1

        if current_section:
            sections.append(current_section)

        return sections

    def _send_text_message(self, title: str, content: str) -> bool:
        """发送文本消息"""
        try:
            # 使用富文本消息格式
            message = f"{title}\n\n{content}"

            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": f"{title}",
                                "content": [
                                    [{"tag": "text", "text": content}]
                                ]
                            }
                        }
                    }
                }),
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            # 降级到普通文本
            try:
                response = requests.post(
                    self.webhook_url,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps({
                        "msg_type": "text",
                        "content": {"text": f"{title}\n\n{content}"}
                    }),
                    timeout=30
                )
                response.raise_for_status()
                return True
            except Exception as e2:
                print(f"降级发送也失败: {e2}")
                return False

# 全局通知器实例
notifier = FeishuNotifier()
