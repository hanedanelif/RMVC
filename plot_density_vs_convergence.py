# -*- coding: utf-8 -*-
"""
Veri Yoğunluğu vs Yakınsama Hızı Grafiği
========================================
Epsilon düzeltmeli sonuçları kullanarak scatter plot + curve fitting
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'

# JSON'dan veri oku
with open('epsilon_corrected_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Veri setine göre ayır
movielens_density = []
movielens_iterations = []
textile_density = []
textile_iterations = []

for test in data:
    density = test['density']
    iterations = test['final_iteration']
    
    if test['dataset'] == 'MovieLens':
        movielens_density.append(density)
        movielens_iterations.append(iterations)
    else:  # Textile
        textile_density.append(density)
        textile_iterations.append(iterations)

# Tüm verileri birleştir
all_density = movielens_density + textile_density
all_iterations = movielens_iterations + textile_iterations

print(f"Toplam Veri Noktası: {len(all_density)}")
print(f"MovieLens: {len(movielens_density)}, Tekstil: {len(textile_density)}")

# NumPy array'e çevir
x_data = np.array(all_density)
y_data = np.array(all_iterations)

# Sıralama (grafikte smooth eğri için)
sort_indices = np.argsort(x_data)
x_sorted = x_data[sort_indices]
y_sorted = y_data[sort_indices]

# Eğri uydurma fonksiyonları
def linear(x, a, b):
    """y = ax + b"""
    return a * x + b

def polynomial_2(x, a, b, c):
    """y = ax^2 + bx + c"""
    return a * x**2 + b * x + c

def exponential(x, a, b, c):
    """y = a * exp(bx) + c"""
    return a * np.exp(b * x) + c

def logarithmic(x, a, b):
    """y = a * ln(x) + b"""
    return a * np.log(x + 1) + b  # +1 to avoid log(0)

# Her model için fitting yap
models = {
    'Linear': (linear, 2),
    'Polynomial (2nd)': (polynomial_2, 3),
    'Logarithmic': (logarithmic, 2),
}

best_model = None
best_r2 = -np.inf
best_params = None
best_fitted = None

print("\n" + "="*60)
print("EĞRİ UYDURMA SONUÇLARI")
print("="*60)

for model_name, (func, param_count) in models.items():
    try:
        params, _ = curve_fit(func, x_data, y_data, maxfev=10000)
        y_fitted = func(x_data, *params)
        
        # R² hesapla
        ss_res = np.sum((y_data - y_fitted) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        print(f"\n{model_name}:")
        print(f"  R² = {r2:.4f}")
        print(f"  Parametreler: {params}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model_name
            best_params = params
            best_fitted = y_fitted
    except Exception as e:
        print(f"\n{model_name}: BAŞARISIZ ({e})")

print(f"\n{'='*60}")
print(f"EN İYİ MODEL: {best_model} (R² = {best_r2:.4f})")
print(f"{'='*60}")

# Grafik çiz
fig, ax = plt.subplots(figsize=(12, 8))

# Scatter plot
ax.scatter(movielens_density, movielens_iterations, 
           s=120, alpha=0.7, c='#3498db', edgecolors='black', 
           linewidths=1.5, label='MovieLens', zorder=3)
ax.scatter(textile_density, textile_iterations, 
           s=120, alpha=0.7, c='#e74c3c', edgecolors='black', 
           linewidths=1.5, label='Tekstil', zorder=3)

# En iyi modelin eğrisini çiz
x_smooth = np.linspace(x_data.min(), x_data.max(), 300)
y_smooth = models[best_model][0](x_smooth, *best_params)
ax.plot(x_smooth, y_smooth, 
        color='#2ecc71', linewidth=3, 
        label=f'{best_model} Fit (R²={best_r2:.3f})', 
        zorder=2, linestyle='--')

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)

# Etiketler
ax.set_xlabel('Veri Yoğunluğu (%)', fontsize=14, fontweight='bold')
ax.set_ylabel('İterasyon Sayısı', fontsize=14, fontweight='bold')
ax.set_title('RMVC: Veri Yoğunluğu vs Yakınsama Hızı\n(Epsilon Toleranslı Sonuçlar)', 
             fontsize=16, fontweight='bold', pad=20)

# Legend
ax.legend(fontsize=11, loc='best', framealpha=0.95, edgecolor='black')

# Y ekseni tamsayı
ax.set_yticks(range(int(y_data.min()), int(y_data.max()) + 2))

# Arka plan rengi
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

# Denklem ekle
if best_model == 'Linear':
    equation = f'y = {best_params[0]:.4f}x + {best_params[1]:.4f}'
elif best_model == 'Polynomial (2nd)':
    equation = f'y = {best_params[0]:.4f}x² + {best_params[1]:.4f}x + {best_params[2]:.4f}'
elif best_model == 'Logarithmic':
    equation = f'y = {best_params[0]:.4f}ln(x+1) + {best_params[1]:.4f}'

ax.text(0.05, 0.95, equation, 
        transform=ax.transAxes, fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()

# Kaydet
output_file = 'density_vs_convergence.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nGrafik kaydedildi: {output_file}")

# İstatistikler
print(f"\n{'='*60}")
print("VERİ İSTATİSTİKLERİ")
print(f"{'='*60}")
print(f"Yoğunluk Aralığı: {x_data.min():.2f}% - {x_data.max():.2f}%")
print(f"İterasyon Aralığı: {y_data.min()} - {y_data.max()}")
print(f"Ortalama İterasyon: {y_data.mean():.2f}")
print(f"Standart Sapma: {y_data.std():.2f}")

# Korelasyon
correlation = np.corrcoef(x_data, y_data)[0, 1]
print(f"\nPearson Korelasyonu: {correlation:.4f}")

plt.show()
