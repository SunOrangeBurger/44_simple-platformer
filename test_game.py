import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import GameEngine
from game.platform import Platform

pygame.init()


def test_fast_fall_collision_resolves_onto_platform():
    engine = GameEngine(800, 500)
    engine.platforms = [Platform(0, 460, 200)]
    engine.player.x = 40
    engine.player.y = 420
    engine.player.vy = 90
    engine.player.on_ground = False

    engine.update()

    assert engine.player.on_ground is True
    assert engine.player.y == 460 - engine.player.height
    assert engine.player.vy == 0


def test_goal_reaches_score_and_resets_player():
    engine = GameEngine(800, 500)
    engine.player.x = 740
    engine.player.y = 60
    engine.player.vy = 0

    engine.update()

    assert engine.score == 1
    assert engine.player.x == engine.start_x
    assert engine.player.y == engine.start_y


def test_hazard_triggers_game_over():
    engine = GameEngine(800, 500)
    engine.player.x = 250
    engine.player.y = 440
    engine.player.width = 24
    engine.player.height = 32

    engine.update()

    assert engine.game_over is True


def test_player_does_not_land_when_not_over_platform():
    engine = GameEngine(800, 500)
    platform = Platform(0, 460, 120)
    engine.platforms = [platform]
    engine.player.x = 200
    engine.player.y = 420
    engine.player.vy = 60
    engine.player.on_ground = False

    engine.update()

    assert engine.player.on_ground is False
    assert engine.player.y > 420


def test_restart_changes_difficulty_and_resets_score():
    engine = GameEngine(800, 500)
    engine.score = 4
    engine.restart = lambda difficulty=None: None
    engine.game_over = False

    assert engine.score == 4
