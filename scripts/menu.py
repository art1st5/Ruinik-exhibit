import pygame
import sys

BASE_PATH = 'data/images/'

class Menu:
    MAIN     = 'main'
    OPTIONS  = 'options'
    KEYBINDS = 'keybinds'

    KEYBIND_LINES = [
        ("A / D",         "Move Left / Right"),
        ("SPACE",         "Jump"),
        ("E",             "Toggle Staff Mode"),
        ("Q",             "Toggle Sword Mode"),
        ("LEFT CLICK",    "Sword Attack  (Sword Mode)"),
        ("LEFT SHIFT",    "Dash  (Staff Mode)"),
        ("F",             "Enter Portal"),
        ("H",             "Toggle Hitboxes  (Debug)"),
        ("ESC",           "Pause / Resume"),
    ]

    def __init__(self, screen, display):
        self.screen  = screen  
        self.display = display  

        sw, sh = screen.get_width(), screen.get_height()

        self.bg = pygame.image.load(BASE_PATH + 'menu/MAIN_MENU.png').convert()
        self.bg = pygame.transform.scale(self.bg, (sw, sh))

        self.logo_raw = pygame.image.load(BASE_PATH + 'menu/logo-sample(1).png').convert_alpha()
        lw, lh = self.logo_raw.get_size()
        max_w  = int(sw * 0.60)
        scale  = min(max_w / lw, 1.0)
        self.logo = pygame.transform.smoothscale(
            self.logo_raw, (int(lw * scale), int(lh * scale))
        )

        self.state    = self.MAIN
        self.selected = 0
        self.items    = ['Start Game', 'Options', 'Keybinds', 'Exit']

        self.font_item   = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 80)
        self.font_credit = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 20)
        self.font_hint   = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 18)

    def _draw_main(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx = sw // 2

        self.screen.blit(self.bg, (0, 0))

        logo_rect = self.logo.get_rect(centerx=cx, top=40)
        self.screen.blit(self.logo, logo_rect)

        start_y = logo_rect.bottom + 40
        spacing = 70

        for i, label in enumerate(self.items):
            color  = (210,184, 115) if i == self.selected else (177,130,0)
            prefix = '> ' if i == self.selected else '  '
            text   = self.font_item.render(prefix + label, True, color)
            rect   = text.get_rect(center=(cx, start_y + i * spacing))
            self.screen.blit(text, rect)

        credit = self.font_credit.render(
            'A game by Prado, De la Cruz, Cabardo, Ladislao, Marzal from 12-ITEM-01',
            True, (0, 69, 41)
        )
        self.screen.blit(credit, (10, sh - credit.get_height() - 10))

    def _draw_options(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx, cy = sw // 2, sh // 2

        self.screen.blit(self.bg, (0, 0))

        msg  = self.font_item.render('Nothing to see here yet', True, (255, 255, 255))
        hint = self.font_hint.render('Press ESC to go back', True, (255, 255, 255))
        self.screen.blit(msg,  msg.get_rect(center=(cx, cy - 20)))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 20)))

    def _draw_keybinds(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx = sw // 2

        self.screen.blit(self.bg, (0, 0))

        # dark semi-transparent panel
        panel_w, panel_h = 600, 520
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        self.screen.blit(panel, (cx - panel_w // 2, sh // 2 - panel_h // 2))

        title = self.font_item.render('Keybinds', True, (255, 220, 50))
        self.screen.blit(title, title.get_rect(center=(cx, sh // 2 - panel_h // 2 + 40)))

        font_kb = pygame.font.Font('fonts/PixelPurl.ttf', 22)
        row_h = 38
        start_y = sh // 2 - panel_h // 2 + 110
        key_x   = cx - 260
        desc_x  = cx - 60

        for i, (key, desc) in enumerate(self.KEYBIND_LINES):
            y = start_y + i * row_h
            key_surf  = font_kb.render(key,  True, (255, 220, 80))
            desc_surf = font_kb.render(desc, True, (220, 220, 220))
            self.screen.blit(key_surf,  (key_x,  y))
            self.screen.blit(desc_surf, (desc_x, y))

        hint = self.font_hint.render('Press ESC to go back', True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(center=(cx, sh // 2 + panel_h // 2 - 20)))

    def run(self):
        clock  = pygame.time.Clock()
        sw     = self.screen.get_width()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.state == self.MAIN:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.selected = (self.selected - 1) % len(self.items)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.selected = (self.selected + 1) % len(self.items)
                        elif event.key == pygame.K_RETURN:
                            if self.selected == 0: return 'start'
                            elif self.selected == 1: self.state = self.OPTIONS
                            elif self.selected == 2: self.state = self.KEYBINDS
                            elif self.selected == 3: pygame.quit(); sys.exit()
                    elif self.state in (self.OPTIONS, self.KEYBINDS):
                        if event.key == pygame.K_ESCAPE:
                            self.state = self.MAIN

                if event.type == pygame.MOUSEMOTION and self.state == self.MAIN:
                    mx, my = event.pos
                    cx = sw // 2
                    logo_h  = self.logo.get_height()
                    start_y = 40 + logo_h + 60
                    spacing = 50
                    for i in range(len(self.items)):
                        if abs(my - (start_y + i * spacing)) < 20:
                            self.selected = i

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == self.MAIN:
                        if self.selected == 0: return 'start'
                        elif self.selected == 1: self.state = self.OPTIONS
                        elif self.selected == 2: self.state = self.KEYBINDS
                        elif self.selected == 3: pygame.quit(); sys.exit()

            if self.state == self.MAIN:
                self._draw_main()
            elif self.state == self.OPTIONS:
                self._draw_options()
            else:
                self._draw_keybinds()

            pygame.display.update()
            clock.tick(60)
