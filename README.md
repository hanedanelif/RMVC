# 📊 RMVC - Rough Multi-Valued Choice Decision Support System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**RMVC (Rough Multi-Valued Choice)**, belirsizlik altında karar verme problemleri için geliştirilmiş, Rough Set Teorisi tabanlı bir algoritmik çerçevedir. Bu proje, akademik makalede tanımlanan RMVC yöntemini kullanıcı dostu bir web arayüzü ile sunmaktadır.

> 📄 **Referans Makale:** *"RMVC: A Validated Algorithmic Framework for Decision-Making Under Uncertainty"* (Mathematics, 2024)

---

## 🎯 Ne İşe Yarar?

RMVC, birden fazla kriter (parametre) altında en iyi seçeneği belirlemenize yardımcı olur:

- 🏢 **İş Kararları:** En iyi tedarikçi, müşteri veya ürün seçimi
- 🎓 **Akademik:** Aday değerlendirme, proje seçimi
- 📊 **Veri Analizi:** Çok kriterli sıralama ve puanlama
- 🔬 **Araştırma:** Soft Set ve Rough Set tabanlı karar destek sistemleri

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Yükleyin

```bash
pip install streamlit pandas plotly openpyxl
```

### 2. Uygulamayı Çalıştırın

```bash
cd RMVC
streamlit run rmvc_app_v2.py --server.port 8515
```

### 3. Tarayıcıda Açın

```
http://localhost:8515
```

---

## 📁 Dosya Yapısı

```
RMVC/
├── rmvc_app_v2.py          # 🌐 Ana web uygulaması (Streamlit)
├── RMVC-git.py             # 📟 Orijinal konsol uygulaması
├── RMVC-csv.py             # 📄 CSV entegreli konsol versiyonu
├── test_example1.py        # ✅ Makale doğrulama testi
├── Example.1..xlsx         # 📊 Örnek veri (Makaledeki Example 1)
├── README.md               # 📖 Bu dosya
├── RMVC-git-ACIKLAMA.md    # 📚 Detaylı Türkçe açıklama
└── requirements.txt        # 📦 Python bağımlılıkları
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

### Üyelik Değeri

```
M(u, eᵢ) = 1                           eğer u ∈ Φ(eᵢ)
M(u, eᵢ) = δ(u, eᵢ) / γ(eᵢ)            eğer u ∉ Φ(eᵢ)
```

### Delta Fonksiyonu

```
δ(u, eᵢ) = Σ_{v ∈ Φ(eᵢ)} |{eⱼ ∈ E : {u, v} ⊆ Φ(eⱼ)}|
```

**Açıklama:** u elemanı ile Φ(eᵢ) içindeki her v elemanının, diğer tüm kümelerde kaç kez birlikte bulunduğunu sayar.

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

1. *"RMVC: A Validated Algorithmic Framework for Decision-Making Under Uncertainty"* - Mathematics Journal, 2024
2. Pawlak, Z. (1982). Rough sets. International Journal of Computer & Information Sciences.
3. Molodtsov, D. (1999). Soft set theory—First results. Computers & Mathematics with Applications.

---

**⭐ Bu proje işinize yaradıysa yıldız vermeyi unutmayın!**
