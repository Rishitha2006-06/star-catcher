import pygame
import random
import math
import os
import sys

pygame.init()
pygame.mixer.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Collector")

# Colors
TEXT_COLOR = (200, 220, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
HOVER_BLUE = (100, 200, 255)

# Assets (set these to your files)
ASSET_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECT_SOUND_FILE = "catch.mp3"
COLLISION_SOUND_FILE = "miss.mp3"
BACKGROUND_MUSIC_FILE = "background.mp3"

# Try safe-loading sounds
try:
    collect_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLECT_SOUND_FILE))
except Exception:
    collect_sound = None
try:
    collision_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLISION_SOUND_FILE))
except Exception:
    collision_sound = None
try:
    pygame.mixer.music.load(os.path.join(ASSET_PATH, BACKGROUND_MUSIC_FILE))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception:
    pass

# Levels
levels = [
    {"name": "Pink City", "background_color": (255, 182, 193), "stars_needed": 10, "obstacles": 15, "blackholes": 2},
    {"name": "Blue Space", "background_color": (30, 144, 255), "stars_needed": 12, "obstacles": 18, "blackholes": 3},
    {"name": "Ocean Block", "background_color": (0, 105, 148), "stars_needed": 15, "obstacles": 22, "blackholes": 4}
]

# Riddles
riddles = [
    {"question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"},
    {"question": "I’m tall when I’m young, and short when I’m old. What am I?", "answer": "candle"},
    {"question": "What has keys but can’t open locks?", "answer": "piano"},
    {"question": "The more of me you take, the more you leave behind. What am I?", "answer": "footsteps"},
    {"question": "I have cities but no houses, forests but no trees, and water but no fish. What am I?", "answer": "map"},
    {"question": "What can run but never walks, has a mouth but never talks?", "answer": "river"},
    {"question": "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?", "answer": "fire"},
    {"question": "I can fly without wings, cry without eyes. What am I?", "answer": "cloud"},
    {"question": "The more you take away from me, the bigger I get. What am I?", "answer": "hole"},
    {"question": "What has many teeth, but cannot bite?", "answer": "comb"},
    {"question": "What goes up but never comes down?", "answer": "age"},
    {"question": "What has a neck but no head?", "answer": "bottle"},
    {"question": "What can travel around the world while staying in a corner?", "answer": "stamp"},
    {"question": "What has hands but cannot clap?", "answer": "clock"},
    {"question": "I’m light as a feather, yet the strongest man cannot hold me for long. What am I?", "answer": "breath"},
    {"question": "What begins with T, ends with T, and has T in it?", "answer": "teapot"},
    {"question": "What comes once in a minute, twice in a moment, but never in a thousand years?", "answer": "m"}
]


# Helper function to draw wrapped text
def draw_wrapped_text(surface, text, color, x, y, font, max_width, line_spacing=5):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)
    for i, line in enumerate(lines):
        surface.blit(font.render(line, True, color), (x, y + i * (font.get_height() + line_spacing)))

# UFO / Player
class UFO:
    def __init__(self):
        self.x = 0
        self.y = HEIGHT // 2
        self.radius = 25
        self.speed = 5
        self.crashes = 0

    def draw(self, surface):
        pygame.draw.ellipse(surface, (0, 200, 200), (self.x - 30, self.y - 15, 60, 30))
        pygame.draw.ellipse(surface, (180, 250, 250), (self.x - 15, self.y - 25, 30, 20))

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

