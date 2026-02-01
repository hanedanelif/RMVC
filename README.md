# 📊 RMVC - Relational Membership Value Calculation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **⚠️ ÖNEMLİ GÜNCELLEME (1 Şubat 2026):**  
> **V3 Ana Versiyondur!** Delta fonksiyonunda kritik düzeltme yapıldı (kendi kümesi hariç hesaplama).  
> - ✅ **Kullanın:** `rmvc_app_v3.py` (Port 8516) - Makaledeki formüle tam uyumlu  
> - ⚠️ **Yedek:** `rmvc_app_v2.py` (Port 8515) - Eski versiyon (referans için saklanıyor)  
> - 📄 Detaylar: [DELTA_FUNCTION_FIX_REPORT.md](DELTA_FUNCTION_FIX_REPORT.md)

**RMVC (Relational Membership Value Calculation)**, belirsizlik altında karar verme problemleri için geliştirilmiş, **Soft Set Teorisi (Esnek Küme Teorisi)** tabanlı yeni bir algoritmik çerçevedir. Bu proje, akademik makalede tanımlanan RMVC yöntemini ve ilişkisel üyelik fonksiyonunu kullanıcı dostu bir web arayüzü ile sunmaktadır.

> 📄 **Referans Makale:** Dayioglu, A.; Erdogan, F.O.; Celik, B. *"RMVC: A Validated Algorithmic Framework for Decision-Making Under Uncertainty"*. Mathematics **2025**, 13, 2693.

---

## 🎯 Ne İşe Yarar?

RMVC, geleneksel ikili (binary) yaklaşımların aksine, adayların sahip olmadığı özellikler arasındaki **ilişkisel bağları (relational connections)** analiz ederek daha hassas bir sıralama sunar:

- 🏢 **İş Kararları:** En iyi tedarikçi, müşteri veya ürün seçimi
- 🎓 **Akademik:** Aday değerlendirme, proje seçimi
- 📊 **Veri Analizi:** Çok kriterli sıralama ve puanlama (MCDM)
- 🔬 **Araştırma:** Soft Set tabanlı karar destek sistemleri ve yapay zeka araçları

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Yükleyin

```bash
pip install streamlit pandas plotly openpyxl
```

### 2. Uygulamayı Çalıştırın

**V3 (Önerilen - Düzeltilmiş Versiyon):**
```bash
cd RMVC
streamlit run rmvc_app_v3.py --server.port 8516
```

**V2 (Yedek - Eski Versiyon):**
```bash
streamlit run rmvc_app_v2.py --server.port 8515
```

### 3. Tarayıcıda Açın

**V3:** `http://localhost:8516`  
**V2:** `http://localhost:8515`

---

## 📁 Dosya Yapısı

```
RMVC/
├── rmvc_app_v2.py                      # 🌐 Ana web uygulaması (Streamlit)
├── RMVC-git.py                         # 📟 Orijinal konsol uygulaması
├── RMVC-csv.py                         # 📄 CSV entegreli konsol versiyonu
├── test_example1.py                    # ✅ Makale doğrulama testi
├── Example.1..xlsx                     # 📊 Örnek veri (Makaledeki Example 1)
├── README.md                           # 📖 Bu dosya
├── RMVC-git-ACIKLAMA.md                # 📚 Detaylı Türkçe açıklama
├── ITERATIVE_ANALYSIS_COMPARISON.md    # 🔄 İteratif analiz karşılaştırma raporu (YENİ!)
└── requirements.txt                    # 📦 Python bağımlılıkları
```

---

## 📊 Veri Formatı

### Girdi Dosyası (CSV veya Excel)

RMVC iki farklı matris formatını destekler:

#### Format 1: Satırlar = Elemanlar, Sütunlar = Parametreler (Varsayılan)

```csv
,e1,e2,e3,e4
1,1,0,1,1
2,1,1,0,1
3,1,0,1,0
4,0,1,1,0
5,1,1,0,1
```

#### Format 2: Satırlar = Parametreler, Sütunlar = Elemanlar (Transpose Gerekli)

```csv
,1,2,3,4,5
e1,1,1,1,0,1
e2,0,1,0,1,1
e3,1,0,1,1,0
e4,1,1,0,0,1
```

> ⚠️ **Not:** Format 2 kullanıyorsanız, uygulamada **"Matrisi transpose et"** seçeneğini işaretleyin.

