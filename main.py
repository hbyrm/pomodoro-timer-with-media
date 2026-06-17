import sys
import math
import threading
import os
import random
from PyQt6.QtCore import Qt, QTimer, QPointF, QUrl, QRectF, QPoint, QMetaObject, Q_ARG
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QResizeEvent
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTabWidget, 
                             QGroupBox, QFrame, QSlider, QListWidget, QListWidgetItem, 
                             QFileDialog, QTextEdit)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import yt_dlp

import win32gui
import win32con

class TomatoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0  
        self.is_dragging = False
        self.parent_app = parent
        self.last_minute_tick = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2)
        radius = min(width, height) / 2 - (10 * self.parent_app.scale_factor)

        is_break = self.parent_app.is_break_mode if hasattr(self.parent_app, 'is_break_mode') else False
        
        if is_break:
            base_dark = QColor(20, 80, 45)
            base_med = QColor(40, 145, 75)
            grad_start = QColor(76, 201, 240) 
            grad_end = QColor(34, 112, 63)
            leaf_color = QColor(210, 130, 40)
            lcd_color = QColor(0, 255, 255) 
        else:
            base_dark = QColor(130, 20, 20)
            base_med = QColor(180, 35, 35)
            grad_start = QColor(240, 70, 70)
            grad_end = QColor(190, 30, 30)
            leaf_color = QColor(46, 139, 87)
            lcd_color = QColor(57, 255, 20) 

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(base_dark))
        painter.drawEllipse(int(center.x() - radius), int(center.y() - radius + (3 * self.parent_app.scale_factor)), int(radius * 2), int(radius * 2))

        painter.setBrush(QBrush(base_med))
        painter.drawPie(int(center.x() - radius), int(center.y() - radius), 
                        int(radius * 2), int(radius * 2), 180 * 16, 180 * 16)

        painter.save()
        painter.translate(center)
        painter.rotate(self.angle)
        
        gradient = QLinearGradient(-radius, -radius, radius, radius)
        gradient.setColorAt(0.0, grad_start)
        gradient.setColorAt(1.0, grad_end)
        painter.setBrush(QBrush(gradient))
        painter.drawPie(int(-radius), int(-radius), int(radius * 2), int(radius * 2), 0, 180 * 16)
        
        painter.setBrush(QBrush(leaf_color))
        painter.drawEllipse(int(-10 * self.parent_app.scale_factor), int(-radius - (3 * self.parent_app.scale_factor)), int(20 * self.parent_app.scale_factor), int(8 * self.parent_app.scale_factor))
        painter.restore()

        painter.setPen(QPen(QColor(255, 255, 255, 180), max(1.0, 1.5 * self.parent_app.scale_factor)))
        font_size = max(7, int(radius / 10))
        painter.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
        for i in range(0, 61, 5):
            angle_rad = math.radians(i * 6 - 90)
            x1 = center.x() + (radius - (8 * self.parent_app.scale_factor)) * math.cos(angle_rad)
            y1 = center.y() + (radius - (8 * self.parent_app.scale_factor)) * math.sin(angle_rad)
            x2 = center.x() + radius * math.cos(angle_rad)
            y2 = center.y() + radius * math.sin(angle_rad)
            
            if y2 >= center.y():
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                painter.drawText(int(x1 - (8 * self.parent_app.scale_factor)), int(y1 + (11 * self.parent_app.scale_factor)), f"{i:02d}")

        painter.setPen(QPen(QColor(255, 255, 255), max(1, int(2 * self.parent_app.scale_factor))))
        painter.drawLine(int(center.x()), int(center.y() - radius), int(center.x()), int(center.y() - radius + (8 * self.parent_app.scale_factor)))

        rect_width = max(75, int(radius * 0.75))
        rect_height = max(24, int(radius * 0.30))
        rect_x = center.x() - rect_width / 2
        rect_y = center.y() - rect_height / 2
        
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 210)))  
        painter.drawRoundedRect(QRectF(rect_x, rect_y, rect_width, rect_height), 4, 4)
        
        mins = self.parent_app.total_seconds // 60
        secs = self.parent_app.total_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"
        
        painter.setPen(QPen(lcd_color, 250))  
        painter.setFont(QFont("Courier New", int(rect_height * 0.65), QFont.Weight.Bold))
        painter.drawText(QRectF(rect_x, rect_y + 1, rect_width, rect_height), Qt.AlignmentFlag.AlignCenter, time_str)

    def mousePressEvent(self, event):
        if self.parent_app.ghost_mode: return
        if event.button() == Qt.MouseButton.LeftButton and not self.parent_app.is_running:
            self.is_dragging = True
            self.update_angle(event.position())

    def mouseMoveEvent(self, event):
        if self.parent_app.ghost_mode: return
        if self.is_dragging:
            self.update_angle(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def update_angle(self, mouse_pos):
        center_x = self.width() / 2
        center_y = self.height() / 2
        dx = mouse_pos.x() - center_x
        dy = mouse_pos.y() - center_y
        
        rad = math.atan2(dy, dx)
        deg = math.degrees(rad)
        
        if deg < 0:
            deg += 360
            
        self.angle = deg
        minutes = int((self.angle / 360) * 60)
        
        if minutes != self.last_minute_tick:
            self.parent_app.play_click_sound()
            self.last_minute_tick = minutes
            
        self.parent_app.set_minutes_from_wheel(minutes)
        self.update()


class TopControlBar(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222222; color: white; border-top-left-radius: 4px; border-top-right-radius: 4px;")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(6, 0, 6, 0)
        self.layout.setSpacing(4)
        
        self.lbl_title = QLabel("🍅 Pomodoro")
        self.btn_ghost_toggle = QPushButton("👻 Hayalet: KAPALI")
        self.btn_ghost_toggle.clicked.connect(self.main_app.toggle_ghost_mode)
        
        self.btn_min = QPushButton("🗕")
        self.btn_min.clicked.connect(self.main_app.showMinimized)
        
        self.btn_close = QPushButton("🗙")
        self.btn_close.clicked.connect(QApplication.quit)
        
        self.layout.addWidget(self.lbl_title)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_ghost_toggle)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_close)
        
        self.drag_position = QPoint()
        self.update_bar_scaling()

    def update_bar_scaling(self):
        sf = self.main_app.scale_factor
        self.setFixedHeight(int(32 * sf))
        self.setFixedWidth(self.main_app.width())
        
        title_font = int(10 * sf)
        ghost_font = int(9 * sf)
        btn_font = int(11 * sf)
        
        self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: {title_font}px; border: none; background: transparent;")
        self.btn_ghost_toggle.setStyleSheet(f"background-color: #444; font-size: {ghost_font}px; font-weight: bold; padding: {int(2*sf)}px {int(4*sf)}px; border-radius: 3px; color: white; border: none;")
        self.btn_min.setStyleSheet(f"background: transparent; font-weight: bold; color: white; border: none; font-size: {btn_font}px;")
        self.btn_min.setFixedWidth(int(20 * sf))
        self.btn_close.setStyleSheet(f"background: transparent; font-weight: bold; color: #ff5555; border: none; font-size: {btn_font}px;")
        self.btn_close.setFixedWidth(int(20 * sf))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            self.main_app.blockSignals(True)
            self.main_app.move(new_pos.x(), new_pos.y() + self.height())
            self.main_app.blockSignals(False)
            event.accept()


