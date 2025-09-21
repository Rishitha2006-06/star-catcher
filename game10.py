import pygame
import random
import math
import os
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
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

# Paths
ASSET_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECT_SOUND_FILE = "catch.mp3"
COLLISION_SOUND_FILE = "miss.mp3"
BACKGROUND_MUSIC_FILE = "background.mp3"

# Load sounds
collect_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLECT_SOUND_FILE))
collision_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, COLLISION_SOUND_FILE))
pygame.mixer.music.load(os.path.join(ASSET_PATH, BACKGROUND_MUSIC_FILE))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Levels
levels = [
    {"name": "Pink City", "background_color": (255, 182, 193), "stars_needed": 10, "obstacles": 5, "blackholes": 2},
    {"name": "Blue Space", "background_color": (30, 144, 255), "stars_needed": 12, "obstacles": 8, "blackholes": 3},
    {"name": "Ocean Block", "background_color": (0, 105, 148), "stars_needed": 15, "obstacles": 12, "blackholes": 4}
]

# Riddles
riddles = [
    {"question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"},
    {"question": "I’m tall when I’m young, and short when I’m old. What am I?", "answer": "candle"},
    {"question": "What has keys but can’t open locks?", "answer": "piano"}
]

# Player UFO
class UFO:
    def __init__(self):
        self.x = WIDTH // 2
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

