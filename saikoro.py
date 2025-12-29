import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import pygame
from PIL import Image, ImageTk
import os

class DiceGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎲 サイコロゲーム")
        self.stage = 0
        self.num_players = 0
        self.positions = []
        self.quest_map = {}
        self.current_player = 0
        self.turn = 1

        # pygame 初期化（音用）
        pygame.init()
        pygame.mixer.init()

        self.dice_images = []
        for i in range(1, 7):
            img_path = os.path.join("dice_images", f"dice{i}.png")
            img = Image.open(img_path).resize((60, 60))
            self.dice_images.append(ImageTk.PhotoImage(img))

        self.quest_img = ImageTk.PhotoImage(Image.open("image/quest.png").resize((100, 100)))

        self.setup_screen()

    def setup_screen(self):
        self.clear_window()
        tk.Label(self.root, text="🎮 サイコロゲーム設定", font=("Helvetica", 16)).pack(pady=10)

        self.stage_entry = self.create_labeled_entry("🗺️ ステージのマス数:")
        self.players_entry = self.create_labeled_entry("👥 プレイヤーの人数:")

        tk.Button(self.root, text="次へ", command=self.configure_quests).pack(pady=10)

    def configure_quests(self):
        try:
            self.stage = int(self.stage_entry.get())
            self.num_players = int(self.players_entry.get())
            if self.stage <= 0 or self.num_players <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "正しい数値を入力してください。")
            return

        self.positions = [0] * self.num_players
        self.quest_map = {}

        answer = messagebox.askquestion("クエスト設定", "クエストをランダムに設定しますか？")
        if answer == 'yes':
            sample_quests = [
                "腕立て伏せを5回する",
                "罰金",
                "一気飲み",
                "隣の質問に正直に答える",
            ]
            available_positions = list(range(1, self.stage))
            random.shuffle(available_positions)
            for i in range(min(5, len(available_positions))):
                pos = available_positions[i]
                self.quest_map[pos] = random.choice(sample_quests)
        else:
            while True:
                pos = simpledialog.askstring("クエスト", "クエストマス番号を入力（空欄で終了）:")
                if not pos:
                    break
                if pos.isdigit() and 1 <= int(pos) < self.stage:
                    text = simpledialog.askstring("クエスト内容", f"{pos}マス目のクエスト内容:")
                    self.quest_map[int(pos)] = text

        self.start_game()

    def start_game(self):
        self.clear_window()
        self.info_label = tk.Label(self.root, text="🎲 ゲームスタート！", font=("Helvetica", 14))
        self.info_label.pack(pady=10)

        self.status = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.status.pack(pady=10)

        self.dice_label = tk.Label(self.root)
        self.dice_label.pack(pady=10)

        self.quest_image_label = tk.Label(self.root)
        self.quest_image_label.pack()

        self.roll_button = tk.Button(self.root, text="🎯 サイコロを振る", command=self.roll_dice)
        self.roll_button.pack(pady=20)

    def roll_dice(self):
        # サイコロアニメーション
        self.animate_dice()

        # 最終の出目決定
        dice = random.randint(1, 6)
        self.root.after(600, lambda: self.process_turn(dice))

    def animate_dice(self, count=0):
        if count >= 6:
            return
        img = random.choice(self.dice_images)
        self.dice_label.config(image=img)
        self.root.after(100, lambda: self.animate_dice(count + 1))

    def process_turn(self, dice):
        player = self.current_player
        self.positions[player] += dice
            # 正しい画像に更新
        self.dice_label.config(image=self.dice_images[dice - 1])

        log = f"プレイヤー{player+1}の出目は {dice} → 現在位置: {self.positions[player]}\n"

        if self.positions[player] == self.stage:
            messagebox.showinfo("勝利！", f"🏆 プレイヤー{player+1}がゴールしました！")
            self.reset_game()
            return
        elif self.positions[player] > self.stage:
            self.positions[player] -= self.stage
            log += f"ゴールを超えたため振り出しに戻って {self.positions[player]} マス目へ\n"

        if self.positions[player] in self.quest_map:
            quest_text = self.quest_map[self.positions[player]]
            log += f"🧙 クエスト発生！: {quest_text}\n"
            self.trigger_quest_effect()

        self.status.config(text=log)
        self.current_player = (self.current_player + 1) % self.num_players
        self.turn += 1

    def trigger_quest_effect(self):
        # 音を再生
        try:
            pygame.mixer.music.load("music/quest_sound.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print("音声エラー:", e)

        # クエスト画像を一時的に表示
        self.quest_image_label.config(image=self.quest_img)
        self.root.after(2000, lambda: self.quest_image_label.config(image=''))

    def reset_game(self):
        choice = messagebox.askquestion("もう一度？", "同じ設定でもう一度プレイしますか？")
        if choice == 'yes':
            self.positions = [0] * self.num_players
            self.current_player = 0
            self.turn = 1
            self.start_game()
        else:
            self.setup_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_labeled_entry(self, label):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        tk.Label(frame, text=label).pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left")
        return entry


if __name__ == "__main__":
    root = tk.Tk()
    app = DiceGameApp(root)
    root.mainloop()
