"""
Tum Matrisleri Excel'e Kaydetme - Makale Ek Dosyasi
====================================================
250 deneyin tum matrislerini (baslangic ve son) Excel'e kaydeder.
Makale icin ek dosya olarak kullanilabilir.
"""

import json
import pandas as pd
import os
from datetime import datetime

def load_experiment_results(filename):
    """Deney sonuclarini yukle."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[OK] {len(data)} deney yuklendi: {filename}")
    return data

def save_all_matrices_to_excel(results, output_file='ALL_EXPERIMENT_MATRICES.xlsx'):
    """
    Tum deneylerin matrislerini Excel'e kaydet.
    Her deney icin ayri sayfa: Baslangic ve Son matris.
    """
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    
    print(f"\n[1/3] Excel dosyasi olusturuluyor: {output_file}")
    print(f"  - Toplam {len(results)} deney")
    print(f"  - Her deney icin 2 sayfa (baslangic + son)")
    print(f"  - Toplam ~{len(results) * 2} sayfa olusturulacak")
    print(f"  - Bu islem birka dakika surebilir...")
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 1. Ozet sayfa
        print(f"\n[2/3] Ozet sayfasi olusturuluyor...")
        summary_data = []
        for exp in results:
            summary_data.append({
                'Exp_ID': exp['experiment_id'],
                'Target_Sparsity': exp['config']['target_sparsity'],
                'Size': f"{exp['config']['num_params']}x{exp['config']['num_elements']}",
                'Actual_Sparsity': round(exp['initial_statistics']['sparsity'], 4),
                'Initial_Mean': round(exp['initial_statistics']['mean'], 4),
                'Initial_Density': round(exp['initial_statistics']['density'], 4),
                'Conv_Type': exp['convergence']['type'],
                'Iterations': exp['convergence']['iterations'] if exp['convergence']['iterations'] is not None else -1,
                'Initial_Zeros': exp['initial_statistics']['num_zeros'],
                'Initial_Ones': exp['initial_statistics']['num_ones'],
                'Initial_Fractional': exp['initial_statistics']['num_fractional']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        print(f"  - Ozet sayfasi tamamlandi ({len(summary_df)} satir)")
        
        # 2. Her deney icin matrisler
        print(f"\n[3/3] Deney matrisleri kaydediliyor...")
        
        for i, exp in enumerate(results, 1):
            exp_id = exp['experiment_id']
            
            if len(exp['iteration_history']) == 0:
                continue
            
            # Baslangic matrisi
            initial_matrix = exp['iteration_history'][0]['membership_matrix']
            df_init = pd.DataFrame(initial_matrix).T
            df_init = df_init.round(6)
            
            # Sayfa adi (Excel limiti: 31 karakter)
            sheet_name_init = f"E{exp_id:03d}_Init"[:31]
            df_init.to_excel(writer, sheet_name=sheet_name_init)
            
            # Son matris
            if len(exp['iteration_history']) > 1:
                final_matrix = exp['iteration_history'][-1]['membership_matrix']
                df_final = pd.DataFrame(final_matrix).T
                df_final = df_final.round(6)
                
                sheet_name_final = f"E{exp_id:03d}_Final"[:31]
                df_final.to_excel(writer, sheet_name=sheet_name_final)
            
            # Ilerleme goster
            if i % 25 == 0:
                print(f"  - {i}/{len(results)} deney tamamlandi...")
    
    print(f"\n[OK] Tum matrisler kaydedildi: {filepath}")
    print(f"  - Dosya boyutu: ~{os.path.getsize(filepath) / (1024*1024):.2f} MB")
    return filepath

def create_supplementary_materials(results):
    """
    Makale icin ek dosyalar olustur.
    1. Tum matrisler (Excel)
    2. Deney konfigurasyonlari (CSV)
    3. Istatistik ozeti (CSV)
    """
    print("\n" + "=" * 80)
    print("MAKALE EK DOSYALARI OLUSTURULUYOR")
    print("=" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Tum matrisler
    matrices_file = save_all_matrices_to_excel(results, f'SUPPLEMENTARY_MATRICES_{timestamp}.xlsx')
    
    # 2. Deney konfigurasyonlari
    print(f"\n[1/2] Deney konfigurasyonlari kaydediliyor...")
    config_data = []
    for exp in results:
        config_data.append({
            'Experiment_ID': exp['experiment_id'],
            'Target_Sparsity': exp['config']['target_sparsity'],
            'Num_Params': exp['config']['num_params'],
            'Num_Elements': exp['config']['num_elements'],
            'Matrix_Size': exp['config']['matrix_size'],
            'Param_Element_Ratio': exp['config']['param_element_ratio']
        })
    
    config_df = pd.DataFrame(config_data)
    config_file = os.path.join(os.path.dirname(__file__), f'SUPPLEMENTARY_CONFIGS_{timestamp}.csv')
    config_df.to_csv(config_file, index=False)
    print(f"  - Konfigurasyonlar kaydedildi: {config_file}")
    
    # 3. Istatistik ozeti
    print(f"\n[2/2] Istatistik ozeti kaydediliyor...")
    stats_data = []
    for exp in results:
        stats_data.append({
            'Experiment_ID': exp['experiment_id'],
            'Initial_Sparsity': exp['initial_statistics']['sparsity'],
            'Initial_Density': exp['initial_statistics']['density'],
            'Initial_Mean': exp['initial_statistics']['mean'],
            'Initial_Min': exp['initial_statistics']['min'],
            'Initial_Max': exp['initial_statistics']['max'],
            'Num_Zeros': exp['initial_statistics']['num_zeros'],
            'Num_Ones': exp['initial_statistics']['num_ones'],
            'Num_Fractional': exp['initial_statistics']['num_fractional'],
            'Converged': exp['convergence']['converged'],
            'Convergence_Type': exp['convergence']['type'],
            'Iterations': exp['convergence']['iterations'] if exp['convergence']['iterations'] is not None else -1
        })
    
    stats_df = pd.DataFrame(stats_data)
    stats_file = os.path.join(os.path.dirname(__file__), f'SUPPLEMENTARY_STATISTICS_{timestamp}.csv')
    stats_df.to_csv(stats_file, index=False)
    print(f"  - Istatistikler kaydedildi: {stats_file}")
    
    # Ozet
    print("\n" + "=" * 80)
    print("EK DOSYALAR TAMAMLANDI")
    print("=" * 80)
    print(f"\nOlusturulan dosyalar:")
    print(f"  1. {os.path.basename(matrices_file)}")
    print(f"     - Tum matrislerin baslangic ve son halleri")
    print(f"     - {len(results)} deney x 2 sayfa = ~{len(results)*2} sayfa")
    print(f"  2. {os.path.basename(config_file)}")
    print(f"     - Deney konfigurasyonlari (CSV)")
    print(f"  3. {os.path.basename(stats_file)}")
    print(f"     - Istatistik ozeti (CSV)")
    print(f"\nBu dosyalar makaleye ek olarak eklenebilir.")
    
    return {
        'matrices_file': matrices_file,
        'config_file': config_file,
        'stats_file': stats_file
    }

def main():
    """Ana fonksiyon."""
    print("=" * 80)
    print("MAKALE EK DOSYALARI - TUM MATRISLER")
    print("=" * 80)
    print()
    
    # En son deney sonuclarini yukle
    import glob
    json_files = glob.glob(os.path.join(os.path.dirname(__file__), "convergence_experiment_*.json"))
    
    if not json_files:
        print("[HATA] Hic deney dosyasi bulunamadi!")
        return
    
    # En son dosyayi sec
    latest_file = max(json_files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    
    print(f"En son deney dosyasi: {filename}\n")
    
    # Sonuclari yukle
    results = load_experiment_results(filename)
    
    # Ek dosyalari olustur
    files = create_supplementary_materials(results)
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI!")
    print("=" * 80)
    print("\nHocaya gonderilecek dosyalar hazir.")

if __name__ == "__main__":
    main()
