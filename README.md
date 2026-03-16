# 股票市场复盘报告自动生成系统

## 功能说明

自动生成每日A股市场复盘及次日操作策略建议报告，支持：
- 自动采集市场数据（指数、板块、个股）
- 基于数据生成分析建议（短线+技术面+情绪面）
- 填充模板生成Markdown报告
- **飞书推送完整报告**
- **GitHub Actions 自动运行**（电脑不开机也能工作）

---

## 部署方式

### 方式一：GitHub Actions（推荐，无需本地电脑）

1. **Fork 本项目到你的 GitHub**

2. **配置 GitHub Secrets**

   进入 GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret，添加以下密钥：

   | Secret名称 | 值 |
   |------------|-----|
   | `ZHIPUAI_API_KEY` | 智谱AI API Key |
   | `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL |
   | `ZHIPUAI_MODEL` | glm-4-plus（可选） |

3. **推送代码到 GitHub**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/stock-reporter.git
   git push -u origin main
   ```

4. **等待 GitHub Actions 首次运行**

   - 自动触发：每天 15:30（北京时间）
   - 手动触发：进入 Actions 标签页，选择 "每日股票复盘报告" → Run workflow

5. **查看报告**

   - 飞书自动推送完整报告
   - GitHub Actions 日志查看执行情况
   - 报告文件保存在仓库的 `reports/` 目录

---

### 方式二：本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key 和 Webhook URL
```

#### 3. 立即生成报告

```bash
python3 main.py --generate
```

#### 4. 启动定时任务

```bash
python3 main.py --schedule
```

---

## 配置文件

编辑你的 `stocks_config.json` 来配置持仓和关注股票。

- **本地运行**：`/Users/cece/Documents/Obsidian Vault/投资/stocks_config.json`
- **GitHub Actions**：需要在 GitHub 中配置（当前从用户配置读取，后续可改进）

---

## 命令说明

| 命令 | 说明 |
|------|------|
| `python3 main.py --generate` | 立即生成今日报告 |
| `python3 main.py --schedule` | 启动本地定时任务 |
| `python3 main.py --schedule --test` | 测试模式（5分钟后执行） |
| `python3 main.py --help` | 查看帮助 |

---

## GitHub Actions 定时

| 配置 | 值 |
|------|-----|
| 执行时间 | 每天 15:30（北京时间） |
| 执行日期 | 周一到周五 |
| 时区 | UTC 07:30 = 北京 15:30 |

如需修改执行时间，编辑 `.github/workflows/daily-report.yml` 中的 cron 表达式。

---

## 报告位置

| 环境 | 路径 |
|------|------|
| GitHub Actions | 仓库 `reports/` 目录 |
| 本地运行 | `reports/` 目录 |
| Obsidian（本地） | `/Users/cece/Documents/Obsidian Vault/投资/` |

---

## 项目结构

```
stock-reporter/
├── .github/workflows/    # GitHub Actions 配置
│   └── daily-report.yml
├── reports/              # 生成的报告文件
├── analyzer.py           # 智谱AI 分析模块
├── config.py            # 配置读取
├── data_fetcher.py      # AkShare 数据采集
├── main.py              # 主程序
├── notifier.py          # 飞书推送
├── report_generator.py   # 报告生成
├── requirements.txt      # Python 依赖
└── README.md           # 本文件
```

