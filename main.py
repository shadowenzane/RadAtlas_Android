import os
import sqlite3

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrolllayout import ScrollLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.lang import Builder

from models import (
    init_user_db, authenticate_user, init_db, load_data,
    get_all_users, create_user, delete_user, change_password,
    hash_password, DATABASE, USER_DB, APP_DIR, copy_public_to_user
)

KV = '''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<CustomLabel@Label>:
    color: (1, 1, 1, 1)
    font_size: sp(14)

<CustomButton@Button>:
    background_color: (0.25, 0.59, 1, 1)
    color: (1, 1, 1, 1)
    font_size: sp(14)
    size_hint_y: None
    height: dp(44)
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]

<DangerButton@Button>:
    background_color: (0.9, 0.3, 0.24, 1)
    color: (1, 1, 1, 1)
    font_size: sp(14)
    size_hint_y: None
    height: dp(44)
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]

<CustomTextInput@TextInput>:
    size_hint_y: None
    height: dp(44)
    font_size: sp(14)
    padding: [dp(10), dp(10), dp(10), dp(10)]
    background_color: (0.15, 0.15, 0.18, 1)
    foreground_color: (1, 1, 1, 1)
    cursor_color: (0.25, 0.59, 1, 1)

<CustomSpinner@Spinner>:
    size_hint_y: None
    height: dp(44)
    font_size: sp(14)
    background_color: (0.15, 0.15, 0.18, 1)
    color: (1, 1, 1, 1)

<DiseaseButton@Button>:
    background_color: (0.12, 0.12, 0.15, 1)
    color: (1, 1, 1, 1)
    font_size: sp(13)
    size_hint_y: None
    height: dp(48)
    halign: 'left'
    valign: 'middle'
    text_size: self.width - dp(20), None
    padding: [dp(10), 0]
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
    canvas.after:
        Color:
            rgba: 0.2, 0.2, 0.25, 1
        Rectangle:
            pos: self.x, self.y
            size: self.width, dp(0.5)

<TabButton@ToggleButton>:
    group: 'tabs'
    allow_no_selection: False
    background_color: (0.1, 0.1, 0.12, 1)
    color: (0.6, 0.6, 0.65, 1)
    font_size: sp(12)
    size_hint_x: 1
    canvas.before:
        Color:
            rgba: (0.25, 0.59, 1, 1) if self.state == 'down' else (0.1, 0.1, 0.12, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: (0.25, 0.59, 1, 1) if self.state == 'down' else (0, 0, 0, 0)
        Rectangle:
            pos: self.x, self.y
            size: self.width, dp(3)

<ScrollLabel@Label>:
    color: (0.85, 0.85, 0.88, 1)
    font_size: sp(13)
    size_hint_y: None
    height: self.texture_size[1] if self.texture else dp(20)
    text_size: self.width - dp(16), None
    halign: 'left'
    valign: 'top'
    padding: [dp(8), dp(8)]
'''


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        layout = BoxLayout(orientation='vertical', padding=[dp(30), dp(40), dp(30), dp(20)],
                           spacing=dp(12))

        with layout.canvas.before:
            Color(0.08, 0.08, 0.1, 1)
            Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda i, v: setattr(layout.canvas.before.children[1], 'pos', v),
                    size=lambda i, v: setattr(layout.canvas.before.children[1], 'size', v))

        title = Label(text='RadAtlas', font_size=sp(32), color=(0.25, 0.59, 1, 1),
                      size_hint_y=None, height=dp(60))
        layout.add_widget(title)

        subtitle = Label(text='影像图鉴助手', font_size=sp(14), color=(0.5, 0.5, 0.55, 1),
                         size_hint_y=None, height=dp(30))
        layout.add_widget(subtitle)

        layout.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        self.username_input = TextInput(hint_text='用户名', multiline=False,
                                        size_hint_y=None, height=dp(48),
                                        font_size=sp(15),
                                        padding=[dp(12), dp(12), dp(12), dp(12)])
        layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text='密码', multiline=False,
                                        password=True,
                                        size_hint_y=None, height=dp(48),
                                        font_size=sp(15),
                                        padding=[dp(12), dp(12), dp(12), dp(12)])
        layout.add_widget(self.password_input)

        layout.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))

        login_btn = Button(text='登 录', size_hint_y=None, height=dp(48),
                           font_size=sp(16), background_color=(0.25, 0.59, 1, 1),
                           color=(1, 1, 1, 1))
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)

        layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        hint = Label(text='默认管理员: admin / admin123', font_size=sp(11),
                     color=(0.4, 0.4, 0.45, 1), size_hint_y=None, height=dp(20))
        layout.add_widget(hint)

        self.add_widget(layout)

    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self._show_msg('提示', '请输入用户名和密码')
            return
        user = authenticate_user(username, password)
        if user:
            app = App.get_running_app()
            app.user_info = user
            app.active_db = user.get('database') or DATABASE
            init_db(app.active_db)
            if app.active_db == DATABASE:
                load_data(app.active_db)
            self.manager.current = 'main'
        else:
            self._show_msg('错误', '用户名或密码错误')

    def _show_msg(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg, font_size=sp(14)),
                      size_hint=(0.7, 0.35))
        popup.open()


