"""Capture deterministic engine evidence; not a human gameplay recording."""
import os
import subprocess
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame
from game.game_engine import GameEngine
from game.platform import Platform

pygame.init()
out = ROOT / "evidence"
out.mkdir(exist_ok=True)
source = subprocess.check_output(
    ["git", "show", "140ee4d:game/game_engine.py"], text=True
)
namespace = {"__name__": "game.baseline_engine", "__package__": "game"}
exec(compile(source, "baseline_game_engine.py", "exec"), namespace)
results = []
for label, cls in [("Starter 140ee4d", namespace["GameEngine"]), ("Final", GameEngine)]:
    engine = cls(800, 500)
    engine.platforms = [Platform(0, 460, 200)]
    engine.player.x, engine.player.y = 40, 420
    engine.player.vy = 90
    engine.update()
    results.append(f"{label}: y={engine.player.y}, vy={engine.player.vy}, "
                   f"on_ground={engine.player.on_ground}, game_over={engine.game_over}")
(out / "collision_comparison.txt").write_text(
    "Controlled scenario: x=40, y=420, vy=90, platform top=460, height=32.\n"
    + "\n".join(results) + "\n", encoding="utf-8"
)
screen = pygame.Surface((800, 500))
engine = GameEngine(800, 500)
def save(name):
    screen.fill((100, 160, 220))
    engine.render(screen)
    pygame.image.save(screen, str(out / name))
save("level.png")
engine.score = 2
engine.player.x, engine.player.y = 250, 440
engine.update()
assert engine.game_over
save("game_over.png")
engine.restart("hard")
assert engine.score == 0 and not engine.game_over
save("replay_hard.png")
pygame.quit()
result = subprocess.run([sys.executable, "-m", "pytest", "test_game.py", "-v"],
                        capture_output=True, text=True)
(out / "tests.txt").write_text(result.stdout + result.stderr +
                               f"\nExit code: {result.returncode}\n", encoding="utf-8")
print("\n".join(results))
print(result.stdout)
raise SystemExit(result.returncode)
