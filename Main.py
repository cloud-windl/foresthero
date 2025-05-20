import sys
import json
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFrame, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QTransform, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent

# ---- 游戏常量 ----
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 400
GROUND_Y = 320
PLAYER_SIZE = 64
MONSTER_SIZE = 64
JUMP_HEIGHT = 100
GRAVITY = 8
PLAYER_SPEED = 8   # 玩家左右移动速度
ATTACK_DAMAGE = 1  # 每次攻击怪物扣血
MONSTER_DAMAGE = 1 # 每次怪物攻击玩家扣血
MONSTER_SCORE = 10 # 每击杀一只怪物得分

class PauseMenu(QWidget):
    def __init__(self, parent=None, save_callback=None, exit_callback=None):
        super().__init__(parent)
        if parent is not None:
            self.setFixedSize(parent.width(), parent.height())
        else:
            self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.bg_frame = QFrame(self)
        self.bg_frame.setFixedSize(480, 280)
        self.bg_frame.move((self.width()-480)//2, (self.height()-280)//2)
        self.bg_frame.setStyleSheet('background: none; border: none;')
        vbox = QVBoxLayout(self.bg_frame)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(44)
        # 保存按钮
        btn_save = QPushButton(self.bg_frame)
        import os
        icon_path = 'save_btn.png'
        if os.path.exists(icon_path):
            btn_save.setIcon(QIcon(icon_path))
        btn_save.setIconSize(QSize(320, 100))
        btn_save.setFixedSize(320, 100)
        btn_save.setStyleSheet('border:none; background:transparent;')
        # 退出按钮
        btn_exit = QPushButton(self.bg_frame)
        icon_path_exit = 'exit_btn.png'
        if os.path.exists(icon_path_exit):
            btn_exit.setIcon(QIcon(icon_path_exit))
        btn_exit.setIconSize(QSize(320, 100))
        btn_exit.setFixedSize(320, 100)
        btn_exit.setStyleSheet('border:none; background:transparent;')
        vbox.addStretch(1)
        vbox.addWidget(btn_save, alignment=Qt.AlignHCenter)
        vbox.addWidget(btn_exit, alignment=Qt.AlignHCenter)
        vbox.addStretch(1)
        btn_save.clicked.connect(lambda: save_callback() if save_callback else None)
        btn_exit.clicked.connect(lambda: exit_callback() if exit_callback else None)
        self.hide()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, False)
        qp.fillRect(self.rect(), QColor(0,0,0,120))
        x = (self.width()-480)//2
        y = (self.height()-280)//2
        w, h = 480, 280
        qp.setPen(QColor(30,30,30))
        qp.setBrush(QColor(80,80,80))
        qp.drawRect(x, y, w, h)
        qp.setPen(QColor(180,220,180))
        qp.drawRect(x+4, y+4, w-8, h-8)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(60, 60, 60, 220))
        qp.drawRect(x+8, y+8, w-16, h-16)
        super().paintEvent(event)

    def showEvent(self, event):
        self.raise_()
        self.activateWindow()
        super().showEvent(event)

    def mousePressEvent(self, event):
        if not self.bg_frame.geometry().contains(event.pos()):
            self.hide()


