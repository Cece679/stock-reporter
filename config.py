"""配置读取模块"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类"""

    def __init__(self):
        # 从环境变量读取Obsidian路径
        self.obsidian_vault_path = os.getenv(
            'OBSIDIAN_VAULT_PATH',
            '/Users/cece/Documents/Obsidian Vault'
        )
        self.config_file = os.path.join(self.obsidian_vault_path, '投资', 'stocks_config.json')

        # API配置
        self.zhipuai_api_key = os.getenv('ZHIPUAI_API_KEY')
        self.feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
        self.zhipuai_model = os.getenv('ZHIPUAI_MODEL', 'glm-4-plus')

        # 模板文件
        self.template_file = os.path.join(
            self.obsidian_vault_path,
            '投资',
            '股票市场复盘及操作策略建议（YYYY-MM-DD ）.md'
        )

    def read_config(self) -> Dict[str, Any]:
        """读取完整配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def read_positions(self) -> List[Dict[str, Any]]:
        """读取持仓股票"""
        config = self.read_config()
        return config.get('positions', [])

    def read_watchlist(self) -> List[Dict[str, Any]]:
        """读取关注股票"""
        config = self.read_config()
        return config.get('watchlist', [])

    def read_preference(self) -> Dict[str, Any]:
        """读取交易偏好"""
        config = self.read_config()
        return config.get('preference', {})

    def get_stock_codes(self) -> List[str]:
        """获取所有股票代码（持仓+关注）"""
        positions = self.read_positions()
        watchlist = self.read_watchlist()

        codes = [p['code'] for p in positions] + [w['code'] for w in watchlist]
        return list(set(codes))

    def validate(self) -> bool:
        """验证配置是否完整"""
        if not self.zhipuai_api_key:
            raise ValueError("ZHIPUAI_API_KEY 未设置")
        if not self.feishu_webhook_url:
            raise ValueError("FEISHU_WEBHOOK_URL 未设置")
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        if not os.path.exists(self.template_file):
            raise FileNotFoundError(f"模板文件不存在: {self.template_file}")
        return True


# 全局配置实例
config = Config()
