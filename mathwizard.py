import pygame
from pygame.locals import *

from assetmanager import AssetManager
from config import configvalues
from scenes.title import TitleScene


def init():
    """
    Initializes pygame and loads resources.
    :return:
    """
    pygame.init()
    pygame.display.set_mode((configvalues.WIDTH, configvalues.HEIGHT), 0, 32)

    pygame.time.set_timer(USEREVENT + 1, 1000)

    pygame.key.set_repeat(configvalues.KEY_REPEAT_DELAY, configvalues.KEY_REPEAT_INTERVAL)
    pygame.joystick.init()

    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

    pygame.display.set_caption('Math Wizard')

    return load_resources()


def load_resources():
    """
    Loads all resources and returns an AssetManager instance that can be used by scenes to access resources.
    :return:
    """
    mgr = AssetManager(configvalues.RESOURCE_DIR)
    # load fonts
    mgr.register_resource('targetfont', pygame.font.SysFont("monospace", 75, True))
    mgr.register_resource('eqfont', pygame.font.SysFont("monospace", 25, True))
    mgr.register_resource('scorefont', pygame.font.SysFont("monospace", 30))

    # load regular images
    mgr.load_image('title', 'title.png', -1)
    mgr.load_image('gameover', 'gameover.png', -1)
    mgr.load_image('pause', 'paused.png', -1)
    mgr.load_image('leveldone', 'levelDone.png', -1)
    mgr.load_image('anykey', 'anyKey.png', -1)
    mgr.load_image('background', 'background.jpg')
    mgr.load_image('floor', 'stone.jpg')

    # load sprite sheets
    mgr.load_sprite_sheet('sprites', 'wizardSprites.png')
    mgr.load_sprite_sheet('explosion', 'explosionSprite.png')

    # load sound effects
    mgr.load_sound('boom', 'bomb.ogg', .2)
    mgr.load_sound('zap', 'zap.ogg')
    mgr.load_sound('fanfare', 'fanfare.ogg', 2)

    return mgr


def run_game(assets, starting_scene):
    """
    Runs the main loop for the game. On each frame, it will filter the set of events received since the last frame and
    then call the following on the active scene in order: process_events, update, render.

    :param assets:
    :param starting_scene:
    :return:
    """
    clock = pygame.time.Clock()
    active_scene = starting_scene
    screen = pygame.display.set_mode((configvalues.WIDTH, configvalues.HEIGHT), 0, 32)

    while active_scene is not None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        has_quit = False
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            if quit_attempt:
                if active_scene.get_name() == 'title':
                    has_quit = active_scene.terminate()
                else:
                    active_scene.switch_to_scene(TitleScene(assets))
            else:
                filtered_events.append(event)

        if not has_quit:
            active_scene = process_frame(active_scene, filtered_events, pressed_keys, screen)
            clock.tick(configvalues.FPS)
        else:
            active_scene = None


def process_frame(active_scene, filtered_events, pressed_keys, screen):
    active_scene.process_input(filtered_events, pressed_keys)
    active_scene.update()
    rects = active_scene.render(screen)
    if rects is not None:
        pygame.display.update(rects)
    else:
        pygame.display.update()
    return active_scene.next


if __name__ == '__main__':
    game_assets = init()
    run_game(game_assets, TitleScene(game_assets))
