#
# 回避し続けるゲーム
#

# モジュールのインポート
import tkinter as tk
import random
import math
import time
from PIL import Image, ImageTk

# 定数の設定
WINDOW_HEIGHT = 400 # ウィンドウの高さ
WINDOW_WIDTH = 400 # ウィンドウの幅

PLAYER_SIZE = 10 # 操作する球体の大きさ
ENEMY_SIZE = 5 # 敵の球体の大きさ


COLLISION_DETECTION = 300  # 当たり判定(厳密にはこれの平方根)

START_MOVE = 3 # 敵が動くまでの時間
CLEAR_TIME = 10 # クリアまでの時間

ATTACK_SPEED2 = 20 # 攻撃の速さ(何msごとに描画を更新するか) (この速度は定数)

#ゲームの状態 プレイ中だとTrueになる
game_state = False

#
# 最初の画面（難易度選択画面）
class Select_Display(tk.Frame):
    def __init__(self, master = None, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=None):
        super().__init__(master, width=width, height=height, bg=bg)

        #ウィジェットの作成
        self.dp = tk.Label(self, text = '難易度選択',font=('Helvetica', 40), bg="blue", fg="white")
        self.advan = tk.Button(self, text="上級", width = 15, command=self.advanced, font=('Helvetica', 20), bg="white")
        self.interm = tk.Button(self, text="中級", width = 15, command=self.intermediate, font=('Helvetica', 20), bg="white")
        self.begin = tk.Button(self, text="初級", width = 15, command=self.beginner, font=('Helvetica', 20), bg="white")

        self.pack_propagate(False) # サイズや位置の設定が他に依存しなくなる

        self.dp.pack(fill=tk.X) # 横方向いっぱいに広がる
        self.advan.pack(expand=True)  # 余った領域を全て使う。
        self.interm.pack(expand=True) # この三つで残りの領域を独占するから
        self.begin.pack(expand=True)  # サイズによらず均等に配置される。

    #上級を押したとき
    def advanced(self):
        global NUMBER_OF_ENEMY # 一辺あたりの攻撃の数
        global ATTACK_SPEED1 # 攻撃の速さ(一度の描画で進む距離)
        NUMBER_OF_ENEMY = 4
        ATTACK_SPEED1 = 6
        play()
        background_label.destroy() # 最初の画面を消す

    #中級を押したとき
    def intermediate(self):
        global NUMBER_OF_ENEMY
        global ATTACK_SPEED1
        global ATTACK_SPEED2 
        NUMBER_OF_ENEMY = 3
        ATTACK_SPEED1 = 5
        play()
        background_label.destroy()

    #初級を押したとき
    def beginner(self):
        global NUMBER_OF_ENEMY
        global ATTACK_SPEED1
        global ATTACK_SPEED2
        NUMBER_OF_ENEMY = 2
        ATTACK_SPEED1 = 3
        play()
        background_label.destroy()

#
# 操作する球体
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.draw()
        self.bind()

    def draw(self):
        play_canvas.create_oval(self.x-PLAYER_SIZE, self.y-PLAYER_SIZE,
                       self.x+PLAYER_SIZE, self.y+PLAYER_SIZE,
                       fil="yellow", tag="player")
    
    def bind(self):
        play_canvas.tag_bind("player", "<Button1-Motion>", self.dragged)
        
    def dragged(self, event):
        if event.x>=0 and event.x<=WINDOW_WIDTH and event.y>=0 and event.y<=WINDOW_HEIGHT: # 画面外では動かない
            dx = event.x - self.x
            dy = event.y - self.y
            x1, y1, x2, y2 = play_canvas.coords("player") # 今の座標を取得
            self.x = (x1 + x2) / 2  # 楕円の中心の x 座標
            self.y = (y1 + y2) / 2  # 楕円の中心の y 座標

            play_canvas.coords("player", x1+dx, y1+dy, x2+dx, y2+dy) # 座標の更新
            self.x = event.x
            self.y = event.y
#
# 敵の球体
class Enemy:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2*math.pi)
        self.trans_x = ATTACK_SPEED1 * math.cos(self.angle)
        self.trans_y = ATTACK_SPEED1 * math.sin(self.angle)
        self.draw()
        root.after(START_MOVE*1000, self.move)

    def draw(self):
        self.enemy = play_canvas.create_oval(self.x-ENEMY_SIZE, self.y-ENEMY_SIZE,
                       self.x+ENEMY_SIZE, self.y+ENEMY_SIZE,
                       fil="red", tag="enemy")

    def move(self):
        if game_state: # プレイ中のみ作動
            if self.x < 0 or self.x > WINDOW_WIDTH: # 画面端で反射
                self.angle = math.pi - self.angle
                self.trans_x = ATTACK_SPEED1 * math.cos(self.angle)
                self.trans_y = ATTACK_SPEED1 * math.sin(self.angle)
            if self.y < 0 or self.y > WINDOW_HEIGHT:
                self.angle = 2*math.pi - self.angle
                self.trans_x = ATTACK_SPEED1 * math.cos(self.angle)
                self.trans_y = ATTACK_SPEED1 * math.sin(self.angle)
                    
            self.x += self.trans_x
            self.y += self.trans_y
            self.collision()
            play_canvas.move(self.enemy, self.trans_x, self.trans_y)
            root.after(ATTACK_SPEED2, self.move) # 一定時間ごとにこの関数を繰り返す

    # 敵と衝突した時
    def collision(self):
        global game_state
        if game_state:
            if ((self.x-player.x)**2+(self.y-player.y)**2) < COLLISION_DETECTION:
                gameover()

                game_state = False
                
