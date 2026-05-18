import pygame
import sys
import math
import random

# Инициализация
pygame.init()
pygame.display.set_caption("Heart Landing")
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Цвета
BLACK = (5, 5, 5)
WHITE = (255, 255, 255)
PINK_DARK = (255, 77, 109)
PINK_LIGHT = (255, 143, 177)
GREEN = (100, 255, 100)

# Шрифты
try:
    font_console = pygame.font.SysFont("fira code", 18, bold=False)
    font_button = pygame.font.SysFont("fira code", 14, bold=False)
    font_text = pygame.font.SysFont("fira code", 12, bold=False)
except:
    font_console = pygame.font.SysFont("monospace", 18)
    font_button = pygame.font.SysFont("monospace", 14)
    font_text = pygame.font.SysFont("monospace", 12)

# Состояния
STATE_CONSOLE = 0
STATE_REVEAL = 1

# ========== Частицы для сердца ==========
class HeartParticle:
    def __init__(self, x, y, delay):
        self.x = x
        self.y = y
        self.alpha = 0.0
        self.target_alpha = random.uniform(0.5, 0.9)
        self.delay = delay
        self.text = "i love you"

    def update(self, elapsed_time):
        if elapsed_time > self.delay:
            self.alpha += (self.target_alpha - self.alpha) * 0.05

    def draw(self, surface):
        if self.alpha <= 0:
            return
        color = (*PINK_DARK, int(self.alpha * 255))
        # Рендерим текст с прозрачностью
        text_surf = font_text.render(self.text, True, PINK_DARK)
        text_surf.set_alpha(int(self.alpha * 255))
        w, h = text_surf.get_size()
        surface.blit(text_surf, (self.x - w//2, self.y - h//2))

# Генерация точек сердца по формуле
def generate_heart_particles(center_x, center_y, scale):
    particles = []
    # Внешний контур
    for t in range(0, 360, 6):
        rad = math.radians(t)
        x = 16 * (math.sin(rad) ** 3)
        y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
        px = center_x + x * scale
        py = center_y + y * scale
        particles.append(HeartParticle(px, py, random.uniform(0, 2000)))
    # Внутренние слои
    for s in [0.7, 0.4]:
        for t in range(0, 360, 12):
            rad = math.radians(t)
            x = 16 * (math.sin(rad) ** 3)
            y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
            px = center_x + x * scale * s
            py = center_y + y * scale * s
            particles.append(HeartParticle(px, py, random.uniform(800, 3500)))
    return particles

# ========== Эффект печатающегося текста ==========
class Typewriter:
    def __init__(self, text, delay=30):
        self.full_text = text
        self.delay = delay
        self.current_text = ""
        self.index = 0
        self.last_update = pygame.time.get_ticks()
        self.complete = False

    def update(self):
        if self.complete:
            return
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.delay:
            self.last_update = now
            if self.index < len(self.full_text):
                self.current_text += self.full_text[self.index]
                self.index += 1
            else:
                self.complete = True

    def draw(self, surface, x, y, color=WHITE):
        rendered = font_console.render(self.current_text, True, color)
        surface.blit(rendered, (x, y))

# ========== Основной класс приложения ==========
class HeartApp:
    def __init__(self):
        self.state = STATE_CONSOLE
        self.console_complete = False

        # Консольный текст
        self.console_lines = [
            "[system] Initializing heart.PROTOCOL_v2.0...",
            "[status] ",
        ]
        self.typewriters = []
        for line in self.console_lines:
            self.typewriters.append(Typewriter(line, 30))
        self.current_line = 0
        self.status_ready = False
        self.show_button = False
        self.button_rect = None

        # Сердце
        self.particles = []
        self.elapsed_reveal = 0
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.scale = min(WIDTH, HEIGHT) / 45
        self.heart_visible = False

        # Фон (звёзды)
        self.stars = []
        for _ in range(200):
            self.stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.2, 1.0)])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state == STATE_CONSOLE and self.show_button:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_reveal()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == STATE_CONSOLE and self.show_button:
                    if self.button_rect and self.button_rect.collidepoint(event.pos):
                        self.start_reveal()
        return True

    def start_reveal(self):
        self.state = STATE_REVEAL
        self.heart_visible = True
        self.particles = generate_heart_particles(self.center_x, self.center_y, self.scale)
        self.elapsed_reveal = 0

    def update_console(self):
        # Обновляем печать строк
        if self.current_line < len(self.typewriters):
            tw = self.typewriters[self.current_line]
            tw.update()
            if tw.complete:
                self.current_line += 1
        # После завершения всех строк
        if not self.console_complete and self.current_line >= len(self.typewriters):
            self.console_complete = True
            # Добавляем сообщение о готовности
            self.status_ready = True
            self.show_button = True

    def draw_console(self):
        screen.fill(BLACK)
        x = 50
        y = HEIGHT // 3
        line_height = font_console.get_linesize() + 6
        for i, tw in enumerate(self.typewriters):
            tw.draw(screen, x, y + i * line_height, (200, 200, 200))
        # Строка [status] READY
        if self.status_ready:
            ready_text = font_console.render("READY", True, GREEN)
            # Рисуем строку status на той же позиции, что и второй typewriter
            status_x = x + font_console.size("[status] ")[0]
            status_y = y + line_height
            screen.blit(ready_text, (status_x, status_y))

        # Дополнительный текст
        if self.show_button:
            # Текст "One encrypted package found for you."
            info_text = font_console.render("> One encrypted package found for you.", True, (100, 100, 100))
            info_rect = info_text.get_rect(topleft=(x, y + 2 * line_height + 20))
            screen.blit(info_text, info_rect)

            # Кнопка
            btn_text = font_button.render("Decrypt Message", True, PINK_LIGHT)
            btn_w, btn_h = btn_text.get_size()
            btn_x = x + 10
            btn_y = info_rect.bottom + 30
            self.button_rect = pygame.Rect(btn_x - 20, btn_y - 10, btn_w + 40, btn_h + 20)
            pygame.draw.rect(screen, PINK_DARK, self.button_rect, 1, border_radius=4)
            screen.blit(btn_text, (btn_x, btn_y))

            # Подпись
            hint_text = font_console.render("(or click anywhere)", True, (50, 50, 50))
            screen.blit(hint_text, (x, btn_y + btn_h + 15))

    def draw_reveal(self):
        screen.fill(BLACK)
        # Звёзды
        for sx, sy, bright in self.stars:
            pygame.draw.circle(screen, (255, 255, 255, int(bright * 100)), (sx, sy), 1)

        # Частицы сердца
        now = pygame.time.get_ticks()
        # Для анимации используем общее время с начала раскрытия
        for p in self.particles:
            p.update(now)
            p.draw(screen)

        # Текст "Decrypted" с задержкой
        if self.elapsed_reveal > 3000:
            decrypted_text = font_console.render("Decrypted", True, PINK_DARK)
            tw, th = decrypted_text.get_size()
            screen.blit(decrypted_text, (self.center_x - tw//2, self.center_y + self.scale * 10))
            # Линия
            pygame.draw.line(screen, PINK_DARK, (self.center_x - 50, self.center_y + self.scale * 10 + 25),
                             (self.center_x + 50, self.center_y + self.scale * 10 + 25), 1)
            # Кнопка "Re-encrypt"
            re_text = font_button.render("Re-encrypt", True, (80, 80, 80))
            re_rect = re_text.get_rect(center=(self.center_x, self.center_y + self.scale * 12))
            screen.blit(re_text, re_rect)

        # Технические надписи по углам
        corner_text = font_console.render("ln: 420 | id: 0xDEADBEEF | type: organic_emotion", True, (30, 30, 30))
        screen.blit(corner_text, (20, HEIGHT - 30))
        corner_text2 = font_console.render("heart_reveal // success", True, (30, 30, 30))
        screen.blit(corner_text2, (WIDTH - 250, 20))

    def run(self):
        running = True
        start_time = pygame.time.get_ticks()
        while running:
            running = self.handle_events()
            if self.state == STATE_CONSOLE:
                self.update_console()
                self.draw_console()
                # Клик мыши в любом месте (для удобства)
                if self.show_button and pygame.mouse.get_pressed()[0]:
                    # Небольшая задержка, чтобы не сработало при нажатии на кнопку дважды
                    pygame.time.wait(100)
                    self.start_reveal()
            else:
                self.elapsed_reveal = pygame.time.get_ticks() - start_time
                self.draw_reveal()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = HeartApp()
    app.run()