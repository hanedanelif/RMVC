# 📊 MovieLens Yoğunluk Analizi Raporu

**Tarih:** 2026-01-29 10:01:25

---

## 1. Genel Bilgiler

- **Veri Seti:** MovieLens 100k
- **Global Yoğunluk:** %3.4912
- **Analiz Edilen Bölge Sayısı:** 8

## 2. Bölge Bazlı Yoğunluk Analizi

| Boyut | Yoğunluk (%) | İyileşme Faktörü |
|-------|--------------|------------------|
| 3x5 | 100.0000 | 28.64x |
| 5x10 | 88.0000 | 25.21x |
| 10x20 | 80.5000 | 23.06x |
| 20x30 | 79.0000 | 22.63x |
| 30x50 | 70.0667 | 20.07x |
| 50x75 | 64.0267 | 18.34x |
| 75x100 | 56.6933 | 16.24x |
| 100x150 | 49.0800 | 14.06x |

## 3. Sonuçlar

- **En Yoğun Bölge:** 3x5 (%100.0000)
- **Maksimum İyileşme:** 28.64x

## 4. Yorum

Tekstil veri setinde olduğu gibi, MovieLens veri setinde de **Pareto İlkesi** geçerlidir:

- En aktif kullanıcılar ve en popüler filmler matrisin sol üst köşesinde toplanır.
- Bu bölge, genel matrise kıyasla çok daha yoğundur.
- RMVC algoritması için bu yoğun bölgeler, daha iyi sonuçlar üretebilir.

## 5. Öneriler

1. RMVC analizini önce yoğun bölgelerde test edin.
2. Farklı boyutlardaki matrisleri karşılaştırarak optimal boyutu belirleyin.
3. Cold start problemini azaltmak için yoğun bölgedeki kullanıcıları önceliklendirin.

## 6. Oluşturulan Dosyalar

- datasets/movielens_dense_*.csv (8 farklı matris)
- analysis_plots/movielens_density_heatmaps.png
- analysis_plots/movielens_density_comparison.png
- MOVIELENS_DENSITY_REPORT.md