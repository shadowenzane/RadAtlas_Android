"""各屏幕页面"""
import threading
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock

from .theme import (
    C_BG_DARK, C_BG_PANEL, C_BG_CARD, C_BG_INPUT,
    C_TEXT_PRIMARY, C_TEXT_SECONDARY, C_ACCENT, C_ACCENT_GREEN,
    C_ACCENT_RED, C_BORDER,
)
from .widgets import (
    TitleBar, CardView, DiseaseListItem, SearchBar,
    NoteListItem, BottomNavBar, LoadingOverlay,
)
from core.models import (
    init_db, init_user_db, authenticate_user, search_diseases,
    get_disease, load_data,
)
from core.ai_helper import (
    call_diagnosis_multi, load_multi_config, PROVIDERS,
)


# ── 登录屏幕 ──
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))

        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C_BG_DARK)
            self._bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda i, v: setattr(self._bg, 'pos', v),
                    size=lambda i, v: setattr(self._bg, 'size', v))

        # 标题
        title = Label(
            text='RadAtlas\n影像图鉴助手',
            font_size=sp(28),
            color=C_TEXT_PRIMARY,
            size_hint_y=0.3,
        )
        layout.add_widget(title)

        # 制作人信息
        author = Label(
            text='楚雄州人民医院 医学影像中心 张兴文',
            font_size=sp(12),
            color=C_TEXT_SECONDARY,
            size_hint_y=0.08,
        )
        layout.add_widget(author)

        # 用户名
        self.username_input = TextInput(
            hint_text='用户名',
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
        )
        layout.add_widget(self.username_input)

        # 密码
        self.password_input = TextInput(
            hint_text='密码',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
        )
        layout.add_widget(self.password_input)

        # 登录按钮
        login_btn = Button(
            text='登 录',
            size_hint_y=None,
            height=dp(48),
            background_color=C_ACCENT[:3] + (1,),
            color=(1, 1, 1, 1),
            font_size=sp(16),
        )
        login_btn.bind(on_press=self._do_login)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def _do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            return
        user = authenticate_user(username, password)
        if user:
            app = App.get_running_app()
            app.user_info = user
            app.active_db = user.get('database')
            self.manager.current = 'main'
        else:
            popup = Popup(
                title='登录失败',
                content=Label(text='用户名或密码错误', color=C_TEXT_PRIMARY[:3]),
                size_hint=(0.8, 0.3),
                background_color=C_BG_PANEL[:3] + (1,),
            )
            popup.open()


# ── 主屏幕（疾病列表） ──
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        layout = BoxLayout(orientation='vertical', spacing=0)

        # 标题栏
        self.title_bar = TitleBar(title_text='RadAtlas 影像图鉴')
        layout.add_widget(self.title_bar)

        # 搜索栏
        self.search_bar = SearchBar()
        self.search_bar.btn.bind(on_press=self._do_search)
        self.search_bar.input.bind(on_text_validate=lambda _: self._do_search(None))
        layout.add_widget(self.search_bar)

        # 疾病列表
        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(1))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)

        # 底部导航
        self.nav_bar = BottomNavBar()
        layout.add_widget(self.nav_bar)

        self.add_widget(layout)
        self._disease_items = []

    def on_enter(self, *args):
        """进入屏幕时加载疾病列表"""
        self._load_diseases()

    def _load_diseases(self, keyword=''):
        app = App.get_running_app()
        db_path = getattr(app, 'active_db', None)
        if not db_path:
            return
        if keyword:
            rows = search_diseases(db_path, keyword)
        else:
            import sqlite3
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('SELECT id, name_cn, name_en, system, category FROM diseases ORDER BY system, name_cn')
            rows = c.fetchall()
            conn.close()

        self.list_layout.clear_widgets()
        self._disease_items = []

        current_system = ''
        for row in rows:
            disease_id, name_cn, name_en, system, category = row
            # 系统分组标题
            if system != current_system:
                current_system = system
                header = Label(
                    text=f'── {system} ──',
                    color=C_ACCENT[:3] + (1,),
                    font_size=sp(13),
                    size_hint_y=None,
                    height=dp(32),
                    halign='left',
                )
                header.bind(size=header.setter('text_size'))
                self.list_layout.add_widget(header)

            item = DiseaseListItem(name=name_cn, system=system, category=category or '')
            item.disease_id = disease_id
            # 点击事件
            item_bind = lambda dt, did=disease_id: self._show_disease_detail(did)
            item.bind(on_touch_down=lambda w, t, cb=item_bind: cb() if w.collide_point(*t.pos) else None)
            self.list_layout.add_widget(item)
            self._disease_items.append(item)

    def _do_search(self, instance):
        keyword = self.search_bar.input.text.strip()
        self._load_diseases(keyword)

    def _show_disease_detail(self, disease_id):
        app = App.get_running_app()
        app.current_disease_id = disease_id
        self.manager.current = 'detail'


