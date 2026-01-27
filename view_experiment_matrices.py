"""
Deney Matrislerini Görüntüleme
================================
250 deneyde oluşturulan matrisleri görüntüler ve özetler.
"""

import json
import pandas as pd
import os

def load_experiment_data(filename):
    """JSON dosyasından deney verilerini yükler."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[OK] {len(data)} deney yuklendi: {filename}\n")
    return data

def display_experiment_summary(data):
    """Deney özetini gösterir."""
    print("=" * 80)
    print("DENEY OZETI")
    print("=" * 80)
    print(f"Toplam Deney Sayisi: {len(data)}\n")
    
    # Konfigürasyonları grupla
    configs = {}
    for exp in data:
        config_key = (exp['config']['target_sparsity'], 
                     exp['config']['num_params'], 
                     exp['config']['num_elements'])
        if config_key not in configs:
            configs[config_key] = []
        configs[config_key].append(exp)
    
    print(f"Farkli Konfigurasyon Sayisi: {len(configs)}\n")
    
    print("Konfigurasyonlar:")
    print("-" * 80)
    for (sparsity, m, n), experiments in sorted(configs.items()):
        print(f"Seyreklik: {sparsity:.2f} | Boyut: {m}x{n} | Deney Sayisi: {len(experiments)}")
    print()

def display_experiment_details(exp, show_matrix=True):
    """Tek bir deneyin detaylarını gösterir."""
    exp_id = exp['experiment_id']
    config = exp['config']
    initial_stats = exp['initial_statistics']
    convergence = exp['convergence']
    
    print("=" * 80)
    print(f"DENEY #{exp_id}")
    print("=" * 80)
    
    print("\n[KONFIGURASYON]")
    print(f"  Hedef Seyreklik: {config['target_sparsity']:.2f}")
    print(f"  Matris Boyutu: {config['num_params']}x{config['num_elements']} = {config['matrix_size']} deger")
    print(f"  Parametre/Eleman Orani: {config['param_element_ratio']:.3f}")
    
    print("\n[BASLANGIC ISTATISTIKLERI]")
    print(f"  Gercek Seyreklik: {initial_stats['sparsity']:.3f}")
    print(f"  Yogunluk (1'lerin orani): {initial_stats['density']:.3f}")
    print(f"  Ortalama Uyelik: {initial_stats['mean']:.3f}")
    print(f"  0 Sayisi: {initial_stats['num_zeros']}")
    print(f"  1 Sayisi: {initial_stats['num_ones']}")
    print(f"  Ondalikli Deger Sayisi: {initial_stats['num_fractional']}")
    
    print("\n[YAKINSAMA]")
    print(f"  Yakinsama Durumu: {'EVET' if convergence['converged'] else 'HAYIR'}")
    print(f"  Yakinsama Tipi: {convergence['type']}")
    print(f"  Iterasyon Sayisi: {convergence['iterations'] if convergence['iterations'] is not None else 'N/A'}")
    
    if show_matrix and len(exp['iteration_history']) > 0:
        print("\n[BASLANGIC UYELIK MATRISI (Iterasyon 0)]")
        initial_matrix = exp['iteration_history'][0]['membership_matrix']
        
        # DataFrame'e dönüştür
        df = pd.DataFrame(initial_matrix).T
        print(df.to_string())
        
        # Son iterasyon
        if len(exp['iteration_history']) > 1:
            print(f"\n[SON UYELIK MATRISI (Iterasyon {len(exp['iteration_history'])-1})]")
            final_matrix = exp['iteration_history'][-1]['membership_matrix']
            df_final = pd.DataFrame(final_matrix).T
            print(df_final.to_string())
    
    print("\n")

def export_matrices_to_excel(data, output_file='experiment_matrices.xlsx'):
    """Tüm matrisleri Excel dosyasına aktarır."""
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Özet sayfa
        summary_data = []
        for exp in data:
            summary_data.append({
                'Experiment_ID': exp['experiment_id'],
                'Target_Sparsity': exp['config']['target_sparsity'],
                'Matrix_Size': f"{exp['config']['num_params']}x{exp['config']['num_elements']}",
                'Actual_Sparsity': exp['initial_statistics']['sparsity'],
                'Initial_Mean': exp['initial_statistics']['mean'],
                'Convergence_Type': exp['convergence']['type'],
                'Iterations': exp['convergence']['iterations'] if exp['convergence']['iterations'] is not None else -1
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Her deney için ayrı sayfa (ilk 50 deney)
        for i, exp in enumerate(data[:50]):  # İlk 50 deney
            exp_id = exp['experiment_id']
            
            if len(exp['iteration_history']) > 0:
                # Başlangıç matrisi
                initial_matrix = exp['iteration_history'][0]['membership_matrix']
                df = pd.DataFrame(initial_matrix).T
                
                sheet_name = f"Exp_{exp_id}_Init"[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name)
                
                # Son matris
                if len(exp['iteration_history']) > 1:
                    final_matrix = exp['iteration_history'][-1]['membership_matrix']
                    df_final = pd.DataFrame(final_matrix).T
                    
                    sheet_name_final = f"Exp_{exp_id}_Final"[:31]
                    df_final.to_excel(writer, sheet_name=sheet_name_final)
    
    print(f"[OK] Matrisler Excel dosyasina aktarildi: {filepath}")
    return filepath

def interactive_viewer(data):
    """İnteraktif matris görüntüleyici."""
    print("\n" + "=" * 80)
    print("INTERAKTIF MATRIS GORUNTULEYI")
    print("=" * 80)
    print("\nKomutlar:")
    print("  [sayi] - Belirli bir deney numarasini goster (ornek: 1, 25, 100)")
    print("  'list' - Tum deneyleri listele")
    print("  'summary' - Ozet istatistikleri goster")
    print("  'export' - Matrisleri Excel'e aktar")
    print("  'filter [tip]' - Belirli yakinsama tipini filtrele (ornek: filter all_ones)")
    print("  'quit' - Cikis")
    print()
    
    filtered_data = data
    
    while True:
        try:
            command = input("Komut girin: ").strip().lower()
            
            if command == 'quit' or command == 'q':
                print("Cikis yapiliyor...")
                break
            
            elif command == 'list':
                print("\nTum Deneyler:")
                print("-" * 80)
                for exp in filtered_data:
                    exp_id = exp['experiment_id']
                    config = exp['config']
                    conv = exp['convergence']
                    print(f"#{exp_id:3d} | {config['num_params']}x{config['num_elements']} | "
                          f"Seyreklik: {config['target_sparsity']:.2f} | "
                          f"Tip: {conv['type']:15s} | "
                          f"Iter: {conv['iterations'] if conv['iterations'] is not None else 'N/A'}")
                print()
            
            elif command == 'summary':
                display_experiment_summary(filtered_data)
            
            elif command == 'export':
                export_matrices_to_excel(filtered_data)
            
            elif command.startswith('filter'):
                parts = command.split()
                if len(parts) == 2:
                    filter_type = parts[1]
                    filtered_data = [exp for exp in data if exp['convergence']['type'] == filter_type]
                    print(f"\n[OK] {len(filtered_data)} deney filtrelendi (tip: {filter_type})\n")
                else:
                    print("\n[HATA] Kullanim: filter [tip] (ornek: filter all_ones)\n")
            
            elif command.isdigit():
                exp_id = int(command)
                exp = next((e for e in filtered_data if e['experiment_id'] == exp_id), None)
                
                if exp:
                    display_experiment_details(exp, show_matrix=True)
                else:
                    print(f"\n[HATA] Deney #{exp_id} bulunamadi!\n")
            
            else:
                print("\n[HATA] Gecersiz komut! 'list', 'summary', 'export', 'filter', [sayi] veya 'quit' girin.\n")
        
        except KeyboardInterrupt:
            print("\n\nCikis yapiliyor...")
            break
        except Exception as e:
            print(f"\n[HATA] {str(e)}\n")

def main():
    """Ana fonksiyon."""
    print("=" * 80)
    print("DENEY MATRISLERI GORUNTULEME ARACI")
    print("=" * 80)
    print()
    
    # Dosya adı
    filename = "convergence_experiment_20260126_094541.json"
    
    # Veriyi yükle
    data = load_experiment_data(filename)
    
    # Özet göster
    display_experiment_summary(data)
    
    # İlk 3 deneyi örnek olarak göster
    print("=" * 80)
    print("ORNEK DENEYLER (Ilk 3)")
    print("=" * 80)
    for i in range(min(3, len(data))):
        display_experiment_details(data[i], show_matrix=True)
    
    # İnteraktif mod
    print("\nInteraktif moda geciliyor...")
    print("Daha fazla deney gormek icin komutlari kullanin.\n")
    
    interactive_viewer(data)

if __name__ == "__main__":
    main()
