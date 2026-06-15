"""自定义 Kivy 组件"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window

from .theme import (
    hex_to_rgba, C_BG_DARK, C_BG_PANEL, C_BG_CARD, C_BG_INPUT,
    C_TEXT_PRIMARY, C_TEXT_SECONDARY, C_ACCENT, C_ACCENT_GREEN,
    C_ACCENT_RED, C_BORDER, BG_DARK, BG_PANEL, BG_CARD, BG_INPUT,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, BORDER, ACCENT_GREEN, ACCENT_RED,
)


class TitleBar(BoxLayout):
    """自定义标题栏"""
    title_text = StringProperty('RadAtlas')
    subtitle_text = StringProperty('楚雄州人民医院 医学影像中心 张兴文')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        self.orientation = 'horizontal'
        self.padding = [dp(12), 0]

        with self.canvas.before:
            Color(*C_BG_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # 标题
        self.title_label = Label(
            text=self.title_text,
            color=C_TEXT_PRIMARY,
            font_size=sp(16),
            size_hint_x=0.5,
            halign='left',
            valign='middle',
        )
        self.add_widget(self.title_label)

        # 副标题
        self.subtitle_label = Label(
            text=self.subtitle_text,
            color=C_TEXT_SECONDARY,
            font_size=sp(10),
            size_hint_x=0.5,
            halign='right',
            valign='middle',
        )
        self.add_widget(self.subtitle_label)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class CardView(BoxLayout):
    """卡片容器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*C_BG_CARD)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class DiseaseListItem(BoxLayout):
    """疾病列表项"""
    name = StringProperty('')
    system = StringProperty('')
    category = StringProperty('')

    def __init__(self, name='', system='', category='', **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.system = system
        self.category = category
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = [dp(12), dp(8)]

        with self.canvas.before:
            Color(*C_BG_PANEL)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # 疾病名称
        self.name_label = Label(
            text=self.name,
            color=C_TEXT_PRIMARY,
            font_size=sp(15),
            halign='left',
            valign='middle',
            size_hint_y=0.6,
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        self.add_widget(self.name_label)

        # 系统/分类
        self.info_label = Label(
            text=f'{self.system} · {self.category}',
            color=C_TEXT_SECONDARY,
            font_size=sp(11),
            halign='left',
            valign='middle',
            size_hint_y=0.4,
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.add_widget(self.info_label)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class SearchBar(BoxLayout):
    """搜索栏"""
    search_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(44)
        self.spacing = dp(8)

        self.input = TextInput(
            hint_text='搜索疾病名称...',
            multiline=False,
            size_hint_x=0.8,
            font_size=sp(14),
            background_color=C_BG_INPUT[:3] + (1,),
            foreground_color=C_TEXT_PRIMARY[:3],
            cursor_color=C_ACCENT[:3],
        )
        self.add_widget(self.input)

        self.btn = Button(
            text='搜索',
            size_hint_x=0.2,
            background_color=C_ACCENT[:3] + (1,),
            color=(1, 1, 1, 1),
            font_size=sp(14),
        )
        self.add_widget(self.btn)


class NoteListItem(BoxLayout):
    """笔记列表项"""
    note_title = StringProperty('')
    note_time = StringProperty('')

    def __init__(self, title='', time_str='', **kwargs):
        super().__init__(**kwargs)
        self.note_title = title
        self.note_time = time_str
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(52)
        self.padding = [dp(12), dp(6)]

        with self.canvas.before:
            Color(*C_BG_INPUT)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.title_label = Label(
            text=self.note_title,
            color=C_TEXT_PRIMARY,
            font_size=sp(14),
            halign='left',
            valign='middle',
            size_hint_y=0.6,
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.add_widget(self.title_label)

        self.time_label = Label(
            text=self.note_time,
            color=C_TEXT_SECONDARY,
            font_size=sp(10),
            halign='left',
            valign='middle',
            size_hint_y=0.4,
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        self.add_widget(self.time_label)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class BottomNavBar(BoxLayout):
    """底部导航栏"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.spacing = 0

        with self.canvas.before:
            Color(*C_BG_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.tabs = []
        for name, icon in [('疾病', '📋'), ('笔记', '📝'), ('影像', '🖼'), ('AI', '🤖'), ('设置', '⚙')]:
            btn = Button(
                text=f'{icon}\n{name}',
                color=C_TEXT_SECONDARY[:3] + (1,),
                font_size=sp(11),
                background_color=(0, 0, 0, 0),
            )
            self.tabs.append(btn)
            self.add_widget(btn)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class LoadingOverlay(BoxLayout):
    """加载遮罩"""
    message = StringProperty('加载中...')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.progress = ProgressBar(size_hint_y=None, height=dp(4))
        self.add_widget(self.progress)

        self.label = Label(
            text=self.message,
            color=C_TEXT_PRIMARY,
            font_size=sp(14),
        )
        self.add_widget(self.label)

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size
