import os
import pygame
import random

from config import configvalues
from scenes.common import Scene

OPERATORS = ['+', '-']


class GameScene(Scene):
    """
    This class represents the main scene in the game.
    """

    def __init__(self, resources):
        """
        Initialize the scene by starting the play music and initializing the state of the game (avatar, target value,
        score, and equations).
        :param resources:
        """
        Scene.__init__(self, resources)
        pygame.mixer.music.load(os.path.join(configvalues.RESOURCE_DIR, 'gameMusic.ogg'))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        self.avatar = Avatar(resources['sprites'])
        self.first_draw = True
        self.paused = False
        self.won_level = False
        self.display_win = False
        self.wait_tick = 0
        self.target = TargetValue(resources['targetfont'])
        self.floor_tile_w, self.floor_tile_h = resources['floor'].get_rect().size
        self.window_w, self.window_h = pygame.display.get_surface().get_size()
        self.top_of_floor = self.window_h - self.floor_tile_h
        self.score = Score(resources['scorefont'])
        self.equations = [Equation(resources['eqfont'], resources['explosion']) for i in
                          range(configvalues.MAX_CONCURRENT)]
        self.level_score = 0
        self.movedir = 0
        self.joytick = 0
        self.game_over = False
        self.start_level()

    def get_name(self):
        return 'game'

    def process_input(self, events, pressed_keys):
        """
        Handles input events. This scene responds to left/right/up arrow keys (or left/right/up joystick buttons)
        for movement. The "p" key will trigger a paused state.

        :param events:
        :param pressed_keys:
        :return:
        """
        for event in events:
            if self.won_level and self.wait_tick <= 0:
                if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                    if not self.game_over:
                        self.start_level()
                    return

            if (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 61):
                if self.paused:
                    self.paused = False
                else:
                    if event.type == pygame.JOYBUTTONDOWN:
                        self.movedir = 1
                    self.joytick = 0
                    self.avatar.move(1)
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 63):
                if self.paused:
                    self.paused = False
                else:
                    if event.type == pygame.JOYBUTTONDOWN:
                        self.movedir = -1
                    self.joytick = 0
                    self.avatar.move(-1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 60):
                if self.paused:
                    self.paused = False
                else:
                    self.handle_jump()
            elif event.type == pygame.JOYBUTTONUP:
                self.movedir = 0
                self.joytick = 0
        if self.movedir != 0 and not self.paused:
            self.joytick += 1
            if self.joytick % configvalues.JOYSTICK_REPEAT == 0:
                self.avatar.move(self.movedir)

    def handle_jump(self):
        """
        Makes the avatar jump and fire at an equation. This method will also play the 'zap' sound effect and check
        if the zap hit an equation. If it did, it will trigger the explosion effect and increment/decrement the score.
        :return:
        """
        self.avatar.jump()
        self.resources['zap'].play()
        collided_eq = self.get_collision()
        if collided_eq is not None:
            if collided_eq.is_correct():
                self.score.increment_score(1)
                self.level_score += 1
                if self.level_score >= configvalues.SCORE_PER_LEVEL:
                    self.won_level = True
                    self.wait_tick = configvalues.WIN_DELAY
                self.resources['boom'].play()
                collided_eq.explode()
            else:
                self.score.increment_score(-1)
                self.resources['boom'].play()
                collided_eq.explode()

    def get_collision(self):
        """
        Checks if the avatar position overlaps with any equations. If more than 1 equation are hit, the one closest to
        the bottom of the screen will be returned.
        :return: Equation instance that was hit or None
        """
        avatar_pos = self.avatar.get_pos_idx()
        hit = None
        for eq in self.equations:
            if abs(eq.get_pos_idx() - avatar_pos) <= configvalues.ZAP_WIDTH and not eq.exploding:
                if hit is not None:
                    if eq.get_pos()[1] > hit.get_pos()[1]:
                        hit = eq
                else:
                    hit = eq
        return hit

    def start_level(self):
        """
        Starts a level by generating a new target value and resetting the equations based on that target.
        :return:
        """
        pygame.mixer.music.unpause()
        self.won_level = False
        self.display_win = False
        self.paused = False
        self.wait_tick = 0
        self.game_over = not self.target.next_target()
        for eq in self.equations:
            eq.reset(self.target.get_value(), self.window_w)
        self.level_score = 0

    def update(self):
        """
        Updates the state of the scene as long as it is not paused.
        :return:
        """
        if not self.paused and not self.game_over and not self.display_win:
            self.avatar.update()
            for eq in self.equations:
                should_reset = eq.update(self.top_of_floor)
                if should_reset:
                    eq.reset(self.target.get_value(), self.window_w)
        if self.won_level or self.game_over:
            self.wait_tick -= 1
            if not self.display_win and self.wait_tick <= 0:
                pygame.mixer.music.pause()
                self.resources['fanfare'].play()
                self.wait_tick = configvalues.WON_MSG_TICKS
                self.display_win = True

    def render(self, screen):
        """
        Draws the scene.
        :param screen:
        :return:
        """
        screen.fill((0, 0, 0))
        for x in range(0, self.window_w, self.floor_tile_w):
            screen.blit(self.resources['floor'], (x, self.top_of_floor))
        if self.paused:
            dirty_recs = self.render_centered(screen, self.window_w, self.window_h, self.resources['pause'])
        elif self.display_win:
            if self.wait_tick > 0:
                if self.game_over:
                    dirty_recs = self.render_centered(screen, self.window_w, self.window_h, self.resources['gameover'])
                else:
                    dirty_recs = self.render_centered(screen, self.window_w, self.window_h, self.resources['leveldone'])
            else:
                dirty_recs = self.render_centered(screen, self.window_w, self.window_h, self.resources['anykey'])
        else:
            # now render the components and get their rectangles that need to be painted
            dirty_recs = [pygame.Rect(0, self.top_of_floor - 100, self.window_w, self.top_of_floor),
                          self.avatar.render(screen, self.window_w, self.top_of_floor),
                          self.target.render(screen, self.window_w), self.score.render(screen)]

            for eq in self.equations:
                dirty_recs += eq.render(screen)

        if self.first_draw:
            self.first_draw = False
            return pygame.Rect(0, 0, self.window_w, self.window_h)
        else:
            return dirty_recs


