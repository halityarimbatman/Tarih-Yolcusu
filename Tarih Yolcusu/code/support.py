import pygame
from os import walk
import os
from settings import TILESIZE


def import_cut_graphic(path):
    """
    Büyük bir tileset resmini alır ve onu TILESIZE boyutunda
    küçük karelere bölüp bir liste olarak döndürür.
    """
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / TILESIZE)
    tile_num_y = int(surface.get_size()[1] / TILESIZE)

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * TILESIZE
            y = row * TILESIZE
            new_surf = pygame.Surface((TILESIZE, TILESIZE), flags=pygame.SRCALPHA)
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, TILESIZE, TILESIZE))
            cut_tiles.append(new_surf)

    return cut_tiles


def import_folder(path):
    """
    Verilen klasör yolundaki tüm resimleri (png, jpg) yükler
    ve bir liste olarak döndürür (Animasyonlar için).
    """
    surface_list = []

    # Klasörün varlığını kontrol et
    if not os.path.exists(path):
        # Klasör yoksa boş liste dön, hata verme (Player.py bunu handle ediyor)
        return surface_list

    # os.walk kullanarak klasördeki dosyaları gez
    for _, __, img_files in os.walk(path):
        # Dosyaları isme göre sırala ki animasyon sırası karışmasın (1.png, 2.png...)
        img_files.sort()
        for image in img_files:
            if image.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(path, image)
                try:
                    image_surf = pygame.image.load(full_path).convert_alpha()

                    # --- DÜZELTME: BOYUTLANDIRMA ---
                    # Yüklenen resim devasa ise oyun alanına sığması için
                    # TILESIZE (64x64) boyutuna ölçekliyoruz.
                    image_surf = pygame.transform.scale(image_surf, (TILESIZE, TILESIZE))

                    surface_list.append(image_surf)
                except Exception as e:
                    print(f"Resim yükleme hatası ({image}): {e}")

    return surface_list