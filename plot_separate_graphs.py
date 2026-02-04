# -*- coding: utf-8 -*-
"""
Veri Seti Başına Ayrı Grafikler
================================
MovieLens ve Tekstil için ayrı density vs convergence grafikleri
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

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

print(f"MovieLens: {len(movielens_density)} nokta")
print(f"Tekstil: {len(textile_density)} nokta")

# Eğri uydurma fonksiyonları
def linear(x, a, b):
    return a * x + b

def polynomial_2(x, a, b, c):
    return a * x**2 + b * x + c

def logarithmic(x, a, b):
    return a * np.log(x + 1) + b

def fit_best_model(x_data, y_data, dataset_name):
    """En iyi modeli bul"""
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    
    models = {
        'Linear': (linear, 2),
        'Polynomial (2nd)': (polynomial_2, 3),
        'Logarithmic': (logarithmic, 2),
    }
    
    best_model = None
    best_r2 = -np.inf
    best_params = None
    
    print(f"\n{dataset_name} - Eğri Uydurma:")
    
    for model_name, (func, param_count) in models.items():
        try:
            params, _ = curve_fit(func, x_data, y_data, maxfev=10000)
            y_fitted = func(x_data, *params)
            
            # R² hesapla
            ss_res = np.sum((y_data - y_fitted) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            
            print(f"  {model_name}: R² = {r2:.4f}")
            
            if r2 > best_r2:
                best_r2 = r2
                best_model = model_name
                best_params = params
        except Exception as e:
            print(f"  {model_name}: BAŞARISIZ")
    
    print(f"  → EN İYİ: {best_model} (R² = {best_r2:.4f})")
    
    return best_model, best_params, best_r2, models[best_model][0]

# Her veri seti için grafik çiz
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# ============ MOVIELENS GRAFİĞİ ============
print("\n" + "="*60)
best_model_ml, params_ml, r2_ml, func_ml = fit_best_model(
    movielens_density, movielens_iterations, "MOVIELENS"
)

ax1.scatter(movielens_density, movielens_iterations, 
           s=150, alpha=0.8, c='#3498db', edgecolors='black', 
           linewidths=2, zorder=3)

# Eğri
x_ml = np.array(movielens_density)
x_ml_smooth = np.linspace(x_ml.min(), x_ml.max(), 200)
y_ml_smooth = func_ml(x_ml_smooth, *params_ml)
ax1.plot(x_ml_smooth, y_ml_smooth, 
        color='#e74c3c', linewidth=3, 
        label=f'{best_model_ml} (R²={r2_ml:.3f})', 
        zorder=2, linestyle='--')

ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax1.set_xlabel('Veri Yoğunluğu (%)', fontsize=13, fontweight='bold')
ax1.set_ylabel('İterasyon Sayısı', fontsize=13, fontweight='bold')
ax1.set_title('MovieLens\nVeri Yoğunluğu vs Yakınsama', 
             fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=10, loc='best', framealpha=0.95)
ax1.set_facecolor('#f8f9fa')

# İstatistikler ekle
stats_ml = f"Veri: {len(movielens_density)} test\n"
stats_ml += f"Ort. iter: {np.mean(movielens_iterations):.1f}\n"
stats_ml += f"Aralık: {min(movielens_iterations)}-{max(movielens_iterations)}"
ax1.text(0.05, 0.95, stats_ml, transform=ax1.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

# ============ TEKSTİL GRAFİĞİ ============
print("="*60)
best_model_tx, params_tx, r2_tx, func_tx = fit_best_model(
    textile_density, textile_iterations, "TEKSTİL"
)

ax2.scatter(textile_density, textile_iterations, 
           s=150, alpha=0.8, c='#e74c3c', edgecolors='black', 
           linewidths=2, zorder=3)

# Eğri
x_tx = np.array(textile_density)
x_tx_smooth = np.linspace(x_tx.min(), x_tx.max(), 200)
y_tx_smooth = func_tx(x_tx_smooth, *params_tx)
ax2.plot(x_tx_smooth, y_tx_smooth, 
        color='#2ecc71', linewidth=3, 
        label=f'{best_model_tx} (R²={r2_tx:.3f})', 
        zorder=2, linestyle='--')

ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax2.set_xlabel('Veri Yoğunluğu (%)', fontsize=13, fontweight='bold')
ax2.set_ylabel('İterasyon Sayısı', fontsize=13, fontweight='bold')
ax2.set_title('Tekstil\nVeri Yoğunluğu vs Yakınsama', 
             fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=10, loc='best', framealpha=0.95)
ax2.set_facecolor('#f8f9fa')

# İstatistikler ekle
stats_tx = f"Veri: {len(textile_density)} test\n"
stats_tx += f"Ort. iter: {np.mean(textile_iterations):.1f}\n"
stats_tx += f"Aralık: {min(textile_iterations)}-{max(textile_iterations)}"
ax2.text(0.05, 0.95, stats_tx, transform=ax2.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

# Genel başlık
fig.suptitle('RMVC: Veri Yoğunluğu vs Yakınsama Hızı Analizi', 
            fontsize=16, fontweight='bold', y=0.98)

fig.patch.set_facecolor('white')
plt.tight_layout()

# Kaydet
output_file = 'density_vs_convergence_separate.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n{'='*60}")
print(f"Grafik kaydedildi: {output_file}")
print(f"{'='*60}")

plt.show()