class Equation:
    """
    Data structure for an equation. It will load the images needed to render an explosion so equation instances should be
    reused (by calling reset()) rather than constructed anew each time you want to display a new equation.
    """

    def __init__(self, font, sprite_sheet):
        self.font = font
        self.text = None
        self.correct = False
        self.pos = (0, 0)
        self.prev_pos = (0, 0)
        self.step = 1
        self.animation_index = 0
        self.ticks_per_image = 2
        self.tick = 0
        self.exploding = False
        self.has_exploded = False
        self.old_text = None
        self.pos_idx = 0
        self.delay = 0
        self.images = sprite_sheet.images_at([
            (0, 250, 110, 120),
            (0, 380, 110, 120),
            (0, 510, 110, 120),
            (0, 650, 110, 120),
        ], (128, 128, 128))

    def reset(self, target_value, screen_width):
        """
        Resets this instance by picking a new random delay (ticks before starting to fall) and starting location.
        :param target_value:
        :param screen_width:
        :return:
        """
        self.delay = random.randint(0, configvalues.MAX_DELAY)
        self.animation_index = 0
        self.ticks_per_image = 2
        self.tick = 0
        if self.exploding:
            self.has_exploded = True
            self.old_text = self.text
        self.exploding = False
        cor = random.randint(1, 10)
        if cor > configvalues.INCORRECT_ANSWER_RATIO:
            self.correct = True
        else:
            self.correct = False
        self.step = random.randint(1, configvalues.MAX_STEP)
        self.text = self.generate_equation_text(target_value)
        self.pos_idx = random.randint(1, configvalues.MAX_POS - 5)
        x_pos = (screen_width // configvalues.MAX_POS) * self.pos_idx
        self.pos = (x_pos, 0)

    def generate_equation_text(self, target_value):
        """
        Returns a text instance populated with an equation that is randomly generated based on the target value. The
        config value INCORRECT_ANS_RATIO drives how frequently incorrect equations will be generated.
        :param target_value:
        :return:
        """
        op = OPERATORS[random.randint(0, len(OPERATORS) - 1)]
        if op == '+':
            a = random.randint(0, target_value)
        elif op == '-':
            a = random.randint(0, configvalues.MAX_TARGET)
        candidates = []
        for i in range(configvalues.MAX_TARGET):
            if self.correct:
                if op == '+':
                    if a + i == target_value:
                        candidates.append(i)
                elif op == '-':
                    if a - i == target_value:
                        candidates.append(i)
            else:
                if op == '+':
                    if a + i != target_value:
                        candidates.append(i)
                elif op == '-':
                    if a - i != target_value:
                        candidates.append(i)
        if len(candidates) == 0:
            # we couldn't generate a correct equation. try again
            # TODO: do this a more elegant way
            return self.generate_equation_text(target_value)
        else:
            r = random.SystemRandom()
            r.shuffle(candidates)
            b = candidates[0]
            return self.font.render("{a} {o} {b}".format(a=a, o=op, b=b), True, (255, 0, 0))

    def explode(self):
        """
        Sets the exploding flag to True.
        :return:
        """
        self.exploding = True

    def update(self, top_of_floor):
        """
        Updates the position of the equation OR the animation frame of the explosion depending on the state of the
        exploding flag.
        :param top_of_floor:
        :return:
        """
        if self.delay <= 1 and not self.exploding:
            self.has_exploded = False
            self.prev_pos = self.pos
            self.pos = (self.pos[0], self.pos[1] + self.step)
            if self.pos[1] >= top_of_floor:
                return True
        elif self.exploding:
            self.prev_pos = self.pos
            self.tick += 1
            if self.tick > self.ticks_per_image:
                self.tick = 0
                self.animation_index += 1
                if self.animation_index >= len(self.images):
                    self.animation_index = 0
                    return True

        self.delay -= 1
        return False

    def render(self, screen):
        """
        Draws either the equation text or the explosion animation depending on the state of the exploding flag and
        returns rectangles representing both the previous and current position.
        :param screen:
        :return:
        """
        if self.delay <= 0 and not self.exploding:
            screen.blit(self.text, self.pos)
            return [pygame.Rect(self.pos[0], self.pos[1], self.text.get_width(),
                                self.text.get_height()),
                    pygame.Rect(self.prev_pos[0], self.prev_pos[1], self.text.get_width(),
                                self.text.get_height())]
        elif self.exploding:
            screen.blit(self.images[self.animation_index], (self.pos[0], self.pos[1]))
            img_w, img_h = self.images[self.animation_index].get_rect().size
            return [pygame.Rect(self.pos[0], self.pos[1], img_w, img_h),
                    pygame.Rect(self.prev_pos[0], self.prev_pos[1], self.text.get_width(),
                                self.text.get_height())]
        elif self.has_exploded:
            img_w, img_h = self.images[len(self.images) - 1].get_rect().size
            return [pygame.Rect(self.prev_pos[0], self.prev_pos[1], img_w,
                            img_h)]
        else:
            return []


    def is_correct(self):
        return self.correct


    def get_pos_idx(self):
        return self.pos_idx


    def get_pos(self):
        return self.pos


class TargetValue:
    """
    Represents the target value for which the player must find valid equations.
    """

    def __init__(self, font):
        """
        Initializes state by building list of possible values and shuffling them.
        :param font:
        """
        self.targets = list(range(0, configvalues.MAX_TARGET + 1))
        random.SystemRandom().shuffle(self.targets)
        self.text = None
        self.font = font
        self.target_idx = -1

    def next_target(self):
        """
        Updates the state with the next target value.
        :return: True if successful, False if there are no more possible values
        """
        self.target_idx += 1
        if len(self.targets) <= self.target_idx:
            return False
        self.text = self.font.render(str(self.targets[self.target_idx]), True, (0, 0, 255))
        return True

    def render(self, screen, width):
        """
        Draws the text.
        :param screen:
        :param width:
        :return:
        """
        screen.blit(self.text,
                    ((width - self.text.get_width()) // 2, self.text.get_height() + 10))
        return pygame.Rect(width - self.text.get_width(), self.text.get_height() + 20, self.text.get_width(),
                           self.text.get_height())

    def get_value(self):
        """
        Returns currently set value (or None if not set)
        :return:
        """
        if len(self.targets) <= self.target_idx:
            return None
        else:
            return self.targets[self.target_idx]


class Avatar:
    """
    Represents the player's avatar. This sprite class loads the relevant images from the sprite sheet and will reverse
    them to keep a copy facing both directions (so we don't have to do it in the render loop).
    """

    def __init__(self, sprite_sheet):
        """
        Loads images from the sprite sheet and sets initial position to the middle of the floor.
        :param sprite_sheet:
        """
        self.pos = configvalues.MAX_POS // 2
        self.animation_index = 0
        self.ticks_per_image = 2
        self.tick = 0
        self.moving = False
        self.facing_r = True
        self.jumping = False
        self.r_images = sprite_sheet.images_at(
            [(25, 100, 75, 75),
             (105, 100, 75, 75),
             (185, 100, 75, 75),
             (265, 100, 75, 75), ],
            (128, 128, 128)  # alpha color
        )
        # reverse for left images
        self.l_images = [pygame.transform.flip(i, True, False) for i in self.r_images]

        self.r_jump = sprite_sheet.images_at(
            [
                (535, 220, 75, 100),
                (615, 220, 75, 100),
                (680, 220, 75, 100),
                (755, 220, 75, 100),
            ], (128, 128, 128)
        )
        self.l_jump = [pygame.transform.flip(i, True, False) for i in self.r_jump]

    def move(self, unit):
        """
        Handles the move of the avatar either 1 unit to the left or right.
        :param unit:
        :return:
        """
        if not self.jumping:
            if unit < 0:
                self.facing_r = False
                if self.pos > 0:
                    self.pos += unit
            else:
                self.facing_r = True
                if self.pos < configvalues.MAX_POS - 1:
                    self.pos += unit
            self.moving = True

    def jump(self):
        """
        Sets the jumping flag and animation index.
        :return:
        """
        if not self.jumping:
            self.moving = True
            self.jumping = True
            self.animation_index = 0

    def update(self):
        """
        Updates the animation index for the sprite if we moved.
        :return:
        """
        if self.moving:
            self.tick += 1
            if self.tick > self.ticks_per_image:
                self.tick = 0
                self.animation_index += 1
                if self.jumping:
                    if self.animation_index >= len(self.r_jump):
                        self.animation_index = 0
                        self.jumping = False
                else:
                    self.moving = False
                    if self.animation_index >= len(self.r_images):
                        self.animation_index = 0

    def render(self, screen, screen_width, floor_height):
        """Draws the avatar and returns a rectangle the entire width of the screen."""
        # TODO: keep track of prior position so we can return a smaller rect
        x_pos = (screen_width // configvalues.MAX_POS) * self.pos
        # TODO: dynamically get sprite height?
        if self.facing_r:
            if self.jumping:
                screen.blit(self.r_jump[self.animation_index], (x_pos, floor_height - 100))
            else:
                screen.blit(self.r_images[self.animation_index], (x_pos, floor_height - 75))
        else:
            if self.jumping:
                screen.blit(self.l_jump[self.animation_index], (x_pos, floor_height - 100))
            else:
                screen.blit(self.l_images[self.animation_index], (x_pos, floor_height - 75))

    def get_pos_idx(self):
        return self.pos


class Score:
    """ Represents the player's current score."""

    def __init__(self, font):
        self.font = font
        self.text = None
        self.score = 0
        self._update()

    def increment_score(self, by_val):
        """
        Increments the score by the value passed in.
        :param by_val:
        :return:
        """
        self.score += by_val
        self._update()

    def _update(self):
        """
        Generates a text object for the current score.
        :return:
        """
        self.text = self.font.render("Score {v}".format(v=self.score), True, (255, 255, 0))

    def render(self, screen):
        screen.blit(self.text,
                    (10, 10))
        return pygame.Rect(10, 10, self.text.get_width(),
                           self.text.get_height())