# ── 疾病详情屏幕 ──
class DiseaseDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'detail'
        layout = BoxLayout(orientation='vertical', spacing=0)

        # 标题栏（带返回按钮）
        header = BoxLayout(size_hint_y=None, height=dp(48), orientation='horizontal')
        back_btn = Button(text='← 返回', size_hint_x=0.25,
                         background_color=C_BG_PANEL[:3] + (1,),
                         color=C_TEXT_PRIMARY[:3], font_size=sp(14))
        back_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'main'))
        header.add_widget(back_btn)
        self.title_label = Label(text='疾病详情', color=C_TEXT_PRIMARY[:3],
                                font_size=sp(16), size_hint_x=0.75)
        header.add_widget(self.title_label)
        layout.add_widget(header)

        # 内容区
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def on_enter(self, *args):
        app = App.get_running_app()
        disease_id = getattr(app, 'current_disease_id', None)
        if not disease_id:
            return
        db_path = getattr(app, 'active_db', None)
        disease = get_disease(db_path, disease_id) if db_path else None
        if not disease:
            return

        self.title_label.text = disease.get('name_cn', '未知')
        self.content.clear_widgets()

        # 各字段卡片
        fields = [
            ('英文名', disease.get('name_en', '')),
            ('系统', disease.get('system', '')),
            ('分类', disease.get('category', '')),
            ('临床表现', disease.get('clinical', '')),
            ('诊断', disease.get('diagnosis', '')),
            ('X线表现', disease.get('xray_finding', '')),
            ('CT表现', disease.get('ct_finding', '')),
            ('MRI表现', disease.get('mri_finding', '')),
            ('PET表现', disease.get('pet_finding', '')),
            ('报告模板', disease.get('report_template', '')),
            ('鉴别诊断', disease.get('differential_diagnosis', '')),
            ('治疗方法', disease.get('treatment', '')),
        ]

        for field_name, field_value in fields:
            if not field_value:
                continue
            card = CardView()
            title = Label(text=field_name, color=C_ACCENT[:3] + (1,),
                         font_size=sp(13), halign='left',
                         size_hint_y=None, height=dp(24))
            title.bind(size=title.setter('text_size'))
            card.add_widget(title)

            value = Label(text=field_value, color=C_TEXT_PRIMARY[:3],
                         font_size=sp(13), halign='left',
                         size_hint_y=None, height=dp(20))
            value.bind(size=value.setter('text_size'))
            card.add_widget(value)
            self.content.add_widget(card)


