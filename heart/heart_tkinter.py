import tkinter as tk
import math
import random
import time

class HeartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heart Landing")
        self.root.configure(bg='#050505')
        # Полноэкранный режим (нажмите Escape для выхода)
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.quit())

        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()

        self.state = 'console'  # 'console' or 'reveal'
        self.console_complete = False
        self.show_button = False

        # Холст для рисования
        self.canvas = tk.Canvas(root, width=self.width, height=self.height,
                                bg='#050505', highlightthickness=0)
        self.canvas.pack()

        # Шрифты (используем доступные)
        self.console_font = ('Courier', 14)
        self.button_font = ('Courier', 11, 'bold')
        self.text_font = ('Courier', 10)

        # Консольные строки
        self.console_lines = [
            "[system] Initializing heart.PROTOCOL_v2.0...",
            "[status] "
        ]
        self.typewriter_index = 0
        self.typewriter_pos = 0
        self.typewriter_text = ""
        self.status_ready = False

        # Элементы интерфейса (будем создавать динамически)
        self.button_rect = None
        self.button_text = None

        # Параметры сердца
        self.particles = []          # каждый элемент: (x, y, alpha, target_alpha, delay, text)
        self.start_time = None       # для задержки появления Decrypted
        self.heart_visible = False

        # Звёзды (для фона)
        self.stars = []
        for _ in range(150):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            brightness = random.randint(50, 200)
            self.stars.append((x, y, brightness))

        # Запуск консольного режима
        self.draw_console()
        self.update_console()

    def draw_console(self):
        self.canvas.delete("all")
        # Фон
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill='#050505', outline='')
        # Звёзды (для атмосферы)
        for x, y, b in self.stars:
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill=f'#{b:02x}{b:02x}{b:02x}', outline='')

        x0 = self.width // 6
        y0 = self.height // 3
        line_height = 22

        # Печатаем уже завершённые строки
        for i, line in enumerate(self.console_lines):
            if i < self.typewriter_index:
                self.canvas.create_text(x0, y0 + i*line_height, anchor='nw',
                                        text=line, fill='#cccccc', font=self.console_font)
        # Текущая печатаемая строка
        if self.typewriter_index < len(self.console_lines):
            partial = self.typewriter_text
            if self.typewriter_index == 1 and self.status_ready:
                # Строка [status] READY – добавим READY в конец
                partial = partial + "READY" if "READY" not in partial else partial
            self.canvas.create_text(x0, y0 + self.typewriter_index*line_height, anchor='nw',
                                    text=partial, fill='#cccccc', font=self.console_font)

        # Дополнительный текст и кнопка, когда консоль готова
        if self.console_complete and self.show_button:
            # > One encrypted package found for you.
            info_y = y0 + 2*line_height + 20
            self.canvas.create_text(x0, info_y, anchor='nw',
                                    text="> One encrypted package found for you.",
                                    fill='#666666', font=self.console_font)

            # Кнопка
            btn_text = "Decrypt Message"
            btn_w = len(btn_text) * 8
            btn_h = 20
            btn_x = x0
            btn_y = info_y + 30
            # Рисуем рамку и текст
            self.button_rect = self.canvas.create_rectangle(btn_x-10, btn_y-5,
                                                            btn_x+btn_w+10, btn_y+btn_h+5,
                                                            outline='#ff4d6d', width=1)
            self.button_text = self.canvas.create_text(btn_x + btn_w//2, btn_y + btn_h//2,
                                                       text=btn_text, fill='#ff8fb1',
                                                       font=self.button_font)
            # Привязываем клик
            self.canvas.tag_bind(self.button_rect, '<Button-1>', self.start_reveal)
            self.canvas.tag_bind(self.button_text, '<Button-1>', self.start_reveal)

            # Подсказка
            self.canvas.create_text(x0, btn_y + btn_h + 15, anchor='nw',
                                    text="(or click anywhere)", fill='#333333', font=self.console_font)

    def update_console(self):
        if self.state != 'console':
            return

        if not self.console_complete:
            # Обновление печати
            if self.typewriter_index < len(self.console_lines):
                target_line = self.console_lines[self.typewriter_index]
                if self.typewriter_pos < len(target_line):
                    self.typewriter_text += target_line[self.typewriter_pos]
                    self.typewriter_pos += 1
                    self.root.after(35, self.update_console)
                    self.draw_console()
                    return
                else:
                    # Строка закончена
                    self.typewriter_index += 1
                    self.typewriter_text = ""
                    self.typewriter_pos = 0
                    if self.typewriter_index == 2:  # после [status] 
                        self.status_ready = True
                        self.console_complete = True
                        self.show_button = True
                        self.draw_console()
                        self.root.after(100, self.update_console)  # небольшая пауза
                        return
                    else:
                        self.root.after(50, self.update_console)
                        self.draw_console()
                        return
            else:
                self.console_complete = True
                self.show_button = True
                self.draw_console()
                self.root.after(100, self.update_console)
                return
        else:
            # Ждём нажатия кнопки или клика
            self.root.after(100, self.update_console)
            return

    def start_reveal(self, event=None):
        if self.state != 'console':
            return
        self.state = 'reveal'
        self.heart_visible = True
        self.start_time = time.time()
        self.generate_heart_particles()
        self.draw_reveal()
        self.animate_heart()

    def generate_heart_particles(self):
        self.particles = []
        center_x = self.width // 2
        center_y = self.height // 2
        scale = min(self.width, self.height) / 45

        # Формула сердца: x = 16*sin^3(t), y = -(13cos(t)-5cos(2t)-2cos(3t)-cos(4t))
        # Внешний контур
        for deg in range(0, 360, 6):
            rad = math.radians(deg)
            x = 16 * (math.sin(rad) ** 3)
            y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
            px = center_x + x * scale
            py = center_y + y * scale
            delay = random.uniform(0, 2000)
            alpha = 0
            target = random.uniform(0.6, 0.95)
            self.particles.append([px, py, alpha, target, delay, "i love you"])

        # Внутренние слои
        for s in [0.7, 0.4]:
            for deg in range(0, 360, 10):
                rad = math.radians(deg)
                x = 16 * (math.sin(rad) ** 3)
                y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
                px = center_x + x * scale * s
                py = center_y + y * scale * s
                delay = random.uniform(800, 3500)
                alpha = 0
                target = random.uniform(0.4, 0.7)
                self.particles.append([px, py, alpha, target, delay, "i love you"])

    def draw_reveal(self):
        self.canvas.delete("all")
        # Звёзды
        for x, y, b in self.stars:
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill=f'#{b:02x}{b:02x}{b:02x}', outline='')

        # Рисуем частицы сердца
        for (x, y, alpha, target, delay, text) in self.particles:
            if alpha > 0:
                # Уровень прозрачности имитируем через цвет
                intensity = int(alpha * 200) + 55  # от 55 до 255
                color = f'#{intensity:02x}{50:02x}{80:02x}'  # оттенки красного
                self.canvas.create_text(x, y, text=text, fill=color,
                                        font=self.text_font, anchor='center')

        # Текст "Decrypted" появляется через 3 секунды
        if self.start_time and (time.time() - self.start_time) > 3.0:
            cx = self.width // 2
            cy = self.height // 2 + int(min(self.width, self.height) / 45 * 12)
            self.canvas.create_text(cx, cy, text="Decrypted", fill='#ff4d6d',
                                    font=('Courier', 18, 'bold'), anchor='center')
            # линия
            self.canvas.create_line(cx-60, cy+20, cx+60, cy+20, fill='#ff4d6d', width=1)
            # кнопка Re-encrypt
            self.canvas.create_text(cx, cy+50, text="Re-encrypt", fill='#555555',
                                    font=self.button_font, anchor='center')
            # Привязываем клик на re-encrypt
            self.canvas.tag_bind('re', '<Button-1>', self.re_encrypt)

        # Технические уголки
        self.canvas.create_text(20, self.height-30, anchor='nw',
                                text="ln: 420 | id: 0xDEADBEEF | type: organic_emotion",
                                fill='#222222', font=self.console_font)
        self.canvas.create_text(self.width-250, 20, anchor='nw',
                                text="heart_reveal // success",
                                fill='#222222', font=self.console_font)

    def animate_heart(self):
        if self.state != 'reveal':
            return
        # Обновляем alpha частиц
        now_ms = time.time() * 1000  # миллисекунды
        for p in self.particles:
            delay = p[4]
            if now_ms > delay:
                alpha = p[2] + (p[3] - p[2]) * 0.05
                if alpha > p[3]:
                    alpha = p[3]
                p[2] = alpha
        self.draw_reveal()
        self.root.after(50, self.animate_heart)

    def re_encrypt(self, event=None):
        # Возврат в консольный режим
        self.state = 'console'
        self.console_complete = False
        self.show_button = False
        self.typewriter_index = 0
        self.typewriter_pos = 0
        self.typewriter_text = ""
        self.status_ready = False
        self.button_rect = None
        self.button_text = None
        self.particles = []
        self.heart_visible = False
        self.draw_console()
        self.update_console()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartApp(root)
    app.run()