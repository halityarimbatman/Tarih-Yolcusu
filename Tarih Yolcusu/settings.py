# Oyun Ayarları
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

# Renkler (Anadolu & Mezopotamya Teması)
BG_COLOR = (135, 206, 250)      # Gökyüzü
UI_BG_COLOR = (250, 235, 215)   # Parşömen / Kil Tablet
TEXT_COLOR = (60, 40, 20)       # Koyu Kahve
UI_BORDER_COLOR = (139, 69, 19) # Çerçeve Rengi

# Menü Renkleri
MENU_BG_COLOR = (160, 82, 45)
MENU_TEXT_COLOR = (255, 248, 220)
MENU_SELECT_COLOR = (255, 215, 0)
MENU_TITLE_COLOR = (64, 224, 208)

# --- VERİ YAPILARI (Data Structures) ---
# Oyundaki toplanabilir eserlerin verisi
# 'wet_clay' envanterde görünecek anahtar kelimedir, 'name' ise ekranda görünen ismidir.
ARTIFACT_DATA = {
    'tablet': {'name': 'Sümer Tableti', 'color': (205, 133, 63)},        # Kil Rengi
    'tekerlek': {'name': 'Sümer Tekerleği', 'color': (139, 69, 19)},
    'wet_clay': {'name': 'Islak Kil', 'color': (100, 100, 110)},   # Koyu Gri (Nehir çamuru)
    'kutuk': {'name': 'Kütük', 'color': (101, 67, 33)}
}