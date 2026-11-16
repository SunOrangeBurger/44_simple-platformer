import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

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


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard", "unknown"])
def test_restart_changes_difficulty_and_resets_score(difficulty):
    engine = GameEngine(800, 500)
    engine.score = 4
    engine.game_over = True
    engine.player.vx = 4
    engine.player.vy = 20
    engine.restart(difficulty)
    expected = difficulty if difficulty != "unknown" else "medium"
    settings = engine.DIFFICULTIES[expected]
    assert engine.score == 0
    assert engine.game_over is False
    assert engine.difficulty_name == expected
    assert engine.gravity == settings["gravity"]
    assert engine.player.jump_strength == settings["jump_strength"]
    assert engine.player.speed == settings["speed"]
    assert (engine.player.x, engine.player.y) == (engine.start_x, engine.start_y)
    assert (engine.player.vx, engine.player.vy) == (0, 0)


def test_falling_below_screen_ends_game_and_freezes_state():
    engine = GameEngine(800, 500)
    engine.player.y = 501
    engine.update()
    assert engine.game_over
    position = (engine.player.x, engine.player.y)
    engine.update()
    assert (engine.player.x, engine.player.y) == position


def test_jump_sound_only_plays_for_grounded_jump(monkeypatch):
    engine = GameEngine(800, 500)
    played = []
    monkeypatch.setattr(engine, "_play_sound", played.append)
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    engine.handle_event(event)
    assert played == []
    engine.player.on_ground = True
    engine.handle_event(event)
    assert played == ["jump"]
    assert engine.player.vy == engine.player.jump_strength
    assert not engine.player.on_ground


def test_generated_sound_matches_requested_duration():
    engine = GameEngine(800, 500)
    assert engine.sound_enabled
    for name, duration in [("jump", .08), ("goal", .11), ("hit", .2)]:
        assert engine.sounds[name].get_length() == pytest.approx(duration, abs=.001)


def test_audio_initialization_failure_is_nonfatal(monkeypatch):
    def fail():
        raise pygame.error("No audio device")
    monkeypatch.setattr(pygame.mixer, "init", fail)
    engine = GameEngine(800, 500)
    assert not engine.sound_enabled
    assert engine.sounds == {}
    engine._play_sound("jump")


def test_rising_player_does_not_snap_onto_platform():
    engine = GameEngine(800, 500)
    engine.platforms = [Platform(0, 460, 200)]
    engine.player.x, engine.player.y = 40, 450
    engine.player.vy = -20
    engine.update()
    assert not engine.player.on_ground
    assert engine.player.vy < 0
