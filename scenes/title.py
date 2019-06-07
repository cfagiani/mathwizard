import os

import pygame

from common import Scene
from config import configvalues
from game import GameScene


class TitleScene(Scene):
    """
    Title scene for the game. It simply displays the title and plays the theme music. After TITLE_TICKS frames, the
    "press start" message will be displayed along the bottom of the screen as well.
    """

    def __init__(self, resources):
        """
        Initialize the scene by starting the theme music.
        :param resources:
        """
        Scene.__init__(self, resources)
        pygame.mixer.music.load(os.path.join(configvalues.RESOURCE_DIR, 'theme.ogg'))
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
        self.wait_tick = configvalues.TITLE_TICKS

    def get_name(self):
        return 'title'

    def process_input(self, events, pressed_keys):
        """
        Pressing any key starts the game by advancing to the GameScene.
        :param events:
        :param pressed_keys:
        :return:
        """
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self.switch_to_scene(GameScene(self.resources))

    def update(self):
        """
        Updates the internal state for the scene. In this case, just the number of ticks since the scene was first
        displayed.
        :return:
        """
        self.wait_tick -= 1

    def render(self, screen):
        """
        Renders the background, title, and, optionally, the "press any key" message. Returns None to force the entire
        screen to be repainted.
        :param screen:
        :return:
        """
        screen.fill((255, 255, 255))
        screen.blit(self.resources['background'], (0, 0))
        w, h = pygame.display.get_surface().get_size()
        self.render_centered(screen, w, h, self.resources['title'])
        if self.wait_tick <= 0:
            img_w, img_h = self.resources['anykey'].get_rect().size
            screen.blit(self.resources['anykey'],
                        ((w - img_w) // 2, (h - img_h)))
        return None