class DiseaseListWidget(BoxLayout):
    def __init__(self, on_select=None, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.on_select = on_select
        self.diseases = []
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(0.5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        scroll = BoxLayout(size_hint_y=1)
        from kivy.uix.scrollview import ScrollView
        sv = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        sv.add_widget(self.list_layout)
        scroll.add_widget(sv)
        self.add_widget(scroll)

    def load_diseases(self, db_path, search=None):
        self.list_layout.clear_widgets()
        self.diseases = []
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        if search:
            c.execute("""SELECT id, name_cn, name_en, system FROM diseases
                         WHERE name_cn LIKE ? OR name_en LIKE ? OR clinical LIKE ?
                         OR diagnosis LIKE ? OR system LIKE ? OR category LIKE ?
                         ORDER BY system, name_cn""",
                      (f'%{search}%',) * 6)
        else:
            c.execute("SELECT id, name_cn, name_en, system FROM diseases ORDER BY system, name_cn")
        rows = c.fetchall()
        conn.close()

        if not rows:
            lbl = Label(text='暂无数据', font_size=sp(13), color=(0.5, 0.5, 0.55, 1),
                        size_hint_y=None, height=dp(40))
            self.list_layout.add_widget(lbl)
            return

        current_system = None
        for row in rows:
            did, name_cn, name_en, system = row
            if system != current_system:
                current_system = system
                header = Label(text=f'── {system} ──', font_size=sp(12),
                               color=(0.25, 0.59, 1, 0.8), size_hint_y=None, height=dp(32),
                               halign='left', valign='middle')
                header.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] - dp(16), None)))
                self.list_layout.add_widget(header)

            display = name_cn or name_en or f'疾病 #{did}'
            if name_en and name_cn:
                display = f'{name_cn} ({name_en})'
            btn = Button(text=display, font_size=sp(13), size_hint_y=None, height=dp(46),
                         halign='left', valign='middle',
                         background_color=(0.12, 0.12, 0.15, 1), color=(1, 1, 1, 1))
            btn.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] - dp(20), None)),
                     padding=[dp(12), 0])
            btn.bind(on_press=lambda inst, d=did: self._on_disease_selected(d))
            self.list_layout.add_widget(btn)
            self.diseases.append(did)

    def _on_disease_selected(self, disease_id):
        if self.on_select:
            self.on_select(disease_id)


class DetailPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.current_disease_id = None
        self.active_db = DATABASE

        self.tab_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(0))
        self.tab_buttons = []
        tab_names = ['临床与诊断', '标准报告模板', '影像所见与资料', '医学资料', '影像解剖图谱与资料']
        for i, name in enumerate(tab_names):
            btn = ToggleButton(text=name, group='detail_tabs', font_size=sp(11),
                               allow_no_selection=False)
            btn.bind(on_press=lambda inst, idx=i: self.switch_tab(idx))
            self.tab_buttons.append(btn)
            self.tab_bar.add_widget(btn)
        self.add_widget(self.tab_bar)

        from kivy.uix.scrollview import ScrollView
        self.scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        self.content_label = Label(font_size=sp(13), color=(0.85, 0.85, 0.88, 1),
                                   halign='left', valign='top',
                                   size_hint_y=None,
                                   padding=[dp(12), dp(12)])
        self.content_label.bind(texture_size=self.content_label.setter('size'),
                                width=lambda i, v: setattr(i, 'text_size', (v - dp(24), None)))
        self.scroll.add_widget(self.content_label)
        self.add_widget(self.scroll)

        self.current_tab = 0
        self.disease_data = None
        self.tab_buttons[0].state = 'down'

    def switch_tab(self, idx):
        self.current_tab = idx
        for i, btn in enumerate(self.tab_buttons):
            btn.state = 'down' if i == idx else 'normal'
        self._refresh_content()

    def load_disease(self, disease_id, db_path):
        self.current_disease_id = disease_id
        self.active_db = db_path
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM diseases WHERE id=?", (disease_id,))
        row = c.fetchone()
        conn.close()
        if row:
            self.disease_data = {
                'name_cn': row[1] or '', 'name_en': row[2] or '',
                'system': row[3] or '', 'category': row[4] or '',
                'clinical': row[5] or '', 'diagnosis': row[6] or '',
                'primary_img': row[7] or '', 'secondary_img': row[8] or '',
                'xray': row[9] or '', 'ct': row[10] or '',
                'mri': row[11] or '', 'pet': row[12] or '',
                'report': row[13] or '', 'diff': row[14] or '',
                'treatment': row[15] or '',
            }
        else:
            self.disease_data = None
        self._refresh_content()

    def _refresh_content(self):
        if not self.disease_data:
            self.content_label.text = '请从左侧选择一个疾病'
            return
        d = self.disease_data
        if self.current_tab == 0:
            text = f'[size=18][b]{d["name_cn"]}[/b][/size]\n'
            if d['name_en']:
                text += f'[i]{d["name_en"]}[/i]\n'
            text += f'\n[b]系统:[/b] {d["system"]}  [b]分类:[/b] {d["category"]}\n\n'
            text += f'[b]临床表现:[/b]\n{d["clinical"]}\n\n'
            text += f'[b]诊断要点:[/b]\n{d["diagnosis"]}\n\n'
            text += f'[b]鉴别诊断:[/b]\n{d["diff"]}\n\n'
            text += f'[b]治疗原则:[/b]\n{d["treatment"]}'
            self.content_label.markup = True
            self.content_label.text = text
        elif self.current_tab == 1:
            text = f'[b]影像报告模板:[/b]\n\n{d["report"]}'
            self.content_label.markup = True
            self.content_label.text = text
        elif self.current_tab == 2:
            self._show_imaging_tab()
            return
        elif self.current_tab == 3:
            self._show_medical_tab()
            return
        elif self.current_tab == 4:
            self._show_anatomy_tab()
            return

    def _show_imaging_tab(self):
        if not self.current_disease_id:
            self.content_label.text = '请先选择疾病'
            return
        conn = sqlite3.connect(self.active_db)
        c = conn.cursor()
        c.execute("SELECT id, filename, caption, media_type FROM images WHERE disease_id=?",
                  (self.current_disease_id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            self.content_label.markup = False
            self.content_label.text = '暂无影像资料'
            return
        text = '[b]影像所见:[/b]\n\n'
        d = self.disease_data
        if d.get('xray'):
            text += f'[b]X线:[/b] {d["xray"]}\n\n'
        if d.get('ct'):
            text += f'[b]CT:[/b] {d["ct"]}\n\n'
        if d.get('mri'):
            text += f'[b]MRI:[/b] {d["mri"]}\n\n'
        if d.get('pet'):
            text += f'[b]PET:[/b] {d["pet"]}\n\n'
        text += f'\n共 {len(rows)} 张影像'
        self.content_label.markup = True
        self.content_label.text = text

    def _show_medical_tab(self):
        if not self.current_disease_id:
            self.content_label.text = '请先选择疾病'
            return
        conn = sqlite3.connect(self.active_db)
        c = conn.cursor()
        c.execute("SELECT title, content FROM medical_records WHERE disease_id=?",
                  (self.current_disease_id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            self.content_label.markup = False
            self.content_label.text = '暂无医学资料'
            return
        text = '[b]医学资料:[/b]\n\n'
        for title, content in rows:
            text += f'[b]{title}[/b]\n{content}\n\n'
        self.content_label.markup = True
        self.content_label.text = text

    def _show_anatomy_tab(self):
        conn = sqlite3.connect(self.active_db)
        c = conn.cursor()
        c.execute("SELECT title, content FROM anatomy_records")
        rows = c.fetchall()
        conn.close()
        if not rows:
            self.content_label.markup = False
            self.content_label.text = '暂无影像解剖图谱资料'
            return
        text = '[b]影像解剖图谱与资料:[/b]\n\n'
        for title, content in rows:
            text += f'[b]{title}[/b]\n{content}\n\n'
        self.content_label.markup = True
        self.content_label.text = text


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'

        root_layout = BoxLayout(orientation='vertical')

        with root_layout.canvas.before:
            Color(0.08, 0.08, 0.1, 1)
            Rectangle(pos=root_layout.pos, size=root_layout.size)
        root_layout.bind(pos=lambda i, v: setattr(root_layout.canvas.before.children[1], 'pos', v),
                         size=lambda i, v: setattr(root_layout.canvas.before.children[1], 'size', v))

        top_bar = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(8), dp(4), dp(8), dp(4)],
                            spacing=dp(6))
        with top_bar.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=lambda i, v: setattr(top_bar.canvas.before.children[1], 'pos', v),
                     size=lambda i, v: setattr(top_bar.canvas.before.children[1], 'size', v))

        self.search_input = TextInput(hint_text='搜索疾病...', multiline=False,
                                      size_hint_x=0.7, height=dp(38),
                                      font_size=sp(14), padding=[dp(8), dp(8), dp(8), dp(8)])
        self.search_input.bind(on_text_validate=self.do_search)
        top_bar.add_widget(self.search_input)

        search_btn = Button(text='搜索', size_hint_x=0.15, height=dp(38),
                            font_size=sp(13), background_color=(0.25, 0.59, 1, 1),
                            color=(1, 1, 1, 1))
        search_btn.bind(on_press=self.do_search)
        top_bar.add_widget(search_btn)

        clear_btn = Button(text='清除', size_hint_x=0.15, height=dp(38),
                           font_size=sp(13), background_color=(0.3, 0.3, 0.35, 1),
                           color=(1, 1, 1, 1))
        clear_btn.bind(on_press=self.clear_search)
        top_bar.add_widget(clear_btn)

        root_layout.add_widget(top_bar)

        content = BoxLayout(orientation='horizontal', spacing=dp(2))

        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.35,
                               padding=[dp(4), dp(4), dp(2), dp(4)])
        with left_panel.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            Rectangle(pos=left_panel.pos, size=left_panel.size)
        left_panel.bind(pos=lambda i, v: setattr(left_panel.canvas.before.children[1], 'pos', v),
                        size=lambda i, v: setattr(left_panel.canvas.before.children[1], 'size', v))

        left_label = Label(text='疾病列表', font_size=sp(13), color=(0.5, 0.5, 0.55, 1),
                           size_hint_y=None, height=dp(28))
        left_panel.add_widget(left_label)

        self.disease_list = DiseaseListWidget(on_select=self.on_disease_selected)
        left_panel.add_widget(self.disease_list)
        content.add_widget(left_panel)

        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.65,
                                padding=[dp(2), dp(4), dp(4), dp(4)])
        with right_panel.canvas.before:
            Color(0.1, 0.1, 0.13, 1)
            Rectangle(pos=right_panel.pos, size=right_panel.size)
        right_panel.bind(pos=lambda i, v: setattr(right_panel.canvas.before.children[1], 'pos', v),
                         size=lambda i, v: setattr(right_panel.canvas.before.children[1], 'size', v))

        self.detail = DetailPanel()
        right_panel.add_widget(self.detail)
        content.add_widget(right_panel)

        root_layout.add_widget(content)

        bottom_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(8), dp(2), dp(8), dp(4)],
                               spacing=dp(8))
        with bottom_bar.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            Rectangle(pos=bottom_bar.pos, size=bottom_bar.size)
        bottom_bar.bind(pos=lambda i, v: setattr(bottom_bar.canvas.before.children[1], 'pos', v),
                        size=lambda i, v: setattr(bottom_bar.canvas.before.children[1], 'size', v))

        self.status_label = Label(text='就绪', font_size=sp(11), color=(0.5, 0.5, 0.55, 1),
                                  halign='left', valign='middle', size_hint_x=0.6)
        self.status_label.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        bottom_bar.add_widget(self.status_label)

        user_label_text = 'admin'
        self.user_label = Label(text=user_label_text, font_size=sp(11),
                                color=(0.4, 0.4, 0.45, 1), size_hint_x=0.2)
        bottom_bar.add_widget(self.user_label)

        logout_btn = Button(text='退出', size_hint_x=0.2, height=dp(32),
                            font_size=sp(12), background_color=(0.6, 0.2, 0.2, 1),
                            color=(1, 1, 1, 1))
        logout_btn.bind(on_press=self.do_logout)
        bottom_bar.add_widget(logout_btn)

        root_layout.add_widget(bottom_bar)

        self.add_widget(root_layout)

    def on_enter(self, *args):
        app = App.get_running_app()
        self.disease_list.load_diseases(app.active_db)
        self.user_label.text = app.user_info.get('username', 'admin')
        self.status_label.text = f'已连接数据库: {os.path.basename(app.active_db)}'

    def on_disease_selected(self, disease_id):
        app = App.get_running_app()
        self.detail.load_disease(disease_id, app.active_db)
        self.status_label.text = f'已选择疾病 ID: {disease_id}'

    def do_search(self, instance):
        app = App.get_running_app()
        keyword = self.search_input.text.strip()
        self.disease_list.load_diseases(app.active_db, search=keyword if keyword else None)
        self.status_label.text = f'搜索: {keyword}' if keyword else '就绪'

    def clear_search(self, instance):
        self.search_input.text = ''
        app = App.get_running_app()
        self.disease_list.load_diseases(app.active_db)
        self.status_label.text = '就绪'

    def do_logout(self, instance):
        self.manager.current = 'login'


class RadAtlasApp(App):
    def build(self):
        self.title = 'RadAtlas 影像图鉴助手'
        self.user_info = {}
        self.active_db = DATABASE

        Window.clearcolor = (0.08, 0.08, 0.1, 1)

        Builder.load_string(KV)

        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(MainScreen())
        return sm

    def on_start(self):
        init_user_db()


if __name__ == '__main__':
    RadAtlasApp().run()