class SafeListWidget(QListWidget):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_path = url.toLocalFile()
                if local_path and os.path.exists(local_path):
                    self.main_app.add_track_to_current_list(local_path, is_local=True)
                else:
                    self.main_app.add_track_to_current_list(url.toString(), is_local=False)
            event.acceptProposedAction()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            current_item = self.currentItem()
            if current_item:
                row = self.row(current_item)
                self.takeItem(row)
                self.main_app.sync_data_structures_after_delete()
        else:
            super().keyPressEvent(event)


class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint)
        
        self._is_initialized = False  
        self._in_resize_loop = False  
        self.scale_factor = 1.0 
        self.resize(280, 660) 
        
        self.total_seconds = 25 * 60 
        self.is_running = False
        self.is_break_mode = False 
        self.ghost_mode = False 
        
        self.work_tracks = {}
        self.break_tracks = {}
        self.current_playing_url = ""
        self.show_titles_mode = True 
        
        self.work_target_minutes = 25
        self.break_target_minutes = 5
        
        self.bg_player = QMediaPlayer()
        self.bg_audio = QAudioOutput()
        self.bg_player.setAudioOutput(self.bg_audio)
        self.bg_audio.setVolume(0.4)
        
        self.fx_player = QMediaPlayer()
        self.fx_audio = QAudioOutput()
        self.fx_player.setAudioOutput(self.fx_audio)
        
        self.bg_player.positionChanged.connect(self.on_media_position_changed)
        self.bg_player.durationChanged.connect(self.on_media_duration_changed)
        
        self.control_bar = TopControlBar(self)
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.tomato.angle = (25 / 60) * 360
        
        self._is_initialized = True
        self.update_dynamic_styles()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if not self._is_initialized or self._in_resize_loop: 
            return
            
        self._in_resize_loop = True  
        new_width = event.size().width()
        self.scale_factor = new_width / 280.0
        
        self.update_dynamic_styles()
        
        if hasattr(self, 'control_bar') and self.control_bar:
            self.control_bar.update_bar_scaling()
            self.control_bar.move(self.x(), self.y() - self.control_bar.height())
        self._in_resize_loop = False  

    def moveEvent(self, event):
        super().moveEvent(event)
        if self._is_initialized and hasattr(self, 'control_bar') and self.control_bar and not self.signalsBlocked():
            self.control_bar.blockSignals(True)
            self.control_bar.move(self.x(), self.y() - self.control_bar.height())
            self.control_bar.blockSignals(False)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame_body = QFrame(self)
        self.frame_body.setObjectName("FrameBody")
        self.body_layout = QVBoxLayout(self.frame_body)
        
        self.tomato = TomatoWidget(self)
        self.body_layout.addWidget(self.tomato, stretch=2)
        
        self.config_group = QGroupBox("Zaman Ayarları")
        self.config_layout = QHBoxLayout(self.config_group)
        
        self.lbl_w = QLabel("💼 Çalışma:")
        self.txt_work_min = QLineEdit("25")
        self.lbl_b = QLabel("☕ Mola:")
        self.txt_break_min = QLineEdit("5")
        self.btn_apply_config = QPushButton("Set")
        self.btn_apply_config.clicked.connect(self.apply_custom_times)
        
        self.config_layout.addWidget(self.lbl_w)
        self.config_layout.addWidget(self.txt_work_min)
        self.config_layout.addStretch()
        self.config_layout.addWidget(self.lbl_b)
        self.config_layout.addWidget(self.txt_break_min)
        self.config_layout.addStretch()
        self.config_layout.addWidget(self.btn_apply_config)
        self.body_layout.addWidget(self.config_group)
        
        self.lbl_mode = QLabel("🎯 ÇALIŞMA MODU - HAZIR")
        self.lbl_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layout.addWidget(self.lbl_mode)
        
        # ÜST LİSTE PANEL KONTROLLERİ
        self.list_header_layout = QHBoxLayout()
        self.btn_view_toggle = QPushButton("👁 Başlık Modu")
        self.btn_view_toggle.clicked.connect(self.toggle_view_mode)
        self.btn_local_file = QPushButton("📁 Dosya Ekle")
        self.btn_local_file.clicked.connect(self.open_local_file_dialog)
        self.list_header_layout.addWidget(self.btn_view_toggle)
        self.list_header_layout.addWidget(self.btn_local_file)
        self.body_layout.addLayout(self.list_header_layout)

        self.tabs = QTabWidget()
        
        # Listeleri Önce Tanımlıyoruz (Çökme Güvenliği)
        self.list_work = SafeListWidget(self)
        self.list_work.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.list_break = SafeListWidget(self)
        self.list_break.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Şimdi Sekmelere Ekliyoruz
        self.tabs.addTab(self.list_work, "💼 İş Listesi")
        self.tabs.addTab(self.list_break, "☕ Mola Listesi")
        
        # Nesneler oluştuktan SONRA sinyal bağlantısını güvenle yapıyoruz
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.body_layout.addWidget(self.tabs, stretch=4)
        
        # TOPLU LINK YAPISTIRMA ALANI
        self.add_track_layout = QVBoxLayout()
        self.txt_new_url = QTextEdit()
        self.txt_new_url.setPlaceholderText("YouTube linklerini satır satır buraya yapıştırın...")
        self.btn_add_url = QPushButton("➕ Linkleri Seçili Listeye Ekle")
        self.btn_add_url.clicked.connect(self.add_multiple_tracks_from_input)
        self.add_track_layout.addWidget(self.txt_new_url)
        self.add_track_layout.addWidget(self.btn_add_url)
        self.body_layout.addLayout(self.add_track_layout)
        
        # MEDYA KUMANDASI
        self.music_layout = QVBoxLayout()
        self.music_layout.setSpacing(4)
        
        self.btn_row_layout = QHBoxLayout()
        self.lbl_mus = QLabel("Müzik Kumandası:")
        
        self.btn_prev_music = QPushButton("⏮")
        self.btn_prev_music.clicked.connect(lambda: self.navigate_track(-1))
        self.btn_rewind_music = QPushButton("⏪")
        self.btn_rewind_music.clicked.connect(lambda: self.seek_relative(-10000)) 
        self.btn_play_music = QPushButton("▶")
        self.btn_play_music.clicked.connect(self.trigger_independent_music)
        self.btn_pause_music = QPushButton("⏸")
        self.btn_pause_music.clicked.connect(self.safe_pause_media)
        self.btn_stop_music = QPushButton("⏹")
        self.btn_stop_music.clicked.connect(self.safe_stop_media)
        self.btn_forward_music = QPushButton("⏩")
        self.btn_forward_music.clicked.connect(lambda: self.seek_relative(10000)) 
        self.btn_next_music = QPushButton("⏭")
        self.btn_next_music.clicked.connect(lambda: self.navigate_track(1))
        
        self.btn_row_layout.addWidget(self.lbl_mus)
        self.btn_row_layout.addStretch()
        self.btn_row_layout.addWidget(self.btn_prev_music)
        self.btn_row_layout.addWidget(self.btn_rewind_music)
        self.btn_row_layout.addWidget(self.btn_play_music)
        self.btn_row_layout.addWidget(self.btn_pause_music)
        self.btn_row_layout.addWidget(self.btn_stop_music)
        self.btn_row_layout.addWidget(self.btn_forward_music)
        self.btn_row_layout.addWidget(self.btn_next_music)
        self.music_layout.addLayout(self.btn_row_layout)
        
        self.timeline_layout = QHBoxLayout()
        self.slider_timeline = QSlider(Qt.Orientation.Horizontal)
        self.slider_timeline.setRange(0, 0)
        self.slider_timeline.sliderMoved.connect(self.on_slider_user_moved)
        self.lbl_time_track = QLabel("00:00 / 00:00")
        
        self.timeline_layout.addWidget(self.slider_timeline, stretch=1)
        self.timeline_layout.addWidget(self.lbl_time_track)
        self.music_layout.addLayout(self.timeline_layout)
        
        self.body_layout.addLayout(self.music_layout)
        
        self.btn_start = QPushButton("Zamanlayıcıyı Başlat")
        self.btn_start.clicked.connect(self.toggle_timer)
        self.body_layout.addWidget(self.btn_start)
        
        main_layout.addWidget(self.frame_body)

    def update_dynamic_styles(self):
        if not self._is_initialized: 
            return
        sf = self.scale_factor
        
        self.body_layout.setContentsMargins(int(8*sf), int(8*sf), int(8*sf), int(8*sf))
        self.body_layout.setSpacing(int(5*sf))
        self.config_layout.setContentsMargins(int(6*sf), int(10*sf), int(6*sf), int(6*sf))
        self.config_layout.setSpacing(int(4*sf))
        self.btn_row_layout.setSpacing(int(3*sf))
        self.add_track_layout.setSpacing(int(3*sf))
        
        self.frame_body.setStyleSheet("QFrame#FrameBody { background-color: #fcfcfc; border: 1px solid #cccccc; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; }")
        self.config_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; color: #444; border: 1px solid #ddd; border-radius: 4px; font-size: {int(10*sf)}px; padding-top: {int(10*sf)}px; }}")
        
        self.lbl_w.setStyleSheet(f"font-size: {int(10*sf)}px; color: #333; background: transparent; border: none;")
        self.lbl_b.setStyleSheet(f"font-size: {int(10*sf)}px; color: #333; background: transparent; border: none;")
        
        self.txt_work_min.setFixedSize(int(32*sf), int(20*sf))
        self.txt_work_min.setStyleSheet(f"color:#000; background-color:#FFF; text-align:center; font-size:{int(10*sf)}px; border:1px solid #ccc; border-radius:2px;")
        self.txt_break_min.setFixedSize(int(32*sf), int(20*sf))
        self.txt_break_min.setStyleSheet(f"color:#000; background-color:#FFF; text-align:center; font-size:{int(10*sf)}px; border:1px solid #ccc; border-radius:2px;")
        
        self.btn_apply_config.setFixedSize(int(36*sf), int(20*sf))
        self.btn_apply_config.setStyleSheet(f"font-size: {int(9*sf)}px; font-weight: bold; background-color: #e0e0e0; border: 1px solid #aaa; border-radius: 2px; color: black;")
        
        self.btn_view_toggle.setStyleSheet(f"font-size: {int(9*sf)}px; font-weight: bold; padding: 2px; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 3px; color:#333;")
        self.btn_local_file.setStyleSheet(f"font-size: {int(9*sf)}px; font-weight: bold; padding: 2px; background-color: #e3f2fd; border: 1px solid #90caf9; border-radius: 3px; color:#0d47a1;")

        if self.is_break_mode:
            self.lbl_mode.setStyleSheet(f"font-weight: bold; color: #2a9d8f; font-size: {int(9*sf)}px; background-color: #e6f4f1; padding: {int(4*sf)}px; border-radius: 3px;")
        else:
            self.lbl_mode.setStyleSheet(f"font-weight: bold; color: #e63946; font-size: {int(9*sf)}px; background-color: #fce8e6; padding: {int(4*sf)}px; border-radius: 3px;")
            
        self.tabs.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid #ccc; }} QTabBar::tab {{ font-size: {int(10*sf)}px; padding: {int(4*sf)}px {int(8*sf)}px; }}")
        
        list_style = f"color: #000; background-color: #FFF; font-size: {int(10*sf)}px; border: 1px solid #eee; outline: 0;"
        self.list_work.setStyleSheet(list_style)
        self.list_break.setStyleSheet(list_style)
        
        self.txt_new_url.setFixedHeight(int(50*sf))
        self.txt_new_url.setStyleSheet(f"color:#000; background-color:#FFF; font-size:{int(9.5*sf)}px; border:1px solid #ccc; border-radius:2px; padding:4px;")
        self.btn_add_url.setFixedHeight(int(24*sf))
        self.btn_add_url.setStyleSheet(f"background-color:#4caf50; color:white; border:none; font-weight:bold; border-radius:2px; font-size:{int(10*sf)}px;")

        self.lbl_mus.setStyleSheet(f"font-size: {int(10*sf)}px; font-weight: bold; color: #555; background: transparent; border: none;")
        self.lbl_time_track.setStyleSheet(f"font-size: {int(9*sf)}px; font-family: 'Courier New'; color: #444; background: transparent; border: none;")
        
        btn_m_size = max(20, min(int(22 * sf), 30))
        for btn in [self.btn_prev_music, self.btn_rewind_music, self.btn_play_music, 
                    self.btn_pause_music, self.btn_stop_music, self.btn_forward_music, self.btn_next_music]:
            btn.setFixedSize(btn_m_size, btn_m_size)
            
        btn_style_base = f"color: white; font-weight: bold; border-radius: 3px; font-size: {int(9*sf)}px; border: none;"
        self.btn_prev_music.setStyleSheet("background-color: #555555;" + btn_style_base)
        self.btn_rewind_music.setStyleSheet("background-color: #6c757d;" + btn_style_base)
        self.btn_play_music.setStyleSheet("background-color: #2a9d8f;" + btn_style_base)
        self.btn_pause_music.setStyleSheet("background-color: #f4a261;" + btn_style_base)
        self.btn_stop_music.setStyleSheet("background-color: #e76f51;" + btn_style_base)
        self.btn_forward_music.setStyleSheet("background-color: #6c757d;" + btn_style_base)
        self.btn_next_music.setStyleSheet("background-color: #555555;" + btn_style_base)
        
        self.slider_timeline.setStyleSheet(f"""
            QSlider::groove:horizontal {{ border: 1px solid #bbb; height: {int(4*sf)}px; background: #ddd; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: #2a9d8f; border: 1px solid #1e7167; width: {int(10*sf)}px; margin-top: -{int(3*sf)}px; margin-bottom: -{int(3*sf)}px; border-radius: {int(5*sf)}px; }}
        """)
        
        self.btn_start.setFixedHeight(int(32 * sf))
        if self.is_running:
            self.btn_start.setStyleSheet(f"background-color: #457b9d; color: white; font-weight: bold; font-size: {int(11*sf)}px; border-radius: 3px; border: none;")
        elif self.is_break_mode:
            self.btn_start.setStyleSheet(f"background-color: #2a9d8f; color: white; font-weight: bold; font-size: {int(11*sf)}px; border-radius: 3px; border: none;")
        else:
            self.btn_start.setStyleSheet(f"background-color: #e63946; color: white; font-weight: bold; font-size: {int(11*sf)}px; border-radius: 3px; border: none;")

    # --- MEDYA OYNATICI TETİKLEYİCİLERİ ---
    def on_media_position_changed(self, position):
        try:
            if not self.slider_timeline.isSliderDown():
                self.slider_timeline.setValue(position)
            self.update_track_time_label(position, self.bg_player.duration())
        except: pass

    def on_media_duration_changed(self, duration):
        try:
            self.slider_timeline.setRange(0, duration)
            self.update_track_time_label(self.bg_player.position(), duration)
        except: pass

    def on_slider_user_moved(self, position):
        try: self.bg_player.setPosition(position)
        except: pass

    def seek_relative(self, ms_offset):
        try:
            new_pos = max(0, min(self.bg_player.position() + ms_offset, self.bg_player.duration()))
            self.bg_player.setPosition(new_pos)
        except: pass

    def safe_pause_media(self):
        try: self.bg_player.pause()
        except: pass

    def safe_stop_media(self):
        try: self.bg_player.stop()
        except: pass

    def update_track_time_label(self, position, duration):
        pos_sec, dur_sec = position // 1000, duration // 1000
        self.lbl_time_track.setText(f"{pos_sec//60:02d}:{pos_sec%60:02d} / {dur_sec//60:02d}:{dur_sec%60:02d}")

    # --- PLAYLIST MANTIĞI VE SEÇİMLER ---
    def add_track_to_current_list(self, raw_path, is_local=False):
        if not raw_path.strip(): return
        path = raw_path.strip()
        target_dict = self.break_tracks if self.tabs.currentIndex() == 1 else self.work_tracks
        target_list_widget = self.list_break if self.tabs.currentIndex() == 1 else self.list_work
        
        if path in target_dict: return 
        
        display_name = os.path.basename(path) if is_local else path
        target_dict[path] = {"title": display_name, "is_local": is_local, "played": False}
        
        item = QListWidgetItem(display_name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        target_list_widget.addItem(item)
        
        if not is_local: 
            threading.Thread(target=self.async_fetch_youtube_title, args=(path, target_dict, item), daemon=True).start()

    def add_multiple_tracks_from_input(self):
        raw_text = self.txt_new_url.toPlainText().strip()
        if raw_text:
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            for url in lines:
                self.add_track_to_current_list(url, is_local=False)
            self.txt_new_url.clear()

    def open_local_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Ses Dosyaları Seç", "", "Ses Dosyaları (*.mp3 *.wav *.ogg *.m4a *.aac)")
        for f in files:
            self.add_track_to_current_list(f, is_local=True)

    def on_item_double_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        target_dict = self.break_tracks if self.tabs.currentIndex() == 1 else self.work_tracks
        
        if path in target_dict:
            self.current_playing_url = path
            target_dict[path]["played"] = True
            self.update_list_display_texts()
            
            if target_dict[path]["is_local"]:
                self.bg_player.setSource(QUrl.fromLocalFile(path))
                self.bg_player.play()
            else:
                threading.Thread(target=self.play_youtube_audio, args=(path,), daemon=True).start()

    def toggle_view_mode(self):
        self.show_titles_mode = not self.show_titles_mode
        self.btn_view_toggle.setText("👁 Başlık Modu" if self.show_titles_mode else "🔗 URL Modu")
        self.update_list_display_texts()

    def update_list_display_texts(self):
        # Nesnelerin mevcut olup olmadığını kontrol eden koruma satırı
        if not hasattr(self, 'list_work') or not hasattr(self, 'list_break'):
            return
            
        for idx in range(2):
            list_widget = self.list_break if idx == 1 else self.list_work
            track_dict = self.break_tracks if idx == 1 else self.work_tracks
            
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                path = item.data(Qt.ItemDataRole.UserRole)
                if path in track_dict:
                    info = track_dict[path]
                    if info["is_local"]:
                        display = os.path.basename(path)
                    else:
                        display = info["title"] if self.show_titles_mode else path
                    
                    if info["played"]:
                        font = item.font()
                        font.setStrikeOut(True)
                        item.setFont(font)
                        item.setForeground(QColor(140, 140, 140))
                    else:
                        font = item.font()
                        font.setStrikeOut(False)
                        item.setFont(font)
                        item.setForeground(QColor(0, 0, 0))
                        
                    item.setText(display)

    def sync_data_structures_after_delete(self):
        idx = self.tabs.currentIndex()
        track_dict = self.break_tracks if idx == 1 else self.work_tracks
        list_widget = self.list_break if idx == 1 else self.list_work
        
        remaining_paths = [list_widget.item(i).data(Qt.ItemDataRole.UserRole) for i in range(list_widget.count())]
        for key in list(track_dict.keys()):
            if key not in remaining_paths:
                del track_dict[key]

    def on_tab_changed(self, index):
        self.update_list_display_texts()

    # --- ARKA PLAN VERİ MOTORU ---
    def async_fetch_youtube_title(self, url, target_dict, item):
        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', url)
                if url in target_dict:
                    target_dict[url]["title"] = title
                    QMetaObject.invokeMethod(self, "update_list_display_texts", Qt.ConnectionType.QueuedConnection)
        except: pass

    def play_youtube_audio(self, url):
        ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info['url']
                QMetaObject.invokeMethod(self.bg_player, "setSource", Qt.ConnectionType.QueuedConnection, Q_ARG(QUrl, QUrl(stream_url)))
                QMetaObject.invokeMethod(self.bg_player, "play", Qt.ConnectionType.QueuedConnection)
        except Exception as e: 
            print("Medya yüklenemedi:", e)

    def trigger_independent_music(self):
        if self.bg_player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.bg_player.play()
            return
            
        list_widget = self.list_break if self.tabs.currentIndex() == 1 else self.list_work
        if list_widget.count() > 0:
            random_idx = random.randint(0, list_widget.count() - 1)
            item = list_widget.item(random_idx)
            self.on_item_double_clicked(item)

    def navigate_track(self, direction):
        list_widget = self.list_break if self.tabs.currentIndex() == 1 else self.list_work
        if list_widget.count() == 0: return
        
        current_idx = -1
        for i in range(list_widget.count()):
            if list_widget.item(i).data(Qt.ItemDataRole.UserRole) == self.current_playing_url:
                current_idx = i
                break
                
        new_idx = (current_idx + direction) % list_widget.count()
        self.on_item_double_clicked(list_widget.item(new_idx))

    # --- TIMER VE DIGER KONTROLLER ---
    def toggle_ghost_mode(self):
        hwnd = int(self.winId())
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        sf = self.scale_factor
        
        if not self.ghost_mode:
            self.ghost_mode = True
            self.setWindowOpacity(0.35) 
            self.control_bar.btn_ghost_toggle.setText("👻 Hayalet: AÇIK")
            self.control_bar.btn_ghost_toggle.setStyleSheet(f"background-color: #2a9d8f; font-size: {int(9*sf)}px; font-weight: bold; padding: {int(2*sf)}px {int(4*sf)}px; border-radius: 3px; color: white; border: none;")
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        else:
            self.ghost_mode = False
            self.setWindowOpacity(1.0)
            self.control_bar.btn_ghost_toggle.setText("👻 Hayalet: KAPALI")
            self.control_bar.btn_ghost_toggle.setStyleSheet(f"background-color: #444; font-size: {int(9*sf)}px; font-weight: bold; padding: {int(2*sf)}px {int(4*sf)}px; border-radius: 3px; color: white; border: none;")
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style & ~win32con.WS_EX_TRANSPARENT)
        self.tomato.update()

    def apply_custom_times(self):
        if self.is_running: return
        try:
            self.work_target_minutes = int(self.txt_work_min.text().strip())
            self.break_target_minutes = int(self.txt_break_min.text().strip())
            current_target = self.break_target_minutes if self.is_break_mode else self.work_target_minutes
            self.total_seconds = current_target * 60
            self.tomato.angle = (current_target / 60) * 360
            self.tomato.update()
            self.play_click_sound()
        except ValueError: pass

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.safe_stop_media()
            self.is_running = False
            self.update_ui_state_visuals()
        else:
            if self.total_seconds > 0:
                self.is_running = True
                self.update_ui_state_visuals()
                self.trigger_independent_music() 
                self.timer.start(1000)

    def update_ui_state_visuals(self):
        sf = self.scale_factor
        if self.is_running:
            self.btn_start.setText("Durdur / Duraklat")
            self.btn_start.setStyleSheet(f"background-color: #457b9d; color: white; font-weight: bold; padding: {int(6*sf)}px; font-size: {int(11*sf)}px; border: none;")
        else:
            if self.is_break_mode:
                self.lbl_mode.setText("☕ MOLA - ONAY BEKLENİYOR")
                self.lbl_mode.setStyleSheet(f"font-weight: bold; color: #2a9d8f; font-size: {int(9*sf)}px; background-color: #e6f4f1; padding: {int(3*sf)}px; border-radius: 3px;")
                self.tabs.setCurrentIndex(1)
                self.btn_start.setText("Mola Süresini Başlat")
                self.btn_start.setStyleSheet(f"background-color: #2a9d8f; color: white; font-weight: bold; padding: {int(6*sf)}px; font-size: {int(11*sf)}px; border: none;")
            else:
                self.lbl_mode.setText("🎯 ÇALIŞMA - ONAY BEKLENİYOR")
                self.lbl_mode.setStyleSheet(f"font-weight: bold; color: #e63946; font-size: {int(9*sf)}px; background-color: #fce8e6; padding: {int(3*sf)}px; border-radius: 3px;")
                self.tabs.setCurrentIndex(0)
                self.btn_start.setText("Çalışma Süresini Başlat")
                self.btn_start.setStyleSheet(f"background-color: #e63946; color: white; font-weight: bold; padding: {int(6*sf)}px; font-size: {int(11*sf)}px; border: none;")

    def tick(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1
            self.play_click_sound()
            self.tomato.angle = (self.total_seconds / 3600) * 360
            self.tomato.update()
        else:
            self.timer.stop()
            self.safe_stop_media()
            self.play_alarm_sound()
            self.is_running = False
            
            if not self.is_break_mode:
                self.is_break_mode = True
                self.total_seconds = self.break_target_minutes * 60
                self.tomato.angle = (self.break_target_minutes / 60) * 360
            else:
                self.is_break_mode = False
                self.total_seconds = self.work_target_minutes * 60
                self.tomato.angle = (self.work_target_minutes / 60) * 360
            
            self.update_ui_state_visuals()
            self.tomato.update()

    def play_click_sound(self):
        if os.path.exists("tick.wav"):
            try:
                self.fx_player.setSource(QUrl.fromLocalFile("tick.wav"))
                self.fx_player.play()
            except: pass

    def play_alarm_sound(self):
        if os.path.exists("alarm.wav"):
            try:
                self.fx_player.setSource(QUrl.fromLocalFile("alarm.wav"))
                self.fx_player.play()
            except: pass

    def set_minutes_from_wheel(self, minutes):
        if self.is_running: return
        self.total_seconds = minutes * 60
        if self.is_break_mode:
            self.break_target_minutes = minutes
            self.txt_break_min.setText(str(minutes))
        else:
            self.work_target_minutes = minutes
            self.txt_work_min.setText(str(minutes))
        self.tomato.update()

    def closeEvent(self, event):
        if hasattr(self, 'control_bar') and self.control_bar:
            self.control_bar.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroApp()
    window.show()
    window.control_bar.move(window.x(), window.y() - window.control_bar.height())
    window.control_bar.show()
    sys.exit(app.exec())