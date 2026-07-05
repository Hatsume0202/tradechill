#!/usr/bin/env python3
"""Generate TradeChill functional architecture diagram using Graphviz."""

import graphviz

# ============================================================
# Global graph setup
# ============================================================
dot = graphviz.Digraph(
    name='TradeChill_Architecture',
    format='png',
    engine='dot',
)

dot.attr(
    rankdir='TB',
    size='14,10',         # 14" x 10" at dpi=150 → 2100×1500 px
    dpi='150',
    fontname='Noto Sans CJK SC',
    bgcolor='#fcfcfb',    # light surface from palette
    pad='0.4',
    compound='true',
    nodesep='0.25',
    ranksep='2.8',
    splines='polyline',
    margin='0.3',
    label='TradeChill  功能架构图',
    labelloc='t',
    labeljust='c',
    fontsize='28',
    fontcolor='#0b0b0b',
)

# ============================================================
# Palette (adapted from dataviz reference)
# ============================================================
# Layer 1 — CLI (blue)
CLI_FILL    = '#2a78d6'
CLI_CLUSTER = '#deeafb'
# Layer 2 — Core (aqua / green)
CORE_FILL    = '#1baf7a'
CORE_CLUSTER = '#def7ed'
# Layer 3 — Database (violet)
DB_FILL    = '#4a3aa7'
DB_CLUSTER = '#e4e1f5'
# Return flow (orange)
RETURN_FILL = '#eb6834'

# Shared node defaults
dot.attr('node', shape='box', style='rounded,filled',
         fontname='Noto Sans CJK SC', fontsize='11', margin='0.12,0.08')

# Shared edge defaults
dot.attr('edge', fontname='Noto Sans CJK SC', fontsize='9')

# ============================================================
# Layer 1 — User Interaction (CLI Commands)
# ============================================================
with dot.subgraph(name='cluster_cli') as s:
    s.attr(
        label='用户交互层 / 命令行界面',
        style='filled,rounded',
        fillcolor=CLI_CLUSTER,
        color=CLI_FILL,
        fontcolor=CLI_FILL,
        fontsize='20',
        fontname='Noto Sans CJK SC',
    )

    commands = [
        ('cli_portfolio', 'tradechill portfolio\nadd / list / remove / update'),
        ('cli_impulse',   'tradechill impulse\nrecord / list'),
        ('cli_cooldown',  'tradechill cooldown\nstart / status / list'),
        ('cli_traps',     'tradechill traps\ncheck / history'),
        ('cli_review',    'tradechill review\npending / do / compare'),
        ('cli_dashboard', 'tradechill dashboard\nTUI 仪表盘'),
    ]

    for nid, label in commands:
        s.node(nid, label, fillcolor=CLI_FILL, fontcolor='white',
               fontsize='10', width='1.5', height='0.75')

# ============================================================
# Layer 2 — Core Functional Modules
# ============================================================
with dot.subgraph(name='cluster_core') as s:
    s.attr(
        label='核心功能模块',
        style='filled,rounded',
        fillcolor=CORE_CLUSTER,
        color=CORE_FILL,
        fontcolor=CORE_FILL,
        fontsize='20',
        fontname='Noto Sans CJK SC',
    )

    modules = [
        ('mod_portfolio', '持仓管理模块\nPortfolio Manager'),
        ('mod_impulse',   '冲动记录模块\nImpulse Recorder'),
        ('mod_cooldown',  '冷静期计算器\nCooldown Calculator'),
        ('mod_traps',     '陷阱检测引擎\nTrap Detector'),
        ('mod_review',    '复盘分析模块\nReview Analyzer'),
        ('mod_dashboard', '数据看板引擎\nDashboard Engine'),
    ]

    for nid, label in modules:
        s.node(nid, label, fillcolor=CORE_FILL, fontcolor='white',
               fontsize='10', width='1.5', height='0.75')

