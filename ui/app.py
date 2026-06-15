"""主应用类"""
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform

from .screens import RadAtlasScreenManager
from .theme import BG_DARK, hex_to_rgba
from core.models import init_db, init_user_db, load_data, DATABASE, USER_DB


class RadAtlasApp(App):
    title = 'RadAtlas 影像图鉴助手'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_info = None
        self.active_db = None
        self.current_disease_id = None

    def build(self):
        # 设置窗口背景色
        Window.clearcolor = hex_to_rgba(BG_DARK)

        # 初始化数据库
        init_user_db()
        init_db()
        load_data()

        # 创建屏幕管理器
        self.sm = RadAtlasScreenManager()
        return self.sm

    def on_pause(self):
        """Android 暂停时保存状态"""
        return True

    def on_resume(self):
        """Android 恢复时"""
        pass
