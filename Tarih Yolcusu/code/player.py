import pygame
import os
from settings import *
from code.support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)

        # --- ANİMASYON KURULUMU ---
        # Görsel yükleme işlemi init içinde çağrılmalı
        self.animations = {}  # Animasyonları tutacak sözlük
        self.import_player_assets()

        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Başlangıç görselini ayarla (idle listesinin ilk elemanı veya placeholder)
        if self.animations and self.animations['down_idle']:
            self.image = self.animations['down_idle'][0]
        else:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill('red')

        self.rect = self.image.get_rect(topleft=pos)

        # Hitbox: Karakterin ayaklarının bastığı yer (Daha küçük ve aşağıda)
        self.hitbox = self.rect.inflate(-30, -30)

        # Hareket Değişkenleri
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites

    def import_player_assets(self):
        """
        Karakter animasyon dosyalarını (run/idle) yükler
        ve eksik yönleri (sol, yukarı, aşağı) otomatik türetir.
        """
        base_path = os.path.join('isimsiz_oyun', 'graphics', 'player')
        if not os.path.exists(base_path):
            base_path = os.path.join('graphics', 'player')

        # 1. Kaynak klasörlerden resimleri yükle
        # Kullanıcının eklediği: graphics/player/run ve graphics/player/idle
        run_imgs = import_folder(os.path.join(base_path, 'run'))
        idle_imgs = import_folder(os.path.join(base_path, 'idle'))

        # Eğer klasörler boşsa veya bulunamazsa hata vermemesi için boş liste kontrolü
        if not run_imgs:
            print("Uyarı: 'run' klasörü boş veya bulunamadı!")
            # Placeholder (Kırmızı Kare) oluştur
            surf = pygame.Surface((64, 64))
            surf.fill('red')
            run_imgs = [surf]

        if not idle_imgs:
            print("Uyarı: 'idle' klasörü boş veya bulunamadı! 'run' görselleri kullanılacak.")
            idle_imgs = run_imgs  # Idle yoksa run kullan

        # 2. Eksik Yönleri Türet (Otomatik Flip)
        # Sola bakış için resimleri yatayda çevir (flip x=True, y=False)
        run_imgs_left = [pygame.transform.flip(img, True, False) for img in run_imgs]
        idle_imgs_left = [pygame.transform.flip(img, True, False) for img in idle_imgs]

        # 3. Animasyon Sözlüğünü Doldur
        # Elimizde sadece sağ (run) var.
        # Sağ -> run_imgs
        # Sol -> run_imgs_left (Çevrilmiş)
        # Yukarı/Aşağı -> run_imgs (Varsayılan olarak sağa baksın veya son yöne göre güncellenebilir)

        self.animations = {
            'up': run_imgs,
            'down': run_imgs,
            'right': run_imgs,
            'left': run_imgs_left,

            'up_idle': idle_imgs,
            'down_idle': idle_imgs,
            'right_idle': idle_imgs,
            'left_idle': idle_imgs_left
        }

    def get_status(self):
        """Karakterin hareketine göre (idle/run) durumunu belirler"""

        # Hareket Durumu Kontrolü
        if self.direction.magnitude() == 0:
            # Duruyor
            if not 'idle' in self.status:
                self.status = self.status + '_idle'
        else:
            # Hareket ediyor
            if 'idle' in self.status:
                self.status = self.status.replace('_idle', '')

    def input(self):
        keys = pygame.key.get_pressed()

        # Yön Tuşları ve Durum Atama
        # Sadece yön değiştiğinde status'u güncelle (Idle modunu bozmamak için burada dikkatli olmalıyız)
        # Ancak get_status fonksiyonu zaten idle eklemesini yapıyor.

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

    def move(self, speed):
        # Çapraz gidildiğinde hızı dengele
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Yatay Hareket ve Çarpışma
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        # Dikey Hareket ve Çarpışma
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        # Rect'i hitbox'a eşitle
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # Sağa gidiyor
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # Sola gidiyor
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # Aşağı gidiyor
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # Yukarı gidiyor
                        self.hitbox.top = sprite.hitbox.bottom

    def animate(self):
        """Mevcut duruma göre resmi günceller"""
        # Hata önleyici: Eğer status sözlükte yoksa varsayılan 'down_idle' kullan
        current_animation = self.animations.get(self.status, self.animations.get('down_idle', []))

        if len(current_animation) > 0:
            self.frame_index += self.animation_speed

            if self.frame_index >= len(current_animation):
                self.frame_index = 0

            # Resmi güncelle
            self.image = current_animation[int(self.frame_index)]
            # Rect merkezini koru
            self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.input()
        self.get_status()  # Durumu güncelle (Idle mı koşuyor mu?)
        self.animate()  # Resmi güncelle
        self.move(self.speed)