import pygame
import math

from scripts.utils import Animation, load_images


class Projectile:
    SPEED = 2.8
    DMG = 60

    def __init__(self, frames, pos, direction):
        self.frames = frames
        self.pos = list(pos)
        self.direction = direction  

        self.frame = 0
        self.frame_timer = 0
        self.img_dur = 2
        self.dead = False

        self.size = (30, 30)

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self):
        self.pos[0] += self.SPEED * self.direction

        self.frame_timer += 1
        if self.frame_timer >= self.img_dur:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % len(self.frames)

    def render(self, surf, offset=(0, 0)):
        img = pygame.transform.scale(self.frames[self.frame], self.size)
        if self.direction == 1:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])))


def _load_sorted(folder, target_size=None):
    import os

    files = sorted(
        os.listdir(folder),
        key=lambda f: int(''.join(filter(str.isdigit, f.split('.')[0])) or 0),
    )
    frames = [pygame.image.load(os.path.join(folder, f)).convert_alpha() for f in files]
    if target_size:
        tw, th = target_size
        scaled = []
        for frame in frames:
            fw, fh = frame.get_size()
            # fit inside the canvas keeping aspect ratio (no clipping)
            scale = min(tw / fw, th / fh)
            new_w = int(fw * scale)
            new_h = int(fh * scale)
            canvas = pygame.Surface((tw, th), pygame.SRCALPHA)
            resized = pygame.transform.scale(frame, (new_w, new_h))
            # centre on canvas
            x_off = (tw - new_w) // 2
            y_off = (th - new_h) // 2
            canvas.blit(resized, (x_off, y_off))
            scaled.append(canvas)
        return scaled
    return frames


