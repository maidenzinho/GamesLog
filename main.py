import sys, os, json, shutil, datetime, requests
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QGridLayout, QDialog, QTextEdit, QMessageBox, QScrollArea,
    QMenu, QColorDialog, QInputDialog, QListWidgetItem, QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtGui import QPixmap, QCursor, QColor, QIcon, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint

import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

RAWG_API = "https://api.rawg.io/api/games"
RAWG_KEY = ""

PLATAFORMAS = ["Steam", "Epic Games", "PSN", "Xbox", "GOG", "Nintendo", "Outros"]
STATUS_OPTIONS = ["Finalizado", "Jogando", "Não jogado", "Desejado"]
BIB_PATH = "biblioteca.json"
BACKUP_DIR = "backups"
PROFILE_PATH = "profile.json"
PRINTS_DIR = "prints"

THEMES = {
    "Steam": {"bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #19202a, stop:1 #293b4a)", "fg": "#f3f6fa", "btn": "#223349", "input": "#212735", "accent": "#66c0f4"},
    "Dark":  {"bg": "#23232b", "fg": "#f3f3fa", "btn": "#444", "input": "#111", "accent": "#6cf"},
    "Neon":  {"bg": "#1a1a27", "fg": "#fafff3", "btn": "#2ee9e2", "input": "#1b1c25", "accent": "#a0f"},
    "Light": {"bg": "#fcfcfd", "fg": "#23232b", "btn": "#edeef3", "input": "#fff", "accent": "#6cf"},
}
THEME_NAMES = list(THEMES.keys())

ICON_URLS = {
    "Biblioteca": "https://img.icons8.com/color/48/000000/books.png",
    "Favoritos": "https://img.icons8.com/color/48/000000/star--v1.png",
    "Resumo/Gráficos": "https://img.icons8.com/color/48/000000/combo-chart--v1.png",
    "Exportar": "https://img.icons8.com/color/48/000000/export-excel.png",
    "Configurações": "https://img.icons8.com/color/48/000000/settings--v1.png",
    "Upload": "https://img.icons8.com/color/48/000000/upload.png",
    "Adicionar": "https://img.icons8.com/color/48/000000/plus--v1.png",
    "Perfil": "https://img.icons8.com/emoji/48/1f464.png"
}
MENU_TOP = [
    ("Biblioteca", ICON_URLS["Biblioteca"]),
    ("Favoritos", ICON_URLS["Favoritos"]),
    ("Resumo/Gráficos", ICON_URLS["Resumo/Gráficos"]),
    ("Exportar", ICON_URLS["Exportar"]),
    ("Configurações", ICON_URLS["Configurações"]),
    ("Perfil", ICON_URLS["Perfil"])
]

def icon_from_url(url):
    try:
        response = requests.get(url)
        pix = QPixmap()
        pix.loadFromData(response.content)
        return QIcon(pix)
    except Exception:
        return QIcon()

def add_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(22)
    shadow.setColor(QColor(0, 0, 0, 140))
    shadow.setOffset(0, 4)
    widget.setGraphicsEffect(shadow)