# ゲーム開始時間
def start_timer():
    global start_time
    start_time = time.time() + START_MOVE #動き出すまでの時間を加算

# ゲームクリアしたかの確認。クリアタイムになったらゲームクリアにする
def check_time_elapsed():
    if game_state:
        elapsed_time = time.time() - start_time  # 現在の時間と開始時間の差を計算
        if elapsed_time >= CLEAR_TIME:  # 一定時間が経過したら
            gameclear()
        else:
            root.after(100, check_time_elapsed)
            
# ゲームオーバー時の描画        
def gameover():
    play_canvas.delete("player", "enemy")
    play_canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text="GAME OVER",
                   fill="red", font=("Helvetica", 40))
    # リスタートボタンの追加（最初の画面では必要ないからここで追加）
    menubar.add_command(label="RESTART", underline=0, command=restart)

# ゲームクリア時の描画 
def gameclear():
    global game_state
    if game_state:
        game_state = False
        play_canvas.delete("player", "enemy")
        play_canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text="GAME CLEAR",
                       fill="lightgreen", font=("Helvetica", 40))
        # リスタートボタンの追加（最初の画面では必要ないからここで追加）
        menubar.add_command(label="RESTART", underline=0, command=restart)
        
# 初期設定
def init():
    global select_frame
    global background_label
    global menubar
    background_label = tk.Label(root, image=background)
    background_label.pack()
    select_frame = Select_Display(background_label, WINDOW_WIDTH, WINDOW_HEIGHT, "")
    select_frame.pack(padx=0, pady=0)
    
    # メニューバー
    menubar = tk.Menu(root)
    root.configure(menu=menubar)
    menubar.add_command(label="QUIT", underline=0, command=root.quit)

# リスタートする
def restart():
    global start_time
    game_state = False
    start_time = None
    play_canvas.destroy()
    menubar.delete(1)
    init()

# ゲーム画面を作りゲームを始める
def play():
    global play_canvas
    global player
    global game_state
    
    game_state = True # プレイ中の状態にする
    play_canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
    play_canvas.pack()
    # キャンバスに背景画像を表示
    play_canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=background)

    # 操作する球体の配置
    player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

    # 敵の球体の配置(一辺に一定数、場所はランダムに)
    for i in range(NUMBER_OF_ENEMY):
        enemy = Enemy(random.uniform(0, WINDOW_WIDTH), 0) 
    for i in range(NUMBER_OF_ENEMY):
        enemy = Enemy(random.uniform(0, WINDOW_WIDTH), WINDOW_HEIGHT)
    for i in range(NUMBER_OF_ENEMY):
        enemy = Enemy(0, random.uniform(0, WINDOW_HEIGHT))
    for i in range(NUMBER_OF_ENEMY):
        enemy = Enemy(WINDOW_WIDTH, random.uniform(0, WINDOW_HEIGHT))

    # 簡単なルール説明
    rule_text1 = play_canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//5, text="１０秒間避け続けろ！",
                       fill="white", font=("Helvetica", 30))
    rule_text2 = play_canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//3, text="※３秒後に始まります",
                       fill="white", font=("Helvetica", 20))
    # ゲームが始まったら説明の文字を消す
    root.after(START_MOVE*1000, lambda:play_canvas.delete(rule_text1))
    root.after(START_MOVE*1000, lambda:play_canvas.delete(rule_text2))
    # ゲーム開始時間を測定
    start_timer()
    
    # クリアチェック機能を作動
    check_time_elapsed()


if __name__ == "__main__":
    # 初期描画
    root = tk.Tk()
    root.geometry("400x400")
    root.title("Cosmic Dodge")
    # ウィンドウのサイズを固定する（最大化を無効にする）
    root.resizable(False, False)


    # 画像の読み込み
    image = Image.open("assets/images/bg.png")
    image = image.resize((WINDOW_WIDTH, WINDOW_HEIGHT))

    # PillowのImageオブジェクトからTkinterのPhotoImageオブジェクトに変換
    background = ImageTk.PhotoImage(image)

    init()
    root.mainloop()
