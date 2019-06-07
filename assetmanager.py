import os

import pygame


class AssetManager:
    """
    Utility to manage game assets.
    """

    def __init__(self, resource_dir="resources"):
        self.dir = resource_dir
        self.resources = {}

    def get(self, key):
        """
        Gets a resource by key. If the key doesn't exist, this will raise a KeyError.
        :param key:
        :return:
        """
        return self.resources[key]

    def load_sound(self, key, file_name, vol=1.0):
        """
        Loads a sound file and sets the volume.
        :param key:
        :param file_name:
        :param vol:
        :return:
        """
        self.resources[key] = pygame.mixer.Sound(os.path.join(self.dir, file_name))
        self.resources[key].set_volume(vol)

    def load_image(self, key, file_name, color_key=None):
        """
        Loads an image and sets the alpha color key if specified.
        :param key:
        :param file_name:
        :param color_key:
        :return:
        """
        try:
            self.resources[key] = pygame.image.load(os.path.join(self.dir, file_name))
            if color_key is not None:
                if color_key is -1:
                    color_key = self.resources[key].get_at((0, 0))
                self.resources[key].set_colorkey(color_key, pygame.RLEACCEL)
                self.resources[key] = self.resources[key].convert_alpha()
            else:
                self.resources[key] = self.resources[key].convert()
        except pygame.error:
            print("Unable to load image {img} ".format(img=file_name))
            raise SystemExit

    def load_sprite_sheet(self, key, file_name):
        """
        Loads an image as a SpriteSheet
        :param key:
        :param file_name:
        :return:
        """
        try:
            self.resources[key] = SpriteSheet(pygame.image.load(os.path.join(self.dir, file_name)).convert_alpha())
        except pygame.error:
            print("Unable to load image {img} as sprite sheet".format(img=file_name))
            raise SystemExit

    def register_resource(self, key, value):
        """
        Registers a resource created elsewhere with this asset manager.
        :param key:
        :param value:
        :return:
        """
        self.resources[key] = value

    def unload_resource(self, key):
        """
        Removes a resource from the internal map.
        :param key:
        :return:
        """
        if key in self.resources:
            del self.resources[key]

    def __getitem__(self, item):
        """
        Accessor so you can use the assetmanager isntance like a dictionary (i.e. am['key'] )
        :param item:
        :return:
        """
        return self.resources[item]


class SpriteSheet:
    """
    Class with helper functions for retrieving sets of sprites from a larger image containing a sprite sheet.
    """

    def __init__(self, image):
        self.sheet = image

    def image_at(self, rectangle, color_key=None):
        """
        Loads image from x,y,x+offset,y+offset
        :param rectangle:
        :param color_key:
        :return:
        """
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if color_key is not None:
            if color_key is -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)
        return image

    def images_at(self, rects, color_key=None):
        """
        Loads multiple images
        :param rects: list of rectangles within the sheet
        :param color_key:
        :return:
        """
        return [self.image_at(rect, color_key) for rect in rects]
