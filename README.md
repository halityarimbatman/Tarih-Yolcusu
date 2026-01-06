Tarih Yolcusu: İlk Uygarlıklar 🏺📜

Tarih Yolcusu, oyuncuları Mezopotamya'nın gizemli topraklarına götüren, Sümer medeniyetini keşfederken eğiten ve yapay zeka destekli bir rehber eşliğinde tarihsel görevleri tamamlamalarını sağlayan 2D bir macera oyunudur.

🌟 Özellikler

Yapay Zeka Destekli Rehber (Huma): Google Gemini API ile güçlendirilmiş bilge baykuş Huma, tarihle ilgili tüm sorularınızı yanıtlar ve size rehberlik eder.

Eğitici Görevler: Tekerleğin icadına yardım edin, kil tabletler hazırlayarak yazının korunmasını sağlayın.

Keşif ve Crafting: Ağaç kesin, kütük toplayın, ıslak kil bulun ve bunları işleyerek tarihi eserlere dönüştürün.

Canlı Pixel Art Dünyası: Hub (Mezopotamya Bozkırları), Sümer Şehri ve görkemli Ziggurat tapınağı arasında portallarla seyahat edin.

Dinamik Etkileşim: NPC'lerle konuşun, envanterinizi yönetin ve tarihe tanıklık edin.

🏗️ Yazılım Mimarisi ve OOP Prensipleri

Bu proje, Python ve Pygame kullanılarak Nesne Yönelimli Programlama (OOP) prensiplerine sıkı sıkıya bağlı kalınarak geliştirilmiştir. Kod tabanı, modülerlik ve sürdürülebilirlik gözetilerek tasarlanmıştır.

1. Sınıflar ve Nesneler (Classes & Objects)

Oyun dünyasındaki her varlık bir nesne olarak modellenmiştir.

Game Sınıfı: Oyunun ana döngüsünü, ekranı ve zamanlayıcıyı yöneten merkezi sınıftır.

Level Sınıfı: Harita yükleme, sprite grupları, çarpışma kontrolleri ve oyun mantığının (görevler, envanter) yönetildiği kapsayıcı sınıftır.

Player ve NPC Sınıfları: Oyuncu ve etkileşime geçilebilen karakterlerin özelliklerini (hız, konum, diyalog) tutar.

2. Kalıtım (Inheritance)

Kod tekrarını önlemek ve hiyerarşik bir yapı kurmak için kalıtım etkin bir şekilde kullanılmıştır.

pygame.sprite.Sprite: Tüm görsel nesneler (Player, Tile, NPC, Particle) Pygame'in temel Sprite sınıfından türetilmiştir.

Tile Sınıfı: Temel yapı taşıdır. Tree (Ağaç), Water (Su), Artifact (Eser) ve Portal sınıfları Tile sınıfından miras alarak özelleşmiş davranışlar (örn: ağaç kesme animasyonu, suyun akışı) kazanmıştır.

3. Çok Biçimlilik (Polymorphism)

Farklı nesnelerin aynı arayüz üzerinden farklı davranışlar sergilemesi sağlanmıştır.

YSortCameraGroup: Bu özel kamera grubu, draw metodunu geçersiz kılarak (override), nesnelerin Y koordinatına göre (derinlik algısı yaratarak) ekrana çizilmesini sağlar. Hem oyuncu hem de bir ağaç aynı grup içindedir ancak kamera her ikisini de kendi konumuna göre farklı şekilde işler.

Etkileşim: Oyuncu [SPACE] tuşuna bastığında karşısındaki nesne bir NPC ise konuşma başlar, bir ağaç ise kesme işlemi tetiklenir (farklı tepkiler).

4. Kapsülleme (Encapsulation)

Veriler ve bu verileri işleyen metotlar sınıflar içinde gizlenmiştir.

UI Sınıfı: Arayüz çizimi, fontlar ve envanter verileri UI sınıfı içinde tutulur. Dışarıdan sadece show_chat() veya show_inventory() gibi metotlarla erişilir, iç çizim mantığı dış dünyadan soyutlanmıştır.