class GameOverMenu(QWidget):
    def __init__(self, parent=None, restart_callback=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(parent.width(), parent.height())
        self.bg_frame = QFrame(self)
        self.bg_frame.setFixedSize(480, 280)
        self.bg_frame.move((self.width()-480)//2, (self.height()-280)//2)
        self.bg_frame.setStyleSheet('background: none; border: none;')
        vbox = QVBoxLayout(self.bg_frame)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(44)
        self.label = QLabel('', self.bg_frame)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('font-size: 28px; color: #e74c3c;')
        btn_restart = QPushButton(self.bg_frame)
        if QPixmap('restart_btn.png').isNull() == False:
            btn_restart.setIcon(QIcon('restart_btn.png'))
        btn_restart.setIconSize(QSize(320, 100))
        btn_restart.setFixedSize(320, 100)
        btn_restart.setStyleSheet('border:none; background:transparent;')
        vbox.addStretch(1)
        vbox.addWidget(self.label, alignment=Qt.AlignHCenter)
        vbox.addWidget(btn_restart, alignment=Qt.AlignHCenter)
        vbox.addStretch(1)
        btn_restart.clicked.connect(lambda: restart_callback() if restart_callback else None)
        self.hide()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, False)
        qp.fillRect(self.rect(), QColor(0,0,0,120))
        x = (self.width()-480)//2
        y = (self.height()-280)//2
        w, h = 480, 280
        qp.setPen(QColor(30,30,30))
        qp.setBrush(QColor(80,80,80))
        qp.drawRect(x, y, w, h)
        qp.setPen(QColor(180,220,180))
        qp.drawRect(x+4, y+4, w-8, h-8)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(60, 60, 60, 220))
        qp.drawRect(x+8, y+8, w-16, h-16)
        super().paintEvent(event)


