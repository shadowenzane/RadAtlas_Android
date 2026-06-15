"""主题配色方案 — 与桌面版深蓝暗夜主题一致"""

# ── 主色调 ──
BG_DARK = '#0d1117'         # 主背景
BG_PANEL = '#161b22'        # 面板背景
BG_CARD = '#1c2128'         # 卡片背景
BG_INPUT = '#21262d'        # 输入框背景
BG_HOVER = '#292e36'        # 悬停态

BORDER = '#30363d'          # 边框
BORDER_LIGHT = '#444c56'    # 浅边框

TEXT_PRIMARY = '#e6edf3'    # 主文字
TEXT_SECONDARY = '#8b949e'  # 次要文字
TEXT_MUTED = '#6e7681'      # 弱化文字

ACCENT = '#58a6ff'          # 强调色（蓝）
ACCENT_GREEN = '#3fb950'    # 成功/绿色
ACCENT_RED = '#f85149'      # 错误/红色
ACCENT_YELLOW = '#d29922'   # 警告/黄色
ACCENT_PURPLE = '#bc8cff'   # 紫色

SELECT_BG = '#1f6feb'       # 选中背景
SELECT_FG = '#ffffff'       # 选中文字

# ── 标题栏 ──
TITLEBAR_BG = BG_DARK
TITLEBAR_FG = TEXT_PRIMARY

# ── 按钮 ──
BTN_PRIMARY_BG = ACCENT
BTN_PRIMARY_FG = '#ffffff'
BTN_SECONDARY_BG = BG_INPUT
BTN_SECONDARY_FG = TEXT_PRIMARY

# ── Kivy 颜色转换（0-1 浮点） ──
def hex_to_rgba(hex_color, alpha=1.0):
    """将 #RRGGBB 转换为 (r, g, b, a) 浮点元组"""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, alpha)

# 预转换常用颜色
C_BG_DARK = hex_to_rgba(BG_DARK)
C_BG_PANEL = hex_to_rgba(BG_PANEL)
C_BG_CARD = hex_to_rgba(BG_CARD)
C_BG_INPUT = hex_to_rgba(BG_INPUT)
C_TEXT_PRIMARY = hex_to_rgba(TEXT_PRIMARY)
C_TEXT_SECONDARY = hex_to_rgba(TEXT_SECONDARY)
C_ACCENT = hex_to_rgba(ACCENT)
C_ACCENT_GREEN = hex_to_rgba(ACCENT_GREEN)
C_ACCENT_RED = hex_to_rgba(ACCENT_RED)
C_BORDER = hex_to_rgba(BORDER)
C_SELECT_BG = hex_to_rgba(SELECT_BG)