Level Yönetimi: Sprite grupları (visible_sprites, obstacle_sprites) sadece Level sınıfı tarafından yönetilir; dışarıdan doğrudan müdahale engellenmiştir.

5. Soyutlama (Abstraction)

Karmaşık işlemler basit arayüzlerin arkasına gizlenmiştir.

ask_ai(text): Arka planda Google Gemini API'ye bağlanma, model seçme, hata yönetimi ve Threading (iş parçacığı) işlemleri UI sınıfı içinde soyutlanmıştır. Oyun döngüsü sadece "soru sor" komutunu verir, arka plandaki karmaşıklığı bilmez.

create_map(): Haritanın CSV veya görsel dosyalardan okunup oyun dünyasına yerleştirilmesi işlemi tek bir metot altında soyutlanmıştır.

🎮 Kontroller

Tuş |---|---|İşlev

W, A, S, D veya Ok Tuşları |---|---| Karakteri hareket ettirir

SPACE (Boşluk)

NPC'lerle konuş / Etkileşime gir

H

Bilge Baykuş Huma'yı çağır (AI Sohbet)

F (Basılı Tut)

Ağaç kes

C

Eşya üret (Craft - Örn: Kil Tablet)

ENTER

Sohbet penceresinde mesajı gönder

ESC

Sohbet pencresini kapat
🛠️ Kurulum Talimatları

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

Gereksinimler

Python 3.10 veya üzeri

İnternet bağlantısı (Yapay zeka özellikleri için gereklidir)

Adım 1: Projeyi Klonlayın

Terminali veya Komut İstemi'ni açın ve aşağıdaki komutu yazın:

git clone [https://github.com/KULLANICI_ADINIZ/Tarih-Yolcusu-Ilk-Uygarliklar.git](https://github.com/KULLANICI_ADINIZ/Tarih-Yolcusu-Ilk-Uygarliklar.git)
cd Tarih-Yolcusu-Ilk-Uygarliklar


Adım 2: Sanal Ortam Oluşturun (Önerilen)

Kütüphanelerin sisteminize karışmaması için sanal ortam kurun:

Windows için:

python -m venv .venv
.venv\Scripts\activate


Mac/Linux için:

python3 -m venv .venv
source .venv/bin/activate


Adım 3: Gerekli Kütüphaneleri Yükleyin

pip install -r requirements.txt


Adım 4: API Anahtarı (Opsiyonel ama Önemli)

Oyun, Google Gemini API kullanmaktadır. Oyunun içinde varsayılan bir anahtar bulunabilir ancak kendi anahtarınızı kullanmanız önerilir.

Google AI Studio adresinden ücretsiz bir API anahtarı alın.

isimsiz_oyun/code/ui.py dosyasını açın.

self.api_key = "..." satırını kendi anahtarınızla değiştirin.

Adım 5: Oyunu Başlatın

cd isimsiz_oyun
python main.py


🗺️ Oynanış İpuçları

Başlangıç: Oyuna "Hub" bölgesinde başlarsınız. Sağ taraftaki portalı kullanarak Sümer şehrine gidin.

Tekerlek Görevi: Nehir kenarındaki işçiyle konuşun. Ağaç keserek "Kütük" elde edin ve ona götürün.

Yazı Görevi: İşçinin görevini bitirdikten sonra Ziggurat'a gidin. Rahip sizden tablet isteyecektir. Nehir kenarından "Islak Kil" bulun ve [C] tuşuyla tablet yapın.

Final: Her iki görevi de tamamladığınızda Sümer şehrinin girişinde açılan yeni portaldan eve dönün.

🤝 Katkıda Bulunma

Bu proje açık kaynaklıdır. Geliştirmek için "Fork" yapabilir, hataları "Issues" kısmından bildirebilir veya "Pull Request" gönderebilirsiniz.

📜 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.


