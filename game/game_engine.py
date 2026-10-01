import pygame

from .hazard import Hazard
from .platform import Platform
from .player import Player

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)


class GameEngine:
    DIFFICULTIES = {
        "easy": {"gravity": 0.45, "speed": 4, "jump_strength": -11},
        "medium": {"gravity": 0.6, "speed": 4, "jump_strength": -12},
        "hard": {"gravity": 0.75, "speed": 5, "jump_strength": -13},
    }

    def __init__(self, width, height, difficulty="medium"):
        self.width = width
        self.height = height
        self.goal_x = 740
        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.score = 0
        self.game_over = False
        self._game_over_logged = False
        self.difficulty_name = "medium"
        self.start_x, self.start_y = 40, height - 120
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.set_difficulty(difficulty)
        self.reset_player()

    def set_difficulty(self, difficulty):
        key = str(difficulty).lower()
        if key not in self.DIFFICULTIES:
            key = "medium"
        self.difficulty_name = key
        settings = self.DIFFICULTIES[key]
        self.gravity = settings["gravity"]
        if hasattr(self, "player"):
            self.player.speed = settings["speed"]
            self.player.jump_strength = settings["jump_strength"]

    def reset_player(self):
        self.player = Player(self.start_x, self.start_y)
        self.player.speed = self.DIFFICULTIES[self.difficulty_name]["speed"]
        self.player.jump_strength = self.DIFFICULTIES[self.difficulty_name]["jump_strength"]
        self.player.vx = 0
        self.player.vy = 0
        self.player.on_ground = False
        self.game_over = False
        self._game_over_logged = False

    def restart(self, difficulty=None):
        if difficulty is not None:
            self.difficulty_name = str(difficulty).lower()
        self.set_difficulty(self.difficulty_name)
        self.score = 0
        self.reset_player()

    def handle_event(self, event):
        if self.game_over:
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            return

        previous_x = self.player.x
        previous_y = self.player.y
        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)
        self.player.y += self.player.vy
        self.player.on_ground = False

        prev_rect = pygame.Rect(previous_x, previous_y, self.player.width, self.player.height)
        current_rect = self.player.rect()

        for platform in self.platforms:
            platform_rect = platform.rect()
            landing_from_above = (
                self.player.vy >= 0
                and prev_rect.bottom <= platform_rect.top + 1
                and current_rect.bottom >= platform_rect.top
            )
            horizontal_overlap = (
                current_rect.right > platform_rect.left
                and current_rect.left < platform_rect.right
            )

            if landing_from_above and horizontal_overlap:
                self.player.y = platform_rect.top - self.player.height
                self.player.vy = 0
                self.player.on_ground = True
                break

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)
        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            title = self.font.render("Game Over", True, WHITE)
            title_x = self.width // 2 - title.get_width() // 2
            screen.blit(title, (title_x, self.height // 2 - 80))

            final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_x = self.width // 2 - final_score.get_width() // 2
            screen.blit(final_score, (score_x, self.height // 2 - 30))

            prompt = self.small_font.render("Press 1 Easy  2 Medium  3 Hard  Esc Quit", True, WHITE)
            prompt_x = self.width // 2 - prompt.get_width() // 2
            screen.blit(prompt, (prompt_x, self.height // 2 + 40))

            if not getattr(self, "_game_over_logged", False):
                print("Game over! Final score:", self.score)
                self._game_over_logged = True
