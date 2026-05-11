import pygame
import sys


from scripts.entities import PhysicsEntity, Player, Slime
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
#from scripts.clouds import Clouds
from scripts.menu import Menu
from scripts.portal import Portal
from scripts.campfire import Campfire
from scripts.boss import Boss


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ruinik")
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.display = pygame.Surface((320, 180), pygame.SRCALPHA)


        self.clock = pygame.time.Clock()
        self.zoom = 4.0
        self.hint_font = pygame.font.SysFont('Arial', 10) 
        self.boss_font = pygame.font.SysFont('Arial', 12, bold=True)
        self.boss_defeated_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.boss_defeated_timer = 0

        self.movement = [False, False]


        self.assets = { 
            'grass': load_images('tiles/grass'),
            'player': load_image('PLAYER/NATIAN.png'),
            'spawners': load_images('spawners'),
            'portal': load_images('portal'),
            'campfire': load_images('campfire'),
            'boss_spawner': load_images('boss_spawner'),
            'player_head': pygame.transform.scale(pygame.image.load('data/images/UI/PLAYER_HEAD.png').convert_alpha(), (16, 16)),
            'player_head_rune': pygame.transform.scale(pygame.image.load('data/images/UI/PLAYER_HEAD_RUNE.png').convert_alpha(), (16, 16)),
            'ui_staff': pygame.transform.scale(pygame.image.load('data/images/UI/staff.png').convert_alpha(), (16, 16)),
            'ui_sword': pygame.transform.scale(pygame.image.load('data/images/UI/sword.png').convert_alpha(), (16, 16)),
            'ui_blank': pygame.transform.scale(pygame.image.load('data/images/UI/blank.png').convert_alpha(), (16, 16)),
            'clouds': [pygame.transform.scale(pygame.transform.flip(img, True, False), (64, 32)) for img in load_images('clouds')],
            'decor': load_images('tiles/decor'),
            'large_decor':load_images('tiles/large_decor'),

            'bg_layers_back': [
                (pygame.transform.scale(pygame.image.load('data/images/maps/1.png').convert_alpha(), (320, 180)), 0.05),
                (pygame.transform.scale(pygame.image.load('data/images/maps/2.png').convert_alpha(), (320, 180)), 0.1),
                (pygame.transform.scale(pygame.image.load('data/images/maps/3.png').convert_alpha(), (320, 180)), 0.15),
                (pygame.transform.scale(pygame.image.load('data/images/maps/4.png').convert_alpha(), (320, 180)), 0.2),
            ],
            # clouds render here
            'bg_layers_front': [
                (pygame.transform.scale(pygame.image.load('data/images/maps/5.png').convert_alpha(), (320, 180)), 0.25),
                (pygame.transform.scale(pygame.image.load('data/images/maps/6.png').convert_alpha(), (320, 180)), 0.3),
                (pygame.transform.scale(pygame.image.load('data/images/maps/7.png').convert_alpha(), (320, 180)), 0.35),
            ],
            'player/idle': Animation(load_images('PLAYER/idle'), img_dur=12),
            'player/idle_left':Animation(load_images('PLAYER/idleLEFT'),img_dur=12),

            'player/run': Animation(load_images('PLAYER/run', scale = (64, 64)), img_dur=4),
            'player/run_left': Animation(load_images('PLAYER/runLEFT'), img_dur=4),

            'player/jump':Animation(load_images('PLAYER/jump'), img_dur=16),
            'player/jump_left':Animation(load_images('PLAYER/jumpLEFT'), img_dur=16),
            'player/death': Animation(load_images('PLAYER/death'), img_dur=8, loop=False),

            'staff/dash':Animation(load_images('PLAYER/dash'), img_dur=8), 
            'staff/dash_left':Animation(load_images('PLAYER/dash_left'), img_dur=8),

            'staff/idle':Animation(load_images('PLAYER/staff_mode/staff_idle'), img_dur=12),
            'staff/idle_left':Animation(load_images('PLAYER/staff_mode/staff_idle_left'), img_dur=12),

            'staff/jump':Animation(load_images('PLAYER/staff_mode/staff_jump'), img_dur=12),
            'staff/jump_left':Animation(load_images('PLAYER/staff_mode/staff_jump_left'), img_dur=12),
        
            'staff/run':Animation(load_images('PLAYER/staff_mode/staff_running'), img_dur=6),
            'staff/run_left':Animation(load_images('PLAYER/staff_mode/staff_running_left'), img_dur=6),



            'sword/idle' : Animation(load_images('PLAYER/sword_mode/sword_idle'), img_dur=12),
            'sword/idle_left' : Animation(load_images('PLAYER/sword_mode/sword_idle_left'), img_dur=12),
    
            'sword/run' : Animation([pygame.transform.flip(img, False, True) for img in load_images('PLAYER/sword_mode/sword_run')], img_dur=5),
            'sword/run_left' : Animation([pygame.transform.flip(img, False, True) for img in load_images('PLAYER/sword_mode/sword_run_left')], img_dur=5),

            'sword/attack': Animation(load_images('PLAYER/sword_mode/attack_sword'), img_dur=3, loop=False),
            'sword/attack_left': Animation(load_images('PLAYER/sword_mode/sword_attack_left'), img_dur=3, loop=False),

            'slime/idle' : Animation(load_images('slime/slime_walking_idle'), img_dur=9),
            'slime/idle_left' : Animation(load_images('slime/slime_walking_idle_left'), img_dur=9),
            'slime/attack' : Animation(load_images('slime/slime_attack'), img_dur=11),
            'slime/attack_left' : Animation(load_images('slime/slime_attack_left'), img_dur=11),
            'slime/death' : Animation(load_images('slime/slime_death'), img_dur=8, loop=False),


        

        }


       # self.clouds = Clouds(self.assets['clouds'], count = 3)

        self.player = Player(self, (180, 300), (12, 28)) #hitbox

        self.levels = ['map.json', 'map1.json']  
        self.current_level = 0

        self.tilemap = Tilemap(self, tile_size=32)
        self.tilemap.load(self.levels[self.current_level])
        self.scroll = [0, 0]
        self.ground_y = 11

        self.slimes = []
        self.portals = []
        self.campfires = []
        self.bosses = []
        for tile in self.tilemap.offgrid_tiles:
            if tile['type'] == 'spawners':
                self.slimes.append(Slime(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'portal':
                self.portals.append(Portal(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'campfire':
                self.campfires.append(Campfire(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'boss_spawner':
                self.bosses.append(Boss(self, (tile['pos'][0], tile['pos'][1])))

        sw, sh = self.screen.get_size()
        self.bg_layers_back_scaled  = [(pygame.transform.scale(img, (sw, sh)), spd) for img, spd in self.assets['bg_layers_back']]
        self.bg_layers_front_scaled = [(pygame.transform.scale(img, (sw, sh)), spd) for img, spd in self.assets['bg_layers_front']]


    def load_level(self, map_path):
        self.tilemap.load(map_path)
        self.slimes = []
        self.portals = []
        self.campfires = []
        self.bosses = []
        for tile in self.tilemap.offgrid_tiles:
            if tile['type'] == 'spawners':
                self.slimes.append(Slime(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'portal':
                self.portals.append(Portal(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'campfire':
                self.campfires.append(Campfire(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'boss_spawner':
                self.bosses.append(Boss(self, (tile['pos'][0], tile['pos'][1])))
        for tile in self.tilemap.offgrid_tiles:
            if tile['type'] == 'spawners':
                self.slimes.append(Slime(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'portal':
                self.portals.append(Portal(self, (tile['pos'][0], tile['pos'][1])))
            elif tile['type'] == 'campfire':
                self.campfires.append(Campfire(self, (tile['pos'][0], tile['pos'][1])))
        self.player.pos = [180, 300]
        self.player.velocity = [0, 0]
        self.scroll = [0, 0]
        self.portals.append(Portal(self, (180, 300), active=False))

    def run(self):
        menu = Menu(self.screen, self.display)
        menu.run()   

        while True:
            self.scroll[0] = self.player.pos[0] + self.player.size[0] / 2 - self.display.get_width() / 2
            self.scroll[1] = self.player.pos[1] + self.player.size[1] / 2 - self.display.get_height() / 2 - 40
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.display.fill((0, 0, 0, 0))

            screen_w, screen_h = self.screen.get_size()

            for layer_img, speed in self.bg_layers_back_scaled:
                offset_x = int(self.scroll[0] * speed) % screen_w
                self.screen.blit(layer_img, (-offset_x, 0))
                self.screen.blit(layer_img, (screen_w - offset_x, 0))

           # self.clouds.update()
          #  self.clouds.render(self.display, offset=(0, 0))

            for layer_img, speed in self.bg_layers_front_scaled:
                offset_x = int(self.scroll[0] * speed) % screen_w
                self.screen.blit(layer_img, (-offset_x, 0))
                self.screen.blit(layer_img, (screen_w - offset_x, 0))

            self.tilemap.render(self.display, offset= render_scroll )

            tile_size = self.tilemap.tile_size
            ground_img = self.assets['grass'][64]
            start_x = int(render_scroll[0] // tile_size) - 1
            end_x   = start_x + (self.display.get_width() // tile_size) + 2
            for x in range(start_x, end_x):
                self.display.blit(ground_img, (x * tile_size - render_scroll[0], self.ground_y * tile_size - render_scroll[1]))

            speed = 3 if self.player.mode == "staff" else 2
            self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * speed, 0))
            self.player.render(self.display, offset=render_scroll)

            if self.player.jump_hint_timer > 0:
                alpha = min(255, self.player.jump_hint_timer * 4)
                hint_surf = self.hint_font.render("can't jump in Sword mode", True, (220, 30, 30))
                hint_surf.set_alpha(alpha)
                hx = int(self.player.pos[0] - render_scroll[0] + self.player.size[0] // 2 - hint_surf.get_width() // 2)
                hy = int(self.player.pos[1] - render_scroll[1] - 12)
                self.display.blit(hint_surf, (hx, hy))

            all_clear = (all(s.dead for s in self.slimes) if self.slimes else True) and \
                        (all(b.dead for b in self.bosses) if self.bosses else True)
            self.near_portal = False
            for portal in self.portals:
                portal.update()
                if all_clear:
                    portal.render(self.display, offset=render_scroll)
                    if portal.active and self.player.rect().colliderect(portal.rect()):
                        self.near_portal = True

            for campfire in self.campfires:
                player_near = self.player.rect().colliderect(campfire.rect())
                campfire.update(player_near)
                campfire.render(self.display, offset=render_scroll)

            for boss in self.bosses[:]:
                boss.update()
                boss.render(self.display, offset=render_scroll)

                if boss.dying and not hasattr(boss, 'death_text_triggered'):
                    boss.death_text_triggered = True
                    self.boss_defeated_timer = 180

                if boss.dead:
                    self.bosses.remove(boss)
                    continue

                if self.player.attacking:
                    p = self.player
                    attack_w, attack_h = 20, 20
                    attack_x = p.pos[0] - attack_w if p.facing_left else p.pos[0] + p.size[0]
                    attack_rect = pygame.Rect(attack_x, p.pos[1] + 4, attack_w, attack_h)
                    if attack_rect.colliderect(boss.rect()):
                        boss.take_damage(300)

                if self.player.dashing > 0 and self.player.mode == "staff":
                    if id(boss) not in self.player.dash_hit and self.player.rect().colliderect(boss.rect()):
                        boss.take_damage(5)
                        self.player.dash_hit.add(id(boss))

            for boss in self.bosses:
                if not boss.dead:
                    bbar_w, bbar_h = 120, 8
                    bbar_x = self.display.get_width() // 2 - bbar_w // 2
                    bbar_y = 10
                    fill_w = int(bbar_w * (boss.hp / boss.MAX_HP))
                    pygame.draw.rect(self.display, (60, 0, 0),     (bbar_x, bbar_y, bbar_w, bbar_h))
                    pygame.draw.rect(self.display, (200, 20, 20),  (bbar_x, bbar_y, fill_w, bbar_h))
                    pygame.draw.rect(self.display, (255, 255, 255),(bbar_x, bbar_y, bbar_w, bbar_h), 1)
                    mid_x = bbar_x + bbar_w // 2
                    pygame.draw.line(self.display, (255, 220, 0), (mid_x, bbar_y - 1), (mid_x, bbar_y + bbar_h + 1), 2)
                    label = self.hint_font.render("BOSS", True, (255, 200, 200))
                    self.display.blit(label, (bbar_x + bbar_w // 2 - label.get_width() // 2, bbar_y - 8))
                    break

            if self.near_portal:
                prompt = self.hint_font.render("Press F to enter", True, (255, 255, 180))
                px = self.display.get_width() // 2 - prompt.get_width() // 2
                py = self.display.get_height() // 2 - 20
                self.display.blit(prompt, (px, py))

            for slime in self.slimes[:]:
                slime.update(self.tilemap)
                slime.render(self.display, offset=render_scroll)
                if slime.dead and slime.animation.done:
                    self.slimes.remove(slime)
                    continue

                if not slime.dead and not self.player.attacking and self.player.rect().colliderect(slime.rect()):
                    # push player away from slime
                    if self.player.rect().centerx < slime.rect().centerx:
                        self.player.pos[0] -= 1 
                    else:
                        self.player.pos[0] += 1

                if self.player.attacking:
                    p = self.player
                    attack_w = 20
                    attack_h = 20
                    if p.facing_left:
                        attack_x = p.pos[0] - attack_w
                    else:
                        attack_x = p.pos[0] + p.size[0]
                    attack_y = p.pos[1] + 4
                    attack_rect = pygame.Rect(attack_x, attack_y, attack_w, attack_h)
                    if attack_rect.colliderect(slime.rect()):
                        slime.take_damage(100)

                if (self.player.dashing > 0 and self.player.mode == "staff"
                        and not slime.dead and id(slime) not in self.player.dash_hit
                        and self.player.rect().colliderect(slime.rect())):
                    slime.take_damage(5)
                    self.player.dash_hit.add(id(slime))

            # head icon at top-left
            head_x, head_y = 4, 4
            head_img = self.assets['player_head'] if self.player.mode == "normal" else self.assets['player_head_rune']
            self.display.blit(head_img, (head_x, head_y))

            bar_w, bar_h = 60, 6
            bar_x = head_x + 16 + 3
            bar_y = head_y + (16 - bar_h) // 2
            fill_w = int(bar_w * (self.player.hp / self.player.max_hp))
            pygame.draw.rect(self.display, (80, 0, 0),    (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.display, (220, 30, 30), (bar_x, bar_y, fill_w, bar_h))
            pygame.draw.rect(self.display, (255, 255, 255),(bar_x, bar_y, bar_w, bar_h), 1)

            if self.player.mode == "staff":
                self.display.blit(self.assets['ui_staff'], (head_x, head_y + 16 + 2))
                if self.player.dash_cooldown > 0:
                    icon_x = head_x
                    icon_y = head_y + 16 + 2
                    icon_size = 16
                    cd_ratio = self.player.dash_cooldown / 150 
                    overlay_h = int(icon_size * cd_ratio)
                    overlay = pygame.Surface((icon_size, overlay_h), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 160))
                    self.display.blit(overlay, (icon_x, icon_y))
            elif self.player.mode == "sword":
                self.display.blit(self.assets['ui_sword'], (head_x, head_y + 16 + 2))
                if self.player.attack_cooldown > 0:
                    icon_x = head_x
                    icon_y = head_y + 16 + 2
                    icon_size = 16
                    cd_ratio = self.player.attack_cooldown / 40 
                    overlay_h = int(icon_size * cd_ratio)
                    overlay = pygame.Surface((icon_size, overlay_h), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 160))
                    self.display.blit(overlay, (icon_x, icon_y))
            else:
                self.display.blit(self.assets['ui_blank'], (head_x, head_y + 16 + 2))
                if self.player.mode_cooldown > 0:
                    icon_x = head_x
                    icon_y = head_y + 16 + 2
                    icon_size = 16
                    cd_ratio = self.player.mode_cooldown / 90 
                    overlay_h = int(icon_size * cd_ratio)
                    overlay = pygame.Surface((icon_size, overlay_h), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 160))
                    self.display.blit(overlay, (icon_x, icon_y))





            if self.boss_defeated_timer > 0:
                self.boss_defeated_timer -= 1
                bd_text = self.boss_defeated_font.render("Boss defeated", True, (255, 215, 0)) 
                outline_color = (0, 0, 0)
                px = self.display.get_width() // 2 - bd_text.get_width() // 2
                py = self.display.get_height() // 2 - bd_text.get_height() // 2 - 20
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_surf = self.boss_defeated_font.render("Boss defeated", True, outline_color)
                    self.display.blit(outline_surf, (px + dx, py + dy))
                self.display.blit(bd_text, (px, py))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.sword_attack()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump()

                    
                    if event.key == pygame.K_LSHIFT:
                        self.player.dash()

                    if event.key == pygame.K_e:
                        self.player.toggle_mode()
                
                    if event.key == pygame.K_q:
                        self.player.toggle_sword_mode()

                    if event.key == pygame.K_f:
                        if self.near_portal:
                            self.current_level = (self.current_level + 1) % len(self.levels)
                            self.load_level(self.levels[self.current_level])
                

                    
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                        


            scaled_width = int(self.display.get_width() * self.zoom)
            scaled_height = int(self.display.get_height() * self.zoom)

            scaled_display = pygame.transform.scale(self.display, (scaled_width, scaled_height))

            self.screen.blit(scaled_display, (0, 0))            

            pygame.display.update()
            self.clock.tick(60)

Game().run()