# Obstacles
class Obstacle:
    def __init__(self, kind="rock"):
        self.kind = kind
        self.size = random.randint(30, 50) if kind == "rock" else random.randint(40, 60)
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(-HEIGHT, -self.size)
        if kind == "rock":
            self.dx = random.uniform(-1.5, 1.5)
            self.dy = random.uniform(-1.5, 1.5)
        else:
            self.dx = 0
            self.dy = random.uniform(1, 3)
        self.already_hit = False
        self.angle = random.uniform(0, 360)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.kind == "rock":
            if self.x < 0 or self.x > WIDTH - self.size:
                self.dx *= -1
            if self.y < 0 or self.y > HEIGHT - self.size:
                self.dy *= -1
        else:
            if self.y > HEIGHT:
                self.y = -self.size
                self.x = random.randint(0, WIDTH - self.size)
            self.angle += 5

    def draw(self, surface):
        if self.kind == "rock":
            pygame.draw.circle(surface, GRAY, (int(self.x + self.size/2), int(self.y + self.size/2)), self.size//2)
        else:
            center = (int(self.x + self.size/2), int(self.y + self.size/2))
            pygame.draw.circle(surface, BLACK, center, self.size//2)
            end_x = center[0] + int(math.cos(math.radians(self.angle)) * self.size//2)
            end_y = center[1] + int(math.sin(math.radians(self.angle)) * self.size//2)
            pygame.draw.line(surface, RED, center, (end_x, end_y), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

# Star collectible
class Star:
    def __init__(self, player=None):
        while True:
            self.x = random.randint(50, WIDTH-50)
            self.y = random.randint(50, HEIGHT-50)
            if not player or math.hypot(self.x - player.x, self.y - player.y) > 50:
                break
        self.size = 20

    def draw(self, surface):
        points = []
        for i in range(5):
            angle = i * 72 - 90
            x = self.x + self.size * math.cos(math.radians(angle))
            y = self.y + self.size * math.sin(math.radians(angle))
            points.append((x, y))
            angle += 36
            x = self.x + self.size//2 * math.cos(math.radians(angle))
            y = self.y + self.size//2 * math.sin(math.radians(angle))
            points.append((x, y))
        pygame.draw.polygon(surface, YELLOW, points)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size*2, self.size*2)

# Game
class Game:
    def __init__(self):
        self.level_index = 0
        self.player = UFO()
        self.obstacles = []
        self.stars = []
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.awaiting_riddle = False
        self.riddle_answer = ""
        self.current_riddle = None
        self.show_hint = False
        self.hint_shown = False
        self.show_level_intro = True
        self.font = pygame.font.SysFont(None, 36)
        self.medium_font = pygame.font.SysFont(None, 48)
        self.large_font = pygame.font.SysFont(None, 72)
        self.background_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
        self.remaining_riddles = riddles.copy()
        self.level_scores = []
        self.wrong_attempts = 0

        # Game states
        self.show_scoreboard = False
        self.show_win = False
        self.win_timer = 0

        # Buttons
        self.try_again_rect = pygame.Rect(WIDTH//2-120, HEIGHT//2+50, 100, 50)
        self.restart_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2+50, 100, 50)

        self.final_ufo_x = -150
        self.final_trail = []

        self.reset_level()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.awaiting_riddle:
                    if event.key == pygame.K_RETURN:
                        self.check_riddle_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        self.riddle_answer = self.riddle_answer[:-1]
                    else:
                        if len(event.unicode) == 1:
                            self.riddle_answer += event.unicode
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.awaiting_riddle and self.current_riddle:
                    if self.show_hint and self.hint_rect.collidepoint(mouse_pos):
                        self.hint_shown = True
                        self.show_hint = False
                if self.game_over:
                    if self.try_again_rect.collidepoint(mouse_pos):
                        self.score = 0
                        self.player.crashes = 0
                        self.reset_level(preserve_level_index=True)
                        self.game_over = False
                    if self.restart_rect.collidepoint(mouse_pos):
                        self.__init__()
                if self.show_win:
                    if self.restart_rect.collidepoint(mouse_pos):
                        self.__init__()

        return True

    def check_riddle_answer(self):
        if self.current_riddle is None:
            return
        answer = self.current_riddle["answer"].strip().lower()
        given = self.riddle_answer.strip().lower()
        if given == answer:
            self.level_scores.append(self.score)
            self.score = 0
            self.riddle_answer = ""
            self.wrong_attempts = 0
            self.hint_shown = False
            self.show_hint = False
            try:
                self.remaining_riddles.remove(self.current_riddle)
            except ValueError:
                pass
            if not self.remaining_riddles:
                self.remaining_riddles = riddles.copy()
            self.current_riddle = None
            self.awaiting_riddle = False
            self.level_index += 1
            if self.level_index >= len(levels):
                self.show_scoreboard = True
            else:
                self.reset_level()
        else:
            self.wrong_attempts += 1
            self.riddle_answer = ""
            self.player.crashes += 1
            if collision_sound:
                collision_sound.play()
            if self.player.crashes >= 5:
                self.game_over = True
            if self.wrong_attempts >= 3:
                self.hint_shown = True
                self.show_hint = False

    def reset_level(self, preserve_level_index=False):
        if not preserve_level_index:
            if self.level_index >= len(levels):
                self.level_index = 0
        self.awaiting_riddle = False
        self.level_complete = False
        self.player.x = 0
        self.player.y = HEIGHT // 2
        self.show_level_intro = True
        self.wrong_attempts = 0
        self.riddle_answer = ""
        self.current_riddle = None
        self.show_hint = False
        self.hint_shown = False
        cfg = levels[self.level_index]
        self.obstacles = [Obstacle("rock") for _ in range(cfg["obstacles"])]
        self.obstacles += [Obstacle("blackhole") for _ in range(cfg["blackholes"])]
        stars_count = 5 + self.level_index * 2
        self.stars = [Star(self.player) for _ in range(stars_count)]

    def update(self):
        if self.show_win:
            return
        if self.show_scoreboard:
            self.final_ufo_x += 4
            trail_y = HEIGHT // 2 + 10
            self.final_trail.append((self.final_ufo_x, trail_y, 255))
            new_trail = []
            for (tx, ty, a) in self.final_trail:
                a -= 10
                if a > 0:
                    new_trail.append((tx, ty, a))
            self.final_trail = new_trail
            if self.final_ufo_x > WIDTH + 200:
                self.win_timer += 1
                if self.win_timer > 120:  # after ~2 seconds
                    self.show_scoreboard = False
                    self.show_win = True
            return
        if self.game_over or self.awaiting_riddle or self.show_level_intro:
            if self.show_level_intro:
                if self.player.x < WIDTH // 2:
                    self.player.x += 10
                else:
                    self.show_level_intro = False
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        if random.randint(1, 120) == 1:
            kind = random.choice(["rock", "blackhole"])
            self.obstacles.append(Obstacle(kind))
        for obs in self.obstacles:
            obs.update()
            if self.player.get_rect().colliderect(obs.get_rect()) and not obs.already_hit:
                if collision_sound:
                    collision_sound.play()
                self.player.crashes += 1
                obs.already_hit = True
                if self.player.crashes >= 5:
                    self.game_over = True
        for star in self.stars[:]:
            if self.player.get_rect().colliderect(star.get_rect()):
                if collect_sound:
                    collect_sound.play()
                self.stars.remove(star)
                self.score += 10
                self.stars.append(Star(self.player))
        needed = levels[self.level_index]["stars_needed"] * 10
        if self.score >= needed and not self.awaiting_riddle:
            self.level_complete = True
            self.awaiting_riddle = True
            self.riddle_answer = ""
            self.wrong_attempts = 0
            self.show_hint = True
            self.hint_shown = False
            if not self.remaining_riddles:
                self.remaining_riddles = riddles.copy()
            self.current_riddle = random.choice(self.remaining_riddles)

    def draw(self, surface):
        if self.show_win:
            surface.fill(BLACK)
            surface.blit(self.large_font.render("YOU WIN ", True, GREEN), (WIDTH//2-150, HEIGHT//2-120))
            total = sum(self.level_scores)
            surface.blit(self.medium_font.render(f"Total Energy: {total}", True, YELLOW), (WIDTH//2-150, HEIGHT//2-40))
            self.restart_rect = pygame.Rect(WIDTH//2-60, HEIGHT//2+40, 120, 50)
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.rect(surface, HOVER_BLUE if self.restart_rect.collidepoint(mouse_pos) else BLUE, self.restart_rect)
            surface.blit(self.font.render("Restart", True, WHITE), (self.restart_rect.x+15, self.restart_rect.y+12))
            pygame.display.flip()
            return
        if self.show_scoreboard:
            surface.fill(BLACK)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            surface.blit(overlay, (0, 0))
            surface.blit(self.large_font.render(" FINAL SCOREBOARD ", True, YELLOW), (WIDTH//2-300, 40))
            y = 140
            for i, s in enumerate(self.level_scores):
                name = levels[i]['name'] if i < len(levels) else f"Level {i+1}"
                surface.blit(self.font.render(f"{i+1}. {name} — {s} Energy", True, WHITE), (WIDTH//2-200, y))
                y += 36
            total = sum(self.level_scores)
            surface.blit(self.font.render(f"Total Energy: {total}", True, GREEN), (WIDTH//2-200, y+10))
            for (tx, ty, a) in self.final_trail:
                surf = pygame.Surface((30, 8), pygame.SRCALPHA)
                surf.fill((0, 255, 200, a//2))
                surface.blit(surf, (tx, ty))
            pygame.draw.ellipse(surface, (0, 200, 200), (self.final_ufo_x, HEIGHT//2, 60, 30))
            pygame.display.flip()
            return
        cfg = levels[self.level_index]
        surface.fill(cfg["background_color"])
        for sx, sy in self.background_stars:
            pygame.draw.circle(surface, WHITE, (sx, sy), 2)
        if self.show_level_intro:
            surface.blit(self.large_font.render(f"LEVEL {self.level_index+1}: {cfg['name']}", True, YELLOW), (WIDTH//2-200, HEIGHT//2-50))
            surface.blit(self.medium_font.render("UFO entering...", True, GREEN), (WIDTH//2-150, HEIGHT//2+20))
            self.player.draw(surface)
            pygame.display.flip()
            return
        if self.game_over:
            surface.fill(BLACK)
            surface.blit(self.large_font.render("GAME OVER", True, RED), (WIDTH//2-150, HEIGHT//2-100))
            surface.blit(self.font.render(f"Final Energy: {sum(self.level_scores)+self.score}", True, YELLOW), (WIDTH//2-150, HEIGHT//2-40))
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.rect(surface, HOVER_BLUE if self.try_again_rect.collidepoint(mouse_pos) else BLUE, self.try_again_rect)
            pygame.draw.rect(surface, HOVER_BLUE if self.restart_rect.collidepoint(mouse_pos) else BLUE, self.restart_rect)
            surface.blit(self.font.render("Try Again", True, WHITE), (self.try_again_rect.x+5, self.try_again_rect.y+12))
            surface.blit(self.font.render("Restart", True, WHITE), (self.restart_rect.x+15, self.restart_rect.y+12))
            pygame.display.flip()
            return
        for obs in self.obstacles:
            obs.draw(surface)
        for star in self.stars:
            star.draw(surface)
        self.player.draw(surface)
        surface.blit(self.font.render(f"Energy: {self.score}", True, WHITE), (10, 10))
        surface.blit(self.font.render(f"Crashes: {self.player.crashes}", True, RED), (10, 50))
        surface.blit(self.font.render(f"Level {self.level_index+1}", True, GREEN), (10, 90))
        if self.awaiting_riddle and self.current_riddle:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            surface.blit(overlay, (0, 0))
            draw_wrapped_text(surface, "RIDDLE:", YELLOW, WIDTH//2-300, HEIGHT//2-120, self.medium_font, 600)
            draw_wrapped_text(surface, self.current_riddle["question"], WHITE, WIDTH//2-300, HEIGHT//2-70, self.font, 600)
            ans_disp = self.riddle_answer if self.riddle_answer else "_"
            surface.blit(self.font.render(f"Your Answer: {ans_disp}", True, GREEN), (WIDTH//2-300, HEIGHT//2))
            if self.show_hint:
                self.hint_rect = pygame.Rect(WIDTH//2-60, HEIGHT//2+40, 120, 40)
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.rect(surface, HOVER_BLUE if self.hint_rect.collidepoint(mouse_pos) else BLUE, self.hint_rect)
                surface.blit(self.font.render("Hint", True, WHITE), (self.hint_rect.x+30, self.hint_rect.y+8))
            if self.hint_shown:
                hint_text = f"Hint: {self.current_riddle['answer'][0].upper()}..."
                surface.blit(self.font.render(hint_text, True, YELLOW), (WIDTH//2-300, HEIGHT//2+100))
        pygame.display.flip()

# Main loop
def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw(screen)
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
