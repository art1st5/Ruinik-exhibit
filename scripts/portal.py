import pygame
from scripts.utils import Animation, load_images


class Portal:
    def __init__(self, game, pos, active=True):
        self.game = game
        self.pos = list(pos)
        self.active = active  # False = decorative only, no interaction
        self.animation = Animation(load_images('portal'), img_dur=8, loop=True)
        img = self.animation.img()
        self.size = (img.get_width(), img.get_height())

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self):
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        # slightly dimmed if inactive
        if not self.active:
            img = img.copy()
            img.set_alpha(140)
        surf.blit(img, (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])))
