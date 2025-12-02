# 📖 RMVC Kullanım Kılavuzu (Türkçe)

**RMVC (Relational Membership Value Calculation)** - Soft Set Teorisi tabanlı karar destek sistemi.

Bu kılavuz, RMVC uygulamasını adım adım nasıl kullanacağınızı açıklamaktadır.

---

## 📋 İçindekiler

1. [Kurulum](#-kurulum)
2. [Veri Hazırlama](#-veri-hazırlama)
3. [Uygulamayı Çalıştırma](#-uygulamayı-çalıştırma)
4. [Arayüz Kullanımı](#-arayüz-kullanımı)
5. [Sonuçları Yorumlama](#-sonuçları-yorumlama)
6. [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

## 🔧 Kurulum

### Adım 1: Python Kontrolü

Bilgisayarınızda Python 3.8 veya üzeri yüklü olmalıdır.

```bash
python --version
```

### Adım 2: Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

veya manuel olarak:

```bash
pip install streamlit pandas plotly openpyxl numpy
```

### Adım 3: Dosyaları İndirin

GitHub'dan projeyi klonlayın veya ZIP olarak indirin:

```bash
git clone https://github.com/KULLANICI_ADI/RMVC.git
cd RMVC
```

---

## 📊 Veri Hazırlama

### Excel/CSV Dosyası Nasıl Hazırlanır?

RMVC, verilerinizi bir matris formatında bekler. İki format desteklenir:

### Format A: Elemanlar Satırlarda (Önerilen)

| | Kriter1 | Kriter2 | Kriter3 | Kriter4 |
|---|---------|---------|---------|---------|
| **Eleman1** | 1 | 0 | 1 | 1 |
| **Eleman2** | 1 | 1 | 0 | 1 |
| **Eleman3** | 1 | 0 | 1 | 0 |
| **Eleman4** | 0 | 1 | 1 | 0 |
| **Eleman5** | 1 | 1 | 0 | 1 |

**Excel'de:**
- A1 hücresi boş bırakın
- B1, C1, D1... → Kriter isimleri (e1, e2, e3... veya Kalite, Fiyat, Hız...)
- A2, A3, A4... → Eleman isimleri (1, 2, 3... veya Firma A, Firma B...)
- Değerler: 1 = ait, 0 = ait değil

### Format B: Parametreler Satırlarda

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **e1** | 1 | 1 | 1 | 0 | 1 |
| **e2** | 0 | 1 | 0 | 1 | 1 |
| **e3** | 1 | 0 | 1 | 1 | 0 |
| **e4** | 1 | 1 | 0 | 0 | 1 |

> ⚠️ Bu formatı kullanıyorsanız, uygulamada **"Matrisi transpose et"** seçeneğini işaretlemelisiniz!

### Değer Anlamları

| Değer | Anlam | Örnek |
|-------|-------|-------|
| `1` | Eleman bu kritere sahip | Firma A kaliteli ürün üretiyor |
| `0` | Eleman bu kritere sahip değil | Firma A hızlı teslimat yapmıyor |
| `>0` | Ağırlıklı değer (1 olarak işlenir) | Satış miktarı, puan vb. |

### Örnek Senaryo: Tedarikçi Seçimi

5 tedarikçi firmayı 4 kritere göre değerlendiriyorsunuz:

| | Kalite | Fiyat | Teslimat | Güvenilirlik |
|---|--------|-------|----------|--------------|
| **Firma A** | 1 | 0 | 1 | 1 |
| **Firma B** | 1 | 1 | 0 | 1 |
| **Firma C** | 1 | 0 | 1 | 0 |
| **Firma D** | 0 | 1 | 1 | 0 |
| **Firma E** | 1 | 1 | 0 | 1 |

Bu tabloyu Excel'e girin ve `.xlsx` veya `.csv` olarak kaydedin.

---

## 🚀 Uygulamayı Çalıştırma

### Adım 1: Terminal/Komut İstemi Açın

Windows:
- `Win + R` → `cmd` yazın → Enter

### Adım 2: RMVC Klasörüne Gidin

```bash
cd C:\Users\KULLANICI\Downloads\RMVC
```

### Adım 3: Uygulamayı Başlatın

```bash
streamlit run rmvc_app_v2.py --server.port 8515
```

### Adım 4: Tarayıcıda Açın

Otomatik açılmazsa, tarayıcınızda şu adresi açın:

```
http://localhost:8515
```

---

## 🖥️ Arayüz Kullanımı

### Sol Panel (Sidebar)

#### 1. Dosya Yükleme
- **"Browse files"** butonuna tıklayın
- CSV veya Excel dosyanızı seçin
- Dosya yüklendikten sonra analiz otomatik başlar

#### 2. Ayarlar

| Seçenek | Açıklama |
|---------|----------|
| **Matrisi transpose et** | Dosyanızda satırlar=parametreler ise işaretleyin |
| **Boş kümeleri filtrele** | Hiç elemanı olmayan kriterleri çıkarır |
| **Kesir olarak göster** | Değerleri 1/3, 5/9 gibi kesir olarak gösterir |

### Ana Sekmeler

#### 🏆 Sonuçlar Sekmesi

- **Metrikler:** Eleman sayısı, parametre sayısı, ortalama skor, maksimum skor
- **Optimal Seçim:** En yüksek skora sahip eleman(lar)
- **Skor Tablosu:** Tüm elemanların sıralı listesi

#### 🔢 Üyelik Matrisi Sekmesi

- **Tablo:** Hesaplanan M(u, eᵢ) değerleri
- **Heatmap:** Görsel matris (sarı=1, mor=0)
- **Sütun Toplamları:** Her elemanın toplam skoru

#### 📊 Grafikler Sekmesi

- **Bar Chart:** Skorların karşılaştırması
- **Histogram:** Skor dağılımı
- **Box Plot:** İstatistiksel özet

#### 📈 Parametre Analizi Sekmesi

- Her kriterin kaç elemana sahip olduğu
- γ(eᵢ) normalizasyon katsayıları
- Hangi elemanların hangi kriterlere ait olduğu

#### 🔍 Detaylı Analiz Sekmesi

- Tek bir elemanı seçerek detaylı inceleme
- Radar chart ile parametre profili
- Sıralama ve yüzdelik bilgisi

### Sonuçları İndirme

Sayfanın altında üç indirme butonu bulunur:

| Buton | İçerik |
|-------|--------|
| **📥 Skorları İndir** | Eleman skorları (CSV) |
| **📥 Matrisi İndir** | Üyelik matrisi (CSV) |
| **📥 Parametreleri İndir** | Kriter bilgileri (CSV) |

---

## 📈 Sonuçları Yorumlama

### Skor Ne Anlama Gelir?

- **Yüksek skor** = Daha fazla kritere uyum
- **Düşük skor** = Daha az kritere uyum
- **Maksimum skor** = m (parametre sayısı) - tüm kriterlere tam uyum

### Üyelik Değerleri

| Değer | Anlam |
|-------|-------|
| `1.000` | Eleman bu kritere **tam olarak** ait |
| `0.000` | Eleman bu kritere **hiç** ait değil ve ilişki yok |
| `0.333`, `0.556` vb. | Eleman bu kritere ait değil ama **dolaylı ilişki** var |

### Dolaylı İlişki Nedir?

Bir eleman (u) bir kritere (eᵢ) ait olmasa bile, o kriterdeki diğer elemanlarla başka kriterlerde birlikte bulunuyorsa, kısmi bir üyelik değeri alır.

**Örnek:**
- Firma D, "Kalite" kriterine ait değil (0)
- Ama Firma D, Kalite kriterindeki Firma A ile "Teslimat" kriterinde birlikte
- Bu dolaylı ilişki, Firma D'ye Kalite için kısmi puan kazandırır

---

## ❓ Sık Sorulan Sorular

### S: Dosyam yüklenmiyor, ne yapmalıyım?

**C:** 
- Dosyanın `.csv` veya `.xlsx` formatında olduğundan emin olun
- İlk satır ve ilk sütunun başlık içerdiğini kontrol edin
- Boş satır/sütun olmadığından emin olun

### S: Sonuçlar makaledekiyle uyuşmuyor?

**C:**
- "Matrisi transpose et" seçeneğini kontrol edin
- Veri formatınızın doğru olduğundan emin olun
- `test_example1.py` dosyasını çalıştırarak doğrulama yapın

### S: Birden fazla eleman aynı skora sahip, hangisini seçmeliyim?

**C:** RMVC matematiksel olarak eşit skorlu elemanları eşit değerlendirir. Ek kriterler veya uzman görüşü ile karar verebilirsiniz.

### S: Ağırlıklı kriterler kullanabilir miyim?

**C:** Mevcut versiyon binary (0/1) değerler kullanır. Ağırlıklı versiyonu için kod geliştirmesi gerekir.

### S: Uygulama açılmıyor?

**C:**
- Port kullanımda olabilir, farklı port deneyin: `--server.port 8520`
- Kütüphanelerin yüklü olduğundan emin olun: `pip list`
- Python versiyonunuzu kontrol edin: `python --version`

---

## 🆘 Yardım

Sorun yaşarsanız:

1. GitHub Issues sayfasından yeni bir issue açın
2. Hata mesajını ve kullandığınız veriyi paylaşın
3. Python ve kütüphane versiyonlarınızı belirtin

---

## 📞 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.

---

**İyi analizler! 🎯**
