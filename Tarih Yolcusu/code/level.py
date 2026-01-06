import pygame
import random
import os
from settings import *
from code.tile import Tile, Artifact, Tree, Water, Portal  # Tree sınıfını buraya ekledik
from code.player import Player
from code.npc import NPC
from code.ui import UI
from code.support import import_cut_graphic, import_folder


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # Sprite grupları
        self.visible_sprites = YSortCameraGroup()
        self.floor_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.artifact_sprites = pygame.sprite.Group()
        self.npc_sprites = pygame.sprite.Group()
        self.portal_sprites = pygame.sprite.Group()
        # Ağaçları ayrı bir grupta tutmak etkileşimi kolaylaştırır
        self.tree_sprites = pygame.sprite.Group()

        # Envanter
        self.inventory = {
            'gunes_kursu': 0, 'tablet': 0, 'tekerlek': 0, 'wet_clay': 0, 'kutuk': 0
        }

        self.collected_items = set()

        # --- YENİ: AĞAÇ HAFIZASI ---
        # Her bölüm için üretilen ağaçların konumunu ve türünü saklar.
        self.generated_trees = {}

        self.quests = {
            'sumer_yazi': 'baslamadi',
            'sumer_tekerlek': 'baslamadi'
        }

        self.chopping_tree = None  # Şu an kesilen ağaç
        self.chop_progress = 0  # 0'dan 120'ye kadar (60 FPS * 2 sn)
        self.pending_huma_text = None

        self.ui = UI()

        # --- GÖRSEL YÜKLEME ---
        self.graphics = {
            'grass': [],
            'water': [],
            'props': [],
            'trees': [],
            'stump': None,
            'log': None, # Log görseli için yer açtık
            'river': [],
            'ziggurat': None
        }
        self.load_graphics()

        # Bölüm Yönetimi
        self.current_level = 'hub'
        self.create_map()


    def load_graphics(self):
        """Tilesetleri ve 'trees' klasöründeki tüm ağaçları yükler"""
        base_path = os.path.join("isimsiz_oyun", "graphics")
        if not os.path.exists(base_path):
            base_path = "graphics"

        # Listeleri sıfırla
        self.graphics['grass'] = []
        self.graphics['water'] = []
        self.graphics['props'] = []
        self.graphics['trees'] = []

        try:
            # 1. Tilesetleri Yükle
            grass_path = os.path.join(base_path, 'tileset-grassland-grass.png')
            if os.path.exists(grass_path):
                self.graphics['grass'] = import_cut_graphic(grass_path)

            # --- YENİ: ANİMASYONLU NEHİR YÜKLEME ---
            # graphics/river klasöründeki river1.png, river2.png vb. hepsini yükler
            river_folder = os.path.join(base_path, 'river')
            if os.path.exists(river_folder):
                river_frames = import_folder(river_folder)
                # Boyutlandırma (Eğer görseller TILESIZE değilse)
                scaled_frames = []
                for frame in river_frames:
                    scaled_frames.append(pygame.transform.scale(frame, (TILESIZE, TILESIZE)))
                self.graphics['water'] = scaled_frames
            else:
                print(f"Uyarı: '{river_folder}' bulunamadı. Mavi kare kullanılacak.")
                s = pygame.Surface((TILESIZE, TILESIZE))
                s.fill((0, 100, 255))
                self.graphics['water'] = [s]

            # 2. Ağaçları Klasörden Otomatik Yükle
            trees_folder = os.path.join(base_path, 'trees')

            if os.path.exists(trees_folder):
                for file_name in os.listdir(trees_folder):
                    if file_name.lower().endswith('.png'):
                        full_path = os.path.join(trees_folder, file_name)
                        try:
                            img = pygame.image.load(full_path).convert_alpha()

                            # --- GÜNCELLEME: AĞAÇLARI BOYUTLANDIR ---
                            target_width = TILESIZE * 1.5

                            if img.get_width() > target_width:
                                scale_factor = target_width / img.get_width()
                                new_height = int(img.get_height() * scale_factor)
                                img = pygame.transform.scale(img, (int(target_width), new_height))
                                print(f"Ağaç küçültüldü ({file_name})")
                            else:
                                print(f"Ağaç yüklendi (Orijinal): {file_name}")

                            self.graphics['trees'].append(img)

                        except Exception as e:
                            print(f"Hata ({file_name}): {e}")
            else:
                print(f"Uyarı: '{trees_folder}' klasörü bulunamadı. Lütfen oluşturun.")

            print(f"Toplam Görseller: {len(self.graphics['grass'])} çim, {len(self.graphics['trees'])} ağaç.")

            # --- YENİ: KÜTÜK (STUMP) VE ODUN (LOG) GÖRSELLERİ ---
            # Yeni yol: graphics/trees/cut_wood/
            cut_wood_path = os.path.join(base_path, 'trees', 'cut_wood')

            # Stump Yükleme
            stump_p = os.path.join(cut_wood_path, 'stump.png')
            if os.path.exists(stump_p):
                img = pygame.image.load(stump_p).convert_alpha()
                self.graphics['stump'] = pygame.transform.scale(img, (TILESIZE, int(TILESIZE * 0.8)))
            else:
                # Placeholder
                s = pygame.Surface((TILESIZE, int(TILESIZE * 0.8)))
                s.fill((101, 67, 33))
                self.graphics['stump'] = s

            # Log Yükleme
            log_p = os.path.join(cut_wood_path, 'log.png')
            if os.path.exists(log_p):
                img = pygame.image.load(log_p).convert_alpha()
                # Log biraz daha küçük olsun (Envanter boyutu gibi)
                self.graphics['log'] = pygame.transform.scale(img, (int(TILESIZE * 0.6), int(TILESIZE * 0.6)))

            # 7. ZIGGURAT YÜKLEME
            ziggurat_p = os.path.join(base_path, 'structures', 'ziggurat.png')
            if os.path.exists(ziggurat_p):
                self.graphics['ziggurat'] = pygame.image.load(ziggurat_p).convert_alpha()


            # --- 8. ZIGGURAT İÇ MEKAN (YENİ) ---
            zig_inner_p = os.path.join(base_path, 'structures', 'ziggurat_ici.png')
            if os.path.exists(zig_inner_p):
                # Convert (alpha değil) çünkü zemin opak olacak
                self.graphics['ziggurat_floor'] = pygame.image.load(zig_inner_p).convert()
            else:
                print("Uyarı: 'ziggurat_ici.png' bulunamadı.")
                self.graphics['ziggurat_floor'] = None

            # 8. ISLAK KİL (WET CLAY) YÜKLEME
            wet_clay_p = os.path.join(base_path, 'wet_clay.png')
            if os.path.exists(wet_clay_p):
                img = pygame.image.load(wet_clay_p).convert_alpha()
                # Biraz küçültelim ki yerde doğal dursun (0.7 oranında)
                self.graphics['wet_clay'] = pygame.transform.scale(img, (int(TILESIZE*0.7), int(TILESIZE*0.7)))
            else:
                self.graphics['wet_clay'] = None

                # 9. PORTAL ANİMASYONU YÜKLEME
            portal_path = os.path.join(base_path, 'structures', 'portal')
            if os.path.exists(portal_path):
                portal_frames = import_folder(portal_path)
                scaled_size = (int(TILESIZE * 1.9), int(TILESIZE * 1.9))
                self.graphics['portal'] = [pygame.transform.scale(img, scaled_size) for img in portal_frames]
            else:
                self.graphics['portal'] = []

            # 10. KAPI (DOOR) YÜKLEME
            door_p = os.path.join(base_path, 'structures', 'door.png')
            if os.path.exists(door_p):
                img = pygame.image.load(door_p).convert_alpha()
                # Kapıyı TILESIZE boyutuna ayarla (veya biraz daha büyük olabilir)
                self.graphics['door'] = pygame.transform.scale(img, (TILESIZE, TILESIZE))
            else:
                self.graphics['door'] = None

        except Exception as e:
            print(f"Görsel Yükleme Hatası: {e}")

    def create_map(self, keep_player_pos=False):
        old_player_pos = None
        if keep_player_pos and hasattr(self, 'player'):
            old_player_pos = self.player.rect.topleft

        self.visible_sprites.empty()
        self.floor_sprites.empty()
        self.obstacle_sprites.empty()
        self.artifact_sprites.empty()
        self.npc_sprites.empty()
        self.portal_sprites.empty()
        self.tree_sprites.empty()

        layouts = {
            'hub': {
                'player_start': (640, 360),
                'npcs': [('owl', (640, 250), 'intro')],
                'artifacts': [],
                'obstacles': [],
                'portals': [((1050, 360), 'sumer')],
                'map_size': (20, 12),
                'tree_count': 12
            },
            'sumer': {
                'player_start': (100, 300),
                'npcs': [('isci', (850, 550), 'sumer_gorev_tekerlek')],
                'artifacts': [],
                'obstacles': [],
                'portals': [((400, 300), 'sumer_ziggurat')],
                'map_size': (25, 15),
                'tree_count': 25
            },
            'sumer_ziggurat': {
                'player_start': (640, 550),
                'npcs': [('rahip', (640, 250), 'sumer_gorev_yazi')],
                'artifacts': [],
                'obstacles': [],  # Obstacles kaldırıldı
                'portals': [((640, 650), 'sumer')],
                'map_size': (20, 12),
                'tree_count': 0
            }
        }

        # --- FİNAL DOKUNUŞU: GÖREVLER BİTTİ Mİ? ---
        # Eğer Sümer bölümündeysek ve her iki görev de tamamlandıysa, Hub'a dönüş portalını aç.
        if self.current_level == 'sumer':
            if self.quests['sumer_yazi'] == 'tamamlandi' and self.quests['sumer_tekerlek'] == 'tamamlandi':
                # Başlangıç noktasına yakın bir yere (100, 200) geri dönüş portalı ekliyoruz.
                # 'portal' görseli varsa onu kullanacak, yoksa varsayılan mavi kare olur.
                layouts['sumer']['portals'].append(((100, 100), 'hub'))

        data = layouts.get(self.current_level, layouts['hub'])
        map_w, map_h = data.get('map_size', (20, 12))

        # --- DEĞİŞKENLERİ EN BAŞA ALDIK ---
        padding = 12
        river_width = 2
        river_gap = 2

        # Özel Durum Kontrolü
        is_ziggurat_level = (self.current_level == 'sumer_ziggurat')
        has_ziggurat_floor = (is_ziggurat_level and self.graphics.get('ziggurat_floor'))

        # --- 1. ZIGGURAT İÇİ BÜYÜK RESİM YERLEŞTİRME ---
        if has_ziggurat_floor:
            floor_img = self.graphics['ziggurat_floor']

            if floor_img.get_height() > 800:
                scale_factor = 0.5
                new_w = int(floor_img.get_width() * scale_factor)
                new_h = int(floor_img.get_height() * scale_factor)
                floor_img = pygame.transform.scale(floor_img, (new_w, new_h))

            Tile((0, 0), [self.floor_sprites], 'floor', surface=floor_img)

            bound_w = floor_img.get_width()
            bound_h = floor_img.get_height()

            Tile((0, -TILESIZE), [self.obstacle_sprites], 'rock', surface=pygame.Surface((bound_w, TILESIZE)))
            Tile((0, bound_h), [self.obstacle_sprites], 'rock', surface=pygame.Surface((bound_w, TILESIZE)))
            Tile((-TILESIZE, 0), [self.obstacle_sprites], 'rock', surface=pygame.Surface((TILESIZE, bound_h)))
            Tile((bound_w, 0), [self.obstacle_sprites], 'rock', surface=pygame.Surface((TILESIZE, bound_h)))

            # Kapıyı ortalama
            door_x = (bound_w // 2) - (TILESIZE // 2)
            door_y = 64
            data['portals'] = [((door_x, door_y), 'sumer')]

        # --- 2. HARİTA DÖNGÜSÜ ---
        for row in range(-padding, map_h + padding):
            for col in range(-padding, map_w + padding):
                x = col * TILESIZE
                y = row * TILESIZE

                if self.graphics['grass'] and not has_ziggurat_floor:
                    grass_surf = random.choice(self.graphics['grass'])
                    Tile((x, y), [self.floor_sprites], 'grass', surface=grass_surf)

                is_left_river = (-river_width <= col <= 0)
                is_right_river = (map_w - 1 <= col <= map_w - 1 + river_width)
                is_river = is_left_river or is_right_river
                in_map_bounds = (0 <= col < map_w) and (0 <= row < map_h)

                if is_ziggurat_level:
                    continue

                if is_river:
                    if self.graphics['water']:
                        Water((x, y), [self.visible_sprites, self.obstacle_sprites], self.graphics['water'])
                elif in_map_bounds:
                    if row == 0 or row == map_h - 1:
                        if self.graphics['trees']:
                            tree_surf = random.choice(self.graphics['trees'])
                            t = Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'tree', surface=tree_surf)
                            t.hitbox = pygame.Rect(0, 0, int(t.rect.width * 0.4), int(t.rect.height * 0.2))
                            t.hitbox.midbottom = t.rect.midbottom
                else:
                    in_left_gap = (-river_width - river_gap <= col < -river_width)
                    in_right_gap = (map_w - 1 + river_width < col <= map_w - 1 + river_width + river_gap)

                    if not in_left_gap and not in_right_gap:
                        if self.graphics['trees'] and random.random() < 0.60:
                            tree_surf = random.choice(self.graphics['trees'])
                            Tile((x, y), [self.visible_sprites], 'tree', surface=tree_surf)

        # --- 3. ZIGGURAT DIŞ CEPHE ---
        ziggurat_rect = None
        if self.current_level == 'sumer' and self.graphics.get('ziggurat'):
            zig_surf = self.graphics['ziggurat']
            scale_factor = 0.6
            new_w = int(zig_surf.get_width() * scale_factor)
            new_h = int(zig_surf.get_height() * scale_factor)
            zig_surf = pygame.transform.scale(zig_surf, (new_w, new_h))

            z_x = 400 - (zig_surf.get_width() // 2) + 32
            z_y = 400 - zig_surf.get_height() + 40

            Tile((z_x, z_y), [self.visible_sprites], 'structure', zig_surf)
            ziggurat_rect = pygame.Rect(z_x, z_y, new_w, new_h).inflate(50, 50)

        # --- 4. DİĞER OBJELER ---
        for pos in data['obstacles']:
            surf = pygame.Surface((TILESIZE, TILESIZE))
            surf.fill((100, 100, 100))
            if is_ziggurat_level:
                surf.set_alpha(0)
            elif self.graphics['props']:
                surf = random.choice(self.graphics['props'])

            tile = Tile(pos, [self.visible_sprites, self.obstacle_sprites], 'rock', surface=surf)
            tile.hitbox = tile.rect.inflate(-10, -10)

        for art_info in data['artifacts']:
            art_name, pos = art_info
            item_id = (self.current_level, art_name, pos)
            if item_id in self.collected_items: continue
            Artifact(pos, [self.visible_sprites, self.artifact_sprites], art_name)

        if self.current_level == 'sumer' and self.quests['sumer_yazi'] == 'alindi':
            pos = (400, 150)
            item_id = (self.current_level, 'wet_clay', pos)
            if item_id not in self.collected_items:
                clay = Artifact(pos, [self.visible_sprites, self.artifact_sprites], 'wet_clay')
                if self.graphics['wet_clay']:
                    clay.image = self.graphics['wet_clay']
                    clay.rect = clay.image.get_rect(center=(pos[0] + TILESIZE // 2, pos[1] + TILESIZE // 2))
                    clay.hitbox = clay.rect.inflate(0, -10)

        for npc_info in data['npcs']:
            npc_type, pos, dialog = npc_info
            npc = NPC(pos, [self.visible_sprites, self.npc_sprites, self.obstacle_sprites], npc_type, dialog)
            npc.hitbox = npc.rect.inflate(-20, -20)

        # Portallar: Hub için özel görsel, diğerleri için kapı
        for portal_info in data['portals']:
            pos, dest = portal_info
            portal_visuals = []

            # Hub portalı ise (veya hub'a gidiyorsa) portal animasyonu kullan
            if dest == 'hub' or self.current_level == 'hub':
                if self.graphics['portal']:
                    portal_visuals = self.graphics['portal']
            # Diğerleri (Ziggurat içi/dışı) kapı görseli kullan
            elif self.graphics['door']:
                portal_visuals = [self.graphics['door']]

            Portal(pos, [self.visible_sprites, self.portal_sprites], dest, portal_visuals)

        if old_player_pos:
            self.player = Player(old_player_pos, [self.visible_sprites], self.obstacle_sprites)
        else:
            self.player = Player(data['player_start'], [self.visible_sprites], self.obstacle_sprites)
        self.player.hitbox = self.player.rect.inflate(-30, -30)

        tree_count = data.get('tree_count', 0)
        if not is_ziggurat_level:
            if self.current_level in self.generated_trees:
                for t_data in self.generated_trees[self.current_level]:
                    if self.graphics['trees']:
                        idx = t_data[1]
                        if idx >= len(self.graphics['trees']): idx = 0
                        tree = Tree(t_data[0],
                                    [self.visible_sprites, self.obstacle_sprites, self.tree_sprites],
                                    self.graphics['trees'][idx],
                                    self.graphics['stump'])
                        hb_w = int(tree.rect.width * 0.4)
                        hb_h = int(tree.rect.height * 0.2)
                        tree.hitbox = pygame.Rect(0, 0, hb_w, hb_h)
                        tree.hitbox.midbottom = tree.rect.midbottom

            elif self.graphics['trees'] and tree_count > 0:
                new_trees_data = []
                placed_trees = 0
                attempts = 0
                max_attempts = tree_count * 15
                while placed_trees < tree_count and attempts < max_attempts:
                    attempts += 1
                    tree_index = random.randint(0, len(self.graphics['trees']) - 1)
                    tree_surf = self.graphics['trees'][tree_index]
                    rand_x = random.randint(TILESIZE, (map_w - 2) * TILESIZE)
                    rand_y = random.randint(TILESIZE, (map_h - 2) * TILESIZE)
                    new_pos = (rand_x, rand_y)
                    check_rect = tree_surf.get_rect(topleft=new_pos).inflate(10, 10)
                    collision = False
                    if ziggurat_rect and check_rect.colliderect(ziggurat_rect): collision = True
                    for sprite in self.obstacle_sprites:
                        if check_rect.colliderect(sprite.rect): collision = True; break
                    for sprite in self.npc_sprites:
                        if check_rect.colliderect(sprite.hitbox): collision = True; break
                    for sprite in self.portal_sprites:
                        if check_rect.colliderect(sprite.rect): collision = True; break
                    if collision: continue
                    player_start_rect = pygame.Rect(data['player_start'][0], data['player_start'][1], TILESIZE * 2,
                                                    TILESIZE * 2)
                    if check_rect.colliderect(player_start_rect): collision = True; continue
                    tree = Tree(new_pos,
                                [self.visible_sprites, self.obstacle_sprites, self.tree_sprites],
                                tree_surf,
                                self.graphics['stump'])
                    hb_w = int(tree.rect.width * 0.4)
                    hb_h = int(tree.rect.height * 0.2)
                    tree.hitbox = pygame.Rect(0, 0, hb_w, hb_h)
                    tree.hitbox.midbottom = tree.rect.midbottom
                    new_trees_data.append((new_pos, tree_index))
                    placed_trees += 1
                self.generated_trees[self.current_level] = new_trees_data

    def spawn_artifact(self, name, pos):
        item_id = (self.current_level, name, pos)
        if item_id not in self.collected_items:
            Artifact(pos, [self.visible_sprites, self.artifact_sprites], name)
            print(f"Spawn edildi: {name} @ {pos}")

    def change_level(self, new_level_key):
        self.current_level = new_level_key
        self.create_map()

    def handle_npc_interaction(self, npc):
        self.ui.chat_active = True
        self.ui.input_active = False
        self.ui.user_text = ""
        self.player.direction = pygame.math.Vector2(0, 0)

        # Huma görünürlüğünü sıfırla
        if hasattr(self.ui, 'huma'):
            self.ui.huma.visible = False

        if npc.npc_type == 'owl':
            self.ui.current_speaker = "Bilge Baykus Huma"
            self.ui.ai_response = "Merhaba Genç Tarihçi! Ben Huma. İstediğin zaman [H] tuşuna basarak beni yanına çağırabilirsin. Sorularını cevaplamak için uçar gelirim!"
            return

        # --- RAHİP (ZİGGURAT) ---
        if npc.npc_type == 'rahip':
            self.ui.current_speaker = "Sümer Rahibi"

            if self.quests['sumer_yazi'] == 'tamamlandi':
                self.ui.ai_response = "Kayıtlar artık güvende, teşekkürler."

            elif self.quests['sumer_yazi'] == 'alindi':
                if self.inventory.get('tablet', 0) > 0:
                    self.ui.ai_response = "Harika! Tableti yaptın. (GÖREV BİTTİ)"
                    self.quests['sumer_yazi'] = 'tamamlandi'
                    self.inventory['tablet'] -= 1
                    self.pending_huma_text = "Harika iş çıkardın! Kayıtları korudun. Şimdi nehir kenarındaki işçiye yardım et."
                else:
                    self.ui.ai_response = "Islak kili buldun mu? [C] ile tablet yap."
                # Kontrol: Tüm görevler bitti mi?
                if self.quests['sumer_tekerlek'] == 'tamamlandi':
                    self.pending_huma_text = "Sümer şehrindeki sorunları hallettin. Şimdi açılan portaldan mezopotamya bozkırlarına geri dön ve yeni maceralara atılmaya hazır ol."
                    # Portalı açmak için haritayı yenile
                    self.create_map(keep_player_pos=True)


            else:
                self.ui.ai_response = "Gelen tahılların kayıtlarını aklımda tutmakta çok zorlanıyorum. Keşke Kayıtları tutabileceğim başka bir şey olsaydı..."
                self.pending_huma_text = "Rahibe yardım etmek için Sümer şehrinden killi toprak bulursan bununla kil tablet yapabiliriz. (Kili Bulunca [C] tuşuna basarsan kil tablet yaparsın.)"
                self.quests['sumer_yazi'] = 'alindi'
            return

        # --- İŞÇİ GÖREVİ ---
        if npc.npc_type == 'isci':
            self.ui.current_speaker = "Sumer İşçisi"

            if self.quests['sumer_tekerlek'] == 'tamamlandi':
                self.ui.ai_response = "Tekerlek işimi çok kolaylaştırdı."

            elif self.quests['sumer_tekerlek'] == 'alindi':
                if self.inventory.get('tekerlek', 0) > 0:
                    self.ui.ai_response = "Artık bu tekerler sayesinde yüklerimi kolayca taşıyabileceğim. İnanılmaz! (GÖREV BİTTİ)"
                    self.quests['sumer_tekerlek'] = 'tamamlandi'
                    self.inventory['tekerlek'] -= 1
                    self.pending_huma_text = "Tebrikler! Medeniyeti ilerlettin! Şimdi Ziggurat'a git."

                    # Kontrol: Tüm görevler bitti mi?
                    if self.quests['sumer_yazi'] == 'tamamlandi':
                         self.pending_huma_text = "Sümer şehrindeki sorunları hallettin. Şimdi açılan portaldan mezopotamya bozkırlarına geri dön ve yeni maceralara atılmaya hazır ol."
                         # Portalı açmak için haritayı yenile
                         self.create_map(keep_player_pos=True)
                    else:
                         self.pending_huma_text = "Tebrikler! Medeniyeti ilerlettin! Şimdi Ziggurat'a git."


                elif self.inventory.get('kutuk', 0) > 0:
                    self.ui.ai_response = "Aha! Sağlam bir kütük bulmuşsun. Gel bunu yontup yuvarlak yapalım... (Kütük -> Tekerlek)"
                    self.inventory['kutuk'] -= 1
                    self.inventory['tekerlek'] = self.inventory.get('tekerlek', 0) + 1
                    self.pending_huma_text = "İşçiyle beraber kütüğü yontarak TEKERLEĞİ icat ettin! Tekrar konuş."


            else:
                self.ui.ai_response = "Bu taşlar çok ağır... Keşke taşımanın kolay yolu olsa."
                self.quests['sumer_tekerlek'] = 'alindi'
                self.pending_huma_text = "İşçiye yardım etmek için kütüklerle tekerlek yapabilirsin. Kütük elde etmek için ağaç kesebilirsin. (Ağaçların yanında [F] tuşuna basılı tut.)"

    def craft_tablet(self):
        if self.inventory.get('wet_clay', 0) > 0:
            self.inventory['wet_clay'] -= 1
            if 'tablet' not in self.inventory:
                self.inventory['tablet'] = 0
            self.inventory['tablet'] += 1

            self.ui.trigger_huma_speech("Harika bir işçilik! Şimdi bu tableti Ziggurat'taki rahibe götür.")

            screen_center_x = self.display_surface.get_width() // 2
            screen_center_y = self.display_surface.get_height() // 2
            if hasattr(self.ui, 'huma'):
                self.ui.huma.rect.x = screen_center_x + 40
                self.ui.huma.target_y = screen_center_y - 90
                self.ui.huma.rect.y = -100
        else:
            self.ui.trigger_huma_speech("Çantanda Islak Kil yok! Nehir kenarına bak.")
            screen_center_x = self.display_surface.get_width() // 2
            screen_center_y = self.display_surface.get_height() // 2
            if hasattr(self.ui, 'huma'):
                self.ui.huma.rect.x = screen_center_x + 40
                self.ui.huma.target_y = screen_center_y - 90
                self.ui.huma.rect.y = -100

    def check_portals(self):
        collided_portals = pygame.sprite.spritecollide(self.player, self.portal_sprites, False)
        if collided_portals:
            portal = collided_portals[0]
            self.change_level(portal.destination)

    def check_artifact_collection(self):
        collected_artifacts = pygame.sprite.spritecollide(self.player, self.artifact_sprites, False)
        for artifact in collected_artifacts:
            item_id = (self.current_level, artifact.artifact_name, artifact.rect.topleft)
            self.collected_items.add(item_id)

            item_name = artifact.artifact_name
            if item_name not in self.inventory: self.inventory[item_name] = 0
            self.inventory[item_name] += 1
            print(f"Toplandı: {item_name}")
            artifact.kill()

    def input(self):
        keys = pygame.key.get_pressed()
        if self.ui.chat_active:
            pass
        else:
            if keys[pygame.K_SPACE]:
                interaction_zone = self.player.hitbox.inflate(20, 20)
                for npc in self.npc_sprites:
                    if interaction_zone.colliderect(npc.hitbox):
                        self.handle_npc_interaction(npc)

            if keys[pygame.K_c]: self.craft_tablet()
            if self.current_level != 'hub' and keys[pygame.K_h]:
                self.pending_huma_text = "Huu huu! Beni çağırdın. Tarihle ilgili merak ettiğin her şeyi sorabilirsin!"

            # --- F TUŞU (AĞAÇ KESME) ---
            if keys[pygame.K_f]:
                interaction_range = self.player.hitbox.inflate(40, 40)
                colliding_trees = [t for t in self.tree_sprites if t.alive and interaction_range.colliderect(t.hitbox)]

                if colliding_trees:
                    target_tree = colliding_trees[0]
                    if self.chopping_tree != target_tree:
                        self.chopping_tree = target_tree
                        self.chop_progress = 0

                    self.chop_progress += 1

                    if self.chop_progress >= 120:
                        # Kesimden önce pozisyonu kaydet
                        old_midbottom = target_tree.rect.midbottom

                        target_tree.chop()

                        # Kökü (Stump) eski ağacın tabanına hizala
                        target_tree.rect.midbottom = old_midbottom
                        target_tree.hitbox.midbottom = target_tree.rect.midbottom
                        # Kütük Eşyasını Düşür
                        drop_pos = (target_tree.rect.centerx, target_tree.rect.centery + 10)

                        # Artifact oluştur
                        new_artifact = Artifact(drop_pos, [self.visible_sprites, self.artifact_sprites], 'kutuk')

                        # Eğer log görseli yüklendiyse kullan
                        if self.graphics['log']:
                            new_artifact.image = self.graphics['log']
                            new_artifact.rect = new_artifact.image.get_rect(center=drop_pos)
                            new_artifact.hitbox = new_artifact.rect.inflate(0, -10)

                        self.chopping_tree = None
                        self.chop_progress = 0
                else:
                    self.chopping_tree = None
                    self.chop_progress = 0
            else:
                self.chopping_tree = None
                self.chop_progress = 0

    def run(self):
        self.input()

        # --- Huma Mesajı Kontrolü ---
        if not self.ui.chat_active and self.pending_huma_text:
            self.ui.trigger_huma_speech(self.pending_huma_text)

            screen_center_x = self.display_surface.get_width() // 2
            screen_center_y = self.display_surface.get_height() // 2

            if hasattr(self.ui, 'huma'):
                self.ui.huma.rect.x = screen_center_x + 40
                self.ui.huma.target_y = screen_center_y - 90
                self.ui.huma.rect.y = -100

            self.pending_huma_text = None

        if not self.ui.chat_active:
            self.visible_sprites.update()

            hit = pygame.sprite.spritecollide(self.player, self.portal_sprites, False)
            if hit: self.change_level(hit[0].destination)

            hit_art = pygame.sprite.spritecollide(self.player, self.artifact_sprites, True)
            for art in hit_art:
                self.inventory[art.artifact_name] = self.inventory.get(art.artifact_name, 0) + 1
                self.collected_items.add((self.current_level, art.artifact_name, art.rect.topleft))

        if self.current_level == 'sumer_ziggurat':
            self.display_surface.fill('black')

        self.visible_sprites.custom_draw(self.player, self.floor_sprites)
        self.ui.show_location(self.current_level)
        self.ui.show_inventory(self.inventory)

        # --- UI ÇİZİMLERİ ---
        if not self.ui.chat_active:
            for npc in self.npc_sprites:
                if self.player.hitbox.colliderect(npc.talk_zone):
                    pos = self.player.rect.topleft - self.visible_sprites.offset
                    t = self.ui.font.render("[SPACE]", True, (255, 255, 255))
                    self.display_surface.blit(t, (pos.x + 30, pos.y - 20))

            # --- AĞAÇ KESME BAR ---
            if self.chopping_tree:
                pos = self.chopping_tree.rect.topleft - self.visible_sprites.offset
                bar_width = 50
                bar_height = 10
                fill_width = (self.chop_progress / 120) * bar_width

                bar_bg = pygame.Rect(pos.x + 10, pos.y - 15, bar_width, bar_height)
                pygame.draw.rect(self.display_surface, (50, 50, 50), bar_bg)

                bar_fill = pygame.Rect(pos.x + 10, pos.y - 15, fill_width, bar_height)
                pygame.draw.rect(self.display_surface, (255, 200, 0), bar_fill)

                pygame.draw.rect(self.display_surface, (255, 255, 255), bar_bg, 1)

        self.ui.show_chat()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player, floor_sprites):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        for sprite in floor_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
