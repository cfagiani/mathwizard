import pygame


class Scene:
    def __init__(self, resources):
        self.next = self
        self.resources = resources

    def process_input(self, events, pressed_keys):
        """
        Processes all user input since last frame.
        :param events:
        :param pressed_keys
        :return:
        """
        pass

    def update(self):
        """
        Updates internal state for the current frame.
        :return:
        """
        pass

    def render(self, screen):
        """
        Draws the scene.
        :param screen:
        :return: list of rectangles to update
        """
        return None

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def get_name(self):
        """
        :return: the name of the scene
        """
        return None

    def terminate(self):
        """
        Ends the scene. Override if you want to display a confirmation prompt.
        :return: True if we should exit immediately
        """
        pygame.quit()
        return True

    def render_centered(self, screen, win_w, win_h, surface):
        """
        Renders the given surface centered in the screen.
        :param screen:
        :param win_w
        :param win_h
        :param surface:
        :return:
        """
        img_w, img_h = surface.get_rect().size
        screen.blit(surface,
                    ((win_w - img_w) // 2, (win_h - img_h) // 2))
        return [pygame.Rect((win_w - img_w) // 2, (win_h - img_h) // 2, img_w, img_h)]