class Boss:
    FRAME_W = 500
    FRAME_H = 500
    MAX_HP = 1000


    RENDER_SCALE = 1       
    RENDER_W = 100 * RENDER_SCALE   
    RENDER_H = 50  * RENDER_SCALE   

    FLOAT_SPEED = 0.4
    FLOAT_SPEED_P2 = 2
    FLOAT_AMP = 8
    FLOAT_FREQ = 0.04

    ATTACK_RANGE = 30
    RANGE_THRESHOLD = 100

    ATTACK_DMG = 15
    RANGE_COOLDOWN = 90

    SPCL_RANGE = 30
    SPCL_DMG = 25
    SPCL_COOLDOWN = 80

    TELEPORT_RANGE = 200
    TELEPORT_COOLDOWN = 300

    FLOAT_SPEED_P2 = 1
    P2_HEAL_PER_SEC = 35
    P2_DMG_REDUCTION = 0.3       
    P2_SLIME_INTERVAL = 3000     

    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.size = (40, self.RENDER_H)

        self.hp = self.MAX_HP
        self.dead = False
        self.dying = False
        self.hurt_cooldown = 0

        self.facing_left = False

        self.base_y = self.pos[1]  # use spawner Y position directly
        self.float_timer = 0

        self.phase = 1
        self.transforming = False
        self.transform_cutscene = False
        self.attacking = False
        self.attack_hit = False
        self.range_attacking = False
        self.range_cd = 0
        self.projectiles = []

        self.spcl_attacking = False
        self.spcl_cd = 0

        self.teleport_cd = 0
        self.teleporting = False
        self.teleport_flash = 0

        self.slime_spawn_cd = 0  
        self.heal_accumulator = 0.0  
        self.anim_offset = (-(self.RENDER_W - self.size[0]) // 2, 0)  

        idle_sheet_path = 'data/images/BOSS/boss_idle/bossidle.Sheet (2).png'
        idle_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        cols = idle_sheet.get_width() // self.FRAME_W
        idle_frames = []
        for i in range(cols):
            frame = pygame.Surface((self.FRAME_W, self.FRAME_H), pygame.SRCALPHA)
            frame.blit(idle_sheet, (0, 0), (i * self.FRAME_W, 0, self.FRAME_W, self.FRAME_H))
            # fit onto the normalised canvas the same way _load_sorted does
            fw, fh = frame.get_size()
            scale = min(self.RENDER_W / fw, self.RENDER_H / fh)
            new_w = int(fw * scale)
            new_h = int(fh * scale)
            canvas = pygame.Surface((self.RENDER_W, self.RENDER_H), pygame.SRCALPHA)
            resized = pygame.transform.scale(frame, (new_w, new_h))
            canvas.blit(resized, ((self.RENDER_W - new_w) // 2, (self.RENDER_H - new_h) // 2))
            idle_frames.append(canvas)

        attack_frames = _load_sorted('data/images/BOSS/boss_attack', target_size=(self.RENDER_W, self.RENDER_H))
        range_frames = _load_sorted('data/images/BOSS/Boss_range', target_size=(self.RENDER_W, self.RENDER_H))
        transf_frames = _load_sorted('data/images/BOSS/2nd_Form_transf', target_size=(self.RENDER_W, self.RENDER_H))
        phase2_frames = _load_sorted('data/images/BOSS/2ndForm_idle', target_size=(self.RENDER_W, self.RENDER_H))
        spcl_frames = _load_sorted('data/images/BOSS/2ndForm_spcl_attack', target_size=(self.RENDER_W, self.RENDER_H))
        death_frames = _load_sorted('data/images/BOSS/boss_death', target_size=(self.RENDER_W, self.RENDER_H))
        teleport_frames = _load_sorted('data/images/BOSS/Boss_Teleport', target_size=(self.RENDER_W, self.RENDER_H))
        proj_frames = _load_sorted('data/images/BOSS/projectile')

        self.proj_frames = proj_frames

        self.anim_idle = Animation(idle_frames, img_dur=5, loop=True)
        self.anim_attack = Animation(attack_frames, img_dur=6, loop=False)
        self.anim_range = Animation(range_frames, img_dur=6, loop=False)
        self.anim_transf = Animation(transf_frames, img_dur=6, loop=False)
        self.anim_phase2 = Animation(phase2_frames, img_dur=10, loop=True)
        self.anim_spcl = Animation(spcl_frames, img_dur=6, loop=False)
        self.anim_death = Animation(death_frames, img_dur=8, loop=False)
        self.anim_teleport = Animation(teleport_frames, img_dur=6, loop=False)

        self.animation = self.anim_idle

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def attack_rect(self):
        """Returns the boss melee attack hitbox rect, or None if not attacking."""
        if not self.attacking:
            return None
        attack_w = 40
        attack_h = self.size[1]
        if self.facing_left:
            ax = self.pos[0] - attack_w
        else:
            ax = self.pos[0] + self.size[0]
        return pygame.Rect(ax, self.pos[1], attack_w, attack_h)

    def spcl_rect(self):
        """Returns the phase 2 special attack hitbox rect, or None if not active."""
        if not self.spcl_attacking:
            return None
        cx = self.pos[0] + self.size[0] // 2
        return pygame.Rect(cx - self.SPCL_RANGE, self.pos[1] - self.SPCL_RANGE // 2,
                           self.SPCL_RANGE * 2, self.size[1] + self.SPCL_RANGE)

    def _spawn_projectile(self):
        direction = -1 if self.facing_left else 1
        px = self.pos[0] + self.size[0] // 2
        py = self.pos[1] + self.size[1] // 3 
        self.projectiles.append(Projectile(self.proj_frames, (px, py), direction))

    def _spawn_slimes(self):
        from scripts.entities import Slime
        for offset_x in (-50, 50):
            sx = self.pos[0] + offset_x
            sy = self.pos[1]
            self.game.slimes.append(Slime(self.game, (sx, sy)))

    def take_damage(self, amount):
        if self.transforming or self.dead or self.dying:
            return

        if self.hurt_cooldown != 0:
            return

        # phase 2 damage reduction
        if self.phase == 2:
            amount = int(amount * (1.0 - self.P2_DMG_REDUCTION))

        self.hp = max(0, self.hp - amount)
        self.hurt_cooldown = 30

        if self.hp == 0:
            self.dying = True
            self.attacking = False
            self.range_attacking = False
            self.spcl_attacking = False
            self.transforming = False

            self.animation = Animation(self.anim_death.images, img_dur=8, loop=False)
            self.game.boss_defeated_timer = 180
            return

        if self.phase == 1 and self.hp <= self.MAX_HP // 3:
            self.phase = 2
            self.transforming = True
            self.transform_cutscene = True
            self.attacking = False
            self.range_attacking = False

            self.animation = Animation(self.anim_transf.images, img_dur=9, loop=False)

    def update(self):
        if self.dead:
            return

        player = self.game.player
        dx = player.pos[0] - self.pos[0]
        self.facing_left = dx < 0

        # track the ground surface the player is standing on
        # player feet = player.pos[1] + player.size[1]
        # boss feet should match that, so base_y = player_feet - RENDER_H
        player_feet = player.pos[1] + player.size[1]
        target_y = player_feet - self.RENDER_H
        self.base_y += (target_y - self.base_y) * 0.05

        self.float_timer += self.FLOAT_FREQ
        self.pos[1] = self.base_y + math.sin(self.float_timer) * self.FLOAT_AMP

        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1
        if self.range_cd > 0:
            self.range_cd -= 1
        if self.spcl_cd > 0:
            self.spcl_cd -= 1
        if self.teleport_cd > 0:
            self.teleport_cd -= 1
        if self.teleport_flash > 0:
            self.teleport_flash -= 1
        if self.phase == 2 and self.slime_spawn_cd > 0:
            self.slime_spawn_cd -= 1

        player_rect = player.rect()
        for proj in self.projectiles[:]:
            proj.update()
            if proj.rect().colliderect(player_rect) and not (player.dashing > 0 and player.mode == "staff"):
                player.take_damage(Projectile.DMG)
                proj.dead = True
            if abs(proj.pos[0] - self.pos[0]) > 400:
                proj.dead = True
        self.projectiles = [p for p in self.projectiles if not p.dead]

        if self.dying:
            self.animation.update()
            if self.animation.done:
                self.dead = True
            return

        if self.teleporting:
            self.animation.update()
            if self.animation.done:
                # snap to behind the player now that the exit anim is done
                player = self.game.player
                dx = player.pos[0] - self.pos[0]
                offset = -40 if dx > 0 else 40
                self.pos[0] = player.pos[0] + offset
                self.pos[1] = self.base_y
                self.teleporting = False
                self.teleport_cd = self.TELEPORT_COOLDOWN
                self.teleport_flash = 12
                self.animation = Animation(self.anim_teleport.images, img_dur=6, loop=False)  # arrival flash reuse same anim
            return

        if self.transforming:
            self.animation.update()
            if self.animation.done:
                self.transforming = False
                self.animation = self.anim_phase2
            return

        if self.spcl_attacking:
            self.animation.update()

            total = len(self.anim_spcl.images)
            cur = int(self.animation.frame / self.animation.img_duration)

            if cur == total // 2 and not self.attack_hit:
                sr = self.spcl_rect()
                if sr and sr.colliderect(player.rect()):
                    player.take_damage(self.SPCL_DMG)
                self.attack_hit = True

            if self.animation.done:
                self.spcl_attacking = False
                self.attack_hit = False
                self.spcl_cd = self.SPCL_COOLDOWN
                self.animation = self.anim_phase2
            return

        if self.range_attacking:
            self.animation.update()
            total = len(self.anim_range.images)
            cur = int(self.animation.frame / self.animation.img_duration)

            if cur == total // 2 and not self.attack_hit:
                self._spawn_projectile()
                self.attack_hit = True

            if self.animation.done:
                self.range_attacking = False
                self.attack_hit = False
                self.range_cd = self.RANGE_COOLDOWN
                self.animation = self.anim_idle
            return

        if self.attacking:
            self.animation.update()
            total_frames = len(self.anim_attack.images)
            cur_frame = int(self.animation.frame / self.animation.img_duration)

            if cur_frame >= total_frames // 3  and not self.attack_hit:
                ar = self.attack_rect()
                in_attack = ar and ar.colliderect(player.rect())
                in_body   = self.rect().colliderect(player.rect())
                if (in_attack or in_body) and not (player.dashing > 0 and player.mode == "staff"):
                    player.take_damage(self.ATTACK_DMG)
                self.attack_hit = True

            if self.animation.done:
                self.attacking = False
                self.attack_hit = False
                self.animation = self.anim_idle
            return
        dist = abs(dx)

        if self.phase == 2:
            if self.spcl_cd == 0 and dist <= self.SPCL_RANGE * 1.5:
                self.spcl_attacking = True
                self.attack_hit = False
                self.animation = Animation(self.anim_spcl.images, img_dur=6, loop=False)
            else:
                self.pos[0] += self.FLOAT_SPEED_P2 * (1 if dx > 0 else -1)
                if self.animation is not self.anim_phase2:
                    self.animation = self.anim_phase2
                self.animation.update()

                # heal 25 HP/sec while chasing
                self.heal_accumulator += self.P2_HEAL_PER_SEC / 60.0
                if self.heal_accumulator >= 1.0:
                    heal_amount = int(self.heal_accumulator)
                    self.hp = min(self.MAX_HP, self.hp + heal_amount)
                    self.heal_accumulator -= heal_amount

                # spawn 2 slimes every 30 seconds
                if self.slime_spawn_cd == 0:
                    self._spawn_slimes()
                    self.slime_spawn_cd = self.P2_SLIME_INTERVAL
        else:
            if dist <= self.ATTACK_RANGE:
                self.attacking = True
                self.attack_hit = False
                self.animation = Animation(self.anim_attack.images, img_dur=10, loop=False)
            elif dist >= self.RANGE_THRESHOLD and self.range_cd == 0:
                self.range_attacking = True
                self.attack_hit = False
                self.animation = Animation(self.anim_range.images, img_dur=6, loop=False)
            else:
                if dist >= self.TELEPORT_RANGE and self.teleport_cd == 0:
                    self.teleporting = True
                    self.animation = Animation(self.anim_teleport.images, img_dur=6, loop=False)
                else:
                    self.pos[0] += self.FLOAT_SPEED * (1 if dx > 0 else -1)
                self.animation.update()

    def render(self, surf, offset=(0, 0)):
        for proj in self.projectiles:
            proj.render(surf, offset)

        img = self.animation.img()
        if not self.facing_left:
            img = pygame.transform.flip(img, True, False)

        if self.hurt_cooldown > 0 or self.teleport_flash > 0:
            img = img.copy()
            white = pygame.Surface(img.get_size())
            white.fill((255, 255, 255))
            img.blit(white, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        surf.blit(
            img,
            (
                int(self.pos[0] - offset[0] + self.anim_offset[0]),
                int(self.pos[1] - offset[1] + self.anim_offset[1]),
            ),
        )