### Değerler

| Değer | Anlam |
|-------|-------|
| `0` | Eleman bu parametreye **ait değil** |
| `1` veya `>0` | Eleman bu parametreye **ait** |

### Terminoloji

| Terim | Açıklama | Örnek |
|-------|----------|-------|
| **U (Evrensel Küme)** | Tüm elemanlar/adaylar | Firmalar, Ürünler, Kişiler |
| **E (Parametre Kümesi)** | Kriterler/özellikler | Kalite, Fiyat, Hız |
| **Φ(eᵢ)** | eᵢ parametresine ait elemanlar | Kaliteli firmalar kümesi |

---

## 🧮 Matematiksel Formüller

Makalede tanımlanan **İlişkisel Üyelik Fonksiyonu (Relational Membership Function)** temel alınmıştır.

> **Not:** Makalede üyelik fonksiyonu Θ (Theta) sembolü ile gösterilir. Kodda `M` kullanılmıştır.

### Üyelik Değeri (Θ)

```
Θ(u, eᵢ) = 1                           eğer u ∈ Φ(eᵢ)
Θ(u, eᵢ) = δ(u, eᵢ) / γ(eᵢ)            eğer u ∉ Φ(eᵢ)
```

### Delta Fonksiyonu (Co-occurrence)

```
δ(u, eᵢ) = Σ_{v ∈ Φ(eᵢ)} Σ_{eₖ ∈ E\{eᵢ}} 𝟙_{if {u, v} ⊆ Φ(eₖ)}
```

**Açıklama:** u elemanı ile Φ(eᵢ) içindeki elemanların, diğer parametre kümelerinde (E\{eᵢ}) ne sıklıkla birlikte bulunduğunu ölçer.

### Normalizasyon Katsayısı

```
γ(eᵢ) = |Φ(eᵢ)| × (m - 1)
```

- `|Φ(eᵢ)|`: eᵢ kümesindeki eleman sayısı
- `m`: Toplam parametre sayısı
- `(m - 1)`: Diğer parametrelerin sayısı

### Toplam Skor

```
S(u) = Σ_{eᵢ ∈ E} M(u, eᵢ)
```

**En yüksek skora sahip eleman optimal seçimdir.**

---

## 📖 Kullanım Kılavuzu

### Web Arayüzü (Önerilen)

1. **Uygulamayı başlatın:**
   ```bash
   streamlit run rmvc_app_v2.py --server.port 8515
   ```

2. **Dosya yükleyin:**
   - Sol panelden CSV veya Excel dosyanızı yükleyin
   - Gerekirse "Matrisi transpose et" seçeneğini işaretleyin

3. **Sonuçları inceleyin:**
   - **🏆 Sonuçlar:** Skorlar ve optimal seçim
   - **🔢 Üyelik Matrisi:** Hesaplanan M değerleri ve heatmap
   - **📊 Grafikler:** Bar chart, histogram, box plot
   - **📈 Parametre Analizi:** Kriter detayları
   - **🔍 Detaylı Analiz:** Eleman bazlı radar chart
   - **🔄 İteratif Analiz:** Eşik tabanlı iteratif RMVC analizi (YENİ!)

4. **Sonuçları indirin:**
   - Skorları CSV olarak indirin
   - Üyelik matrisini CSV olarak indirin

### Konsol Kullanımı

```bash
# CSV dosyası ile
python RMVC-csv.py

# Test dosyası ile doğrulama
python test_example1.py
```

---

## ✅ Doğrulama (Example 1)

Makaledeki Example 1 ile test sonuçları:

### Girdi

```
U = {1, 2, 3, 4, 5}
Φ(e₁) = {1, 2, 3, 5}
Φ(e₂) = {2, 4, 5}
Φ(e₃) = {1, 3, 4}
Φ(e₄) = {1, 2, 5}
```

### Üyelik Matrisi (Hesaplanan)

| Param | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|
| e₁ | 1.000 | 1.000 | 1.000 | **0.333** | 1.000 |
| e₂ | **0.556** | 1.000 | **0.333** | 1.000 | 1.000 |
| e₃ | 1.000 | **0.444** | 1.000 | 1.000 | **0.444** |
| e₄ | 1.000 | 1.000 | **0.444** | **0.333** | 1.000 |

### Doğrulama