def crop_and_fit(img_data, size=(180, 260)):
    try:
        image = Image.open(BytesIO(img_data)).convert('RGB')
        iw, ih = image.size
        tw, th = size
        scale = max(tw / iw, th / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        image = image.resize((nw, nh), Image.LANCZOS)
        left = (nw - tw) // 2
        top = (nh - th) // 2
        image = image.crop((left, top, left + tw, top + th))
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
    except Exception:
        return None

def ensure_dirs():
    if not os.path.exists(PRINTS_DIR): os.makedirs(PRINTS_DIR)

class Toast(QWidget):
    def __init__(self, message, parent=None, duration=1700):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        label = QLabel(message)
        label.setStyleSheet("""
            background: rgba(0,0,0,0.85); color: #fff;
            border-radius: 12px; padding: 15px 35px;
            font-size: 17px; font-weight: bold; letter-spacing: 0.6px;
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.adjustSize()
        scr = QApplication.primaryScreen().geometry()
        self.move(scr.center() - self.rect().center() + QPoint(0, 170))
        QTimer.singleShot(duration, self.close)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        layout = QVBoxLayout(self)
        try:
            label = QLabel(self)
            label.setAlignment(Qt.AlignCenter)
            movie = QMovie("background.gif")
            label.setMovie(movie)
            movie.start()
            layout.addWidget(label)
        except:
            pass
        self.setStyleSheet("background: #101020;")
        lbl_title = QLabel("GAMESLOG")
        lbl_title.setStyleSheet("color: #66c0f4; font-size: 38px; font-weight: bold; letter-spacing:2.5px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        self.setFixedSize(640, 350)

class AddGameDialog(QDialog):
    def __init__(self, parent, add_callback):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Jogo")
        self.setFixedWidth(760)
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        self.inputs = {}
        self.fields = [
            ("Nome", QLineEdit()),
            ("Plataforma", QComboBox()),
            ("Data de compra", QLineEdit()),
            ("Preço pago", QLineEdit()),
            ("Nº comprovante", QLineEdit()),
            ("Nota pessoal", QLineEdit()),
            ("Status", QComboBox()),
            ("Anotações", QLineEdit()),
        ]
        self.fields[1][1].addItems(PLATAFORMAS)
        self.fields[6][1].addItems(STATUS_OPTIONS)
        for i, (label, widget) in enumerate(self.fields):
            grid.addWidget(QLabel(label+":"), i, 0)
            grid.addWidget(widget, i, 1)
            self.inputs[label] = widget
        self.uploaded_img_path = None
        self.img_btn = QPushButton(icon_from_url(ICON_URLS["Upload"]), "Upload Capa")
        self.img_btn.clicked.connect(self.upload_image)
        grid.addWidget(self.img_btn, 7, 2)
        layout.addLayout(grid)
        btn_box = QHBoxLayout()
        self.add_btn = QPushButton(icon_from_url(ICON_URLS["Adicionar"]), "Adicionar")
        self.add_btn.clicked.connect(self.do_add)
        btn_box.addWidget(self.add_btn)
        btn_box.addStretch()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)
        self.add_callback = add_callback

    def upload_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Escolha a imagem", "", "Imagens (*.png *.jpg *.jpeg)")
        if fname:
            self.uploaded_img_path = fname
            Toast("Imagem carregada com sucesso!", self).show()
        else:
            self.uploaded_img_path = None

    def do_add(self):
        vals = {k: (v.currentText() if isinstance(v, QComboBox) else v.text()) for k, v in self.inputs.items()}
        self.add_callback(vals, self.uploaded_img_path)
        self.accept()

class ProfileEditor(QDialog):
    def __init__(self, parent, profile, update_cb):
        super().__init__(parent)
        self.setWindowTitle("Editar Perfil")
        self.setFixedWidth(520)
        self.profile = profile
        layout = QVBoxLayout(self)
        # Avatar
        av_box = QHBoxLayout()
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(92, 92)
        self.avatar_label.setStyleSheet("border-radius: 46px; background: #222;")
        if profile.get("avatar"):
            pix = QPixmap(profile["avatar"])
            self.avatar_label.setPixmap(pix.scaled(92, 92, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        av_box.addWidget(self.avatar_label)
        self.avatar_btn = QPushButton("Alterar Foto")
        self.avatar_btn.clicked.connect(self.upload_avatar)
        av_box.addWidget(self.avatar_btn)
        self.remove_avatar_btn = QPushButton("Remover Foto")
        self.remove_avatar_btn.clicked.connect(self.remove_avatar)
        av_box.addWidget(self.remove_avatar_btn)
        layout.addLayout(av_box)
        # Nickname
        nick_box = QHBoxLayout()
        nick_box.addWidget(QLabel("Nome:"))
        self.nick_input = QLineEdit(profile.get("nickname", ""))
        nick_box.addWidget(self.nick_input)
        layout.addLayout(nick_box)
        # Bio
        layout.addWidget(QLabel("Bio:"))
        self.bio_input = QTextEdit(profile.get("bio", ""))
        layout.addWidget(self.bio_input)
        # Salvar
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
        self.update_cb = update_cb

    def upload_avatar(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Escolha avatar", "", "Imagens (*.png *.jpg *.jpeg)")
        if fname:
            self.profile["avatar"] = fname
            pix = QPixmap(fname)
            self.avatar_label.setPixmap(pix.scaled(92, 92, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def remove_avatar(self):
        self.profile["avatar"] = ""
        self.avatar_label.setPixmap(QPixmap())

    def save(self):
        self.profile["nickname"] = self.nick_input.text()
        self.profile["bio"] = self.bio_input.toPlainText()
        self.update_cb(self.profile)
        self.accept()

class PostDialog(QDialog):
    def __init__(self, parent, add_cb):
        super().__init__(parent)
        self.setWindowTitle("Novo Post/Print")
        self.setFixedWidth(480)
        layout = QVBoxLayout(self)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Texto do post, anotações do jogo, etc...")
        layout.addWidget(self.text_input)
        self.img_btn = QPushButton("Adicionar Print")
        self.img_btn.clicked.connect(self.upload_print)
        layout.addWidget(self.img_btn)
        self.print_path = None
        btn_box = QHBoxLayout()
        add = QPushButton("Postar")
        add.clicked.connect(self.add_post)
        btn_box.addWidget(add)
        btn_box.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        btn_box.addWidget(cancel)
        layout.addLayout(btn_box)
        self.add_cb = add_cb

    def upload_print(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Escolha print", "", "Imagens (*.png *.jpg *.jpeg)")
        if fname:
            self.print_path = fname
            Toast("Print carregado!", self).show()

    def add_post(self):
        self.add_cb(self.text_input.toPlainText(), self.print_path)
        self.accept()

class GameLibrary(QWidget):
    def __init__(self):
        super().__init__()
        ensure_dirs()
        self.setWindowTitle("GAMESLOG by Maiden")
        self.setGeometry(60, 35, 1400, 900)
        self.games = []
        self.theme = "Steam"
        self.profile = {
            "nickname": "Maiden",
            "bio": "Gamer entusiasta!",
            "avatar": "",
            "wallpaper": "",
            "posts": []
        }
        self.setup_ui()
        self.load_library()
        self.load_profile()

    def setup_ui(self):
        font = QFont('Segoe UI', 13)
        QApplication.instance().setFont(font)
        self.setStyleSheet(self.generate_stylesheet())

        layout = QVBoxLayout(self)
        self.topbar = QWidget()
        self.topbar.setFixedHeight(60)
        topbar_layout = QHBoxLayout(self.topbar)
        topbar_layout.setContentsMargins(10, 6, 10, 6)
        topbar_layout.setSpacing(30)
        self.menu_btns = []
        for idx, (name, icon_url) in enumerate(MENU_TOP):
            btn = QPushButton(name)
            btn.setIcon(icon_from_url(icon_url))
            btn.setIconSize(QSize(26, 26))
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton { background: transparent; color: #d8dee9; border: none; font-size: 19px; padding: 6px 20px 4px 12px; }
                QPushButton:checked { color: #66c0f4; border-bottom: 3px solid #66c0f4; font-weight: bold;}
                QPushButton:hover { color: #a0cbff; }
            """)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            self.menu_btns.append(btn)
            topbar_layout.addWidget(btn)
        self.menu_btns[0].setChecked(True)
        topbar_layout.addStretch()
        layout.addWidget(self.topbar)

        self.pages = []

        # ---------- Biblioteca ----------
        self.page_biblioteca = QWidget()
        vbox = QVBoxLayout(self.page_biblioteca)
        vbox.setSpacing(18)
        # Botão Add (MODAL)
        add_btn = QPushButton(icon_from_url(ICON_URLS["Adicionar"]), "Adicionar Jogo")
        add_btn.setFixedWidth(180)
        add_btn.setStyleSheet("QPushButton {background:#66c0f4; color:#fff; font-weight:600; font-size:19px; border-radius:11px; padding:9px 0;}")
        add_btn.clicked.connect(self.open_add_game)
        vbox.addWidget(add_btn, alignment=Qt.AlignLeft)

        # Busca
        search_layout = QHBoxLayout()
        self.input_search = QLineEdit(); self.input_search.setPlaceholderText("Pesquisar")
        self.input_search.textChanged.connect(self.refresh_library)
        search_layout.addWidget(self.input_search)
        vbox.addLayout(search_layout)
        # Grade
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.library_widget = QWidget()
        self.library_grid = QGridLayout(self.library_widget)
        self.scroll.setWidget(self.library_widget)
        vbox.addWidget(self.scroll)
        self.pages.append(self.page_biblioteca)

        # ---------- Favoritos ----------
        self.page_fav = QWidget()
        vbox_fav = QVBoxLayout(self.page_fav)
        self.scroll_fav = QScrollArea()
        self.scroll_fav.setWidgetResizable(True)
        self.widget_fav = QWidget()
        self.grid_fav = QGridLayout(self.widget_fav)
        self.scroll_fav.setWidget(self.widget_fav)
        vbox_fav.addWidget(self.scroll_fav)
        self.pages.append(self.page_fav)

        # ---------- Resumo ----------
        self.page_resumo = QWidget()
        vbox_resumo = QVBoxLayout(self.page_resumo)
        self.resumo_btn = QPushButton(icon_from_url(ICON_URLS["Resumo/Gráficos"]), "Ver Gráficos e Resumo")
        self.resumo_btn.clicked.connect(self.show_summary)
        vbox_resumo.addWidget(self.resumo_btn)
        self.pages.append(self.page_resumo)

        # ---------- Exportar ----------
        self.page_export = QWidget()
        vbox_export = QVBoxLayout(self.page_export)
        self.export_btn = QPushButton(icon_from_url(ICON_URLS["Exportar"]), "Exportar Excel")
        self.export_btn.clicked.connect(self.export_excel)
        vbox_export.addWidget(self.export_btn)
        self.pages.append(self.page_export)

        # ---------- Configurações (temas) ----------
        self.page_config = QWidget()
        vbox_cfg = QVBoxLayout(self.page_config)
        self.theme_btns = []
        for tname in THEME_NAMES:
            btn = QPushButton(f"Tema: {tname}")
            btn.clicked.connect(lambda _, n=tname: self.set_theme(n))
            vbox_cfg.addWidget(btn)
            self.theme_btns.append(btn)
        vbox_cfg.addStretch()
        self.pages.append(self.page_config)

        # ---------- Perfil ----------
        self.page_profile = QWidget()
        vbox_profile = QVBoxLayout(self.page_profile)
        # wallpaper bg
        self.wallpaper_lbl = QLabel()
        self.wallpaper_lbl.setFixedHeight(280)
        self.wallpaper_lbl.setAlignment(Qt.AlignCenter)
        self.wallpaper_lbl.setStyleSheet("background:#b8c6d0; border-radius:20px;")
        vbox_profile.addWidget(self.wallpaper_lbl)
        # Botões wallpaper
        w_btns = QHBoxLayout()
        self.wall_btn = QPushButton("Escolher Wallpaper do Perfil")
        self.wall_btn.clicked.connect(self.choose_wallpaper)
        w_btns.addWidget(self.wall_btn)
        self.wall_rem_btn = QPushButton("Remover Wallpaper")
        self.wall_rem_btn.clicked.connect(self.remove_wallpaper)
        w_btns.addWidget(self.wall_rem_btn)
        w_btns.addStretch()
        vbox_profile.addLayout(w_btns)
        # Avatar e nickname
        top_p_box = QHBoxLayout()
        self.avatar_p = QLabel()
        self.avatar_p.setFixedSize(80, 80)
        self.avatar_p.setStyleSheet("border-radius:40px; background:#eee; border: 5px solid #fff; margin-right: 18px;")
        top_p_box.addWidget(self.avatar_p)
        self.nick_label = QLabel()
        self.nick_label.setStyleSheet("font-size:25px; font-weight:800; color:#a0f;")
        top_p_box.addWidget(self.nick_label)
        top_p_box.addStretch()
        self.edit_profile_btn = QPushButton("Editar Perfil")
        self.edit_profile_btn.clicked.connect(self.edit_profile)
        top_p_box.addWidget(self.edit_profile_btn)
        vbox_profile.addLayout(top_p_box)
        # Bio
        self.bio_label = QLabel()
        self.bio_label.setWordWrap(True)
        self.bio_label.setStyleSheet("font-size:16px; color:#ace; padding:7px;")
        vbox_profile.addWidget(self.bio_label)
        # Conquistas
        self.achievements_label = QLabel()
        vbox_profile.addWidget(self.achievements_label)
        # Jogos zerados
        self.finished_games_label = QLabel("Jogos Finalizados:")
        self.finished_games_label.setStyleSheet("font-weight:600; color:#9ff; font-size:17px;")
        vbox_profile.addWidget(self.finished_games_label)
        self.finished_games_list = QLabel()
        vbox_profile.addWidget(self.finished_games_list)
        # Prints/posts
        self.prints_label = QLabel("Posts e Prints dos Jogos:")
        self.prints_label.setStyleSheet("font-weight:600; color:#9ff; font-size:17px;")
        vbox_profile.addWidget(self.prints_label)
        self.prints_feed = QVBoxLayout()
        prints_feed_widget = QWidget()
        prints_feed_widget.setLayout(self.prints_feed)
        scroll_prints = QScrollArea()
        scroll_prints.setWidgetResizable(True)
        scroll_prints.setWidget(prints_feed_widget)
        vbox_profile.addWidget(scroll_prints)
        self.add_print_btn = QPushButton("Adicionar Post/Print")
        self.add_print_btn.clicked.connect(self.add_print_post)
        vbox_profile.addWidget(self.add_print_btn)
        self.pages.append(self.page_profile)

        self.page_stack = [
            self.page_biblioteca, self.page_fav, self.page_resumo, self.page_export,
            self.page_config, self.page_profile
        ]
        for page in self.page_stack:
            page.hide()
        self.page_biblioteca.show()

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        for page in self.page_stack:
            self.content_layout.addWidget(page)
        layout.addWidget(self.content_widget)
        self.setLayout(layout)
        self.refresh_library()
        self.refresh_profile()

    # ---------- Navegação -----------
    def switch_page(self, idx):
        for i, btn in enumerate(self.menu_btns):
            btn.setChecked(i == idx)
        for i, page in enumerate(self.page_stack):
            page.setVisible(i == idx)
        if idx == 0: self.refresh_library()
        if idx == 1: self.refresh_favs()
        if idx == 5: self.refresh_profile()

    # ----------- Biblioteca ---------
    def open_add_game(self):
        dlg = AddGameDialog(self, self.add_game)
        dlg.exec_()

    def add_game(self, vals, img_path):
        nome = vals["Nome"].strip()
        plataforma = vals["Plataforma"]
        if not nome:
            self.show_toast("Digite o nome do jogo!")
            return
        if img_path:
            with open(img_path, "rb") as f:
                img_data = f.read()
            img_base64 = img_data.hex()
        else:
            img_base64 = None
        dados_jogo = self.fetch_game_data(nome, plataforma) if not img_base64 else {}
        game = {
            "Nome": dados_jogo.get('nome', nome),
            "Plataforma/Loja": plataforma,
            "Data de compra": vals["Data de compra"].strip(),
            "Preço pago": vals["Preço pago"].strip(),
            "Nº comprovante": vals["Nº comprovante"].strip(),
            "Nota pessoal": vals["Nota pessoal"].strip(),
            "Status": vals["Status"],
            "Imagem": img_base64 if img_base64 else dados_jogo.get('imagem'),
            "Imagem_manual": bool(img_base64),
            "Gênero": dados_jogo.get('genero', ''),
            "Descrição": dados_jogo.get('descricao', ''),
            "Data lançamento": dados_jogo.get('data_lancamento', ''),
            "Desenvolvedor": dados_jogo.get('dev', ''),
            "Link": dados_jogo.get('link', ''),
            "Favorito": False,
            "Anotações": vals["Anotações"].strip()
        }
        self.games.append(game)
        self.save_library()
        self.refresh_library()
        self.show_toast("Jogo adicionado com sucesso!")

    def fetch_game_data(self, nome, plataforma):
        if not RAWG_KEY:
            return {}
        self.show_toast("Buscando detalhes do jogo...", 1100)
        params = {"key": RAWG_KEY, "search": nome, "page_size": 1}
        r = requests.get(RAWG_API, params=params)
        if r.status_code == 200 and r.json()['results']:
            game = r.json()['results'][0]
            descricao = self.get_description(game['id'])
            genero = ', '.join([g['name'] for g in game.get('genres', [])])
            imagem = game.get('background_image', '')
            data_lanc = game.get('released', '')
            dev = ', '.join([d['name'] for d in game.get('developers', [])]) if 'developers' in game else ""
            link = f"https://rawg.io/games/{game['slug']}"
            return {
                'nome': game['name'],
                'imagem': imagem,
                'genero': genero,
                'descricao': descricao,
                'data_lancamento': data_lanc,
                'dev': dev,
                'link': link
            }
        return {}

    def get_description(self, game_id):
        if not RAWG_KEY:
            return ""
        url = f"{RAWG_API}/{game_id}"
        r = requests.get(url, params={"key": RAWG_KEY})
        if r.status_code == 200:
            desc = r.json().get('description_raw', '')
            return desc if desc else ""
        return ""

    def refresh_library(self):
        for i in reversed(range(self.library_grid.count())):
            widget = self.library_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        filtro = self.input_search.text().lower()
        jogos = [g for g in self.games if
                 filtro in g['Nome'].lower()
                 or filtro in g['Plataforma/Loja'].lower()
                 or filtro in g.get('Gênero', '').lower()
                 or filtro in g.get('Status', '').lower()]
        colunas = 6
        for idx, game in enumerate(jogos):
            row, col = divmod(idx, colunas)
            capa = QLabel()
            capa.setFixedSize(QSize(180, 260))
            capa.setObjectName("capa")
            fav_borda = "3px solid gold;" if game.get("Favorito") else "1.5px solid #444;"
            capa.setStyleSheet(f"""
                border-radius:17px;
                border:{fav_borda}
                background:#18181f;
                margin:11px;
            """)
            add_shadow(capa)

            def enter(e, c=capa):
                c.setStyleSheet(c.styleSheet() + "box-shadow: 0 0 17px #5af,0 0 1px #000;")
            def leave(e, c=capa):
                c.setStyleSheet(c.styleSheet().replace("box-shadow: 0 0 17px #5af,0 0 1px #000;", ""))
            capa.enterEvent = enter
            capa.leaveEvent = leave

            if game.get("Imagem_manual"):
                try:
                    img_data = bytes.fromhex(game["Imagem"])
                    crop = crop_and_fit(img_data, (180, 260))
                    if crop:
                        pix = QPixmap()
                        pix.loadFromData(crop)
                        capa.setPixmap(pix)
                    else:
                        capa.setText("Sem imagem")
                except:
                    capa.setText("Sem imagem")
            elif game['Imagem']:
                try:
                    img_data = requests.get(game['Imagem'], timeout=4).content
                    crop = crop_and_fit(img_data, (180, 260))
                    if crop:
                        pix = QPixmap()
                        pix.loadFromData(crop)
                        capa.setPixmap(pix)
                    else:
                        capa.setText("Sem imagem")
                except:
                    capa.setText("Sem imagem")
            else:
                capa.setText("Sem imagem")

            capa.setCursor(QCursor(Qt.PointingHandCursor))
            capa.setToolTip(
                f"Nota pessoal: {game['Nota pessoal']}\nStatus: {game['Status']}"
                f"\nClique: Detalhes\nDireito: Favoritar/Remover\nMeio: Editar"
            )
            capa.mousePressEvent = lambda event, g=game: self.handle_mouse(event, g)
            self.library_grid.addWidget(capa, row, col)

    def handle_mouse(self, event, game):
        if event.button() == Qt.LeftButton:
            self.show_game_details(game)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(game)
        elif event.button() == Qt.MiddleButton:
            self.edit_game(game)

    def show_context_menu(self, game):
        menu = QMenu()
        fav_action = menu.addAction("Favoritar" if not game.get("Favorito") else "Desfavoritar")
        rem_action = menu.addAction("Remover")
        action = menu.exec_(QCursor.pos())
        if action == fav_action:
            game["Favorito"] = not game.get("Favorito", False)
            self.save_library()
            self.refresh_library()
            self.refresh_favs()
        elif action == rem_action:
            self.remove_game(game)

    def show_game_details(self, game):
        dlg = QDialog(self)
        dlg.setWindowTitle(game['Nome'])
        dlg.resize(800, 650)
        vbox = QVBoxLayout()
        if game.get("Imagem_manual"):
            try:
                img_data = bytes.fromhex(game["Imagem"])
                crop = crop_and_fit(img_data, (220, 320))
                if crop:
                    pix = QPixmap()
                    pix.loadFromData(crop)
                    lbl_capa = QLabel()
                    lbl_capa.setPixmap(pix)
                    vbox.addWidget(lbl_capa, alignment=Qt.AlignCenter)
            except: pass
        elif game['Imagem']:
            try:
                img_data = requests.get(game['Imagem'], timeout=4).content
                crop = crop_and_fit(img_data, (220, 320))
                if crop:
                    pix = QPixmap()
                    pix.loadFromData(crop)
                    lbl_capa = QLabel()
                    lbl_capa.setPixmap(pix)
                    vbox.addWidget(lbl_capa, alignment=Qt.AlignCenter)
            except: pass
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setHtml(f"""
            <b>{game['Nome']}</b><br>
            <b>Gênero:</b> {game.get('Gênero','')}<br>
            <b>Lançamento:</b> {game.get('Data lançamento','')}<br>
            <b>Desenvolvedor:</b> {game.get('Desenvolvedor','')}<br>
            <b>Plataforma/Loja:</b> {game.get('Plataforma/Loja','')}<br>
            <b>Status:</b> {game.get('Status','')}<br>
            <b>Nota pessoal:</b> {game.get('Nota pessoal','')}<br>
            <b>Preço pago:</b> {game.get('Preço pago','')}<br>
            <b>Data da compra:</b> {game.get('Data de compra','')}<br>
            <b>Número do comprovante:</b> {game.get('Nº comprovante','')}<br>
            <b>Anotações:</b> {game.get('Anotações','')}<br>
            <b>Link:</b> <a href="{game.get('Link','')}">{game.get('Link','')}</a><br>
            <b>Descrição:</b><br>
            {game.get('Descrição','')}
        """)
        vbox.addWidget(desc)
        dlg.setLayout(vbox)
        dlg.exec_()

    def remove_game(self, game):
        reply = QMessageBox.question(self, 'Remover Jogo',
            f"Remover {game['Nome']} da biblioteca?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.games.remove(game)
            self.save_library()
            self.refresh_library()
            self.refresh_favs()
            self.show_toast("Removido!")

    def edit_game(self, game):
        campos = [
            ("Data de compra", game["Data de compra"]),
            ("Preço pago", game["Preço pago"]),
            ("Nº comprovante", game["Nº comprovante"]),
            ("Nota pessoal", game["Nota pessoal"]),
            ("Status", game["Status"]),
            ("Anotações", game["Anotações"])
        ]
        for campo, valor in campos:
            if campo == "Status":
                status, ok = QInputDialog.getItem(self, "Editar Status", "Status:", STATUS_OPTIONS, STATUS_OPTIONS.index(valor), False)
                if ok: game["Status"] = status
            else:
                novo, ok = QInputDialog.getText(self, f"Editar {campo}", f"{campo}:", text=valor)
                if ok: game[campo] = novo
        self.save_library()
        self.refresh_library()
        self.show_toast("Alteração salva!")

    def refresh_favs(self):
        for i in reversed(range(self.grid_fav.count())):
            widget = self.grid_fav.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        favs = [g for g in self.games if g.get("Favorito")]
        colunas = 5
        for idx, game in enumerate(favs):
            row, col = divmod(idx, colunas)
            capa = QLabel()
            capa.setFixedSize(QSize(180, 260))
            capa.setStyleSheet("""
                border-radius:16px;
                border:3px solid gold;
                background:#181818;
                margin:10px;
            """)
            add_shadow(capa)
            if game.get("Imagem_manual"):
                try:
                    img_data = bytes.fromhex(game["Imagem"])
                    crop = crop_and_fit(img_data, (180, 260))
                    if crop:
                        pix = QPixmap()
                        pix.loadFromData(crop)
                        capa.setPixmap(pix)
                except:
                    capa.setText("Sem imagem")
            elif game['Imagem']:
                try:
                    img_data = requests.get(game['Imagem'], timeout=4).content
                    crop = crop_and_fit(img_data, (180, 260))
                    if crop:
                        pix = QPixmap()
                        pix.loadFromData(crop)
                        capa.setPixmap(pix)
                except:
                    capa.setText("Sem imagem")
            else:
                capa.setText("Sem imagem")
            capa.setCursor(QCursor(Qt.PointingHandCursor))
            capa.setToolTip("Clique: Detalhes\nDireito: Desfavoritar\nMeio: Editar")
            capa.mousePressEvent = lambda event, g=game: self.handle_mouse(event, g)
            self.grid_fav.addWidget(capa, row, col)

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Planilha", "", "Excel Files (*.xlsx)")
        if not path: return
        df = pd.DataFrame(self.games)
        df.to_excel(path, index=False)
        self.show_toast(f"Planilha salva!")

    def show_summary(self):
        if not self.games:
            self.show_toast("Nenhum jogo na biblioteca.")
            return
        df = pd.DataFrame(self.games)
        plt.figure(figsize=(15, 10))
        plt.subplot(2, 2, 1)
        lojas = df['Plataforma/Loja'].value_counts()
        plt.pie(lojas, labels=lojas.index, autopct='%1.0f%%')
        plt.title("Jogos por Loja")
        plt.subplot(2, 2, 2)
        status = df['Status'].value_counts()
        plt.pie(status, labels=status.index, autopct='%1.0f%%')
        plt.title("Status dos Jogos")
        plt.subplot(2, 2, 3)
        generos = df['Gênero'].str.split(',').explode().value_counts().head(10)
        generos.plot(kind='bar', color='skyblue')
        plt.title("Jogos por Gênero (Top 10)")
        plt.subplot(2, 2, 4)
        df['Preço pago'] = pd.to_numeric(df['Preço pago'].str.replace(',', '.').str.replace('R$', '').str.strip(), errors='coerce')
        gastos = df.groupby("Plataforma/Loja")["Preço pago"].sum()
        gastos.plot(kind='bar', color='orange')
        plt.title("Gastos por Plataforma")
        plt.tight_layout()
        plt.show()
        total_gasto = df['Preço pago'].sum()
        resumo = (
            f"Quantidade total de jogos: {len(df)}\n"
            f"Total gasto: R$ {total_gasto:.2f}\n"
            f"Jogos por loja:\n{lojas.to_string()}\n"
            f"Jogos por status:\n{status.to_string()}"
        )
        self.show_toast("Resumo exibido nos gráficos!")

    # ----------- Perfil (Aba) ---------
    def refresh_profile(self):
        # Avatar
        if self.profile.get("avatar") and os.path.exists(self.profile["avatar"]):
            pix = QPixmap(self.profile["avatar"])
            self.avatar_p.setPixmap(pix.scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.avatar_p.setPixmap(QPixmap())
        # Nickname
        self.nick_label.setText(f'<span style="color:#a0f;">{self.profile.get("nickname", "Usuário")}</span>')
        # Bio
        self.bio_label.setText(self.profile.get("bio", ""))
        # Wallpaper
        if self.profile.get("wallpaper") and os.path.exists(self.profile["wallpaper"]):
            pix = QPixmap(self.profile["wallpaper"])
            self.wallpaper_lbl.setPixmap(pix.scaled(self.wallpaper_lbl.width(), self.wallpaper_lbl.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.wallpaper_lbl.setPixmap(QPixmap())
        # Conquistas
        conquistas = self.get_achievements()
        self.achievements_label.setText(f'Conquistas: 🏅 x{conquistas}')
        # Jogos zerados
        zerados = [g['Nome'] for g in self.games if g.get("Status") == "Finalizado"]
        self.finished_games_list.setText(', '.join(zerados) if zerados else "Nenhum jogo finalizado.")
        # Posts/Prints
        self.load_prints()

    def edit_profile(self):
        dlg = ProfileEditor(self, self.profile, self.update_profile)
        dlg.exec_()

    def update_profile(self, profile):
        self.profile = profile
        self.save_profile()
        self.refresh_profile()
        self.show_toast("Perfil atualizado!")

    def choose_wallpaper(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Escolha papel de parede", "", "Imagens (*.png *.jpg *.jpeg)")
        if fname:
            self.profile["wallpaper"] = fname
            self.save_profile()
            self.refresh_profile()
            self.show_toast("Wallpaper atualizado!")

    def remove_wallpaper(self):
        self.profile["wallpaper"] = ""
        self.save_profile()
        self.refresh_profile()
        self.show_toast("Wallpaper removido!")

    def add_print_post(self):
        dlg = PostDialog(self, self.save_post)
        dlg.exec_()

    def save_post(self, text, img_path):
        post = {
            "text": text,
            "img": "",
            "created": datetime.datetime.now().isoformat()
        }
        if img_path:
            fname = os.path.basename(img_path)
            dst = os.path.join(PRINTS_DIR, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{fname}")
            shutil.copyfile(img_path, dst)
            post["img"] = dst
        self.profile.setdefault("posts", []).insert(0, post)
        self.save_profile()
        self.refresh_profile()
        self.show_toast("Post adicionado!")

    def load_prints(self):
        # Limpa prints antigos
        while self.prints_feed.count():
            child = self.prints_feed.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for post in self.profile.get("posts", []):
            post_box = QFrame()
            post_box.setFrameShape(QFrame.StyledPanel)
            box = QVBoxLayout(post_box)
            # Se imagem, exibe
            if post["img"] and os.path.exists(post["img"]):
                lbl_img = QLabel()
                lbl_img.setPixmap(QPixmap(post["img"]).scaled(440, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                box.addWidget(lbl_img)
            if post["text"]:
                lbl_txt = QLabel(post["text"])
                lbl_txt.setWordWrap(True)
                lbl_txt.setStyleSheet("font-size:16px; color:#eee;")
                box.addWidget(lbl_txt)
            lbl_dt = QLabel(datetime.datetime.fromisoformat(post["created"]).strftime('%d/%m/%Y %H:%M'))
            lbl_dt.setStyleSheet("color:#77aaff; font-size:13px;")
            box.addWidget(lbl_dt)
            self.prints_feed.addWidget(post_box)

    def get_achievements(self):
        # Exemplo: 1 conquista por jogo finalizado
        return len([g for g in self.games if g.get("Status") == "Finalizado"])

    # ----------- Arquivos -----------
    def save_library(self):
        with open(BIB_PATH, "w", encoding="utf-8") as f:
            json.dump(self.games, f, ensure_ascii=False, indent=2)
        self.backup_library()

    def backup_library(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"biblioteca_{timestamp}.json")
        shutil.copyfile(BIB_PATH, backup_path)

    def load_library(self):
        if os.path.exists(BIB_PATH):
            with open(BIB_PATH, "r", encoding="utf-8") as f:
                self.games = json.load(f)
            self.refresh_library()
            self.refresh_favs()

    def save_profile(self):
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def load_profile(self):
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
            self.refresh_profile()

    def set_theme(self, theme_name):
        self.theme = theme_name
        self.setStyleSheet(self.generate_stylesheet())
        self.show_toast(f"Tema: {theme_name}!")

    def generate_stylesheet(self):
        t = THEMES[self.theme]
        return f"""
            QWidget {{ background: {t['bg']}; color: {t['fg']}; font-size: 17px; font-family:'Segoe UI',Arial,sans-serif;}}
            QPushButton {{ background: {t['btn']}; color: {t['fg']}; border-radius: 8px; padding: 8px 16px; border:none; font-weight:500;}}
            QLineEdit, QComboBox {{ background: {t['input']}; color: {t['fg']}; border-radius: 7px; border:1.2px solid #555;}}
            QScrollArea {{ background:transparent; border-radius:13px;}}
            QDialog {{ background: {t['bg']}; color: {t['fg']};}}
            QTextEdit {{ background:{t['input']}; color:{t['fg']}; border-radius:9px; font-size:16px;}}
        """

    def show_toast(self, msg, duration=1750):
        toast = Toast(msg, self, duration)
        toast.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    def start_main():
        window = GameLibrary()
        window.show()
        splash.close()
        app.window = window
    QTimer.singleShot(1400, start_main)
    sys.exit(app.exec_())
