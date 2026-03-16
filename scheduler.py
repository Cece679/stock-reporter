"""定时任务模块 - 使用APScheduler"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time, timedelta
from data_fetcher import DataFetcher


class ReportScheduler:
    """报告定时任务调度器"""

    def __init__(self, test_mode=False):
        self.scheduler = BlockingScheduler(timezone='Asia/Shanghai')
        self.test_mode = test_mode
        self.fetcher = DataFetcher()

    def is_trading_day(self, check_date=None) -> bool:
        """判断是否为交易日"""
        return self.fetcher.is_trading_day(check_date)

    def _run_task(self, task_func, *args, **kwargs):
        """执行任务的包装函数"""
        try:
            print(f"=== 任务开始执行: {datetime.now()} ===")

            # 检查是否为交易日
            if not self.is_trading_day():
                print(f"今日非交易日，跳过任务执行")
                return

            # 执行任务
            result = task_func(*args, **kwargs)

            print(f"=== 任务执行完成 ===")
            return result

        except Exception as e:
            print(f"任务执行出错: {e}")
            raise

    def schedule_daily_report(self, task_func, test_time_minutes=5):
        """
        设置每日报告定时任务

        Args:
            task_func: 要执行的任务函数
            test_time_minutes: 测试模式下，多少分钟后执行
        """
        if self.test_mode:
            # 测试模式：几分钟后执行一次
            test_time = (datetime.now() + timedelta(minutes=test_time_minutes)).time()
            print(f"测试模式：任务将在 {test_time} 执行")

            self.scheduler.add_job(
                self._run_task,
                'date',
                run_date=datetime.now() + timedelta(minutes=test_time_minutes),
                args=[task_func],
                id='test_report'
            )
        else:
            # 正式模式：每个交易日15:30执行
            print("正式模式：任务将在每个交易日15:30执行")

            self.scheduler.add_job(
                self._run_task,
                CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
                args=[task_func],
                id='daily_report',
                name='每日股票报告生成'
            )

            # 添加交易日检查的每日任务
            self.scheduler.add_job(
                self._check_and_schedule,
                CronTrigger(hour=15, minute=29),
                id='trading_day_check',
                name='交易日检查'
            )

    def _check_and_schedule(self):
        """交易日检查（预留）"""
        # 如果需要更复杂的交易日判断，可以在这里实现
        pass

    def start(self):
        """启动调度器"""
        print("定时任务调度器启动中...")
        print("按 Ctrl+C 退出")
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\n调度器已停止")
            self.scheduler.shutdown()

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()


def schedule_report(task_func, test_mode=False):
    """
    便捷函数：设置并启动定时任务

    Args:
        task_func: 要执行的任务函数
        test_mode: 是否为测试模式
    """
    scheduler = ReportScheduler(test_mode=test_mode)
    scheduler.schedule_daily_report(task_func)
    scheduler.start()