# ============================================================
# Layer 3 — Data Persistence (SQLite Database)
# ============================================================
with dot.subgraph(name='cluster_db') as s:
    s.attr(
        label='数据持久化层',
        style='filled,rounded',
        fillcolor=DB_CLUSTER,
        color=DB_FILL,
        fontcolor=DB_FILL,
        fontsize='20',
        fontname='Noto Sans CJK SC',
    )

    # Database node — HTML table label shows all 5 tables
    s.node('database', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="9">
        <TR>
            <TD COLSPAN="5" BGCOLOR="#4a3aa7" PORT="title">
                <FONT COLOR="white" POINT-SIZE="14" FACE="Noto Sans CJK SC"><B>SQLite 数据库</B></FONT>
            </TD>
        </TR>
        <TR>
            <TD BGCOLOR="#fcfcfb" PORT="h1" CELLPADDING="8">
                <FONT POINT-SIZE="10" FACE="Noto Sans CJK SC">holdings<BR/>持仓表</FONT>
            </TD>
            <TD BGCOLOR="#fcfcfb" PORT="h2" CELLPADDING="8">
                <FONT POINT-SIZE="10" FACE="Noto Sans CJK SC">impulses<BR/>冲动记录表</FONT>
            </TD>
            <TD BGCOLOR="#fcfcfb" PORT="h3" CELLPADDING="8">
                <FONT POINT-SIZE="10" FACE="Noto Sans CJK SC">cooldowns<BR/>冷静期表</FONT>
            </TD>
            <TD BGCOLOR="#fcfcfb" PORT="h4" CELLPADDING="8">
                <FONT POINT-SIZE="10" FACE="Noto Sans CJK SC">reviews<BR/>复盘表</FONT>
            </TD>
            <TD BGCOLOR="#fcfcfb" PORT="h5" CELLPADDING="8">
                <FONT POINT-SIZE="10" FACE="Noto Sans CJK SC">trap_reports<BR/>陷阱报告表</FONT>
            </TD>
        </TR>
    </TABLE>
    >''', shape='none', fillcolor='none')

# ============================================================
# Edges — Forward flow  (CLI → Module → DB)
# ============================================================
# CLI to Core Modules  (command dispatch)
cli_to_mod = [
    ('cli_portfolio', 'mod_portfolio'),
    ('cli_impulse',   'mod_impulse'),
    ('cli_cooldown',  'mod_cooldown'),
    ('cli_traps',     'mod_traps'),
    ('cli_review',    'mod_review'),
    ('cli_dashboard', 'mod_dashboard'),
]
for src, tgt in cli_to_mod:
    dot.edge(src, tgt,
             color=CLI_FILL, penwidth='1.8',
             xlabel='发 送 指 令',
             fontcolor=CLI_FILL, fontsize='10')

# Core Modules to Database  (write / persist)
mod_to_db = [
    'mod_portfolio', 'mod_impulse', 'mod_cooldown',
    'mod_traps',     'mod_review',  'mod_dashboard',
]
for src in mod_to_db:
    dot.edge(src, 'database:title',
             color=CORE_FILL, penwidth='1.8',
             xlabel='  持 久 化  ',
             fontcolor=CORE_FILL, fontsize='10')

# ============================================================
# Edges — Return flow  (DB → Module → CLI output)
# ============================================================
# Database to Core Modules  (read / query)
db_to_mod = [
    'mod_portfolio', 'mod_impulse', 'mod_cooldown',
    'mod_traps',     'mod_review',  'mod_dashboard',
]
for tgt in db_to_mod:
    dot.edge('database:title', tgt,
             color=RETURN_FILL, penwidth='1.2', style='dashed',
             constraint='false', xlabel='  查 询 读 取  ',
             fontcolor=RETURN_FILL, fontsize='10')

# Core Modules to CLI  (output / result)
mod_to_cli = [
    ('mod_portfolio', 'cli_portfolio'),
    ('mod_impulse',   'cli_impulse'),
    ('mod_cooldown',  'cli_cooldown'),
    ('mod_traps',     'cli_traps'),
    ('mod_review',    'cli_review'),
    ('mod_dashboard', 'cli_dashboard'),
]
for src, tgt in mod_to_cli:
    dot.edge(src, tgt,
             color=RETURN_FILL, penwidth='1.2', style='dashed',
             constraint='false', xlabel='  返 回 输 出  ',
             fontcolor=RETURN_FILL, fontsize='10')

# ============================================================
# Legend
# ============================================================
with dot.subgraph(name='cluster_legend') as s:
    s.attr(
        label='图例',
        style='filled,rounded',
        fillcolor='#f9f9f7',
        color='#c3c2b7',
        fontsize='14',
        fontname='Noto Sans CJK SC',
        fontcolor='#52514e',
        margin='10',
    )

    # Invisible row to keep legend compact
    s.node('l_blank', '', shape='plain', width='0', height='0')

    s.node('l_fwd',  '命令 / 写入', shape='plain',
           fontsize='10', fontcolor='#52514e')
    s.node('l_fwd_arrow', '', shape='plain', fontsize='10',
           width='0.8', height='0', margin='0')
    s.edge('l_fwd', 'l_fwd_arrow',
           color=CLI_FILL, penwidth='1.8',
           arrowhead='normal', label='')

    s.node('l_ret',  '读取 / 输出', shape='plain',
           fontsize='10', fontcolor='#52514e')
    s.node('l_ret_arrow', '', shape='plain', fontsize='10',
           width='0.8', height='0', margin='0')
    s.edge('l_ret', 'l_ret_arrow',
           color=RETURN_FILL, penwidth='1.2', style='dashed',
           arrowhead='normal', label='')

    s.node('l_cli',  'CLI 命令节点', shape='box',
           style='filled,rounded',
           fillcolor=CLI_FILL, fontcolor='white',
           fontsize='9', width='1.2', height='0.3')
    s.node('l_core', '功能模块节点', shape='box',
           style='filled,rounded',
           fillcolor=CORE_FILL, fontcolor='white',
           fontsize='9', width='1.2', height='0.3')
    s.node('l_db',   '数据层节点', shape='box',
           style='filled,rounded',
           fillcolor=DB_FILL, fontcolor='white',
           fontsize='9', width='1.2', height='0.3')

# ============================================================
# Render
# ============================================================
output_path = '/work/tradechill/assets/architecture'
dot.render(output_path, cleanup=True)
print(f'✅ Diagram saved to {output_path}.png')