| Değer | Hesaplanan | Makaledeki | Durum |
|-------|------------|------------|-------|
| M(4, e₁) | 1/3 = 0.333 | 0.333 | ✅ |
| M(1, e₂) | 5/9 = 0.556 | 0.556 | ✅ |
| M(3, e₂) | 1/3 = 0.333 | 0.333 | ✅ |
| M(2, e₃) | 4/9 = 0.444 | 0.444 | ✅ |
| M(5, e₃) | 4/9 = 0.444 | 0.444 | ✅ |
| M(3, e₄) | 4/9 = 0.444 | 0.444 | ✅ |
| M(4, e₄) | 1/3 = 0.333 | 0.333 | ✅ |

### Skorlar

| Eleman | Skor | Kesir |
|--------|------|-------|
| **1** | **3.556** | 32/9 ⭐ |
| 2 | 3.444 | 31/9 |
| 5 | 3.444 | 31/9 |
| 3 | 2.778 | 25/9 |
| 4 | 2.667 | 8/3 |

**🏆 Optimal Seçim: Eleman 1**

---

## 🔄 İteratif RMVC Analizi (Yeni Özellik!)

### Ne İşe Yarar?

İteratif analiz, üyelik matrisine **eşik değer (threshold)** uygulayarak yeni binary matrisler oluşturur ve RMVC algoritmasını tekrar çalıştırır. Bu sayede:

- 📊 Zayıf ilişkilerin etkisini gözlemleyebilirsiniz
- 🔍 Farklı eşik değerlerinde sıralama değişimlerini analiz edebilirsiniz
- 🎯 Güçlü ve zayıf ilişkileri ayırt edebilirsiniz
- 📈 İteratif olarak sonuçların nasıl değiştiğini görebilirsiniz

### Nasıl Çalışır?

1. **İlk RMVC Hesaplaması:** Orijinal binary matris ile üyelik matrisi hesaplanır
2. **Eşik Değer Seçimi:** 0.0 ile 1.0 arası bir eşik değer belirlersiniz (örn: 0.50)
3. **Eşikleme Modu Seçimi:**
   - **🔴 Binary Mod:** Eşik altındaki değerler **0'a dönüşür** (zayıf ilişkiler kesilir)
   - **🟡 Mixed Mod:** Eşik altındaki değerler **aynı kalır** (zayıf ilişkiler korunur)
4. **Yeni İterasyon:** Eşiklenmiş matris ile yeni RMVC hesaplaması yapılır
5. **Karşılaştırma:** Sıralama değişimleri, skor değişimleri ve istatistikler gösterilir

### Eşikleme Kuralları

#### Binary Mod (Eşik Altı → 0)
```
Değer > Eşik  →  1  (Güçlü ilişki)
Değer ≤ Eşik  →  0  (Zayıf ilişki kesilir)
```

**Örnek (Eşik = 0.50):**
```
0.3333 → 0
0.4444 → 0
0.5556 → 1
1.0000 → 1
```

**Kullanım Senaryoları:**
- ✅ Sadece güçlü ilişkilere odaklanmak
- ✅ Gürültüyü temizlemek
- ✅ Kararlı sıralama elde etmek
- ✅ Kesin kararlar almak

#### Mixed Mod (Eşik Altı → Aynı Kalır)
```
Değer > Eşik  →  1  (Güçlü ilişki)
Değer ≤ Eşik  →  Değer (Zayıf ilişki korunur)
```

**Örnek (Eşik = 0.50):**
```
0.3333 → 0.3333 (aynı kaldı)
0.4444 → 0.4444 (aynı kaldı)
0.5556 → 1
1.0000 → 1
```

**Kullanım Senaryoları:**
- ✅ Zayıf ilişkileri de değerlendirmek
- ✅ Sıralama değişimlerini gözlemlemek
- ✅ İkinci şans vermek
- ✅ Keşifsel analiz yapmak

### Karşılaştırma Tablosu

| Özellik | Binary Mod | Mixed Mod |
|---------|------------|-----------|
| **Eşik altı değerler** | 0'a dönüşür | Aynı kalır |
| **Bilgi kaybı** | Var (zayıf ilişkiler kesilir) | Yok (tüm bilgi korunur) |
| **Sıralama kararlılığı** | Yüksek | Düşük |
| **Ayırt edicilik** | Yüksek | Düşük (homojenleşme riski) |
| **Kullanım** | Kesin kararlar | Keşifsel analiz |

