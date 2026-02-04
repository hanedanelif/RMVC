# MovieLens Yoğun Matrisler - Yöntem Karşılaştırması

**Tarih:** 2026-01-29 13:02:09

---

## 1. Yaklaşım

**Method-1:** Sabit eşik (rating >= 4)

**Method-2:** Adaptif eşik
- Her parça için ayrı normalize edilir
- Her parçanın ondalıklı ortalaması eşik olarak kullanılır
- Parça boyutu büyüdükçe eşik değişebilir

## 2. Sonuçlar

| Boyut | M1 Eşik | M1 Yoğ. | M2 Eşik | M2 Yoğ. | Fark |
|-------|---------|---------|---------|---------|------|
| 3x5 | 4 | 46.67% | 0.4667 | 46.67% | +0.00% |
| 5x10 | 4 | 52.00% | 0.5926 | 52.00% | +0.00% |
| 10x20 | 4 | 59.00% | 0.5909 | 59.00% | +0.00% |
| 20x30 | 4 | 54.50% | 0.6027 | 54.50% | +0.00% |
| 30x50 | 4 | 57.73% | 0.6074 | 57.73% | +0.00% |
| 50x75 | 4 | 52.64% | 0.6056 | 52.64% | +0.00% |
| 75x100 | 4 | 49.43% | 0.6062 | 49.43% | +0.00% |
| 100x150 | 4 | 43.48% | 0.6062 | 43.48% | +0.00% |

## 3. Gözlemler

- **En büyük fark:** 3x5 (+0.00%)
- **Ortalama fark:** +0.00%

## 4. Sonuç

Method-2, her parça için **adaptif eşik** kullanır. Küçük parçalarda eşik daha yüksek (daha seçici), büyük parçalarda daha düşük (daha kapsayıcı) olabilir.

## 5. Oluşturulan Dosyalar

- `movielens_method1_3x5.csv`
- `movielens_method2_3x5.csv`
- `movielens_method1_5x10.csv`
- `movielens_method2_5x10.csv`
- `movielens_method1_10x20.csv`
- `movielens_method2_10x20.csv`
- `movielens_method1_20x30.csv`
- `movielens_method2_20x30.csv`
- `movielens_method1_30x50.csv`
- `movielens_method2_30x50.csv`
- `movielens_method1_50x75.csv`
- `movielens_method2_50x75.csv`
- `movielens_method1_75x100.csv`
- `movielens_method2_75x100.csv`
- `movielens_method1_100x150.csv`
- `movielens_method2_100x150.csv`