class StartMenu(QWidget):
    def __init__(self, start_callback=None, load_callback=None, exit_callback=None):
        super().__init__()
        self.setWindowTitle('开始菜单')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        self.bg_frame = QFrame(self)
        self.bg_frame.setFixedSize(400, 300)
        self.bg_frame.move((self.width()-400)//2, (self.height()-300)//2)
        self.bg_frame.setStyleSheet('background: none; border: none;')
        vbox = QVBoxLayout(self.bg_frame)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(36)
        label = QLabel('森林勇者', self.bg_frame)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('font-size: 36px; color: #27ae60; font-weight: bold;')
        vbox.addWidget(label, alignment=Qt.AlignHCenter)
        btn_start = QPushButton(self.bg_frame)
        if QPixmap('start_btn.png').isNull() == False:
            btn_start.setIcon(QIcon('start_btn.png'))
        btn_start.setIconSize(QSize(320, 80))
        btn_start.setFixedSize(320, 80)
        btn_start.setStyleSheet('border:none; background:transparent;')
        btn_start.clicked.connect(lambda: start_callback() if start_callback else None)
        vbox.addWidget(btn_start, alignment=Qt.AlignHCenter)
        btn_load = QPushButton(self.bg_frame)
        if QPixmap('load_btn.png').isNull() == False:
            btn_load.setIcon(QIcon('load_btn.png'))
        btn_load.setIconSize(QSize(320, 80))
        btn_load.setFixedSize(320, 80)
        btn_load.setStyleSheet('border:none; background:transparent;')
        btn_load.clicked.connect(lambda: load_callback() if load_callback else None)
        vbox.addWidget(btn_load, alignment=Qt.AlignHCenter)
        btn_exit = QPushButton(self.bg_frame)
        if QPixmap('exit_btn.png').isNull() == False:
            btn_exit.setIcon(QIcon('exit_btn.png'))
        btn_exit.setIconSize(QSize(320, 80))
        btn_exit.setFixedSize(320, 80)
        btn_exit.setStyleSheet('border:none; background:transparent;')
        btn_exit.clicked.connect(lambda: exit_callback() if exit_callback else None)
        vbox.addWidget(btn_exit, alignment=Qt.AlignHCenter)
        vbox.addStretch(1)
        self.hide()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, False)
        bg = QPixmap('bg_sky.png')
        if not bg.isNull():
            bg_scaled = bg.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            qp.drawPixmap(0, 0, bg_scaled)
        else:
            qp.setBrush(QBrush(QColor(180, 180, 180)))
            qp.drawRect(0, 0, self.width(), self.height())


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('森林勇者')
        self.base_width = 1536
        self.base_height = 1024
        self.scale_factor = 0.75
        self.setFixedSize(
            int(self.base_width * self.scale_factor),
            int(self.base_height * self.scale_factor)
        )
        self.setFocusPolicy(Qt.StrongFocus)

        # 初始化游戏状态
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = GROUND_Y
        self.player_vx = 0
        self.player_vy = 0
        self.is_jumping = False
        self.is_crouching = False
        self.player_hp = 10
        self.score = 0
        self.facing_left = False
        self.attack_animating = False
        self.attack_frame = 0
        self.attack_anim_delay = 0
        self.attack_anim_delay_max = 3
        self.attack_frame_count = 4
        self.walk_animating = False
        self.walk_frame = 0
        self.walk_anim_delay = 0
        self.walk_anim_delay_max = 3
        self.walk_frame_count = 4

        # 怪物列表
        self.monsters = []
        self.monster_timer = 0
        self.monster_move_frame_count = 3
        self.monster_attack_frame_count = 3

        # 加载资源（只加载一次）
        pix = QPixmap('player.png')
        self.player_img = pix if not pix.isNull() else None

        pix = QPixmap('monster.png')
        self.monster_img = pix if not pix.isNull() else None

        pix = QPixmap('ground.png')
        self.ground_img = pix if not pix.isNull() else None

        self.attack_imgs = []
        for i in range(self.attack_frame_count):
            pix = QPixmap(f'player_attack_{i}.png')
            self.attack_imgs.append(pix if not pix.isNull() else None)

        self.walk_imgs = []
        for i in range(self.walk_frame_count):
            pix = QPixmap(f'player_walk_{i}.png')
            self.walk_imgs.append(pix if not pix.isNull() else None)

        self.monster_move_imgs = []
        for i in range(self.monster_move_frame_count):
            pix = QPixmap(f'monster_move_{i}.png')
            self.monster_move_imgs.append(pix if not pix.isNull() else None)

        self.monster_attack_imgs = []
        for i in range(self.monster_attack_frame_count):
            pix = QPixmap(f'monster_attack_{i}.png')
            self.monster_attack_imgs.append(pix if not pix.isNull() else None)

        # 定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(30)

        # 暂停按钮
        self.menu_btn = QPushButton(self)
        if QPixmap('exit_btn.png').isNull() == False:
            self.menu_btn.setIcon(QIcon('exit_btn.png'))
        self.menu_btn.setIconSize(QSize(48, 48))
        self.menu_btn.setFixedSize(54, 54)
        self.menu_btn.move(self.width() - 64, 10)
        self.menu_btn.setStyleSheet('border:none; background:rgba(255,255,255,0.2);')
        self.menu_btn.clicked.connect(self.show_menu)

        self.pause_menu = PauseMenu(self, self.save_game, self.exit_game)
        self.pause_menu.hideEvent = self.on_menu_hide

        self.high_score = self.load_high_score()
        self.game_over = False
        self.game_over_menu = GameOverMenu(self, self.restart_game)

    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()
        ratio = self.base_width / self.base_height
        if w / h > ratio:
            w = int(h * ratio)
        else:
            h = int(w / ratio)
        self.setFixedSize(w, h)
        self.menu_btn.move(self.width() - 64, 10)
        self.pause_menu.setFixedSize(self.width(), self.height())
        self.pause_menu.bg_frame.move((self.width()-480)//2, (self.height()-280)//2)
        self.game_over_menu.setFixedSize(self.width(), self.height())
        self.game_over_menu.bg_frame.move((self.width()-480)//2, (self.height()-280)//2)
        super().resizeEvent(event)

    def load_high_score(self):
        try:
            with open('highscore.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open('highscore.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
        data['high_score'] = max(self.high_score, self.score)
        with open('highscore.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_game(self):
        try:
            data = {
                'player_x': self.player_x,
                'player_y': self.player_y,
                'player_hp': self.player_hp,
                'score': self.score,
                'monsters': self.monsters
            }
            with open('save.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.msg = '游戏已保存!'
        except Exception as e:
            self.msg = f'保存失败: {e}'
        self.update()
        # 弹窗反馈
        QMessageBox.information(self, '提示', self.msg)

    def exit_game(self):
        QApplication.quit()

    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = GROUND_Y
        self.player_vx = 0
        self.player_vy = 0
        self.is_jumping = False
        self.is_crouching = False
        self.player_hp = 10
        self.score = 0
        self.facing_left = False
        self.attack_animating = False
        self.attack_frame = 0
        self.attack_anim_delay = 0
        self.walk_animating = False
        self.walk_frame = 0
        self.walk_anim_delay = 0
        self.monsters = []
        self.monster_timer = 0
        self.game_over = False
        self.game_over_menu.hide()
        self.timer.start(30)
        self.update()

    def show_menu(self):
        self.timer.stop()
        self.pause_menu.show()

    def on_menu_hide(self, event):
        # 菜单隐藏时恢复游戏循环
        event.accept()
        self.timer.start(30)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.player_vx = -8
            self.facing_left = True
        elif event.key() == Qt.Key_D:
            self.player_vx = 8
            self.facing_left = False
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_Space:
            if not self.is_jumping:
                self.is_jumping = True
                self.player_vy = -18
        elif event.key() == Qt.Key_S:
            self.is_crouching = True
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in (Qt.Key_A, Qt.Key_D):
            self.player_vx = 0
        elif event.key() == Qt.Key_S:
            self.is_crouching = False
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.attack_animating:
                self.attack_animating = True
                self.attack_frame = 0
                self.attack_anim_delay = 0
        super().mousePressEvent(event)

    def spawn_monster(self):
        side = random.choice(['left', 'right'])
        x = 0 if side == 'left' else SCREEN_WIDTH - MONSTER_SIZE
        y = GROUND_Y
        speed = random.randint(3, 6)
        self.monsters.append({
            'x': x, 'y': y, 'speed': speed,
            'hp': 5, 'state': 'move',
            'frame': 0, 'anim_delay': 0, 'anim_delay_max': 4,
            'has_attacked': False  # 新增字段，标记是否已攻击
        })

    def check_monster_collision(self):
        for m in self.monsters:
            dist = abs((m['x'] + MONSTER_SIZE/2) - (self.player_x + PLAYER_SIZE/2))
            if self.attack_animating  and dist < 200:  # 攻击距离加大
                m['hp'] -= ATTACK_DAMAGE
                if m['hp'] <= 0:
                    self.score += MONSTER_SCORE
        for m in self.monsters:
            dist = abs((m['x'] + MONSTER_SIZE/2) - (self.player_x + PLAYER_SIZE/2))
            if m['state'] == 'attack' and dist < 100:  # 攻击距离加大
                if not m.get('has_attacked', False):
                    self.player_hp -= MONSTER_DAMAGE
                    m['has_attacked'] = True
            else:
                m['has_attacked'] = False  # 离开攻击状态重置
        self.monsters = [m for m in self.monsters if m['hp'] > 0]
        if self.player_hp < 0:
            self.player_hp = 0

    def game_loop(self):
        if self.player_hp <= 0:
            if not self.game_over:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                msg = f'游戏结束! 得分: {self.score}  历史最高分: {self.high_score}'
                self.game_over_menu.label.setText(msg)
                self.timer.stop()
                self.game_over_menu.show()
            self.update()
            return

        # 玩家移动
        self.player_x += self.player_vx
        psize = PLAYER_SIZE * 1.5
        self.player_x = max(0, min(self.player_x, SCREEN_WIDTH - psize))

        # 怪物生成
        self.monster_timer += 1
        if self.monster_timer > 40:
            self.spawn_monster()
            self.monster_timer = 0

        # 怪物更新与动画
        for m in self.monsters:
            m['x'] += m['speed'] if m['x'] < self.player_x else -m['speed']
            dist = abs((m['x'] + MONSTER_SIZE/2) - (self.player_x + PLAYER_SIZE/2))
            m['state'] = 'attack' if dist < 60 else 'move'
            m['anim_delay'] += 1
            if m['anim_delay'] >= m['anim_delay_max']:
                m['anim_delay'] = 0
                frame_count = self.monster_attack_frame_count if m['state']=='attack' else self.monster_move_frame_count
                m['frame'] = (m['frame'] + 1) % frame_count

        # 碰撞检测
        self.check_monster_collision()

        # 跳跃物理
        if self.is_jumping:
            self.player_y += self.player_vy
            self.player_vy += GRAVITY // 2
            if self.player_y >= GROUND_Y:
                self.player_y = GROUND_Y
                self.is_jumping = False
                self.player_vy = 0

        # 攻击动画
        if self.attack_animating:
            self.attack_anim_delay += 1
            if self.attack_anim_delay >= self.attack_anim_delay_max:
                self.attack_anim_delay = 0
                self.attack_frame += 1
                if self.attack_frame >= self.attack_frame_count:
                    self.attack_animating = False
                    self.attack_frame = 0

        # 行走动画
        if not self.attack_animating and self.player_vx != 0 and not self.is_jumping:
            self.walk_animating = True
            self.walk_anim_delay += 1
            if self.walk_anim_delay >= self.walk_anim_delay_max:
                self.walk_anim_delay = 0
                self.walk_frame = (self.walk_frame + 1) % self.walk_frame_count
        else:
            self.walk_animating = False
            self.walk_frame = 0
            self.walk_anim_delay = 0

        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        win_w, win_h = self.width(), self.height()
        scale = min(win_w / self.base_width, win_h / self.base_height)
        offset_x = (win_w - int(self.base_width * scale)) // 2
        offset_y = (win_h - int(self.base_height * scale)) // 2

        # 背景
        bg = QPixmap('bg_sky.png')
        if not bg.isNull():
            bg_scaled = bg.scaled(
                int(self.base_width * scale), int(self.base_height * scale),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            qp.drawPixmap(offset_x, offset_y, bg_scaled)
        else:
            qp.setBrush(QBrush(QColor(180, 180, 180)))
            qp.drawRect(0, 0, win_w, win_h)

        # 地面
        ground_y = int(self.base_height - 100)
        ground_y_scaled = int(ground_y * scale) + offset_y

        # 绘怪物
        for m in self.monsters:
            mx = int(m['x'] * scale) + offset_x
            msize = int(MONSTER_SIZE * 1.3 * scale)
            my = ground_y_scaled - msize
            if m['state']=='move' and self.monster_move_imgs[m['frame']]:
                img = self.monster_move_imgs[m['frame']]
            elif m['state']=='attack' and self.monster_attack_imgs[m['frame']]:
                img = self.monster_attack_imgs[m['frame']]
            else:
                img = self.monster_img
            if img:
                qp.drawPixmap(mx, my, msize, msize,
                              img.scaled(msize, msize, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                qp.setBrush(QBrush(QColor(200,50,50)))
                qp.drawRect(mx, my, msize, msize)

        # 玩家
        px = int(self.player_x * scale) + offset_x
        psize = int(PLAYER_SIZE * 1.5 * scale)
        py = ground_y_scaled - psize
        if self.attack_animating and self.attack_imgs[self.attack_frame]:
            img = self.attack_imgs[self.attack_frame]
        elif self.walk_animating and self.walk_imgs[self.walk_frame]:
            img = self.walk_imgs[self.walk_frame]
        else:
            img = self.player_img
        if img:
            if self.facing_left:
                img = img.transformed(QTransform().scale(-1, 1))
            qp.drawPixmap(px, py, psize, psize, img.scaled(psize, psize, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            qp.setBrush(QBrush(QColor(50, 100, 200)))
            qp.drawEllipse(px, py, psize, psize)

        # 显示分数和血量
        qp.setPen(QColor(255,255,255))
        qp.setFont(self.font())
        qp.drawText(20, 40, f"分数: {self.score}")
        qp.drawText(20, 80, f"生命: {self.player_hp}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    def start_game():
        menu.hide()
        game.show()
    def load_game():
        try:
            with open('save.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            game.player_x = data.get('player_x', game.player_x)
            game.player_y = data.get('player_y', game.player_y)
            game.player_hp = data.get('player_hp', 10)
            game.score = data.get('score', 0)
            game.monsters = data.get('monsters', [])
        except Exception as e:
            pass
        menu.hide()
        game.show()
    def exit_game():
        app.quit()
    game = Game()
    menu = StartMenu(start_game, load_game, exit_game)
    menu.show()
    sys.exit(app.exec_())

