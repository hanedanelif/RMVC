"""
İteratif RMVC Yakınsama Analizi - Görselleştirme ve Detaylı Analiz
===================================================================
Deney sonuçlarını görselleştirir ve matematiksel model geliştirir.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import os

# Görselleştirme ayarları
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_results(filename):
    """JSON dosyasından sonuçları yükler."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"✅ {len(results)} deney sonucu yüklendi: {filename}")
    return results

def create_dataframe(results):
    """Sonuçları pandas DataFrame'e dönüştürür."""
    
    data = []
    for r in results:
        row = {
            'experiment_id': r['experiment_id'],
            'target_sparsity': r['config']['target_sparsity'],
            'num_params': r['config']['num_params'],
            'num_elements': r['config']['num_elements'],
            'matrix_size': r['config']['matrix_size'],
            'param_element_ratio': r['config']['param_element_ratio'],
            'initial_sparsity': r['initial_statistics']['sparsity'],
            'initial_density': r['initial_statistics']['density'],
            'initial_mean': r['initial_statistics']['mean'],
            'initial_fractional_count': r['initial_statistics']['num_fractional'],
            'converged': r['convergence']['converged'],
            'convergence_type': r['convergence']['type'],
            'iterations_to_converge': r['convergence']['iterations'] if r['convergence']['iterations'] is not None else -1
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

def plot_convergence_distribution(df, output_dir='analysis_plots'):
    """Yakınsama tipi dağılımını görselleştirir."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Yakınsama tipi dağılımı
    conv_counts = df['convergence_type'].value_counts()
    axes[0].pie(conv_counts.values, labels=conv_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Yakınsama Tipi Dağılımı', fontsize=14, fontweight='bold')
    
    # Yakınsama durumu
    conv_status = df['converged'].value_counts()
    axes[1].pie(conv_status.values, labels=['Yakınsadı' if x else 'Yakınsamadı' for x in conv_status.index], 
                autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
    axes[1].set_title('Yakınsama Durumu', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_convergence_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafik kaydedildi: 01_convergence_distribution.png")

def plot_iterations_vs_sparsity(df, output_dir='analysis_plots'):
    """İterasyon sayısı vs seyreklik grafiği."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Sadece yakınsayan deneyleri al
    converged_df = df[df['converged'] == True].copy()
    
    if len(converged_df) == 0:
        print("⚠️ Yakınsayan deney bulunamadı, grafik oluşturulamadı.")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Hedef Seyreklik vs İterasyon
    axes[0, 0].scatter(converged_df['target_sparsity'], converged_df['iterations_to_converge'], 
                       alpha=0.6, s=50)
    axes[0, 0].set_xlabel('Hedef Seyreklik', fontsize=12)
    axes[0, 0].set_ylabel('İterasyon Sayısı', fontsize=12)
    axes[0, 0].set_title('Hedef Seyreklik vs İterasyon Sayısı', fontsize=13, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Gerçek Başlangıç Seyreklik vs İterasyon
    axes[0, 1].scatter(converged_df['initial_sparsity'], converged_df['iterations_to_converge'], 
                       alpha=0.6, s=50, c=converged_df['convergence_type'].astype('category').cat.codes, 
                       cmap='viridis')
    axes[0, 1].set_xlabel('Başlangıç Seyreklik (Gerçek)', fontsize=12)
    axes[0, 1].set_ylabel('İterasyon Sayısı', fontsize=12)
    axes[0, 1].set_title('Başlangıç Seyreklik vs İterasyon Sayısı', fontsize=13, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Matris Boyutu vs İterasyon
    axes[1, 0].scatter(converged_df['matrix_size'], converged_df['iterations_to_converge'], 
                       alpha=0.6, s=50)
    axes[1, 0].set_xlabel('Matris Boyutu (m×n)', fontsize=12)
    axes[1, 0].set_ylabel('İterasyon Sayısı', fontsize=12)
    axes[1, 0].set_title('Matris Boyutu vs İterasyon Sayısı', fontsize=13, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Başlangıç Ortalama vs İterasyon
    axes[1, 1].scatter(converged_df['initial_mean'], converged_df['iterations_to_converge'], 
                       alpha=0.6, s=50, c=converged_df['convergence_type'].astype('category').cat.codes, 
                       cmap='viridis')
    axes[1, 1].set_xlabel('Başlangıç Üyelik Ortalaması', fontsize=12)
    axes[1, 1].set_ylabel('İterasyon Sayısı', fontsize=12)
    axes[1, 1].set_title('Başlangıç Ortalama vs İterasyon Sayısı', fontsize=13, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_iterations_vs_features.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafik kaydedildi: 02_iterations_vs_features.png")

def plot_convergence_type_analysis(df, output_dir='analysis_plots'):
    """Yakınsama tipine göre detaylı analiz."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Yakınsama tiplerine göre renk kodları
    conv_types = df['convergence_type'].unique()
    
    # 1. Başlangıç Yoğunluk Dağılımı
    for conv_type in conv_types:
        subset = df[df['convergence_type'] == conv_type]
        axes[0, 0].hist(subset['initial_density'], alpha=0.6, label=conv_type, bins=20)
    axes[0, 0].set_xlabel('Başlangıç Yoğunluk', fontsize=12)
    axes[0, 0].set_ylabel('Frekans', fontsize=12)
    axes[0, 0].set_title('Yakınsama Tipine Göre Başlangıç Yoğunluk', fontsize=13, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Başlangıç Ortalama Dağılımı
    for conv_type in conv_types:
        subset = df[df['convergence_type'] == conv_type]
        axes[0, 1].hist(subset['initial_mean'], alpha=0.6, label=conv_type, bins=20)
    axes[0, 1].set_xlabel('Başlangıç Üyelik Ortalaması', fontsize=12)
    axes[0, 1].set_ylabel('Frekans', fontsize=12)
    axes[0, 1].set_title('Yakınsama Tipine Göre Başlangıç Ortalama', fontsize=13, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Box plot - Yakınsama Tipi vs İterasyon
    converged_df = df[df['converged'] == True]
    if len(converged_df) > 0:
        converged_df.boxplot(column='iterations_to_converge', by='convergence_type', ax=axes[1, 0])
        axes[1, 0].set_xlabel('Yakınsama Tipi', fontsize=12)
        axes[1, 0].set_ylabel('İterasyon Sayısı', fontsize=12)
        axes[1, 0].set_title('Yakınsama Tipine Göre İterasyon Dağılımı', fontsize=13, fontweight='bold')
        plt.sca(axes[1, 0])
        plt.xticks(rotation=45, ha='right')
    
    # 4. Seyreklik vs Yoğunluk (Yakınsama Tipine Göre Renklendirilmiş)
    for conv_type in conv_types:
        subset = df[df['convergence_type'] == conv_type]
        axes[1, 1].scatter(subset['initial_sparsity'], subset['initial_density'], 
                          alpha=0.6, s=50, label=conv_type)
    axes[1, 1].set_xlabel('Başlangıç Seyreklik', fontsize=12)
    axes[1, 1].set_ylabel('Başlangıç Yoğunluk', fontsize=12)
    axes[1, 1].set_title('Seyreklik vs Yoğunluk (Yakınsama Tipine Göre)', fontsize=13, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_convergence_type_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafik kaydedildi: 03_convergence_type_analysis.png")

def build_regression_model(df):
    """İterasyon sayısını tahmin eden regresyon modeli oluşturur."""
    
    # Sadece yakınsayan deneyleri al
    converged_df = df[df['converged'] == True].copy()
    
    if len(converged_df) < 10:
        print("⚠️ Regresyon modeli için yeterli veri yok (min 10 gerekli).")
        return None
    
    print("\n" + "=" * 80)
    print("REGRESYON MODELİ OLUŞTURMA")
    print("=" * 80)
    
    # Özellikler
    features = ['initial_sparsity', 'initial_density', 'initial_mean', 
                'matrix_size', 'param_element_ratio', 'initial_fractional_count']
    
    X = converged_df[features].values
    y = converged_df['iterations_to_converge'].values
    
    # Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X, y)
    lr_score = lr_model.score(X, y)
    
    print(f"\nLinear Regression R² Score: {lr_score:.4f}")
    print("\nKatsayılar:")
    for i, feature in enumerate(features):
        print(f"  {feature:30s}: {lr_model.coef_[i]:10.4f}")
    print(f"  {'Intercept':30s}: {lr_model.intercept_:10.4f}")
    
    # Polynomial Regression (degree=2)
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)
    
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    poly_score = poly_model.score(X_poly, y)
    
    print(f"\nPolynomial Regression (degree=2) R² Score: {poly_score:.4f}")
    
    # Korelasyon analizi
    print("\n" + "=" * 80)
    print("KORELASYON ANALİZİ")
    print("=" * 80)
    
    correlation_data = converged_df[features + ['iterations_to_converge']].corr()
    
    print("\nİterasyon Sayısı ile Korelasyonlar:")
    correlations = correlation_data['iterations_to_converge'].drop('iterations_to_converge').sort_values(ascending=False)
    for feature, corr in correlations.items():
        print(f"  {feature:30s}: {corr:7.4f}")
    
    return {
        'linear_model': lr_model,
        'linear_score': lr_score,
        'poly_model': poly_model,
        'poly_score': poly_score,
        'features': features,
        'correlations': correlations
    }

def generate_mathematical_formula(model_info):
    """Matematiksel formül oluşturur."""
    
    if model_info is None:
        return
    
    print("\n" + "=" * 80)
    print("MATEMATİKSEL MODEL")
    print("=" * 80)
    
    lr_model = model_info['linear_model']
    features = model_info['features']
    
    print("\nTahmin Edilen İterasyon Sayısı Formülü:")
    print("\nk = α₀ + α₁×S + α₂×D + α₃×M + α₄×N + α₅×R + α₆×F")
    print("\nBurada:")
    print("  k = İterasyon sayısı")
    print("  S = Başlangıç seyrekliği (initial_sparsity)")
    print("  D = Başlangıç yoğunluğu (initial_density)")
    print("  M = Başlangıç ortalaması (initial_mean)")
    print("  N = Matris boyutu (matrix_size)")
    print("  R = Parametre/Eleman oranı (param_element_ratio)")
    print("  F = Başlangıç ondalıklı değer sayısı (initial_fractional_count)")
    
    print(f"\nKatsayılar:")
    print(f"  α₀ (Intercept) = {lr_model.intercept_:.4f}")
    for i, feature in enumerate(features):
        print(f"  α{i+1} ({feature}) = {lr_model.coef_[i]:.4f}")
    
    print(f"\nModel Açıklama Gücü (R²): {model_info['linear_score']:.4f}")
    
    # LaTeX formatında formül
    print("\n" + "-" * 80)
    print("LaTeX Formatı (Makale için):")
    print("-" * 80)
    
    latex_formula = "k = "
    latex_formula += f"{lr_model.intercept_:.4f}"
    
    feature_symbols = {
        'initial_sparsity': 'S',
        'initial_density': 'D',
        'initial_mean': 'M',
        'matrix_size': 'N',
        'param_element_ratio': 'R',
        'initial_fractional_count': 'F'
    }
    
    for i, feature in enumerate(features):
        coef = lr_model.coef_[i]
        symbol = feature_symbols.get(feature, f'X_{i+1}')
        if coef >= 0:
            latex_formula += f" + {coef:.4f} \\cdot {symbol}"
        else:
            latex_formula += f" - {abs(coef):.4f} \\cdot {symbol}"
    
    print(f"\n{latex_formula}")

def create_summary_report(df, model_info, output_file='CONVERGENCE_ANALYSIS_REPORT.md'):
    """Özet rapor oluşturur."""
    
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# İteratif RMVC Yakınsama Analizi - Detaylı Rapor\n\n")
        f.write(f"**Tarih:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Genel İstatistikler
        f.write("## 1. Genel İstatistikler\n\n")
        f.write(f"- **Toplam Deney Sayısı:** {len(df)}\n")
        f.write(f"- **Yakınsayan Deney Sayısı:** {df['converged'].sum()} ({df['converged'].sum()/len(df)*100:.1f}%)\n")
        f.write(f"- **Yakınsamayan Deney Sayısı:** {(~df['converged']).sum()} ({(~df['converged']).sum()/len(df)*100:.1f}%)\n\n")
        
        # Yakınsama Tipleri
        f.write("## 2. Yakınsama Tipleri\n\n")
        conv_counts = df['convergence_type'].value_counts()
        for conv_type, count in conv_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"- **{conv_type}:** {count} ({percentage:.1f}%)\n")
        f.write("\n")
        
        # Yakınsayan Deneylerin Analizi
        converged_df = df[df['converged'] == True]
        if len(converged_df) > 0:
            f.write("## 3. Yakınsayan Deneylerin Analizi\n\n")
            
            iterations = converged_df['iterations_to_converge']
            f.write(f"- **Ortalama İterasyon:** {iterations.mean():.2f}\n")
            f.write(f"- **Minimum İterasyon:** {iterations.min()}\n")
            f.write(f"- **Maksimum İterasyon:** {iterations.max()}\n")
            f.write(f"- **Standart Sapma:** {iterations.std():.2f}\n")
            f.write(f"- **Medyan:** {iterations.median():.2f}\n\n")
            
            # Seyrekliğe göre
            f.write("### 3.1. Seyrekliğe Göre İterasyon\n\n")
            sparsity_groups = converged_df.groupby('target_sparsity')['iterations_to_converge'].agg(['mean', 'min', 'max', 'std'])
            f.write(sparsity_groups.to_markdown())
            f.write("\n\n")
            
            # Boyuta göre
            f.write("### 3.2. Matris Boyutuna Göre İterasyon\n\n")
            size_groups = converged_df.groupby('matrix_size')['iterations_to_converge'].agg(['mean', 'min', 'max', 'std'])
            f.write(size_groups.to_markdown())
            f.write("\n\n")
        
        # Tüm 1'e Yakınsama
        all_ones = df[df['convergence_type'] == 'all_ones']
        if len(all_ones) > 0:
            f.write("## 4. Tüm 1'e Yakınsama Analizi\n\n")
            f.write(f"- **Deney Sayısı:** {len(all_ones)}\n")
            f.write(f"- **Başlangıç Yoğunluk Ortalaması:** {all_ones['initial_density'].mean():.4f}\n")
            f.write(f"- **Başlangıç Üyelik Ortalaması:** {all_ones['initial_mean'].mean():.4f}\n")
            f.write(f"- **Ortalama İterasyon:** {all_ones['iterations_to_converge'].mean():.2f}\n\n")
        
        # Tüm 0'a Yakınsama
        all_zeros = df[df['convergence_type'] == 'all_zeros']
        if len(all_zeros) > 0:
            f.write("## 5. Tüm 0'a Yakınsama Analizi\n\n")
            f.write(f"- **Deney Sayısı:** {len(all_zeros)}\n")
            f.write(f"- **Başlangıç Seyreklik Ortalaması:** {all_zeros['initial_sparsity'].mean():.4f}\n")
            f.write(f"- **Başlangıç Üyelik Ortalaması:** {all_zeros['initial_mean'].mean():.4f}\n")
            f.write(f"- **Ortalama İterasyon:** {all_zeros['iterations_to_converge'].mean():.2f}\n\n")
        
        # Matematiksel Model
        if model_info is not None:
            f.write("## 6. Matematiksel Model\n\n")
            f.write("### 6.1. Linear Regression Model\n\n")
            f.write(f"**R² Score:** {model_info['linear_score']:.4f}\n\n")
            
            f.write("**Formül:**\n\n")
            f.write("```\n")
            f.write("k = α₀ + α₁×S + α₂×D + α₃×M + α₄×N + α₅×R + α₆×F\n")
            f.write("```\n\n")
            
            lr_model = model_info['linear_model']
            features = model_info['features']
            
            f.write("**Katsayılar:**\n\n")
            f.write(f"- α₀ (Intercept) = {lr_model.intercept_:.4f}\n")
            for i, feature in enumerate(features):
                f.write(f"- α{i+1} ({feature}) = {lr_model.coef_[i]:.4f}\n")
            f.write("\n")
            
            f.write("### 6.2. Korelasyon Analizi\n\n")
            f.write("İterasyon sayısı ile özellikler arasındaki korelasyonlar:\n\n")
            for feature, corr in model_info['correlations'].items():
                f.write(f"- **{feature}:** {corr:.4f}\n")
            f.write("\n")
        
        # Bulgular ve Sonuçlar
        f.write("## 7. Bulgular ve Sonuçlar\n\n")
        f.write("### 7.1. Ana Bulgular\n\n")
        
        # Otomatik bulgular
        if len(all_ones) > len(all_zeros):
            f.write("1. **Yakınsama eğilimi:** Deneylerin çoğu tüm 1'e yakınsadı.\n")
        elif len(all_zeros) > len(all_ones):
            f.write("1. **Yakınsama eğilimi:** Deneylerin çoğu tüm 0'a yakınsadı.\n")
        
        if model_info is not None:
            top_corr = model_info['correlations'].abs().idxmax()
            top_corr_val = model_info['correlations'][top_corr]
            f.write(f"2. **En etkili faktör:** {top_corr} (korelasyon: {top_corr_val:.4f})\n")
        
        f.write("\n### 7.2. Teorik Açıklamalar\n\n")
        f.write("*(Bu bölüm manuel olarak doldurulacak)*\n\n")
        
        f.write("### 7.3. Makale İçin Öneriler\n\n")
        f.write("*(Bu bölüm manuel olarak doldurulacak)*\n\n")
    
    print(f"\n✅ Özet rapor oluşturuldu: {filepath}")
    return filepath

def main():
    """Ana analiz fonksiyonu."""
    
    print("=" * 80)
    print("ITERATIF RMVC YAKINSAMA ANALIZI")
    print("=" * 80)
    
    # Kullanıcıdan dosya adı al
    print("\nLütfen analiz edilecek JSON dosyasının adını girin:")
    print("(Örnek: convergence_experiment_20260126_095500.json)")
    filename = input("Dosya adı: ").strip()
    
    if not filename:
        print("⚠️ Dosya adı girilmedi. Varsayılan dosya aranıyor...")
        # En son oluşturulan dosyayı bul
        import glob
        files = glob.glob(os.path.join(os.path.dirname(__file__), "convergence_experiment_*.json"))
        if files:
            filename = os.path.basename(max(files, key=os.path.getctime))
            print(f"✅ Bulunan dosya: {filename}")
        else:
            print("❌ Hiç deney dosyası bulunamadı!")
            return
    
    # Sonuçları yükle
    results = load_results(filename)
    
    # DataFrame oluştur
    df = create_dataframe(results)
    
    print(f"\n📊 DataFrame oluşturuldu: {len(df)} satır, {len(df.columns)} sütun")
    
    # Grafikler oluştur
    print("\n" + "=" * 80)
    print("GRAFİKLER OLUŞTURULUYOR")
    print("=" * 80)
    
    plot_convergence_distribution(df)
    plot_iterations_vs_sparsity(df)
    plot_convergence_type_analysis(df)
    
    # Regresyon modeli
    model_info = build_regression_model(df)
    
    # Matematiksel formül
    generate_mathematical_formula(model_info)
    
    # Özet rapor
    report_file = create_summary_report(df, model_info)
    
    print("\n" + "=" * 80)
    print("ANALİZ TAMAMLANDI")
    print("=" * 80)
    print(f"\n📁 Grafikler: analysis_plots/ klasörü")
    print(f"📄 Rapor: {report_file}")
    print("\nSonraki adım: Raporu inceleyin ve makale için bulgular bölümünü yazın.")

if __name__ == "__main__":
    main()
