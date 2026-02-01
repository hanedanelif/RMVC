# MovieLens Binary Dönüşüm Metodolojisi Karşılaştırması

**Tarih:** 2026-01-29 10:30:17

---

## 1. Araştırma Sorusu

**Soru:** MovieLens veri setini RMVC algoritmasında kullanmak için binary (0/1) formatına dönüştürmenin en uygun yöntemi nedir?

## 2. Test Edilen Yöntemler

### Yöntem-1: Basit Eşikleme

**Matematiksel Tanım:**

```
B(u, m) = {
    1, eğer R(u, m) >= 4
    0, eğer R(u, m) < 4
}
```

Burada:
- `R(u, m)`: Kullanıcı u'nun film m için verdiği rating (1-5)
- `B(u, m)`: Binary matristeki değer (0/1)

**Sonuçlar:**

- 1'e dönüşen: 55375 rating (55.38%)
- 0'a dönüşen: 44625 rating (44.62%)

---

### Yöntem-2: RMVC-Uyumlu Normalizasyon + Eşikleme

**Matematiksel Tanım:**

**Adım 1: Min-Max Normalizasyon**

```
R_norm(u, m) = (R(u, m) - R_min) / (R_max - R_min)
```

Burada `R_min = 1.0` ve `R_max = 5.0`

**Adım 2: Eşik Değeri Hesaplama**

```
θ = mean({R_norm(u, m) | 0 < R_norm(u, m) < 1})
```

Yani, sadece ondalıklı normalize değerlerin ortalaması alınır.

**Hesaplanan Eşik:** θ = 0.5784

**Adım 3: Binary Dönüşüm**

```
B(u, m) = {
    1, eğer R_norm(u, m) >= θ
    0, eğer R_norm(u, m) < θ
}
```

**Sonuçlar:**

- 1'e dönüşen: 55375 rating (55.38%)
- 0'a dönüşen: 44625 rating (44.62%)

---

## 3. Karşılaştırma ve Bulgular

| Metrik | Yöntem-1 | Yöntem-2 | Fark |
|--------|----------|----------|------|
| 1'e dönüşen (%) | 55.38% | 55.38% | +0.00% |
| 0'a dönüşen (%) | 44.62% | 44.62% | +0.00% |

## 4. Metodolojik Tutarlılık

**Yöntem-2'nin Avantajları:**

1. **RMVC ile Uyumlu:** İteratif RMVC analizinde kullanılan eşikleme yaklaşımıyla metodolojik olarak tutarlıdır.
2. **Veri-Güdümlü:** Eşik değeri, verinin istatistiksel özelliklerinden (ondalıklı ortalama) otomatik olarak belirlenir.
3. **Normalize Edilmiş Ölçek:** Min-Max normalizasyon, farklı ölçeklerdeki veri setlerinin karşılaştırılabilir hale gelmesini sağlar.

## 5. Öneri

**Makale için önerilen yöntem:** Yöntem-2 (RMVC-Uyumlu Normalizasyon + Eşikleme)

**Gerekçe:**
- RMVC algoritmasının metodolojik felsefesiyle uyumludur
- Veri-güdümlü ve tekrarlanabilir bir süreç sunar
- İteratif RMVC analizinde kullanılan eşikleme mantığını yansıtır

## 6. Detaylı Adım Kayıtları

### Adım 1: Load Raw Ratings

**Zaman:** 2026-01-29 10:30:07

**Detaylar:**

- total_ratings: 100000
- users: 943
- movies: 1682
- rating_min: 1
- rating_max: 5
- rating_mean: 3.5299
- rating_std: 1.1257

### Adım 2: Method-1: Simple Threshold

**Zaman:** 2026-01-29 10:30:07

**Detaylar:**

- method: Simple Threshold
- threshold: 4
- total_ratings: 100000
- ones: 55375
- zeros: 44625
- ones_percentage: 55.3750
- zeros_percentage: 44.6250

### Adım 3: Method-2: RMVC-Style

**Zaman:** 2026-01-29 10:30:08

**Detaylar:**

- method: RMVC-Style Normalization + Threshold
- min_rating: 1.0000
- max_rating: 5.0000
- mean_normalized: nan
- mean_fractional: 0.5784
- threshold: 0.5784
- total_ratings: 100000
- ones: 55375
- zeros: 44625
- ones_percentage: 55.3750
- zeros_percentage: 44.6250

### Adım 4: Method Comparison

**Zaman:** 2026-01-29 10:30:09

**Detaylar:**

- different_cells: 0
- difference_percentage: 0.0000
- comparison_results: [Liste, 4 öğe]