# Obstacle
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
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(50, HEIGHT - 50)
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
        self.stars = [Star(self.player) for _ in range(5)]
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.awaiting_riddle = False
        self.riddle_answer = ""
        self.current_riddle = None
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        self.medium_font = pygame.font.SysFont(None, 48)
        self.background_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
        self.overlay_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1,3)) for _ in range(50)]
        self.buttons = []
        self.remaining_riddles = riddles.copy()
        self.level_scores = []
        self.level_start_time = time.time()
        self.show_level_message = True
        self.wrong_attempts = 0
        self.level_transition = True
        self.transition_x = -50
        self.transition_speed = 8

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.awaiting_riddle:
                    if event.key == pygame.K_RETURN:
                        if self.current_riddle and self.riddle_answer.lower() == self.current_riddle["answer"]:
                            self.wrong_attempts = 0
                            self.next_level()
                        else:
                            self.wrong_attempts += 1
                            self.show_buttons()
                    elif event.key == pygame.K_BACKSPACE:
                        self.riddle_answer = self.riddle_answer[:-1]
                    else:
                        self.riddle_answer += event.unicode
                elif self.game_over and event.key == pygame.K_r:
                    self.__init__()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in self.buttons:
                    if rect.collidepoint(event.pos):
                        if action == "restart":
                            self.__init__()
                        elif action == "tryagain":
                            if self.level_index > 0:
                                self.level_index -= 1
                                if self.level_scores:
                                    self.level_scores.pop()
                                self.score = 0
                                self.reset_level()
        return True

    def show_buttons(self):
        self.buttons = []
        restart_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 180, 40)
        try_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 180, 40)
        self.buttons.append((restart_rect, "restart"))
        self.buttons.append((try_rect, "tryagain"))

    def reset_level(self):
        self.awaiting_riddle = False
        self.level_complete = False
        self.player.x, self.player.y = WIDTH//2, HEIGHT//2
        self.obstacles = []
        for _ in range(levels[self.level_index]["obstacles"]):
            self.obstacles.append(Obstacle("rock"))
        for _ in range(levels[self.level_index]["blackholes"]):
            self.obstacles.append(Obstacle("blackhole"))
        self.stars = [Star(self.player) for _ in range(5 + self.level_index * 2)]
        self.riddle_answer = ""
        self.current_riddle = None
        self.buttons = []
        self.game_over = False
        self.level_start_time = time.time()
        self.show_level_message = True
        self.level_transition = True
        self.transition_x = -50

    def draw_overlay_stars(self, surface):
        for i, (x, y, speed) in enumerate(self.overlay_stars):
            pygame.draw.circle(surface, YELLOW, (x, y), speed)
            y += speed
            if y > HEIGHT:
                y = 0
                x = random.randint(0, WIDTH)
            self.overlay_stars[i] = (x, y, speed)

    def draw_level_transition(self, surface):
        level_bg = levels[self.level_index]["background_color"]
        surface.fill(level_bg)
        self.transition_x += self.transition_speed
        if self.transition_x >= WIDTH // 2:
            self.level_transition = False
            self.player.x, self.player.y = WIDTH // 2, HEIGHT // 2
            return
        pygame.draw.ellipse(surface, (0, 200, 200), (self.transition_x - 30, HEIGHT//2 - 15, 60, 30))
        pygame.draw.ellipse(surface, (180, 250, 250), (self.transition_x - 15, HEIGHT//2 - 25, 30, 20))
        surface.blit(self.font.render(f"Level {self.level_index+1}: {levels[self.level_index]['name']}", True, YELLOW),
                     (WIDTH//2 - 150, HEIGHT//2 - 100))
        pygame.display.flip()

    def update(self):
        if self.game_over or self.level_complete or self.awaiting_riddle or self.level_transition:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        if random.randint(1, 50) == 1:
            kind = random.choice(["rock", "blackhole"])
            self.obstacles.append(Obstacle(kind))

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

        if self.score >= levels[self.level_index]["stars_needed"] * 10:
            self.level_complete = True
            self.awaiting_riddle = True
            self.riddle_answer = ""
            if self.remaining_riddles:
                self.current_riddle = random.choice(self.remaining_riddles)
                self.remaining_riddles.remove(self.current_riddle)
            else:
                self.current_riddle = None

    def draw(self, surface):
        level_bg = levels[self.level_index]["background_color"] if self.level_index < len(levels) else BLACK
        surface.fill(level_bg)

        for x, y in self.background_stars:
            pygame.draw.circle(surface, WHITE, (x, y), random.randint(1, 2))

        for star in self.stars:
            star.draw(surface)
        for obs in self.obstacles:
            obs.draw(surface)
        self.player.draw(surface)

        # UI
        level_name = levels[self.level_index]['name'] if self.level_index < len(levels) else "Finished"
        surface.blit(self.font.render(f"Energy: {self.score}", True, TEXT_COLOR), (10, 10))
        surface.blit(self.font.render(f"Level: {level_name}", True, TEXT_COLOR), (10, 40))
        surface.blit(self.font.render(f"Crashes: {self.player.crashes}/5", True, TEXT_COLOR), (10, 70))

        # Riddle overlay
        if self.awaiting_riddle and self.current_riddle:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            self.draw_overlay_stars(surface)
            if int(time.time()*2) % 2 == 0:
                surface.blit(self.large_font.render("LEVEL COMPLETED!", True, YELLOW), (WIDTH//2-220, HEIGHT//2-120))
            surface.blit(self.medium_font.render(self.current_riddle["question"], True, GREEN), (WIDTH//2-200, HEIGHT//2-50))
            surface.blit(self.font.render(self.riddle_answer, True, TEXT_COLOR), (WIDTH//2-100, HEIGHT//2))
            if self.wrong_attempts >= 3:
                hint_text = f"HINT: The answer starts with '{self.current_riddle['answer'][0].upper()}'"
                surface.blit(self.font.render(hint_text, True, BLUE), (WIDTH//2-180, HEIGHT//2+40))
            for rect, action in self.buttons:
                mouse_pos = pygame.mouse.get_pos()
                color = BLUE if not rect.collidepoint(mouse_pos) else (100, 200, 255)
                pygame.draw.rect(surface, color, rect)
                surface.blit(self.font.render("Restart" if action=="restart" else "Try Again", True, WHITE), (rect.x+10, rect.y+5))

        # Game over / Win screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            surface.blit(overlay, (0, 0))
            self.draw_overlay_stars(surface)
            if self.level_index >= len(levels):
                # Score Summary + Win
                if int(time.time()*2) % 2 == 0:
                    surface.blit(self.large_font.render("🎉 YOU WIN! 🎉", True, YELLOW), (WIDTH//2-180, HEIGHT//2-150))
                surface.blit(self.medium_font.render("📊 LEVEL SCORE SUMMARY 📊", True, YELLOW), (WIDTH//2-180, 50))
                total_energy = sum(self.level_scores)
                for idx, score in enumerate(self.level_scores):
                    surface.blit(self.font.render(f"Level {idx+1}: {score} Energy", True, WHITE), (WIDTH//2-100, 120 + idx*40))
                surface.blit(self.font.render(f"Total Energy: {total_energy}", True, GREEN), (WIDTH//2-100, 120 + len(self.level_scores)*40 + 20))
                # Buttons
                self.buttons = []
                restart_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 180, 40)
                try_rect = pygame.Rect(WIDTH//2-100, HEIGHT-50, 180, 40)
                self.buttons.append((restart_rect, "restart"))
                self.buttons.append((try_rect, "tryagain"))
                for rect, action in self.buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    color = BLUE if not rect.collidepoint(mouse_pos) else (100, 200, 255)
                    pygame.draw.rect(surface, color, rect)
                    surface.blit(self.font.render("Restart" if action=="restart" else "Try Again", True, WHITE), (rect.x+10, rect.y+5))
            else:
                surface.blit(self.font.render("GAME OVER! Press R to Restart", True, RED), (WIDTH//2-180, HEIGHT//2))

        pygame.display.flip()

    def next_level(self):
        if self.level_index < len(levels):
            self.level_scores.append(self.score)
        self.level_index += 1
        if self.level_index >= len(levels):
            self.game_over = True
            return
        self.score = 0
        self.reset_level()

# Main loop
def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        if game.level_transition:
            game.draw_level_transition(screen)
        else:
            game.update()
            game.draw(screen)
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
