"""股票市场复盘报告自动生成系统 - 主程序入口"""
import argparse
import sys
import os
from datetime import datetime
from config import config
from data_fetcher import DataFetcher
from analyzer import MarketAnalyzer
from report_generator import ReportGenerator
from notifier import notifier
from scheduler import schedule_report
from utils import get_today_str, get_report_filename


def generate_daily_report():
    """生成每日复盘报告"""
    print("=" * 50)
    print(f"开始生成股票复盘报告: {datetime.now()}")
    print("=" * 50)

    try:
        # 1. 验证配置
        print("\n[1/7] 验证配置...")
        config.validate()
        print("  配置验证通过")

        # 2. 读取配置数据
        print("\n[2/7] 读取配置...")
        positions = config.read_positions()
        watchlist = config.read_watchlist()
        preference = config.read_preference()
        print(f"  持仓股票: {len(positions)} 只")
        print(f"  关注股票: {len(watchlist)} 只")

        # 3. 采集市场数据
        print("\n[3/7] 采集市场数据...")
        fetcher = DataFetcher()
        stock_codes = config.get_stock_codes()
        market_data = fetcher.fetch_all(stock_codes)
        print(f"  指数数据: {len(market_data.get('index_data', {}))} 个")
        print(f"  个股数据: {len(market_data.get('stock_data', {}))} 个")
        print(f"  领涨板块: {len(market_data.get('sector_data', {}).get('up', []))} 个")
        print(f"  领跌板块: {len(market_data.get('sector_data', {}).get('down', []))} 个")

        # 4. 生成分析
        print("\n[4/7] 生成市场分析（调用智谱AI API）...")
        analyzer = MarketAnalyzer()

        print("  - 分析市场整体...")
        market_analysis = analyzer.analyze_market_overview(market_data)

        print("  - 分析领涨板块...")
        leading_analysis = analyzer.analyze_leading_sectors(market_data.get('sector_data', {}))

        print("  - 分析领跌板块...")
        falling_analysis = analyzer.analyze_falling_sectors(market_data.get('sector_data', {}))

        print("  - 分析持仓股票...")
        position_analysis = analyzer.analyze_position_stocks(
            positions,
            market_data.get('stock_data', {})
        )

        print("  - 分析关注股票...")
        watchlist_analysis = analyzer.analyze_watchlist_stocks(
            watchlist,
            market_data.get('stock_data', {})
        )

        print("  - 生成操作策略...")
        strategy = analyzer.generate_operation_strategy(market_data, positions, watchlist)

        # 5. 生成报告内容
        print("\n[5/7] 生成报告内容...")
        generator = ReportGenerator()
        report_content = generator.generate_report(
            market_data=market_data,
            analysis=market_analysis,
            positions=positions,
            position_analysis=position_analysis,
            watchlist=watchlist,
            watchlist_analysis=watchlist_analysis,
            strategy=strategy
        )

        # 6. 保存报告到reports目录（用于GitHub Actions）
        print("\n[6/7] 保存报告到reports目录...")
        report_filename = get_report_filename()
        local_report_path = os.path.join(os.path.dirname(__file__), 'reports', report_filename)
        with open(local_report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"  报告已保存: {local_report_path}")

        # 如果本地有Obsidian Vault，也保存一份
        if config.obsidian_vault_path and os.path.exists(config.obsidian_vault_path):
            try:
                obsidian_report_path = generator.save_report(report_content)
                print(f"  Obsidian报告已保存: {obsidian_report_path}")
            except Exception as e:
                print(f"  Obsidian保存失败（云端环境正常）: {e}")

        # 7. 发送完整报告到飞书
        print("\n[7/7] 发送完整报告到飞书...")
        notifier.send_full_report(report_content)

        print("\n" + "=" * 50)
        print("报告生成完成！")
        print("=" * 50)
        print(f"\n市场情绪: {market_analysis.get('sentiment')}")
        print(f"明日趋势: {market_analysis.get('tomorrow_trend')}")
        print(f"仓位建议: {strategy.get('position_suggestion')}")
        print(f"关键指令: {strategy.get('key_instruction')}")

        return True

    except Exception as e:
        error_msg = f"报告生成失败: {str(e)}"
        print(f"\n❌ {error_msg}")
        # 发送错误通知
        notifier.send_error_notification(error_msg)
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='股票市场复盘报告自动生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --generate           # 立即生成今日报告
  python main.py --schedule           # 启动定时任务（每日15:30）
  python main.py --schedule --test    # 测试模式（5分钟后执行）

GitHub Actions:
  代码推送到GitHub后，每天15:30（UTC 07:30）自动生成报告
        """
    )
    parser.add_argument(
        '--generate', '-g',
        action='store_true',
        help='立即生成今日报告'
    )
    parser.add_argument(
        '--schedule', '-s',
        action='store_true',
        help='启动定时任务'
    )
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='测试模式（与--schedule配合使用）'
    )

    args = parser.parse_args()

    if args.generate:
        # 立即生成报告
        success = generate_daily_report()
        sys.exit(0 if success else 1)
    elif args.schedule:
        # 启动定时任务
        schedule_report(generate_daily_report, test_mode=args.test)
    else:
        # 默认行为：显示帮助
        parser.print_help()


if __name__ == '__main__':
    main()
