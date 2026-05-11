import pygame
import math

from scripts.utils import Animation, load_images


class Projectile:
    SPEED = 2.5
    DMG = 30

    def __init__(self, frames, pos, direction):
        self.frames = frames
        self.pos = list(pos)
        self.direction = direction  

        self.frame = 0
        self.frame_timer = 0
        self.img_dur = 4
        self.dead = False

        self.size = (40, 40)

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


def _load_sorted(folder):
    import os

    files = sorted(
        os.listdir(folder),
        key=lambda f: int(''.join(filter(str.isdigit, f.split('.')[0])) or 0),
    )
    return [pygame.image.load(os.path.join(folder, f)).convert_alpha() for f in files]


class Boss:
    FRAME_W = 500
    FRAME_H = 500
    MAX_HP = 500

    FLOAT_SPEED = 0.4
    FLOAT_AMP = 8
    FLOAT_FREQ = 0.04

    ATTACK_RANGE = 30
    RANGE_THRESHOLD = 120

    ATTACK_DMG = 5
    RANGE_COOLDOWN = 120

    SPCL_RANGE = 60
    SPCL_DMG = 30
    SPCL_COOLDOWN = 180

    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.size = (60, 80)

        self.hp = self.MAX_HP
        self.dead = False
        self.dying = False
        self.hurt_cooldown = 0

        self.facing_left = False

        self.base_y = self.game.ground_y * 32 - self.size[1] - 80
        self.float_timer = 0

        self.phase = 1
        self.transforming = False
        self.attacking = False
        self.attack_hit = False
        self.range_attacking = False
        self.range_cd = 0
        self.projectiles = []

        self.spcl_attacking = False
        self.spcl_cd = 0

        self.anim_offset = (-10, -30)

        idle_sheet_path = 'data/images/BOSS/boss_idle/bossidle.Sheet (2).png'
        idle_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        cols = idle_sheet.get_width() // self.FRAME_W
        idle_frames = []
        for i in range(cols):
            frame = pygame.Surface((self.FRAME_W, self.FRAME_H), pygame.SRCALPHA)
            frame.blit(idle_sheet, (0, 0), (i * self.FRAME_W, 0, self.FRAME_W, self.FRAME_H))
            idle_frames.append(frame)

        attack_frames = _load_sorted('data/images/BOSS/boss_attack')
        range_frames = _load_sorted('data/images/BOSS/Boss_range')
        transf_frames = _load_sorted('data/images/BOSS/2nd_Form_transf')
        phase2_frames = _load_sorted('data/images/BOSS/2ndForm_idle')
        spcl_frames = _load_sorted('data/images/BOSS/2ndForm_spcl_attack')
        death_frames = _load_sorted('data/images/BOSS/boss_death')
        proj_frames = _load_sorted('data/images/BOSS/projectile')

        self.proj_frames = proj_frames

        self.anim_idle = Animation(idle_frames, img_dur=10, loop=True)
        self.anim_attack = Animation(attack_frames, img_dur=10, loop=False)
        self.anim_range = Animation(range_frames, img_dur=6, loop=False)
        self.anim_transf = Animation(transf_frames, img_dur=6, loop=False)
        self.anim_phase2 = Animation(phase2_frames, img_dur=10, loop=True)
        self.anim_spcl = Animation(spcl_frames, img_dur=6, loop=False)
        self.anim_death = Animation(death_frames, img_dur=8, loop=False)

        self.animation = self.anim_idle

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def _spawn_projectile(self):
        direction = -1 if self.facing_left else 1
        px = self.pos[0] + self.size[0] // 2
        py = self.pos[1] + self.size[1] // 3 - 20
        self.projectiles.append(Projectile(self.proj_frames, (px, py), direction))

    def take_damage(self, amount):
        if self.transforming or self.dead or self.dying:
            return

        if self.hurt_cooldown != 0:
            return

        self.hp = max(0, self.hp - amount)
        self.hurt_cooldown = 30

        if self.hp == 0:
            self.dying = True
            self.attacking = False
            self.range_attacking = False
            self.spcl_attacking = False
            self.transforming = False

            self.animation = Animation(self.anim_death.images, img_dur=8, loop=False)
            return

        if self.phase == 1 and self.hp <= self.MAX_HP // 1.5:
            self.phase = 2
            self.transforming = True
            self.attacking = False
            self.range_attacking = False

            self.animation = Animation(self.anim_transf.images, img_dur=6, loop=False)

    def update(self):
        if self.dead:
            return

        player = self.game.player
        dx = player.pos[0] - self.pos[0]
        self.facing_left = dx < 0

        self.float_timer += self.FLOAT_FREQ
        self.pos[1] = self.base_y + math.sin(self.float_timer) * self.FLOAT_AMP

        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1
        if self.range_cd > 0:
            self.range_cd -= 1
        if self.spcl_cd > 0:
            self.spcl_cd -= 1

        player_rect = player.rect()
        for proj in self.projectiles[:]:
            proj.update()
            if proj.rect().colliderect(player_rect):
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
                if abs(player.pos[0] - self.pos[0]) < self.SPCL_RANGE:
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

            if cur_frame >= total_frames - 1 and not self.attack_hit:
                if abs(player.pos[0] - self.pos[0]) < 30:
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
                self.pos[0] += self.FLOAT_SPEED * (1 if dx > 0 else -1)
                if self.animation is not self.anim_phase2:
                    self.animation = self.anim_phase2
                self.animation.update()
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
                self.pos[0] += self.FLOAT_SPEED * (1 if dx > 0 else -1)
                self.animation.update()

    def render(self, surf, offset=(0, 0)):
        for proj in self.projectiles:
            proj.render(surf, offset)

        img = self.animation.img()
        img = pygame.transform.scale(img, (80, 100))
        if not self.facing_left:
            img = pygame.transform.flip(img, True, False)

        if self.hurt_cooldown > 0:
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

