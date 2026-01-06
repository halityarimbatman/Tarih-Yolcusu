import pygame
from settings import *


# --- OOP PRENSİBİ: KALITIM (Inheritance) ---
# Temel Tile (Kare) Sınıfı
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface

        # Eğer taş ise gri renge boya (Placeholder)
        if sprite_type == 'rock':
            self.image.fill((100, 100, 100))

        self.rect = self.image.get_rect(topleft=pos)
        # Hitbox: Çarpışma kutusu
        self.hitbox = self.rect.inflate(0, -10)

# --- OOP PRENSİBİ: KALITIM & ÖZELLEŞTİRME ---
# Artifact (Hazine) sınıfı Tile sınıfından türetilmiştir.
# Bu sınıf sayesinde 'ImportError: cannot import name Artifact' hatası çözülecek.
class Artifact(Tile):
    def __init__(self, pos, groups, artifact_name):
        # 1. Hazine için boş bir yüzey oluştur
        surface = pygame.Surface((TILESIZE, TILESIZE))

        # 2. Rengini settings.py'daki veriden al
        if artifact_name in ARTIFACT_DATA:
            color = ARTIFACT_DATA[artifact_name]['color']
        else:
            color = (255, 255, 255)  # Hata olursa beyaz olsun

        surface.fill(color)

        # 3. Üst sınıfın (Tile) kurucu fonksiyonunu çağır
        super().__init__(pos, groups, 'artifact', surface)

        # 4. Hazineye özel ismi kaydet
        self.artifact_name = artifact_name


class Tree(Tile):
    def __init__(self, pos, groups, surface, stump_surface):
        # Normal Tile gibi başlat
        super().__init__(pos, groups, 'tree', surface)

        self.original_surface = surface  # Canlı ağaç görseli
        self.stump_surface = stump_surface  # Kesilmiş kök görseli

        self.health = 100  # Kesilme ilerlemesi (0-100 arası)
        self.alive = True  # Kesildi mi?

    def chop(self):
        """Ağacı kütüğe dönüştürür"""
        self.alive = False
        self.image = self.stump_surface
        self.rect = self.image.get_rect(topleft=self.rect.topleft)
        # Hitbox'ı küçült (Artık üzerinden geçilebilir olsun istersen hitbox'ı kaldırabilirsin)
        # Şimdilik kök de engel olsun ama daha küçük olsun
        self.hitbox = self.rect.inflate(-10, -10)
class Water(pygame.sprite.Sprite):
    def __init__(self, pos, groups, frames):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 0.10  # Akış hızı

        # İlk kareyi ayarla
        if self.frames:
            self.image = self.frames[0]
        else:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill((0, 100, 255))

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)  # Oyuncu suya giremesin

    def animate(self):
        if self.frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos, groups, destination, frames=None):
        super().__init__(groups)
        self.destination = destination
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 0.15

        if self.frames:
            self.image = self.frames[0]
            center_x = pos[0] + TILESIZE // 2
            center_y = pos[1] + TILESIZE // 2
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)


            self.rect = self.image.get_rect(topleft=pos)

        self.hitbox = self.rect.inflate(-self.rect.width * 0.2, -self.rect.height * 0.2)

    def animate(self):
        if self.frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()