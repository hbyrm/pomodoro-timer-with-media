# 🍅 Gelişmiş Medya Oynatıcılı Pomodoro Zamanlayıcı

Bu proje, odaklanma sürelerinizi (Pomodoro) yönetirken aynı zamanda favori müzik listelerinizi (YouTube, Yerel Dosyalar, SoundCloud vb.) tek bir arayüzden oynatabilmeniz için tasarlanmış modern bir masaüstü uygulamasıdır.

> ✨ **Önemli Not:** Bu proje, yazılım geliştirme sürecinde **Yapay Zeka (AI)** asistanlığı ve yönlendirmeleri kullanılarak modern temiz kodlama prensiplerine uygun olarak geliştirilmiştir.

---

## 🎯 Yapılış Amacı
Geleneksel Pomodoro uygulamaları tarayıcıda çok yer kaplamakta, müzik dinlemek için ise Spotify veya YouTube gibi harici sekmeler arasında sürekli geçiş yapılması gerekmektedir. Bu durum odaklanma (fokus) kaybına yol açar. 

Bu projenin amacı:
* Çalışma ve mola süreçlerini tek bir şık arayüzden takip etmek.
* Tarayıcı sekmelerinde boğulmadan, doğrudan uygulama içinden toplu link veya yerel müzik dosyası oynatabilmek.
* Ekranı kaplamayan, şeffaflaşabilen (Hayalet Modu) bir asistan araç sunmaktır.

---

## 🚀 Öne Çıkan Özellikler

* **Çoklu URL Giriş Desteği:** YouTube, SoundCloud, Bandcamp gibi platformlardan kopyaladığınız onlarca linki satır satır yapıştırıp tek tıkla çalma listenize ekleyebilirsiniz.
* **Sürükle-Bırak Listeleri:** Bilgisayarınızdaki `.mp3`, `.wav` gibi ses dosyalarını doğrudan listenin üzerine sürükleyerek ekleyebilirsiniz.
* **Hayalet Modu (Ghost Mode):** Tek tıkla uygulamayı şeffaf hale getirebilir ve tıklama geçirmez (click-through) yapabilirsiniz. Böylece kod yazarken veya çalışırken ekranınızın bir köşesinde sürekli asılı kalır.
* **İnteraktif Domates Kadranı:** Fare ile domates üzerindeki çarkı çevirerek zamanı manuel olarak da ayarlayabilirsiniz.
* **Dinamik Ölçekleme:** Pencere boyutunu değiştirdiğinizde tüm arayüz elementleri otomatik olarak yeniden boyutlandırılır.

---

## 💻 Kurulum ve Çalıştırma (Hiç Bilmeyenler İçin)

Uygulamayı bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla takip etmeniz yeterlidir:

### 1. Python Kurulumu
Bilgisayarınızda Python yüklü olmalıdır. Eğer yüklü değilse [python.org](https://www.python.org/) adresinden indirip kurun. *Kurulum yaparken **"Add Python to PATH"** seçeneğini işaretlemeyi unutmayın.*

### 2. Gerekli Kütüphanelerin Yüklenmesi
Sistem terminalini (Komut İstemi / CMD) açın ve aşağıdaki komutu yapıştırarak gerekli paketleri yükleyin:
```bash
pip install PyQt6 yt_dlp pywin32