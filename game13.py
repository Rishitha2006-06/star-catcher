import pygame
import random
import math
import os

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

# Assets
ASSET_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECT_SOUND_FILE = "catch.mp3"
COLLISION_SOUND_FILE = "miss.mp3"
BACKGROUND_MUSIC_FILE = "background.mp3"

collect_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLECT_SOUND_FILE))
collision_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLISION_SOUND_FILE))
pygame.mixer.music.load(os.path.join(ASSET_PATH, BACKGROUND_MUSIC_FILE))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Levels
levels = [
    {"name": "Pink City", "background_color": (255, 182, 193), "stars_needed": 10, "obstacles": 15, "blackholes": 8},  # increased obstacles
    {"name": "Blue Space", "background_color": (30, 144, 255), "stars_needed": 12, "obstacles": 15, "blackholes": 9},
    {"name": "Ocean Block", "background_color": (0, 105, 148), "stars_needed": 15, "obstacles": 20, "blackholes": 10}
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
    {"question": "The more you take away from me, the bigger I get. What am I?", "answer": "hole"}
]

# Helper: wrapped text
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

# UFO class
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

# Obstacle class
class Obstacle:
    def __init__(self, kind="rock"):
        self.kind = kind
        self.size = random.randint(30, 50) if kind=="rock" else random.randint(40,60)
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(-HEIGHT, -self.size)
        if kind=="rock":
            self.dx = random.uniform(-1.5, 1.5)
            self.dy = random.uniform(-1.5, 1.5)
        else:
            self.dx = 0
            self.dy = random.uniform(1,3)
        self.already_hit = False
        self.angle = random.uniform(0, 360)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.kind=="rock":
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
        if self.kind=="rock":
            pygame.draw.circle(surface, GRAY, (int(self.x + self.size/2), int(self.y + self.size/2)), self.size//2)
        else:
            center = (int(self.x + self.size/2), int(self.y + self.size/2))
            pygame.draw.circle(surface, BLACK, center, self.size//2)
            end_x = center[0] + int(math.cos(math.radians(self.angle))*self.size//2)
            end_y = center[1] + int(math.sin(math.radians(self.angle))*self.size//2)
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

# Game class
class Game:
    def __init__(self):
        self.level_index = 0
        self.player = UFO()
        self.obstacles = []
        self.stars = [Star(self.player) for _ in range(5)]
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
        self.buttons = []
        self.remaining_riddles = riddles.copy()
        self.level_scores = []
        self.player.x = 0
        self.player.y = HEIGHT//2
        self.wrong_attempts = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.awaiting_riddle:
                    if event.key == pygame.K_RETURN:
                        if self.current_riddle and self.riddle_answer.lower() == self.current_riddle["answer"]:
                            self.next_level()
                        else:
                            self.wrong_attempts += 1
                    elif event.key == pygame.K_BACKSPACE:
                        self.riddle_answer = self.riddle_answer[:-1]
                    else:
                        self.riddle_answer += event.unicode
                elif self.game_over and event.key == pygame.K_r:
                    self.__init__()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.show_hint and self.hint_rect.collidepoint(mouse_pos):
                    self.hint_shown = True
        return True

    def reset_level(self):
        self.awaiting_riddle = False
        self.level_complete = False
        self.player.x = 0
        self.player.y = HEIGHT // 2
        self.show_level_intro = True
        self.obstacles = []
        obs_count = levels[self.level_index]["obstacles"] + self.level_index*2
        for _ in range(obs_count):
            self.obstacles.append(Obstacle("rock"))
        for _ in range(levels[self.level_index]["blackholes"]):
            self.obstacles.append(Obstacle("blackhole"))
        self.stars = [Star(self.player) for _ in range(5+self.level_index*2)]
        self.riddle_answer = ""
        self.current_riddle = None
        self.show_hint = False
        self.hint_shown = False
        self.wrong_attempts = 0

    def update(self):
        if self.game_over or self.level_complete or self.awaiting_riddle or self.show_level_intro:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        for obs in self.obstacles:
            obs.update()
            if self.player.get_rect().colliderect(obs.get_rect()) and not obs.already_hit:
                collision_sound.play()
                self.player.crashes += 1
                obs.already_hit = True
                if self.player.crashes >= 5:
                    self.game_over = True
        for star in self.stars[:]:
            if self.player.get_rect().colliderect(star.get_rect()):
                collect_sound.play()
                self.stars.remove(star)
                self.score += 10
                self.stars.append(Star(self.player))
        if self.score >= levels[self.level_index]["stars_needed"]*10:
            self.level_complete = True
            self.awaiting_riddle = True
            self.riddle_answer = ""
            self.show_hint = True
            self.hint_shown = False
            self.current_riddle = random.choice(self.remaining_riddles)

    def draw(self, surface):
        # Final scoreboard
        if self.game_over and self.level_index >= len(levels):
            surface.fill(BLACK)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,220))
            surface.blit(overlay,(0,0))
            surface.blit(self.large_font.render("YOU WIN!", True, YELLOW),(WIDTH//2-180,50))
            surface.blit(self.medium_font.render("LEVEL SCORE SUMMARY   ", True, YELLOW),(WIDTH//2-180,150))
            for idx, score in enumerate(self.level_scores):
                surface.blit(self.font.render(f"Level {idx+1}: {levels[idx]['name']} - {score} Energy", True, WHITE),(WIDTH//2-180,220+idx*40))
            total_energy = sum(self.level_scores)
            surface.blit(self.font.render(f"Total Energy: {total_energy}", True, GREEN),(WIDTH//2-180,220+len(self.level_scores)*40+20))
            pygame.display.flip()
            return

        # Level intro
        if self.level_index < len(levels):
            level = levels[self.level_index]
            if self.show_level_intro:
                surface.fill(level["background_color"])
                if self.player.x < WIDTH // 2:
                    self.player.x += 10
                self.player.draw(surface)
                surface.blit(self.large_font.render(level["name"], True, YELLOW), (WIDTH//2-150, HEIGHT//2-50))
                pygame.display.flip()
                if self.player.x >= WIDTH // 2:
                    self.show_level_intro = False
                return

            # Draw background & objects
            surface.fill(level["background_color"])
            for x, y in self.background_stars:
                pygame.draw.circle(surface, WHITE, (x, y), random.randint(1, 2))
            for star in self.stars: star.draw(surface)
            for obs in self.obstacles: obs.draw(surface)
            self.player.draw(surface)

            # HUD
            surface.blit(self.font.render(f"Energy: {self.score}", True, TEXT_COLOR), (10,10))
            surface.blit(self.font.render(f"Level: {level['name']}", True, TEXT_COLOR), (10,40))
            surface.blit(self.font.render(f"Crashes: {self.player.crashes}/5", True, TEXT_COLOR), (10,70))

            # Riddle overlay
            if self.awaiting_riddle and self.current_riddle:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0,0,0,180))
                surface.blit(overlay,(0,0))
                draw_wrapped_text(surface, self.current_riddle["question"], GREEN, WIDTH//2-300, HEIGHT//2-50, self.medium_font, 600)
                surface.blit(self.font.render(self.riddle_answer, True, TEXT_COLOR), (WIDTH//2-100, HEIGHT//2+60))
                # Hint button
                if self.show_hint:
                    self.hint_rect = pygame.Rect(WIDTH//2+200, HEIGHT//2+50, 100, 40)
                    pygame.draw.rect(surface, HOVER_BLUE if self.hint_rect.collidepoint(pygame.mouse.get_pos()) else BLUE, self.hint_rect)
                    surface.blit(self.font.render("Hint", True, WHITE), (self.hint_rect.x+10, self.hint_rect.y+5))
                if self.hint_shown:
                    hint_letter = self.current_riddle["answer"][0].upper()
                    surface.blit(self.font.render(f"Hint: First letter is '{hint_letter}'", True, YELLOW), (WIDTH//2-180, HEIGHT//2+110))

            pygame.display.flip()

    def next_level(self):
        self.level_scores.append(self.score)
        self.level_index += 1
        if self.level_index >= len(levels):
            self.game_over = True
        else:
            self.score = 0
            self.player.crashes = 0
            self.reset_level()

# Main game loop
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

if __name__=="__main__":
    main()