### Örnek Sonuçlar

**Example 1 Verisi, Eşik = 0.50:**

| Mod | Yükselenler | Düşenler | Aynı Kalanlar | Skor Değişimi |
|-----|-------------|----------|---------------|---------------|
| **Binary** | 0 | 0 | 5 (Tümü) | Küçük (+0.08 ~ +0.44) |
| **Mixed** | 2 | 1 | 2 | Büyük (+0.44 ~ +1.33) |

**Detaylı karşılaştırma için:** [ITERATIVE_ANALYSIS_COMPARISON.md](ITERATIVE_ANALYSIS_COMPARISON.md)

### Kullanım Adımları

1. **Dosya yükleyin** ve ilk RMVC hesaplamasını yapın
2. **"🔄 İteratif Analiz"** sekmesine gidin
3. **Eşik değer** seçin (slider ile 0.0 - 1.0 arası)
4. **Eşikleme modu** seçin:
   - 🔴 "0'a dönüştür (Binary)" veya
   - 🟡 "Aynı kalsın (Mixed)"
5. **"Eşikleme Uygula"** butonuna tıklayın
6. **Sonuçları inceleyin:**
   - Eşiklenmiş matris
   - Yeni üyelik matrisi
   - Sıralama değişimleri (🟢 Yükseldi, 🔴 Düştü, ⚪ Aynı)
   - İstatistikler ve grafikler
7. **İsterseniz tekrarlayın:** Yeni iterasyonlar oluşturup karşılaştırın

### İteratif Strateji Önerileri

**Yaklaşım 1: Aşamalı Temizleme**
1. İterasyon 1: Binary (0.5) → Gürültüyü temizle
2. İterasyon 2: Mixed (0.6) → Zayıf ilişkileri değerlendir
3. İterasyon 3: Binary (0.7) → Final kararı ver

**Yaklaşım 2: Karşılaştırmalı Analiz**
1. İterasyon 1: Binary (0.5) → Kararlı sonuç
2. İterasyon 2: Mixed (0.5) → Alternatif sonuç
3. Karşılaştır ve karar ver

**Yaklaşım 3: Eşik Tarama**
1. Farklı eşik değerleri dene (0.3, 0.5, 0.7)
2. Sıralama değişimlerini gözlemle
3. Optimal eşik değerini belirle

**🏆 Optimal Seçim: Eleman 1**

---

## 🖼️ Ekran Görüntüleri

### Ana Sayfa
- Dosya yükleme paneli
- Transpose ve filtre seçenekleri
- Formül gösterimi

### Sonuçlar Sekmesi
- Metrikler (eleman sayısı, parametre sayısı, ortalama skor)
- Optimal seçim vurgusu
- Sıralı skor tablosu

### Üyelik Matrisi
- Interaktif heatmap
- Sütun toplamları (skorlar)

### Grafikler
- Bar chart (skorlar)
- Histogram (dağılım)
- Box plot (istatistikler)

### Detaylı Analiz
- Eleman seçimi
- Radar chart (parametre profili)

---

## 🔧 Geliştirici Notları

### Önemli Düzeltmeler (v2)

1. **Delta Fonksiyonu Hatası:**
   - ❌ Eski: `break` ile sadece ilk küme sayılıyordu
   - ✅ Yeni: Tüm kümelerde ikili sayımı yapılıyor

2. **Matris Yönü:**
   - Satırlar = Parametreler (eᵢ)
   - Sütunlar = Elemanlar (u)

3. **Kesirli Hesaplama:**
   - `Fraction` sınıfı ile hassas aritmetik

### Bağımlılıklar

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
```

---

## 📄 Lisans

Bu proje MIT lisansı altında sunulmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Push edin (`git push origin feature/YeniOzellik`)
5. Pull Request açın

---

## 📬 İletişim

Sorularınız için issue açabilirsiniz.

---

## 📚 Referanslar

1. Dayioglu, A.; Erdogan, F.O.; Celik, B. *"RMVC: A Validated Algorithmic Framework for Decision-Making Under Uncertainty"*. Mathematics **2025**, 13, 2693.
2. Molodtsov, D. (1999). Soft set theory—First results. Computers & Mathematics with Applications.

---

**⭐ Bu proje işinize yaradıysa yıldız vermeyi unutmayın!**
