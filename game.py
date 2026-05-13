import pygame
import sys


from scripts.entities import PhysicsEntity, Player, Slime
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.menu import Menu
from scripts.portal import Portal
from scripts.campfire import Campfire
from scripts.boss import Boss


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ruinik")
        self.screen = pygame.display.set_mode((1280, 720))#, pygame.FULLSCREEN)
        self.running = True
        self.display = None  

        self.clock = pygame.time.Clock()
        self.zoom = 5.5
        self.level_zoom = [5.5 , 2.5] 
        self._update_display_surface()
        self.show_hitboxes = False
        self.barrier_warning_timer = 0  
        self.hint_font = pygame.font.Font('fonts/PixelPurl.TTF', 12) 
        self.boss_font = pygame.font.Font('fonts/PixelPurl.ttf', 12)
        self.boss_defeated_font = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 16)
        self.boss_defeated_timer = 0
        
        self.death_font = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 64)
        self.option_font = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 32)
        self.pause_font = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 28)

        self.paused = False
        pause_btn_raw = pygame.image.load('data/images/UI/pause.png').convert_alpha()
        self.pause_btn_img = pygame.transform.scale(pause_btn_raw, (48, 48))

        self.movement = [False, False]


        self.assets = { 
            'grass': load_images('tiles/grass'),
            'castle': load_images('tiles/castle', scale=(32, 32)),
            'walls': load_images('tiles/walls', scale = (32,32)),
            'player': load_image('PLAYER/NATIAN.png'),
            'spawners': load_images('spawners'),
            'portal': load_images('portal'),
            'campfire': load_images('campfire'),
            'boss_spawner': load_images('boss_spawner'),
            'player_head': pygame.transform.scale(pygame.image.load('data/images/UI/PLAYER_HEAD.png').convert_alpha(), (16, 16)),
            'hit_effect': pygame.image.load('data/images/PLAYER/HIT.png').convert_alpha(),
            'player_head_rune': pygame.transform.scale(pygame.image.load('data/images/UI/PLAYER_HEAD_RUNE.png').convert_alpha(), (16, 16)),
            'ui_staff': pygame.transform.scale(pygame.image.load('data/images/UI/staff.png').convert_alpha(), (16, 16)),
            'ui_sword': pygame.transform.scale(pygame.image.load('data/images/UI/sword.png').convert_alpha(), (16, 16)),
            'ui_blank': pygame.transform.scale(pygame.image.load('data/images/UI/blank.png').convert_alpha(), (16, 16)),
            'clouds': [pygame.transform.scale(pygame.transform.flip(img, True, False), (64, 32)) for img in load_images('clouds')],
            'decor': load_images('tiles/decor'),
            'large_decor':load_images('tiles/large_decor'),

            'bg_layers_back': [
                (pygame.transform.scale(pygame.image.load('data/images/maps/0.png').convert_alpha(), (320, 180)), 0.0),
                (pygame.transform.scale(pygame.image.load('data/images/maps/1.png').convert_alpha(), (320, 180)), 0.05),
                (pygame.transform.scale(pygame.image.load('data/images/maps/2.png').convert_alpha(), (320, 180)), 0.1),
            ],
            'bg_layers_front': [
                (pygame.transform.scale(pygame.image.load('data/images/maps/3.png').convert_alpha(), (320, 180)), 0.2),
                (pygame.transform.scale(pygame.image.load('data/images/maps/4.png').convert_alpha(), (320, 180)), 0.3),
            ],
            # map_home layers for map.json (level 0)
            'bg_home_back': [
                (pygame.transform.scale(pygame.image.load('data/images/map_home/0.png').convert_alpha(), (320, 180)), 0.0),
                (pygame.transform.scale(pygame.image.load('data/images/map_home/1.png').convert_alpha(), (320, 180)), 0.05),
                (pygame.transform.scale(pygame.image.load('data/images/map_home/2.png').convert_alpha(), (320, 180)), 0.1),
                (pygame.transform.scale(pygame.image.load('data/images/map_home/3.png').convert_alpha(), (320, 180)), 0.15),
            ],
            'bg_home_front': [
                (pygame.transform.scale(pygame.image.load('data/images/map_home/4.png').convert_alpha(), (320, 180)), 0.2),
                (pygame.transform.scale(pygame.image.load('data/images/map_home/5.png').convert_alpha(), (320, 180)), 0.25),
                (pygame.transform.scale(pygame.image.load('data/images/map_home/6.png').convert_alpha(), (320, 180)), 0.3),
            ],
            'player/idle': Animation(load_images('PLAYER/idle'), img_dur=12),
            'player/idle_left':Animation(load_images('PLAYER/idleLEFT'),img_dur=12),

            'player/run': Animation(load_images('PLAYER/run'), img_dur=4),
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

            'slime/idle' : Animation(load_images('slime/slime_walking_idle'), img_dur=5),
            'slime/idle_left' : Animation(load_images('slime/slime_walking_idle_left'), img_dur=5),
            'slime/attack' : Animation(load_images('slime/slime_attack'), img_dur=8),
            'slime/attack_left' : Animation(load_images('slime/slime_attack_left'), img_dur=8),
            'slime/death' : Animation(load_images('slime/slime_death'), img_dur= 5, loop=False),


        

        }



        self.player = Player(self, (180, 200), (12, 28)) 

        self.levels = ['map.json', 'map1.json']  
        self.current_level = 0
        self.level_spawns = [(180, 300), (180, 160)]  

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
        self.bg_home_back_scaled  = [(pygame.transform.scale(img, (sw, sh)), spd) for img, spd in self.assets['bg_home_back']]
        self.bg_home_front_scaled = [(pygame.transform.scale(img, (sw, sh)), spd) for img, spd in self.assets['bg_home_front']]
        self.clouds = Clouds(self.assets['clouds'], count = 3)

        self._set_bg_for_level()



    def _play_boss_transform_cutscene(self, boss):
        """Zoom into boss, show dialogue, zoom back out."""
        clock = pygame.time.Clock()
        sw, sh = self.screen.get_size()
        dialogue_font = pygame.font.Font('fonts/PixelPurl.ttf', 50)

        ZOOM_IN_FRAMES  = 70
        HOLD_FRAMES     = 90   
        ZOOM_OUT_FRAMES = 100
        TARGET_ZOOM     = self.zoom * 3.0
        DIALOGUE        = "ENOUGH GAMES!!"

        def render_frame(current_zoom, text_alpha):
            # centre camera on boss
            boss_cx = boss.pos[0] + boss.size[0] // 2
            boss_cy = boss.pos[1] + boss.size[1] // 2
            scroll_x = boss_cx - self.display.get_width() // 2
            scroll_y = boss_cy - self.display.get_height() // 2
            rs = (int(scroll_x), int(scroll_y))

            self.display.fill((0, 0, 0, 0))
            for layer_img, speed in self.active_bg_back:
                ox = int(scroll_x * speed) % sw
                self.screen.blit(layer_img, (-ox, 0))
                self.screen.blit(layer_img, (sw - ox, 0))
            for layer_img, speed in self.active_bg_front:
                ox = int(scroll_x * speed) % sw
                self.screen.blit(layer_img, (-ox, 0))
                self.screen.blit(layer_img, (sw - ox, 0))
            self.tilemap.render(self.display, offset=rs)
            boss.render(self.display, offset=rs)

            scaled_w = int(self.display.get_width() * current_zoom)
            scaled_h = int(self.display.get_height() * current_zoom)
            scaled = pygame.transform.scale(self.display, (scaled_w, scaled_h))
            bx = (sw - scaled_w) // 2
            by = (sh - scaled_h) // 2
            self.screen.blit(scaled, (bx, by))

            if text_alpha > 0:
                txt = dialogue_font.render(DIALOGUE, True, (165,6,54))
                txt.set_alpha(text_alpha)
                self.screen.blit(txt, txt.get_rect(center=(sw // 2, sh // 2 + 200)))

            pygame.display.update()

        # suppress hurt flash during cutscene
        saved_hurt = boss.hurt_cooldown
        boss.hurt_cooldown = 0

        # zoom in
        for f in range(ZOOM_IN_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            t = f / ZOOM_IN_FRAMES
            t_e = 1 - (1 - t) ** 2
            render_frame(self.zoom + (TARGET_ZOOM - self.zoom) * t_e, 0)
            clock.tick(60)

        # hold with dialogue
        for f in range(HOLD_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            alpha = min(255, f * 10)
            render_frame(TARGET_ZOOM, alpha)
            clock.tick(60)

        # zoom out
        for f in range(ZOOM_OUT_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            t = f / ZOOM_OUT_FRAMES
            t_e = 1 - (1 - t) ** 2
            alpha = max(0, 255 - f * (255 // ZOOM_OUT_FRAMES))
            render_frame(TARGET_ZOOM + (self.zoom - TARGET_ZOOM) * t_e, alpha)
            clock.tick(60)

        # restore hurt cooldown
        boss.hurt_cooldown = saved_hurt

    def _set_bg_for_level(self):
        if self.current_level == 0:
            self.active_bg_back  = self.bg_home_back_scaled
            self.active_bg_front = self.bg_home_front_scaled
        else:
            self.active_bg_back  = self.bg_layers_back_scaled
            self.active_bg_front = self.bg_layers_front_scaled

    def _update_display_surface(self):
        sw, sh = self.screen.get_size()
        dw = int(sw / self.zoom)
        dh = int(sh / self.zoom)
        self.display = pygame.Surface((dw, dh), pygame.SRCALPHA)

    def restart_game(self):
        self.player = Player(self, (180, 160), (12, 28))
        self.current_level = 0
        self.movement = [False, False]
        self.zoom = self.level_zoom[0]
        self._update_display_surface()
        self.load_level(self.levels[self.current_level])

    def load_level(self, map_path):
        self.tilemap.load(map_path)
        self.zoom = self.level_zoom[self.current_level]
        self._update_display_surface()
        self._set_bg_for_level()
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
        self.player.pos = list(self.level_spawns[self.current_level])
        self.player.velocity = [0, 0]
        self.scroll = [0, 0]

    def run(self):
        menu = Menu(self.screen, self.display)
        menu.run()

        from scripts.cutscene import Cutscene
        Cutscene(self.screen).run()

    
        ZOOM_START  = self.zoom * 2  
        ZOOM_END    = self.zoom      
        ZOOM_FRAMES = 130    

        for f in range(ZOOM_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            t = f / ZOOM_FRAMES
            t_eased = 1 - (1 - t) ** 5
            current_zoom = ZOOM_START + (ZOOM_END - ZOOM_START) * t_eased

            # render one game frame at current zoom
            self.scroll[0] = self.player.pos[0] + self.player.size[0] / 2 - self.display.get_width() / 2
            self.scroll[1] = self.player.pos[1] + self.player.size[1] / 2 - self.display.get_height() / 2 - 40
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            screen_w, screen_h = self.screen.get_size()

            for layer_img, speed in self.active_bg_back:
                offset_x = int(self.scroll[0] * speed) % screen_w
                self.screen.blit(layer_img, (-offset_x, -50))
                self.screen.blit(layer_img, (screen_w - offset_x, 0))
            for layer_img, speed in self.active_bg_front:
                offset_x = int(self.scroll[0] * speed) % screen_w
                self.screen.blit(layer_img, (-offset_x, -50))
                self.screen.blit(layer_img, (screen_w - offset_x, 0))

            self.tilemap.render(self.display, offset=render_scroll)

            scaled_w = int(self.display.get_width() * current_zoom)
            scaled_h = int(self.display.get_height() * current_zoom)
            scaled = pygame.transform.scale(self.display, (scaled_w, scaled_h))
            blit_x = (screen_w - scaled_w) // 2
            blit_y = (screen_h - scaled_h) // 2
            self.screen.blit(scaled, (blit_x, blit_y))

            pygame.display.update()
            self.clock.tick(60)

        while True:
            self.scroll[0] = self.player.pos[0] + self.player.size[0] / 2 - self.display.get_width() / 2
            self.scroll[1] = self.player.pos[1] + self.player.size[1] / 2 - self.display.get_height() / 2 - 40
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.display.fill((0, 0, 0, 0))

            screen_w, screen_h = self.screen.get_size()

            for layer_img, speed in self.active_bg_back:
                offset_x = int(self.scroll[0] * speed) % screen_w
                self.screen.blit(layer_img, (-offset_x, 0))
                self.screen.blit(layer_img, (screen_w - offset_x, 0))

            for layer_img, speed in self.active_bg_front:
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

            speed = 4 if self.player.mode == "staff" else 3
  
            self.player.p2_boss_nearby = any(
                not b.dead and b.phase == 2 for b in self.bosses
            )
            if not self.paused:
                self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * speed, 0))

            if self.player.jump_hint_timer > 0:
                alpha = min(255, self.player.jump_hint_timer * 4)
                hint_surf = self.hint_font.render("can't jump in Sword mode", True, (220, 30, 30))
                hint_surf.set_alpha(alpha)
                hx = int(self.player.pos[0] - render_scroll[0] + self.player.size[0] // 2 - hint_surf.get_width() // 2)
                hy = int(self.player.pos[1] - render_scroll[1] - 12)
                self.display.blit(hint_surf, (hx, hy))

            # barrier warning — only on map1
            if self.current_level == 1:
                if self.player.hp / self.player.max_hp <= 0.25 and not self.player.dead:
                    if self.barrier_warning_timer == 0:
                        self.barrier_warning_timer = 180
                    self.barrier_warning_timer = max(self.barrier_warning_timer, 1)
                else:
                    if self.barrier_warning_timer > 0:
                        self.barrier_warning_timer -= 1

                if self.barrier_warning_timer > 0:
                    alpha = min(255, self.barrier_warning_timer * 4)
                    warn_surf = self.hint_font.render("No escape!", True, (255, 60, 60))
                    warn_surf.set_alpha(alpha)
                    wx = int(self.player.pos[0] - render_scroll[0] + self.player.size[0] // 2 - warn_surf.get_width() // 2)
                    wy = int(self.player.pos[1] - render_scroll[1] - 22)
                    self.display.blit(warn_surf, (wx, wy))

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

            self.player.render(self.display, offset=render_scroll)

            if self.player.hurt_cooldown > 0:
                hit_img = self.assets['hit_effect'].copy()
                white = pygame.Surface(hit_img.get_size(), pygame.SRCALPHA)
                for x in range(hit_img.get_width()):
                    for y in range(hit_img.get_height()):
                        a = hit_img.get_at((x, y))[3]
                        if a > 0:
                            white.set_at((x, y), (255, 255, 255, a))
                hit_img = white
                hit_img.set_alpha(int(255 * (self.player.hurt_cooldown / 60)))
                hit_img = pygame.transform.scale(hit_img, (32, 32))
                p = self.player
                if p.mode == "sword" and p.action in ("idle", "idle_left"):
                    aoff = (-17, -9)
                elif p.mode == "sword" and p.action in ("attack", "attack_left"):
                    aoff = (-40, -22)
                else:
                    aoff = p.anim_offset
                hx = int(p.pos[0] - render_scroll[0] + aoff[0])
                hy = int(p.pos[1] - render_scroll[1] + aoff[1])
                self.display.blit(hit_img, (hx, hy))

            for boss in self.bosses[:]:
                boss.update() if not self.paused else None
                boss.render(self.display, offset=render_scroll)

                if boss.transform_cutscene:
                    boss.transform_cutscene = False
                    self._play_boss_transform_cutscene(boss)

                if boss.dead:
                    self.bosses.remove(boss)
                    continue

                if self.player.attacking:
                    p = self.player
                    attack_w, attack_h = 30, 30
                    attack_x = p.pos[0] - attack_w if p.facing_left else p.pos[0] + p.size[0]
                    attack_rect = pygame.Rect(attack_x, p.pos[1] - attack_h + p.size[1], attack_w, attack_h)
                    if attack_rect.colliderect(boss.rect()):
                        dmg = 80 if boss.phase == 2 else 40
                        boss.take_damage(dmg)

                if self.player.dashing > 0 and self.player.mode == "staff":
                    if id(boss) not in self.player.dash_hit and self.player.rect().colliderect(boss.rect()):
                        dmg = 30 if boss.phase == 2 else 60
                        boss.take_damage(dmg)
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
                    label = self.hint_font.render("ROLVAN", False, (255, 255 , 255))
                    self.display.blit(label, (bbar_x + bbar_w // 2 - label.get_width() // 2, bbar_y - 8))
                    break

            if self.near_portal:
                prompt = self.hint_font.render("Press F to enter", True, (255, 255, 180))
                px = self.display.get_width() // 2 - prompt.get_width() // 2
                py = self.display.get_height() // 2 - 20
                self.display.blit(prompt, (px, py))

            for slime in self.slimes[:]:
                if not self.paused:
                    slime.update(self.tilemap)
                slime.render(self.display, offset=render_scroll)
                if slime.dead and slime.animation.done:
                    self.slimes.remove(slime)
                    continue
                
                if self.player.attacking and not slime.dead:
                    p = self.player
                    attack_w = 20
                    attack_h = 20   
                    if p.facing_left:
                        attack_x = p.pos[0] - attack_w
                    else:
                        attack_x = p.pos[0] + p.size[0]
                    attack_rect = pygame.Rect(attack_x, p.pos[1], attack_w, attack_h)
                    if attack_rect.colliderect(slime.rect()):
                        slime.take_damage(10)

                if (self.player.dashing > 0 and self.player.mode == "staff"
                        and not slime.dead and id(slime) not in self.player.dash_hit
                        and self.player.rect().colliderect(slime.rect())):
                    slime.take_damage(5)
                    self.player.dash_hit.add(id(slime))

            if self.show_hitboxes:
                def draw_hitbox(rect, color):
                    dx = rect.x - render_scroll[0]
                    dy = rect.y - render_scroll[1]
                    pygame.draw.rect(self.display, color, (dx, dy, rect.width, rect.height), 1)

                draw_hitbox(self.player.rect(), (0, 255, 0))        # player — green

                for slime in self.slimes:
                    if not slime.dead:
                        draw_hitbox(slime.rect(), (255, 165, 0))    # slimes — orange
                        if slime.action in ('attack', 'attack_left'):
                            draw_hitbox(slime.attack_rect(), (255, 80, 0))  # slime attack — dark orange

                for boss in self.bosses:
                    if not boss.dead:
                        draw_hitbox(boss.rect(), (255, 0, 0))       # boss body — red
                        ar = boss.attack_rect()
                        if ar:
                            draw_hitbox(ar, (255, 0, 255))          # boss melee attack — magenta
                        sr = boss.spcl_rect()
                        if sr:
                            draw_hitbox(sr, (255, 100, 0))          # boss spcl attack — orange

                # player attack rect
                if self.player.attacking:
                    p = self.player
                    attack_w, attack_h = 20, 25
                    if p.facing_left:
                        attack_x = p.pos[0] - attack_w
                    else:
                        attack_x = p.pos[0] + p.size[0]
                    draw_hitbox(pygame.Rect(attack_x, p.pos[1] - attack_h + p.size[1], attack_w, attack_h), (255, 255, 0))  # sword — yellow

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
                bd_text = self.boss_defeated_font.render("Boss defeated", False, (255, 215, 0)) 
                outline_color = (0, 0, 0)
                px = self.display.get_width() // 2 - bd_text.get_width() // 2
                py = self.display.get_height() // 2 - bd_text.get_height() // 2 - 20
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_surf = self.boss_defeated_font.render("Boss defeated", True, outline_color)
                    self.display.blit(outline_surf, (px + dx, py + dy))
                self.display.blit(bd_text, (px, py))

            # pause button — top right of screen
            screen_w, screen_h = self.screen.get_size()
            pause_btn_rect = pygame.Rect(screen_w - 58, 10, 48, 48)

            # pause menu overlay
            if self.paused:
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, (0, 0))

                cx = screen_w // 2
                cy = screen_h // 2
                mx, my = pygame.mouse.get_pos()
                gap = 55

                for i, label in enumerate(["Resume", "Restart Level", "Menu"]):
                    y = cy - gap + i * gap
                    color = (255, 220, 80) if pygame.Rect(cx - 100, y - 20, 200, 40).collidepoint(mx, my) else (255, 255, 255)
                    txt = self.pause_font.render(label, True, color)
                    self.screen.blit(txt, txt.get_rect(center=(cx, y)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.player.dead:
                            screen_w, screen_h = self.screen.get_size()
                            restart_rect = pygame.Rect(screen_w//2 - 100, screen_h//2 + 20, 200, 40)
                            menu_rect    = pygame.Rect(screen_w//2 - 100, screen_h//2 + 80, 200, 40)
                            if restart_rect.collidepoint(mx, my):
                                self.restart_game()
                            elif menu_rect.collidepoint(mx, my):
                                main_menu = Menu(self.screen, self.display)
                                main_menu.run()
                            continue

                        # pause button click
                        if pause_btn_rect.collidepoint(mx, my):
                            self.paused = not self.paused
                            continue

                        # pause menu clicks
                        if self.paused:
                            cx = screen_w // 2
                            cy = screen_h // 2
                            gap = 55
                            labels = ["Resume", "Restart Level", "Menu"]
                            for i, label in enumerate(labels):
                                y = cy - gap + i * gap
                                if pygame.Rect(cx - 100, y - 20, 200, 40).collidepoint(mx, my):
                                    if label == "Resume":
                                        self.paused = False
                                    elif label == "Restart Level":
                                        self.paused = False
                                        self.restart_game()
                                    elif label == "Menu":
                                        self.paused = False
                                        main_menu = Menu(self.screen, self.display)
                                        main_menu.run()
                            continue

                if self.paused:
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.sword_attack()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
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

                    if event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes

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

            # pause button and menu — always on top of everything
            self.screen.blit(self.pause_btn_img, (pause_btn_rect.x, pause_btn_rect.y))
            if self.paused:
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, (0, 0))
                cx = screen_w // 2
                cy = screen_h // 2
                mx, my = pygame.mouse.get_pos()
                gap = 55
                for i, label in enumerate(["Resume", "Restart Level", "Menu"]):
                    y = cy - gap + i * gap
                    color = (255, 220, 80) if pygame.Rect(cx - 100, y - 20, 200, 40).collidepoint(mx, my) else (255, 255, 255)
                    txt = self.pause_font.render(label, True, color)
                    self.screen.blit(txt, txt.get_rect(center=(cx, y)))
                self.screen.blit(self.pause_btn_img, (pause_btn_rect.x, pause_btn_rect.y))

            if self.player.dead:
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))

                screen_w, screen_h = self.screen.get_size()

                death_text = self.death_font.render("YOU DIED", True, (220, 20, 20))
                self.screen.blit(death_text, (screen_w//2 - death_text.get_width()//2, screen_h//2 - 80))

                mx, my = pygame.mouse.get_pos()
                restart_rect = pygame.Rect(screen_w//2 - 100, screen_h//2 + 20, 200, 40)
                menu_rect    = pygame.Rect(screen_w//2 - 100, screen_h//2 + 80, 200, 40)

                r_color = (255, 255, 255) if restart_rect.collidepoint((mx, my)) else (180, 180, 180)
                m_color = (255, 255, 255) if menu_rect.collidepoint((mx, my))    else (180, 180, 180)

                restart_text = self.option_font.render("Restart", True, r_color)
                menu_text    = self.option_font.render("Menu",    True, m_color)

                self.screen.blit(restart_text, (screen_w//2 - restart_text.get_width()//2, screen_h//2 + 20))
                self.screen.blit(menu_text,    (screen_w//2 - menu_text.get_width()//2,    screen_h//2 + 80))

            pygame.display.update()
            self.clock.tick(60)

Game().run()