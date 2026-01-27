"""
Deney Sonuclarini Excel'e Aktar ve Grafikleri Olustur
======================================================
250 deneyin matrislerini Excel'e aktarir ve grafikleri olusturur.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Encoding sorununu coz
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_data(filename):
    """JSON dosyasindan veriyi yukle."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"[OK] {len(data)} deney yuklendi")
    return data

def export_to_excel(data, output_file='experiment_matrices_full.xlsx'):
    """Tum matrisleri Excel'e aktar."""
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    
    print("\n[1/4] Excel dosyasi olusturuluyor...")
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 1. Ozet sayfa
        print("  - Ozet sayfasi olusturuluyor...")
        summary_data = []
        for exp in data:
            summary_data.append({
                'ID': exp['experiment_id'],
                'Sparsity': exp['config']['target_sparsity'],
                'Size': f"{exp['config']['num_params']}x{exp['config']['num_elements']}",
                'Actual_Sparsity': round(exp['initial_statistics']['sparsity'], 3),
                'Initial_Mean': round(exp['initial_statistics']['mean'], 3),
                'Initial_Density': round(exp['initial_statistics']['density'], 3),
                'Fractional_Count': exp['initial_statistics']['num_fractional'],
                'Conv_Type': exp['convergence']['type'],
                'Iterations': exp['convergence']['iterations'] if exp['convergence']['iterations'] is not None else -1
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # 2. Yakinsamaya gore grupla
        print("  - Yakinsama tipleri sayfasi olusturuluyor...")
        all_ones = [exp for exp in data if exp['convergence']['type'] == 'all_ones']
        binary_mixed = [exp for exp in data if exp['convergence']['type'] == 'binary_mixed']
        
        all_ones_summary = pd.DataFrame([{
            'ID': e['experiment_id'],
            'Size': f"{e['config']['num_params']}x{e['config']['num_elements']}",
            'Sparsity': e['config']['target_sparsity'],
            'Iterations': e['convergence']['iterations']
        } for e in all_ones])
        all_ones_summary.to_excel(writer, sheet_name='All_Ones', index=False)
        
        binary_mixed_summary = pd.DataFrame([{
            'ID': e['experiment_id'],
            'Size': f"{e['config']['num_params']}x{e['config']['num_elements']}",
            'Sparsity': e['config']['target_sparsity'],
            'Iterations': e['convergence']['iterations']
        } for e in binary_mixed])
        binary_mixed_summary.to_excel(writer, sheet_name='Binary_Mixed', index=False)
        
        # 3. Ornek matrisler (ilk 20 deney)
        print("  - Ornek matrisler olusturuluyor (ilk 20 deney)...")
        for i, exp in enumerate(data[:20]):
            exp_id = exp['experiment_id']
            
            if len(exp['iteration_history']) > 0:
                # Baslangic matrisi
                initial_matrix = exp['iteration_history'][0]['membership_matrix']
                df = pd.DataFrame(initial_matrix).T
                df = df.round(4)
                
                sheet_name = f"E{exp_id}_Init"[:31]
                df.to_excel(writer, sheet_name=sheet_name)
                
                # Son matris
                if len(exp['iteration_history']) > 1:
                    final_matrix = exp['iteration_history'][-1]['membership_matrix']
                    df_final = pd.DataFrame(final_matrix).T
                    df_final = df_final.round(4)
                    
                    sheet_name_final = f"E{exp_id}_Final"[:31]
                    df_final.to_excel(writer, sheet_name=sheet_name_final)
    
    print(f"[OK] Excel dosyasi olusturuldu: {filepath}\n")
    return filepath

def create_visualizations(data, output_dir='analysis_plots'):
    """Grafikleri olustur."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("[2/4] Grafikler olusturuluyor...")
    
    # DataFrame olustur
    df_data = []
    for exp in data:
        df_data.append({
            'experiment_id': exp['experiment_id'],
            'target_sparsity': exp['config']['target_sparsity'],
            'num_params': exp['config']['num_params'],
            'num_elements': exp['config']['num_elements'],
            'matrix_size': exp['config']['matrix_size'],
            'initial_sparsity': exp['initial_statistics']['sparsity'],
            'initial_density': exp['initial_statistics']['density'],
            'initial_mean': exp['initial_statistics']['mean'],
            'initial_fractional': exp['initial_statistics']['num_fractional'],
            'convergence_type': exp['convergence']['type'],
            'iterations': exp['convergence']['iterations'] if exp['convergence']['iterations'] is not None else 0
        })
    
    df = pd.DataFrame(df_data)
    
    # Grafik 1: Yakinsama tipi dagilimi
    print("  - Grafik 1/6: Yakinsama tipi dagilimi")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    conv_counts = df['convergence_type'].value_counts()
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
    axes[0].pie(conv_counts.values, labels=conv_counts.index, autopct='%1.1f%%', 
                startangle=90, colors=colors[:len(conv_counts)])
    axes[0].set_title('Convergence Type Distribution', fontsize=14, fontweight='bold')
    
    # Iterasyon dagilimi
    axes[1].hist(df['iterations'], bins=range(0, df['iterations'].max()+2), 
                 edgecolor='black', alpha=0.7, color='#3498db')
    axes[1].set_xlabel('Iterations', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Iteration Distribution', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_convergence_overview.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Grafik 2: Seyreklik vs Iterasyon
    print("  - Grafik 2/6: Seyreklik vs Iterasyon")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Hedef seyreklik vs iterasyon
    for conv_type in df['convergence_type'].unique():
        subset = df[df['convergence_type'] == conv_type]
        axes[0, 0].scatter(subset['target_sparsity'], subset['iterations'], 
                          alpha=0.6, s=50, label=conv_type)
    axes[0, 0].set_xlabel('Target Sparsity', fontsize=12)
    axes[0, 0].set_ylabel('Iterations', fontsize=12)
    axes[0, 0].set_title('Target Sparsity vs Iterations', fontsize=13, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gercek seyreklik vs iterasyon
    axes[0, 1].scatter(df['initial_sparsity'], df['iterations'], alpha=0.6, s=50, c=df['iterations'], cmap='viridis')
    axes[0, 1].set_xlabel('Actual Initial Sparsity', fontsize=12)
    axes[0, 1].set_ylabel('Iterations', fontsize=12)
    axes[0, 1].set_title('Actual Sparsity vs Iterations', fontsize=13, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Matris boyutu vs iterasyon
    axes[1, 0].scatter(df['matrix_size'], df['iterations'], alpha=0.6, s=50, c=df['target_sparsity'], cmap='coolwarm')
    axes[1, 0].set_xlabel('Matrix Size (m x n)', fontsize=12)
    axes[1, 0].set_ylabel('Iterations', fontsize=12)
    axes[1, 0].set_title('Matrix Size vs Iterations', fontsize=13, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Baslangic ortalama vs iterasyon
    axes[1, 1].scatter(df['initial_mean'], df['iterations'], alpha=0.6, s=50, c=df['initial_density'], cmap='plasma')
    axes[1, 1].set_xlabel('Initial Mean', fontsize=12)
    axes[1, 1].set_ylabel('Iterations', fontsize=12)
    axes[1, 1].set_title('Initial Mean vs Iterations', fontsize=13, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_sparsity_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Grafik 3: Seyreklik seviyelerine gore box plot
    print("  - Grafik 3/6: Seyreklik seviyelerine gore analiz")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    df.boxplot(column='iterations', by='target_sparsity', ax=axes[0])
    axes[0].set_xlabel('Target Sparsity', fontsize=12)
    axes[0].set_ylabel('Iterations', fontsize=12)
    axes[0].set_title('Iterations by Sparsity Level', fontsize=13, fontweight='bold')
    plt.sca(axes[0])
    plt.xticks(rotation=0)
    
    # Ortalama iterasyon
    sparsity_groups = df.groupby('target_sparsity')['iterations'].agg(['mean', 'std', 'min', 'max'])
    sparsity_groups['mean'].plot(kind='bar', ax=axes[1], color='#3498db', alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Target Sparsity', fontsize=12)
    axes[1].set_ylabel('Average Iterations', fontsize=12)
    axes[1].set_title('Average Iterations by Sparsity', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    plt.sca(axes[1])
    plt.xticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_sparsity_boxplot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Grafik 4: Matris boyutuna gore analiz
    print("  - Grafik 4/6: Matris boyutuna gore analiz")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    size_labels = df.apply(lambda x: f"{x['num_params']}x{x['num_elements']}", axis=1)
    df_with_labels = df.copy()
    df_with_labels['size_label'] = size_labels
    
    df_with_labels.boxplot(column='iterations', by='size_label', ax=axes[0])
    axes[0].set_xlabel('Matrix Size', fontsize=12)
    axes[0].set_ylabel('Iterations', fontsize=12)
    axes[0].set_title('Iterations by Matrix Size', fontsize=13, fontweight='bold')
    plt.sca(axes[0])
    plt.xticks(rotation=45, ha='right')
    
    # Ortalama iterasyon
    size_groups = df_with_labels.groupby('size_label')['iterations'].mean().sort_values()
    size_groups.plot(kind='barh', ax=axes[1], color='#2ecc71', alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Average Iterations', fontsize=12)
    axes[1].set_ylabel('Matrix Size', fontsize=12)
    axes[1].set_title('Average Iterations by Size', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_size_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Grafik 5: Yakinsama tipine gore ozellikler
    print("  - Grafik 5/6: Yakinsama tipine gore ozellikler")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Baslangic yogunluk
    for conv_type in df['convergence_type'].unique():
        subset = df[df['convergence_type'] == conv_type]
        axes[0, 0].hist(subset['initial_density'], alpha=0.6, label=conv_type, bins=20)
    axes[0, 0].set_xlabel('Initial Density', fontsize=12)
    axes[0, 0].set_ylabel('Frequency', fontsize=12)
    axes[0, 0].set_title('Initial Density by Convergence Type', fontsize=13, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Baslangic ortalama
    for conv_type in df['convergence_type'].unique():
        subset = df[df['convergence_type'] == conv_type]
        axes[0, 1].hist(subset['initial_mean'], alpha=0.6, label=conv_type, bins=20)
    axes[0, 1].set_xlabel('Initial Mean', fontsize=12)
    axes[0, 1].set_ylabel('Frequency', fontsize=12)
    axes[0, 1].set_title('Initial Mean by Convergence Type', fontsize=13, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Seyreklik vs Yogunluk
    for conv_type in df['convergence_type'].unique():
        subset = df[df['convergence_type'] == conv_type]
        axes[1, 0].scatter(subset['initial_sparsity'], subset['initial_density'], 
                          alpha=0.6, s=50, label=conv_type)
    axes[1, 0].set_xlabel('Initial Sparsity', fontsize=12)
    axes[1, 0].set_ylabel('Initial Density', fontsize=12)
    axes[1, 0].set_title('Sparsity vs Density by Type', fontsize=13, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Iterasyon box plot
    df.boxplot(column='iterations', by='convergence_type', ax=axes[1, 1])
    axes[1, 1].set_xlabel('Convergence Type', fontsize=12)
    axes[1, 1].set_ylabel('Iterations', fontsize=12)
    axes[1, 1].set_title('Iterations by Convergence Type', fontsize=13, fontweight='bold')
    plt.sca(axes[1, 1])
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_convergence_type_features.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Grafik 6: Heatmap - Seyreklik vs Boyut
    print("  - Grafik 6/6: Heatmap analizi")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Ortalama iterasyon heatmap
    pivot_iter = df.pivot_table(values='iterations', 
                                 index='target_sparsity', 
                                 columns='matrix_size', 
                                 aggfunc='mean')
    sns.heatmap(pivot_iter, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[0], cbar_kws={'label': 'Avg Iterations'})
    axes[0].set_xlabel('Matrix Size', fontsize=12)
    axes[0].set_ylabel('Target Sparsity', fontsize=12)
    axes[0].set_title('Average Iterations Heatmap', fontsize=13, fontweight='bold')
    
    # all_ones orani heatmap
    df['is_all_ones'] = (df['convergence_type'] == 'all_ones').astype(int)
    pivot_ones = df.pivot_table(values='is_all_ones', 
                                 index='target_sparsity', 
                                 columns='matrix_size', 
                                 aggfunc='mean')
    sns.heatmap(pivot_ones, annot=True, fmt='.2f', cmap='RdYlGn', ax=axes[1], cbar_kws={'label': 'All Ones Ratio'})
    axes[1].set_xlabel('Matrix Size', fontsize=12)
    axes[1].set_ylabel('Target Sparsity', fontsize=12)
    axes[1].set_title('All Ones Convergence Ratio', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_heatmap_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] 6 grafik olusturuldu: {output_dir}/\n")

def create_statistics_report(data, output_file='statistics_report.txt'):
    """Detayli istatistik raporu olustur."""
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    
    print("[3/4] Istatistik raporu olusturuluyor...")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ITERATIF RMVC YAKINSAMA ANALIZI - ISTATISTIK RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Toplam Deney: {len(data)}\n\n")
        
        # Genel istatistikler
        f.write("-" * 80 + "\n")
        f.write("1. GENEL ISTATISTIKLER\n")
        f.write("-" * 80 + "\n\n")
        
        converged = [d for d in data if d['convergence']['converged']]
        iterations = [d['convergence']['iterations'] for d in converged]
        
        f.write(f"Yakinsayan Deney: {len(converged)} (%{len(converged)/len(data)*100:.1f})\n")
        f.write(f"Ortalama Iterasyon: {np.mean(iterations):.2f}\n")
        f.write(f"Std Iterasyon: {np.std(iterations):.2f}\n")
        f.write(f"Min Iterasyon: {min(iterations)}\n")
        f.write(f"Max Iterasyon: {max(iterations)}\n")
        f.write(f"Medyan Iterasyon: {np.median(iterations):.2f}\n\n")
        
        # Yakinsama tipleri
        f.write("-" * 80 + "\n")
        f.write("2. YAKINSAMA TIPLERI\n")
        f.write("-" * 80 + "\n\n")
        
        conv_types = {}
        for d in data:
            ct = d['convergence']['type']
            conv_types[ct] = conv_types.get(ct, 0) + 1
        
        for ct, count in sorted(conv_types.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{ct:20s}: {count:4d} (%{count/len(data)*100:5.1f})\n")
        f.write("\n")
        
        # Seyreklige gore
        f.write("-" * 80 + "\n")
        f.write("3. SEYREKLIGE GORE ANALIZ\n")
        f.write("-" * 80 + "\n\n")
        
        sparsity_groups = {}
        for d in data:
            sp = d['config']['target_sparsity']
            if sp not in sparsity_groups:
                sparsity_groups[sp] = []
            if d['convergence']['converged']:
                sparsity_groups[sp].append(d['convergence']['iterations'])
        
        f.write(f"{'Seyreklik':12s} {'Deney':8s} {'Ort':8s} {'Std':8s} {'Min':8s} {'Max':8s}\n")
        f.write("-" * 60 + "\n")
        for sp in sorted(sparsity_groups.keys()):
            iters = sparsity_groups[sp]
            f.write(f"{sp:12.2f} {len(iters):8d} {np.mean(iters):8.2f} {np.std(iters):8.2f} "
                   f"{min(iters):8d} {max(iters):8d}\n")
        f.write("\n")
        
        # Boyuta gore
        f.write("-" * 80 + "\n")
        f.write("4. MATRIS BOYUTUNA GORE ANALIZ\n")
        f.write("-" * 80 + "\n\n")
        
        size_groups = {}
        for d in data:
            size = d['config']['matrix_size']
            size_label = f"{d['config']['num_params']}x{d['config']['num_elements']}"
            if size_label not in size_groups:
                size_groups[size_label] = []
            if d['convergence']['converged']:
                size_groups[size_label].append(d['convergence']['iterations'])
        
        f.write(f"{'Boyut':12s} {'Deney':8s} {'Ort':8s} {'Std':8s} {'Min':8s} {'Max':8s}\n")
        f.write("-" * 60 + "\n")
        for size_label in sorted(size_groups.keys()):
            iters = size_groups[size_label]
            f.write(f"{size_label:12s} {len(iters):8d} {np.mean(iters):8.2f} {np.std(iters):8.2f} "
                   f"{min(iters):8d} {max(iters):8d}\n")
        f.write("\n")
    
    print(f"[OK] Istatistik raporu olusturuldu: {filepath}\n")
    return filepath

def main():
    """Ana fonksiyon."""
    print("\n" + "=" * 80)
    print("DENEY SONUCLARI - EXCEL EXPORT VE GORSELLESTIME")
    print("=" * 80 + "\n")
    
    # Veriyi yukle
    filename = "convergence_experiment_20260126_094541.json"
    data = load_data(filename)
    
    # Excel'e aktar
    excel_file = export_to_excel(data)
    
    # Grafikleri olustur
    create_visualizations(data)
    
    # Istatistik raporu
    stats_file = create_statistics_report(data)
    
    # Ozet
    print("[4/4] TAMAMLANDI!")
    print("=" * 80)
    print(f"\nOlusturulan Dosyalar:")
    print(f"  1. Excel: {excel_file}")
    print(f"  2. Grafikler: analysis_plots/ (6 grafik)")
    print(f"  3. Istatistik Raporu: {stats_file}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