# ── AI 诊断查询屏幕 ──
class AIDiagnosisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ai_diagnosis'
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        # 标题
        title = Label(text='AI 影像诊断查询\n楚雄州人民医院 医学影像中心 张兴文',
                      color=C_TEXT_PRIMARY[:3], font_size=sp(16),
                      size_hint_y=None, height=dp(60))
        layout.add_widget(title)

        # 检查类型
        exam_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        exam_row.add_widget(Label(text='检查类型:', color=C_TEXT_PRIMARY[:3],
                                 size_hint_x=0.3, font_size=sp(14)))
        self.exam_spinner = Spinner(
            text='CT', values=('CT', 'X-Ray', 'MRI', 'PET-CT', '超声', 'DSA'),
            size_hint_x=0.7,
        )
        exam_row.add_widget(self.exam_spinner)
        layout.add_widget(exam_row)

        # 关键字
        self.keywords_input = TextInput(
            hint_text='输入关键字，如：腹部 胃 包块 等密度...',
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=sp(14),
        )
        layout.add_widget(self.keywords_input)

        # 查询按钮
        self.query_btn = Button(
            text='开始查询',
            size_hint_y=None,
            height=dp(44),
            background_color=C_ACCENT[:3] + (1,),
            color=(1, 1, 1, 1),
            font_size=sp(16),
        )
        self.query_btn.bind(on_press=self._do_query)
        layout.add_widget(self.query_btn)

        # 状态
        self.status_label = Label(text='', color=C_TEXT_SECONDARY[:3],
                                 font_size=sp(12), size_hint_y=None, height=dp(24))
        layout.add_widget(self.status_label)

        # 结果区
        self.result_scroll = ScrollView()
        self.result_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.result_scroll.add_widget(self.result_layout)
        layout.add_widget(self.result_scroll)

        self.add_widget(layout)

    def _do_query(self, instance):
        keywords = self.keywords_input.text.strip()
        if not keywords:
            return
        exam_type = self.exam_spinner.text
        self.status_label.text = '查询中...'
        self.query_btn.disabled = True

        # 获取已配置的模型
        providers = load_multi_config()
        selected = [p for p in providers if p.get('api_key')]

        if not selected:
            self.status_label.text = '未配置AI模型，请先在设置中配置'
            self.query_btn.disabled = False
            return

        def _query():
            try:
                results = call_diagnosis_multi(exam_type, keywords, selected_providers=selected)
                Clock.schedule_once(lambda dt: self._show_results(results))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))

        threading.Thread(target=_query, daemon=True).start()

    def _show_results(self, results):
        self.query_btn.disabled = False
        self.result_layout.clear_widgets()

        for provider_name, result in results.items():
            # 提供商标题
            header = Label(
                text=f'── {provider_name} ──',
                color=C_ACCENT[:3] + (1,),
                font_size=sp(14),
                size_hint_y=None,
                height=dp(32),
            )
            self.result_layout.add_widget(header)

            if not result.get('success'):
                err = Label(text=f'错误: {result.get("error", "未知")}',
                           color=C_ACCENT_RED[:3], font_size=sp(12),
                           size_hint_y=None, height=dp(28))
                self.result_layout.add_widget(err)
                continue

            for item in result.get('data', []):
                name = item.get('disease_name', '未知')
                confidence = item.get('confidence', '')
                btn = Button(
                    text=f'{name} [{confidence}]',
                    size_hint_y=None,
                    height=dp(40),
                    background_color=C_BG_INPUT[:3] + (1,),
                    color=C_TEXT_PRIMARY[:3],
                    font_size=sp(13),
                    halign='left',
                )
                btn.diagnosis_data = item
                btn.bind(on_press=self._show_diagnosis_detail)
                self.result_layout.add_widget(btn)

        self.status_label.text = '查询完成'

    def _show_error(self, error):
        self.query_btn.disabled = False
        self.status_label.text = f'查询失败: {error}'

    def _show_diagnosis_detail(self, instance):
        data = getattr(instance, 'diagnosis_data', {})
        if not data:
            return

        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        scroll = ScrollView()
        text_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        text_layout.bind(minimum_height=text_layout.setter('height'))

        fields = [
            ('疾病名称', data.get('disease_name', '')),
            ('置信度', data.get('confidence', '')),
            ('影像学表现', data.get('imaging_findings', '')),
            ('标准报告模板', data.get('report_template', '')),
            ('鉴别诊断', data.get('differential_diagnosis', '')),
            ('临床表现', data.get('clinical_manifestation', '')),
            ('病理生理', data.get('pathophysiology', '')),
            ('治疗方法', data.get('treatment', '')),
        ]

        for fname, fvalue in fields:
            if not fvalue:
                continue
            lbl = Label(text=f'[b]{fname}[/b]\n{fvalue}',
                       markup=True, color=C_TEXT_PRIMARY[:3],
                       font_size=sp(12), halign='left',
                       size_hint_y=None, height=dp(60))
            lbl.bind(size=lbl.setter('text_size'))
            text_layout.add_widget(lbl)

        scroll.add_widget(text_layout)
        content.add_widget(scroll)

        close_btn = Button(text='关闭', size_hint_y=None, height=dp(40))
        popup = Popup(
            title=data.get('disease_name', '诊断详情'),
            content=content,
            size_hint=(0.9, 0.85),
            background_color=C_BG_PANEL[:3] + (1,),
        )
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()


# ── 设置屏幕 ──
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(16))

        title = Label(text='设置', color=C_TEXT_PRIMARY[:3], font_size=sp(20),
                     size_hint_y=None, height=dp(40))
        layout.add_widget(title)

        # AI 配置
        ai_card = CardView()
        ai_title = Label(text='AI 模型配置', color=C_ACCENT[:3], font_size=sp(14),
                        size_hint_y=None, height=dp(28))
        ai_card.add_widget(ai_title)

        self.ai_config_btn = Button(
            text='配置 AI 模型',
            size_hint_y=None, height=dp(40),
            background_color=C_BG_INPUT[:3] + (1,),
            color=C_TEXT_PRIMARY[:3], font_size=sp(14),
        )
        ai_card.add_widget(self.ai_config_btn)
        layout.add_widget(ai_card)

        # 知识库配置
        kb_card = CardView()
        kb_title = Label(text='知识库配置', color=C_ACCENT[:3], font_size=sp(14),
                        size_hint_y=None, height=dp(28))
        kb_card.add_widget(kb_title)

        self.kb_config_btn = Button(
            text='配置知识库',
            size_hint_y=None, height=dp(40),
            background_color=C_BG_INPUT[:3] + (1,),
            color=C_TEXT_PRIMARY[:3], font_size=sp(14),
        )
        kb_card.add_widget(self.kb_config_btn)
        layout.add_widget(kb_card)

        # 关于
        about_card = CardView()
        about_label = Label(
            text='RadAtlas 影像图鉴助手 v1.0\n楚雄州人民医院 医学影像中心 张兴文',
            color=C_TEXT_SECONDARY[:3], font_size=sp(12),
        )
        about_card.add_widget(about_label)
        layout.add_widget(about_card)

        self.add_widget(layout)


# ── 屏幕管理器 ──
class RadAtlasScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(LoginScreen())
        self.add_widget(MainScreen())
        self.add_widget(DiseaseDetailScreen())
        self.add_widget(AIDiagnosisScreen())
        self.add_widget(SettingsScreen())
