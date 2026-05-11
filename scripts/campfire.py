import pygame
import os
from scripts.utils import Animation

BASE_PATH = 'data/images/'


def load_campfire_images():
    folder = BASE_PATH + 'campfire/'
    files = sorted(os.listdir(folder), key=lambda f: int(f.split('_')[0]))
    images = []
    for f in files:
        img = pygame.image.load(folder + f).convert_alpha()
        images.append(img)
    return images


class Campfire:
    HEAL_INTERVAL = 60  
    HEAL_AMOUNT   = 15

    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.animation = Animation(load_campfire_images(), img_dur=4, loop=True)
        img = self.animation.img()
        self.size = (img.get_width(), img.get_height())
        self.heal_timer = 0

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, player_near):
        self.animation.update()
        if player_near:
            self.heal_timer += 1
            if self.heal_timer >= self.HEAL_INTERVAL:
                self.heal_timer = 0
                p = self.game.player
                p.hp = min(p.max_hp, p.hp + self.HEAL_AMOUNT)
        else:
            self.heal_timer = 0

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])))
