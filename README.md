# 📊 TradeChill · 交易冷静期助手

> **管理交易情绪，做出更理性的投资决策**
>
> *"在金融市场中，最大的敌人往往是你自己。"*

---

## ✨ 核心理念

TradeChill 基于行为金融学的研究成果，帮助个人投资者：

- 🧠 **识别情绪驱动** — 记录交易时的情绪状态（FOMO、恐慌、贪婪…）
- ⏳ **强制冷静期** — 根据情绪自动建议冷静时长，倒计时强制执行
- 🔍 **发现行为陷阱** — 检测频繁交易、追涨杀跌等不理性模式
- 📝 **冷静后复盘** — 对比冲动决策 vs 冷静后的理性判断
- 📊 **数据看板** — 可视化你的投资行为模式

---

## 🚀 功能一览

| 命令 | 功能 | Emoji |
|------|------|-------|
| `tradechill portfolio add` | 添加持仓 | 📦 |
| `tradechill portfolio list` | 查看持仓列表 | 📋 |
| `tradechill portfolio update` | 更新持仓 | ✏️ |
| `tradechill portfolio remove` | 删除持仓 | 🗑️ |
| `tradechill impulse record` | 记录交易冲动 | 💭 |
| `tradechill impulse list` | 查看冲动记录 | 📜 |
| `tradechill cooldown start` | 开始冷静期 | ⏳ |
| `tradechill cooldown status` | 查看冷静期状态 | 📊 |
| `tradechill cooldown list` | 冷静期历史 | 📋 |
| `tradechill traps check` | 检测行为陷阱 | 🔍 |
| `tradechill traps history` | 查看检测历史 | 📜 |
| `tradechill review pending` | 待复盘列表 | 📝 |
| `tradechill review do` | 执行复盘 | ✅ |
| `tradechill review compare` | 冷静前后对比 | 📊 |
| `tradechill dashboard` | 数据看板 | 📊 |

---

## 📦 安装

### 通过 pip 安装

```bash
pip install tradechill
```

### 从源码安装

```bash
git clone https://github.com/Hatsume0202/tradechill.git
cd tradechill
pip install -e .
```

---

## 🏃 快速上手

### 1. 添加你的持仓

```bash
tradechill portfolio add 600519 贵州茅台 185.60 100
tradechill portfolio add 000858 五粮液 168.50 200
```

### 2. 查看持仓

```bash
tradechill portfolio list
```

### 3. 记录交易冲动

```bash
tradechill impulse record buy 600519 贵州茅台 --emotion FOMO --reason "感觉要大涨"
```

### 4. 开始冷静期

```bash
tradechill cooldown start 1
tradechill cooldown status
```

### 5. 检测行为陷阱

```bash
tradechill traps check
```

### 6. 冷静后复盘

```bash
tradechill review pending
tradechill review do 1 --decision abandoned --note "冷静后觉得追高风险太大"
```

### 7. 打开看板

```bash
tradechill dashboard
```

---

## 📖 详细命令文档

### portfolio - 持仓管理

```bash
# 添加持仓
tradechill portfolio add <股票代码> <名称> <成本价> <数量>

# 查看持仓
tradechill portfolio list

# 更新持仓
tradechill portfolio update <ID> --cost-price <新成本价> --quantity <新数量>

# 删除持仓
tradechill portfolio remove <ID>
```

### impulse - 冲动记录

```bash
# 记录冲动
tradechill impulse record <buy|sell> <代码> <名称> --emotion <情绪> --reason <理由>

# 查看记录
tradechill impulse list
```

### cooldown - 冷静期

```bash
# 开始冷静期
tradechill cooldown start <冲动ID>

# 查看状态
tradechill cooldown status

# 查看历史
tradechill cooldown list
```

### traps - 陷阱检测

```bash
# 执行检测
tradechill traps check

# 查看历史
tradechill traps history
```

### review - 复盘

```bash
# 待复盘列表
tradechill review pending

# 执行复盘
tradechill review do <冲动ID> --decision <executed|abandoned|modified> --note <备注>

# 对比分析
tradechill review compare
```

---

## 🏗️ 项目结构

```
tradechill/
├── tradechill/
│   ├── __init__.py          # 包定义
│   ├── __main__.py          # python -m 支持
│   ├── cli.py               # CLI 命令定义
│   ├── db.py                # 数据库操作
│   ├── portfolio.py         # 持仓管理
│   ├── impulse.py           # 冲动记录
│   ├── cooldown.py          # 冷静期计算
│   ├── trap_detector.py     # 行为陷阱检测
│   ├── review.py            # 复盘分析
│   ├── dashboard.py         # Rich 数据看板
│   └── utils.py             # 工具函数
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🛠️ 技术栈

- **Python 3.10+** — 现代 Python
- **Typer** — CLI 框架
- **Rich** — 终端 UI（颜色、表格、面板、进度条）
- **SQLite** — 本地数据存储（标准库）
- **类型提示** — 全量类型注解
- **行为金融学** — 内置心理学模型

---

## 🔐 数据隐私

所有数据存储在本地 `~/.tradechill/tradechill.db`，不会上传到任何服务器。你的交易数据完全由你自己掌控。

---

## 📄 开源协议

MIT License

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发设置

```bash
git clone https://github.com/Hatsume0202/tradechill.git
cd tradechill
pip install -e ".[dev]"
```

---

## ⚠️ 免责声明

TradeChill 是一个**教育工具**，旨在帮助投资者认识和管理自己的交易情绪。它不提供投资建议，所有模拟价格仅供参考。投资有风险，决策需谨慎。

---

<p align="center">
  <strong>保持冷静，理性投资</strong> 🧘
</p>
