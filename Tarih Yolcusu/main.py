import pygame, sys
import os

# --- IMPORT DÜZELTMESİ (KRİTİK) ---
# Sorunun kaynağı: Python'ın standart 'code' kütüphanesi ile bizim klasörümüz çakışıyor.
# Çözüm: 'code' klasörüne __init__.py ekleyerek onu öncelikli bir paket haline getiriyoruz.

current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.join(current_dir, 'code')
init_file = os.path.join(code_dir, '__init__.py')

# Eğer code klasörü var ama içinde __init__.py yoksa, otomatik oluştur.
if os.path.exists(code_dir) and not os.path.exists(init_file):
    try:
        with open(init_file, 'w') as f:
            pass  # Boş dosya oluştur
        print(f"Sistem Düzeltmesi: {init_file} dosyası oluşturuldu.")
    except Exception as e:
        print(f"Uyarı: {init_file} oluşturulamadı. Hata: {e}")

# Proje dizinini arama yolunun en başına ekle
sys.path.insert(0, current_dir)

# Eğer standart 'code' kütüphanesi yanlışlıkla hafızaya alındıysa, onu sil.
# Böylece Python mecburen bizim klasörümüzü yükleyecek.
if 'code' in sys.modules:
    del sys.modules['code']
# ------------------------------------

from settings import *
from code.level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Tarih Yolcusu')
        self.clock = pygame.time.Clock()

        # Oyun Durumu
        self.game_active = False

        # Level Kurulumu
        self.level = Level()

        # Font Ayarları
        self.font_title = pygame.font.SysFont("comicsansms", 80, bold=True)
        self.font_main = pygame.font.SysFont("comicsansms", 40)

        # Menü Arka Plan Resmi Yükleme Denemesi
        self.menu_bg_image = None
        try:
            # Önce proje dizinindeki graphics klasörüne bak
            img_path = os.path.join(current_dir, "graphics", "menu_background.png")

            if os.path.exists(img_path):
                self.menu_bg_image = pygame.image.load(img_path).convert()
                self.menu_bg_image = pygame.transform.scale(self.menu_bg_image, (WIDTH, HEIGHT))
            else:
                print(f"Bilgi: Menü resmi bulunamadı ({img_path}), varsayılan renk kullanılacak.")
        except Exception as e:
            print(f"Menü resmi yüklenemedi, düz renk kullanılacak. Hata: {e}")

    def draw_text_with_shadow(self, text, font, color, x, y, shadow_offset=3):
        """Yazıyı gölgesiyle beraber çizer"""
        # Önce gölge (Siyah)
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(x + shadow_offset, y + shadow_offset))
        self.screen.blit(shadow_surf, shadow_rect)

        # Sonra asıl yazı
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)

    def show_menu(self):
        """Menü ekranını çizer ve girişleri kontrol eder"""

        # Arka planı çiz (Resim varsa resim, yoksa renk)
        if self.menu_bg_image:
            self.screen.blit(self.menu_bg_image, (0, 0))
        else:
            self.screen.fill(MENU_BG_COLOR)

        # Başlık (Gölgesiyle beraber)
        self.draw_text_with_shadow("TARİH YOLCUSU", self.font_title, MENU_TITLE_COLOR, WIDTH // 2, HEIGHT // 3)

        # Talimatlar (Seçenekler)
        self.draw_text_with_shadow("Başlamak için [ENTER]", self.font_main, MENU_SELECT_COLOR, WIDTH // 2,
                                   HEIGHT // 2 + 50)
        self.draw_text_with_shadow("Çıkış için [Q]", self.font_main, MENU_TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 120)

        # Menü olay döngüsü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter tuşu
                    self.game_active = True  # Oyunu başlat
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

    def run_game(self):
        """Oyunun çalıştığı ana döngü"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- YENİ: KLAVYE GİRİŞLERİ ---
            if event.type == pygame.KEYDOWN:
                if self.level.ui.chat_active:
                    # Sohbet açıkken tuşlar yazı yazar
                    if event.key == pygame.K_RETURN:
                        # Enter'a basınca AI'ya sor
                        response = self.level.ui.ask_ai(self.level.ui.user_text)
                        self.level.ui.ai_response = response
                        self.level.ui.user_text = ""  # Kutuyu temizle
                    elif event.key == pygame.K_BACKSPACE:
                        self.level.ui.user_text = self.level.ui.user_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.level.ui.chat_active = False  # Sohbetten çık
                    else:
                        # Harf ekle
                        self.level.ui.user_text += event.unicode
                else:
                    # Sohbet kapalıyken normal tuşlar
                    if event.key == pygame.K_ESCAPE:
                        self.game_active = False
            if event.type == pygame.MOUSEWHEEL:
                self.level.ui.handle_event(event)
        self.screen.fill(BG_COLOR)
        self.level.run()
        pygame.display.update()

    def run(self):
        while True:
            if self.game_active:
                self.run_game()
            else:
                self.show_menu()

            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()