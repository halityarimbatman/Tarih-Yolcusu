import pygame
import os
from settings import *
from code.support import import_folder


class NPC(pygame.sprite.Sprite):
    """Harita üzerindeki etkileşime girilebilir karakterler"""

    def __init__(self, pos, groups, npc_type, dialog_key):
        super().__init__(groups)
        self.npc_type = npc_type
        self.dialog_key = dialog_key

        # --- ANİMASYON DEĞİŞKENLERİ ---
        self.frame_index = 0
        self.animation_speed = 0.10  # Varsayılan hız
        self.animations = []  # Sadece bu NPC'nin animasyon kareleri

        # Görsel Yükleme
        if self.npc_type == 'owl':
            self.animation_speed = 0.15
            self.import_npc_assets()
            if self.animations:
                self.image = self.animations[0]
            else:
                self.image = pygame.Surface((TILESIZE, TILESIZE))
                self.image.fill('purple')

        elif self.npc_type == 'rahip':
            self.animation_speed = 0.08  # Rahip yavaş nefes alsın
            self.import_npc_assets()
            if self.animations:
                # Rahibi 1.2 kat büyüt
                scaled_anims = []
                for anim in self.animations:
                    w, h = anim.get_size()
                    scaled_surf = pygame.transform.scale(anim, (int(w * 1.2), int(h * 1.2)))
                    scaled_anims.append(scaled_surf)
                self.animations = scaled_anims
                self.image = self.animations[0]
            else:
                self.image = pygame.Surface((TILESIZE, TILESIZE))
                self.image.fill((100, 100, 200))

        elif self.npc_type == 'isci':
            # --- YENİ: İŞÇİ ANİMASYONU ---
            self.animation_speed = 0.10  # Zorlanma hissi için orta-yavaş hız
            self.import_npc_assets()
            if self.animations:
                self.image = self.animations[0]
            else:
                self.image = pygame.Surface((TILESIZE, TILESIZE))
                self.image.fill((150, 100, 50))  # Resim yoksa Kahverengi kare

        else:
            # Tanımsız NPC
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill('white')

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

        # Konuşma alanı
        self.talk_zone = self.rect.inflate(50, 50)

    def import_npc_assets(self):
        """NPC tipine göre ilgili klasörden resimleri yükler"""
        path = ""

        if self.npc_type == 'owl':
            path = os.path.join('isimsiz_oyun', 'graphics', 'npcs', 'owl', 'idle')
            if not os.path.exists(path):
                path = os.path.join('graphics', 'npcs', 'owl', 'idle')

        elif self.npc_type == 'rahip':
            path = os.path.join('isimsiz_oyun', 'graphics', 'npcs', 'priest')
            if not os.path.exists(path):
                path = os.path.join('graphics', 'npcs', 'priest')

        elif self.npc_type == 'isci':
            # --- YENİ: İşçi Klasörü ---
            path = os.path.join('isimsiz_oyun', 'graphics', 'npcs', 'worker')
            if not os.path.exists(path):
                path = os.path.join('graphics', 'npcs', 'worker')

        # Eğer path belirlendiyse yükle
        if path:
            self.animations = import_folder(path)

    def animate(self):
        """Animasyon oynatma mantığı"""
        if self.animations:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations):
                self.frame_index = 0

            self.image = self.animations[int(self.frame_index)]

    def update(self):
        self.animate()


class HumaGuide(pygame.sprite.Sprite):
    """
    UI üzerinde uçarak gelen rehber Baykuş Huma.
    Harita koordinatlarından bağımsız, ekran koordinatlarında yaşar.
    """

    def __init__(self):
        super().__init__()

        # Görseller
        self.assets = {'idle': [], 'fly': []}
        self.import_assets()

        # Durum ve Konum
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Başlangıç Görseli
        if self.assets['fly']:
            self.image = self.assets['fly'][0]
        else:
            self.image = pygame.Surface((64, 64))
            self.image.fill('gold')

        self.rect = self.image.get_rect(topleft=(0, -100))  # Ekran dışı

        # Hareket Hedefleri
        self.target_y = -100
        self.visible = False

    def import_assets(self):
        base_path = os.path.join('isimsiz_oyun', 'graphics', 'npcs', 'owl')
        if not os.path.exists(base_path):
            base_path = os.path.join('graphics', 'npcs', 'owl')

        self.assets['idle'] = import_folder(os.path.join(base_path, 'idle'))
        self.assets['fly'] = import_folder(os.path.join(base_path, 'fly'))

        # Fallback
        if not self.assets['idle']:
            s = pygame.Surface((64, 64))
            s.fill('gold')
            self.assets['idle'] = [s]
        if not self.assets['fly']:
            self.assets['fly'] = self.assets['idle']

    def appear(self, start_x, target_y):
        """Huma'yı belirtilen X konumunda ve ekranın üstünden uçurarak getirir"""
        self.visible = True
        self.status = 'fly'
        self.rect.x = start_x
        self.rect.y = -100  # Ekranın üstünden başla
        self.target_y = target_y

    def update(self):
        if not self.visible: return

        # 1. Hareket Mantığı (Interpolation)
        if self.rect.y < self.target_y:
            self.status = 'fly'
            # Hedefe yaklaştıkça yavaşlayan yumuşak hareket
            dist = self.target_y - self.rect.y
            speed = max(2, dist * 0.08)
            self.rect.y += speed

            if abs(self.rect.y - self.target_y) < 2:
                self.rect.y = self.target_y
                self.status = 'idle'
        else:
            self.status = 'idle'

        # 2. Animasyon Karesi Güncelleme
        frames = self.assets.get(self.status, [])
        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0

            self.image = frames[int(self.frame_index)]

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)