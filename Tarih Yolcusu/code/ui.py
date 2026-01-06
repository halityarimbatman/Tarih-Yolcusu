import pygame
import google.generativeai as genai
import threading
from settings import *
from code.support import import_folder
from code.npc import HumaGuide


class UI:
    def __init__(self):
        # --- EKRAN VE FONT KURULUMLARI ---
        self.display_surface = pygame.display.get_surface()

        # Fontları tanımla (Hata almamak için)
        self.font = pygame.font.Font(None, 24)
        self.location_font = pygame.font.Font(None, 40)
        self.title_font = pygame.font.Font(None, 30)

        # --- DİKDÖRTGENLER (RECTS) ---
        # Chat kutusu ve envanter boyutlarını burada belirliyoruz
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()

        # Chat kutusu alt ortada
        self.chat_box_rect = pygame.Rect(20, screen_height - 300, 400, 280)
        # Envanter sol üstte (biraz aşağıda)
        self.inventory_rect = pygame.Rect(20, 60, 200, 300)

        # --- DEĞİŞKENLER ---
        self.chat_active = True  # Chat görünür mü?
        self.input_active = True  # Yazı yazılabilir mi?
        self.user_text = ""
        self.scroll_offset = 0
        self.current_speaker = "Bilge Baykus Huma"
        self._ai_response = "Merhaba! Ben Huma. Tarihle ilgili sorularını bana sorabilirsin. Cevaplamaktan mutluluk duyarım! Ayrıca Sümer şehrinde bir maceraya atılmak için sağ taraftaki gizemli portalı kullanabilirsin."
        self.is_typing = False
        self.ai_ready = False

        self.huma = HumaGuide()  # baykuş huma yönlendirmesi
        # --- AI KURULUMLARI ---
        self.api_key = "AIzaSyBEOsL9nCtf4O7Ii_1sXe49eBDWTlz-GyA"
        self.chat_history = []
        self.model = None
        self.chat = None

        print("API Bağlantısı kuruluyor...")
        try:
            genai.configure(api_key=self.api_key)

            # --- MODEL BULUCU ---
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
            except Exception as e:
                print(f"Model listeleme hatası: {e}")

            # Öncelik sırasına göre model seç
            target_model = None
            if 'models/gemini-1.5-flash' in available_models:
                target_model = 'models/gemini-1.5-flash'
            elif 'models/gemini-pro' in available_models:
                target_model = 'models/gemini-pro'
            elif available_models:
                target_model = available_models[0]
            else:
                # Hiçbir şey bulamazsa varsayılanı dene
                target_model = 'gemini-1.5-flash'

            print(f"Seçilen Model: {target_model}")
            self.model = genai.GenerativeModel(target_model)
            # Sohbeti başlat
            self.chat = self.model.start_chat(history=[])
            self.ai_ready = True
            print("AI Başarıyla başlatıldı.")

        except Exception as e:
            print(f"AI KRİTİK HATA: {e}")
            self.ai_ready = False
            self._ai_response = "API Hatasi! Anahtarini kontrol et."

    def trigger_huma_speech(self, text):
        """Huma'yı uçarak sahneye çağırır"""
        self.chat_active = True
        self.current_speaker = "Bilge Baykus Huma"
        self.ai_response = text
        self.input_active = True

        # Sohbet kutusunu konumlandır
        self.chat_box_rect.x = 20

        # Huma'yı çağır (Mantık artık HumaGuide sınıfında)
        target_y = self.chat_box_rect.y - 70
        self.huma.appear(start_x=self.chat_box_rect.x, target_y=target_y)

    # --- PROPERTY (GETTER/SETTER) ---
    @property
    def ai_response(self):
        return self._ai_response

    @ai_response.setter
    def ai_response(self, value):
        self._ai_response = value
        self.scroll_offset = 0  # Yeni cevap gelince en başa sar

    # --- METOTLAR ---
    def handle_event(self, event):
        """Mouse tekerleği ve Klavye olaylarını yönetir"""
        if self.chat_active:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y

            # Klavye ile yazma işlemi (main.py'dan da yönetilebilir ama buraya da ekledim)
            if event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Enter'a basınca sor
                    if self.user_text.strip():
                        # Cevabı ask_ai'den beklemek yerine placeholder alıyoruz
                        # Gerçek cevap thread bitince gelecek.
                        response = self.ask_ai(self.user_text)
                        self.ai_response = response
                        self.user_text = ""
                else:
                    self.user_text += event.unicode

    def ask_ai(self, text):
        if not self.ai_ready:
            return "AI Baglantisi yok. Kod icine API Key girdiginden emin ol."

        self.is_typing = True

        # --- THREADING (ARKA PLAN İŞLEMİ) ---
        # API çağrısı bloklayıcı olduğu için (oyunu dondurduğu için)
        # bunu ayrı bir iş parçacığında (thread) çalıştırıyoruz.
        def fetch_response_thread():
            try:
                prompt = f"Sen bir 5. sınıf öğrencisine tarih anlatan bilge bir baykuşsun. Adın Huma. Kısa, eğitici ve eğlenceli cevap ver. Soru: {text}"

                # Bu işlem 1-2 saniye sürebilir, thread içinde olduğu için oyunu durdurmaz
                response = self.chat.send_message(prompt)

                # Cevap geldiğinde değişkeni güncelle
                self.ai_response = response.text
            except Exception as e:
                print(f"Cevap Alma Hatası: {e}")
                self.ai_response = "Baglanti koptu. Lutfen tekrar dene."
            finally:
                # İşlem bitti, yazıyor durumunu kapat
                self.is_typing = False

        # Thread'i başlat (daemon=True, oyun kapanırsa thread de kapansın diye)
        thread = threading.Thread(target=fetch_response_thread, daemon=True)
        thread.start()

        # Thread çalışırken kullanıcıya gösterilecek geçici metin (ancak show_chat is_typing=True olduğu için "Huma düşünüyor..." gösterecek)
        return "..."

    def show_location(self, location_name):
        """Ekranın sağ üst köşesine mevcut bölgenin adını yazar"""
        # İsimleri güzelleştir
        display_name = location_name.replace('_', ' ').title()
        if location_name == 'hub': display_name = "Mezopotamya"
        if location_name == 'sumer': display_name = "Sümer Şehri"
        if location_name == 'sumer_ziggurat': display_name = "Ziggurat Tapınağı"

        text_surf = self.location_font.render(display_name, True, (255, 255, 255))
        # Gölge
        shadow_surf = self.location_font.render(display_name, True, (0, 0, 0))

        # WIDTH settings.py'dan gelmeli, gelmezse ekran genişliğini kullan
        screen_w = self.display_surface.get_width()

        rect = text_surf.get_rect(topright=(screen_w - 20, 20))
        shadow_rect = shadow_surf.get_rect(topright=(screen_w - 18, 22))

        self.display_surface.blit(shadow_surf, shadow_rect)
        self.display_surface.blit(text_surf, rect)

    def show_chat(self):
        if not self.chat_active:
            return
        self.huma.update()
        self.huma.draw(self.display_surface)
        # Arka plan
        pygame.draw.rect(self.display_surface, (40, 40, 50), self.chat_box_rect)
        pygame.draw.rect(self.display_surface, (200, 200, 200), self.chat_box_rect, 4)

        # İsim
        name_surf = self.title_font.render(self.current_speaker, True, (255, 215, 0))
        self.display_surface.blit(name_surf, (self.chat_box_rect.x + 20, self.chat_box_rect.y + 10))

        # Çıkış İpucu (Sağ Alt)
        hint_surf = self.font.render("[ESC] Kapat / [ENTER] Gönder", True, (150, 150, 150))
        hint_rect = hint_surf.get_rect(bottomright=(self.chat_box_rect.right - 10, self.chat_box_rect.bottom - 10))
        self.display_surface.blit(hint_surf, hint_rect)

        # Metin Gösterimi
        display_text = "Huma düşünüyor..." if self.is_typing else self.ai_response

        # Metni satırlara böl
        response_lines = self.wrap_text(display_text, self.font, self.chat_box_rect.width - 40)
        total_lines = len(response_lines)
        line_height = self.font.get_linesize()
        text_area_height = self.chat_box_rect.height - 80  # Input alanı için biraz daha yer açtık
        max_visible_lines = int(text_area_height // line_height)

        # Scroll Sınırlandırma
        max_scroll = max(0, total_lines - max_visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        visible_lines = response_lines[int(self.scroll_offset): int(self.scroll_offset) + max_visible_lines]

        for i, line in enumerate(visible_lines):
            text_surf = self.font.render(line, True, (255, 255, 255))
            y_pos = self.chat_box_rect.y + 40 + (i * line_height)
            self.display_surface.blit(text_surf, (self.chat_box_rect.x + 20, y_pos))

        # Scrollbar Çizimi
        if total_lines > max_visible_lines:
            bar_area_height = text_area_height
            scrollbar_height = max(20, (max_visible_lines / total_lines) * bar_area_height)
            # Sıfıra bölme hatasını önle
            scroll_ratio = 0
            if total_lines > 0:
                scroll_ratio = self.scroll_offset / total_lines

            scrollbar_y = self.chat_box_rect.y + 40 + scroll_ratio * bar_area_height

            # Kaydırma çubuğu arka planı
            pygame.draw.rect(self.display_surface, (60, 60, 70),
                             (self.chat_box_rect.right - 15, self.chat_box_rect.y + 40, 8, bar_area_height))
            # Kaydırma çubuğu
            pygame.draw.rect(self.display_surface, (200, 200, 200),
                             (self.chat_box_rect.right - 15, scrollbar_y, 8, scrollbar_height))

        # Oyuncu Giriş Alanı
        if self.input_active:
            # Kutunun en altına
            input_rect = pygame.Rect(self.chat_box_rect.x + 20, self.chat_box_rect.bottom - 40,
                                     self.chat_box_rect.width - 150, 30)
            pygame.draw.rect(self.display_surface, (255, 255, 255), input_rect)

            # Oyuncunun yazdığı yazı (Eğer boşsa placeholder gösterilebilir)
            display_user_text = self.user_text
            player_text_surf = self.font.render(display_user_text, True, (0, 0, 0))

            # Yazı taşarsa sağdan kırp (basit çözüm)
            text_rect = player_text_surf.get_rect()
            if text_rect.width > input_rect.width - 10:
                # Sadece son kısmı göster
                display_user_text = "..." + self.user_text[-20:]
                player_text_surf = self.font.render(display_user_text, True, (0, 0, 0))

            self.display_surface.blit(player_text_surf, (input_rect.x + 5, input_rect.y + 2))

            # İmleç (Cursor) Yanıp Sönme Efekti
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = input_rect.x + 5 + player_text_surf.get_width()
                pygame.draw.line(self.display_surface, (0, 0, 0), (cursor_x, input_rect.y + 2),
                                 (cursor_x, input_rect.bottom - 2), 2)

    def wrap_text(self, text, font, max_width):
        """Metni kutuya sığacak şekilde satırlara böler"""
        paragraphs = text.split('\n')
        lines = []

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = []

            for word in words:
                if not word: continue
                test_line = ' '.join(current_line + [word])
                width, _ = font.size(test_line)

                if width < max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            if not current_line and not paragraph:
                lines.append('')

        return lines

    def show_inventory(self, inventory_dict):
        # Ayarlardan renk gelmezse varsayılan kullan
        bg_color = (30, 30, 30)
        border_color = (200, 200, 200)
        text_color = (255, 255, 255)

        # globals() kontrolü yerine settings modülünden almaya çalışıyoruz,
        # ancak hata almamak için local tanımlar daha güvenlidir eğer import * çalışmazsa.
        try:
            bg_color = UI_BG_COLOR
            border_color = UI_BORDER_COLOR
            text_color = TEXT_COLOR
        except NameError:
            pass

        pygame.draw.rect(self.display_surface, bg_color, self.inventory_rect)
        pygame.draw.rect(self.display_surface, border_color, self.inventory_rect, 3)

        title_surf = self.font.render("Canta:", True, text_color)
        self.display_surface.blit(title_surf, (self.inventory_rect.x + 10, self.inventory_rect.y + 10))

        y_offset = 40
        for item_key, count in inventory_dict.items():
            if count > 0:
                # settings.py'dan ARTIFACT_DATA çekmeye çalış
                display_name = item_key.replace('_', ' ').title()
                try:
                    if 'ARTIFACT_DATA' in globals():
                        item_data = ARTIFACT_DATA.get(item_key, {})
                        display_name = item_data.get('name', display_name)
                except:
                    pass

                text = f"- {display_name}: {count}"
                text_surf = self.font.render(text, True, text_color)
                self.display_surface.blit(text_surf, (self.inventory_rect.x + 10, self.inventory_rect.y + y_offset))
                y_offset += 25

    def display(self, player):
        # Bu fonksiyon oyun döngüsünde sürekli çağrılır
        # UI elemanlarını çizmek için kullanılır
        pass