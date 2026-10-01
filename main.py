import pygame

from game.game_engine import GameEngine

pygame.init()
WIDTH, HEIGHT = 800, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer - Pygame Version")
SKY = (100, 160, 220)
clock = pygame.time.Clock()
FPS = 60
engine = GameEngine(WIDTH, HEIGHT)


def main():
    running = True
    while running:
        SCREEN.fill(SKY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if engine.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        engine.restart("easy")
                    elif event.key == pygame.K_2:
                        engine.restart("medium")
                    elif event.key == pygame.K_3:
                        engine.restart("hard")
                continue

            engine.handle_event(event)

        if not engine.game_over and running:
            engine.handle_input()
            engine.update()

        engine.render(SCREEN)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
