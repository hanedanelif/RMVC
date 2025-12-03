# -*- coding: utf-8 -*-
"""
RMVC Web Arayüzü v2.1 - Relational Membership Value Calculation
===============================================================
Soft Set Teorisi tabanlı karar destek sistemi.

Referans:
    Dayioglu, A.; Erdogan, F.O.; Celik, B. "RMVC: A Validated Algorithmic 
    Framework for Decision-Making Under Uncertainty". Mathematics 2025, 13, 2693.

Düzeltmeler (v2.1):
1. Delta fonksiyonu: Tüm kümelerde ikili sayımı (break kaldırıldı)
2. Matris yönü: Satırlar=Parametreler, Sütunlar=Elemanlar
3. Formül doğrulaması: Example 1 ile test edildi
4. Hocanın CSV formatı desteği (Satırlar=Parametreler)
5. Üyelik matrisi çıktısı hocanın formatına uygun

Çalıştırma:
    streamlit run rmvc_app_v2.py --server.port 8515
"""

import streamlit as st
import pandas as pd
import numpy as np
from fractions import Fraction
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go

# Sayfa Konfigürasyonu
st.set_page_config(
    page_title="RMVC Analiz Aracı v2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .best-choice {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .formula-box {
        background: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# RMVC FONKSİYONLARI - MAKALEYE UYGUN DÜZELTILMIŞ VERSİYON
# ============================================================

def safe_sort_key(x):
    """Güvenli sıralama - hem sayı hem string için çalışır."""
    try:
        return (0, int(str(x)))  # Sayılar önce
    except (ValueError, TypeError):
        return (1, str(x))  # Stringler sonra


def param_sort_key(x):
    """Parametre sıralama - e1, e2, e_1, e_2 gibi formatları destekler."""
    import re
    # Sayıyı bul (e1 -> 1, e_1 -> 1, param_10 -> 10)
    match = re.search(r'(\d+)', str(x))
    if match:
        return int(match.group(1))
    return str(x)


def csv_to_soft_set(df, rows_are_params=False):
    """
    CSV verisini Soft Set formatına dönüştürür.
    Hocanın Colab koduna tam uyumlu.
    
    Makaledeki notasyon:
    - U: Evrensel küme (elemanlar/adaylar)
    - E: Parametre kümesi (kriterler)
    - Φ(e_i): e_i parametresine ait elemanlar kümesi
    
    Args:
        df: DataFrame
        rows_are_params: True ise satırlar=parametreler, sütunlar=elemanlar (Hocanın formatı)
                        False ise satırlar=elemanlar, sütunlar=parametreler
    """
    if rows_are_params:
        # Hocanın formatı: Satırlar=Parametreler (e1,e2..), Sütunlar=Elemanlar (1,2..)
        
        parametre_ids = df.index.tolist()
        original_columns = df.columns.tolist()
        
        # Hocanın kodu: Sadece sayısal verileri olan sütunları al
        # Boş, NaN, Unnamed ve tamamen 0 olan sütunları filtrele
        valid_columns = []
        for col in original_columns:
            col_str = str(col).strip()
            # Boş string, NaN, Unnamed sütunları atla
            if not col_str or col_str.lower() == 'nan' or col_str.startswith('Unnamed'):
                continue
            # Sütunda en az bir sayısal değer olmalı
            try:
                col_data = pd.to_numeric(df[col], errors='coerce')
                if col_data.notna().any():
                    valid_columns.append(col)
            except:
                pass
        
        # Ürün sayısını belirle (hocanın yaklaşımı: 1'den başla)
        num_products = len(valid_columns)
        
        # U: Evrensel küme - 1'den num_products'a kadar
        eleman_ids = [str(i) for i in range(1, num_products + 1)]
        U = set(eleman_ids)
        
        # Sütun eşleştirmesi: simple_id -> original_col
        col_mapping = {str(i+1): valid_columns[i] for i in range(num_products)}
        
        # E: Parametre kümeleri
        E_named = {}
        E_info = {}
        
        for i, param_id in enumerate(parametre_ids):
            # Hocanın formatı: e_1, e_2, ... şeklinde adlandır
            e_key = f"e_{i+1}"
            satir_verisi = df.loc[param_id]
            
            phi_e = set()
            toplam_deger = 0
            
            # Her ürünü kontrol et
            for simple_id, orig_col in col_mapping.items():
                try:
                    deger = satir_verisi[orig_col]
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if pd.notna(numeric_val) and numeric_val > 0:
                        phi_e.add(simple_id)
                        toplam_deger += numeric_val
                except:
                    pass
            
            E_named[e_key] = phi_e
            E_info[e_key] = {
                'orijinal_ad': str(param_id),
                'eleman_sayisi': len(phi_e),
                'toplam_deger': toplam_deger,
                'elemanlar': phi_e
            }
    else:
        # Varsayılan format: Satırlar=Elemanlar, Sütunlar=Parametreler
        eleman_ids = df.index.tolist()
        parametre_ids = df.columns.tolist()
        
        # U: Evrensel küme (satırlar)
        U = set(str(eid) for eid in eleman_ids)
        
        # E: Parametre kümeleri
        E_named = {}
        E_info = {}
        
        for i, param_id in enumerate(parametre_ids):
            e_key = f"e_{i+1}"
            sutun_verisi = df[param_id]
            
            phi_e = set()
            toplam_deger = 0
            
            for eleman_id, deger in sutun_verisi.items():
                try:
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if numeric_val > 0:
                        phi_e.add(str(eleman_id))
                        toplam_deger += numeric_val
                except:
                    pass
            
            E_named[e_key] = phi_e
            E_info[e_key] = {
                'orijinal_ad': str(param_id),
                'eleman_sayisi': len(phi_e),
                'toplam_deger': toplam_deger,
                'elemanlar': phi_e
            }
    
    return U, E_named, E_info, eleman_ids, parametre_ids


def delta_function(e_i, E_named, U):
    """
    Delta fonksiyonu - Makaledeki formüle göre DÜZELTİLMİŞ versiyon.
    
    Formül (Makaleden):
    δ(u, e_i) = Σ_{v ∈ Φ(e_i)} |{e_j ∈ E : {u, v} ⊆ Φ(e_j)}|
    
    Açıklama:
    - u: e_i'ye ait OLMAYAN bir eleman
    - v: e_i'ye ait olan her eleman
    - {u, v} ikilisinin diğer TÜM kümelerde kaç kez birlikte bulunduğunu say
    
    ÖNEMLİ: break KULLANILMAMALI - her küme için ayrı ayrı sayılmalı!
    """
    phi_e_i = E_named[e_i]  # Φ(e_i): e_i'ye ait elemanlar
    not_in_phi = U - phi_e_i  # U \ Φ(e_i): e_i'ye ait olmayan elemanlar
    
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        
        # Her v ∈ Φ(e_i) için
        for v in phi_e_i:
            # {u, v} ikilisinin bulunduğu küme sayısını say
            pair = {u, v}
            
            # TÜM kümeleri kontrol et (break YOK!)
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
                    # break KALDIRILDI - tüm kümelerde sayılmalı
        
        results[u] = delta_sum
    
    return results


def create_membership_matrix(E_named, U):
    """
    Üyelik matrisini oluşturur - Makaledeki formüle göre.
    
    Formül:
    M(u, e_i) = 1                           eğer u ∈ Φ(e_i)
    M(u, e_i) = δ(u, e_i) / γ(e_i)          eğer u ∉ Φ(e_i)
    
    Normalizasyon katsayısı:
    γ(e_i) = |Φ(e_i)| × (m - 1)
    
    Burada:
    - |Φ(e_i)|: e_i kümesindeki eleman sayısı
    - m: Toplam parametre sayısı
    - (m - 1): Diğer parametrelerin sayısı
    """
    m = len(E_named)  # Toplam parametre sayısı
    
    # Matris: Satırlar = Parametreler (e_i), Sütunlar = Elemanlar (u)
    membership_matrix = {}
    
    for e_i in E_named.keys():
        phi_e_i = E_named[e_i]
        delta_results = delta_function(e_i, E_named, U)
        
        # γ(e_i) = |Φ(e_i)| × (m - 1)
        gamma = len(phi_e_i) * (m - 1)
        
        membership_matrix[e_i] = {}
        
        for u in U:
            if u in phi_e_i:
                # u ∈ Φ(e_i) → Tam üyelik
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                # u ∉ Φ(e_i) → Kısmi üyelik
                if gamma > 0 and u in delta_results:
                    delta_val = delta_results[u]
                    membership_matrix[e_i][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    
    return membership_matrix


def calculate_scores(membership_matrix, U):
    """
    Her eleman için toplam skoru hesaplar.
    
    S(u) = Σ_{e_i ∈ E} M(u, e_i)
    """
    scores = {}
    
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    
    return scores


def matrix_to_dataframe(membership_matrix, U, E_info):
    """
    Üyelik matrisini DataFrame'e dönüştürür.
    Satırlar = Parametreler, Sütunlar = Elemanlar (Hocanın formatı)
    
    Format:
    SETS    1       2       3       ...
    e_1     0.0000  0.1111  0.0000  ...
    e_2     0.0000  1.0000  0.0278  ...
    """
    # Elemanları sayısal sıraya göre sırala (1, 2, 3, ...)
    sorted_elements = sorted(U, key=safe_sort_key)
    
    data = []
    for e_i in sorted(membership_matrix.keys(), key=param_sort_key):
        row = {'SETS': e_i}  # İlk sütun parametre adı
        for u in sorted_elements:
            val = membership_matrix[e_i].get(u, Fraction(0, 1))
            row[u] = float(val)
        data.append(row)
    
    # DataFrame oluştur - sütun sırası: SETS, 1, 2, 3, ...
    df = pd.DataFrame(data)
    
    # Sütunları doğru sıraya koy
    cols = ['SETS'] + sorted_elements
    df = df[cols]
    
    return df


def get_element_detail(u, membership_matrix, E_info):
    """Bir elemanın tüm parametrelerdeki üyelik değerlerini döndürür."""
    details = []
    for e_i in sorted(membership_matrix.keys(), key=param_sort_key):
        val = membership_matrix[e_i].get(u, Fraction(0, 1))
        details.append({
            'Parametre': e_i,
            'Orijinal Ad': E_info[e_i]['orijinal_ad'],
            'Üyelik (Kesir)': str(val),
            'Üyelik (Ondalık)': round(float(val), 4)
        })
    return pd.DataFrame(details)


def threshold_matrix(membership_matrix, U, threshold_value):
    """
    Üyelik matrisini eşik değerine göre binary matrise dönüştürür.
    threshold_value üzerindeki değerler 1, altındakiler 0 olur.
    """
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            binary_matrix[e_i][u] = 1 if val > threshold_value else 0
    return binary_matrix


def binary_to_dataframe(binary_matrix, U, E_info):
    """Binary matrisi DataFrame'e dönüştürür."""
    sorted_elements = sorted(U, key=safe_sort_key)
    data = []
    for e_i in sorted(binary_matrix.keys(), key=param_sort_key):
        row = {'SETS': e_i}
        for u in sorted_elements:
            row[u] = binary_matrix[e_i].get(u, 0)
        data.append(row)
    
    df = pd.DataFrame(data)
    cols = ['SETS'] + sorted_elements
    df = df[cols]
    return df


def compare_rankings(scores_old, scores_new):
    """İki iterasyonun sıralamalarını karşılaştırır."""
    sorted_old = sorted(scores_old.items(), key=lambda x: float(x[1]), reverse=True)
    sorted_new = sorted(scores_new.items(), key=lambda x: float(x[1]), reverse=True)
    
    rank_old = {u: i+1 for i, (u, _) in enumerate(sorted_old)}
    rank_new = {u: i+1 for i, (u, _) in enumerate(sorted_new)}
    
    comparison = []
    for u in sorted(scores_old.keys(), key=safe_sort_key):
        old_rank = rank_old[u]
        new_rank = rank_new[u]
        rank_change = old_rank - new_rank
        
        if rank_change > 0:
            change_str = f"↑ +{rank_change}"
            status = "🟢 Yükseldi"
        elif rank_change < 0:
            change_str = f"↓ {rank_change}"
            status = "🔴 Düştü"
        else:
            change_str = "="
            status = "⚪ Aynı"
        
        comparison.append({
            'Eleman': u,
            'Eski Rank': old_rank,
            'Yeni Rank': new_rank,
            'Değişim': change_str,
            'Durum': status,
            'Eski Skor': round(float(scores_old[u]), 4),
            'Yeni Skor': round(float(scores_new[u]), 4)
        })
    
    return pd.DataFrame(comparison)


# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

def main():
    # Başlık
    st.markdown('<div class="main-header">📊 RMVC Analiz Aracı v2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Relational Membership Value Calculation - Soft Set Teorisi Tabanlı</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📁 Veri Yükleme")
        
        uploaded_file = st.file_uploader(
            "CSV veya Excel dosyası yükleyin",
            type=['csv', 'xlsx', 'xls'],
            help="Satırlar=Elemanlar, Sütunlar=Parametreler. Değerler: 0=yok, >0=var"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Ayarlar")
        
        rows_are_params = st.checkbox(
            "Satırlar = Parametreler (Hocanın formatı)", 
            value=True,
            help="✅ İşaretli: Satırlar=Parametreler(e1,e2..), Sütunlar=Elemanlar(1,2..) - Hocanın CSV formatı"
        )
        bos_filtrele = st.checkbox(
            "Boş kümeleri filtrele", 
            value=False,
            help="İşaretlenirse hiç elemanı olmayan parametreler (boş kümeler) hesaplamadan çıkarılır. Hocanın yaklaşımı: dahil et (işaretsiz)"
        )
        kesir_goster = st.checkbox("Kesir olarak göster", value=True)
        
        st.markdown("---")
        st.markdown("### 📖 Formüller")
        st.latex(r"M(u, e_i) = \frac{\delta(u, e_i)}{|\Phi(e_i)| \times (m-1)}")
        st.latex(r"\delta(u, e_i) = \sum_{v \in \Phi(e_i)} |\{e_j : \{u,v\} \subseteq \Phi(e_j)\}|")
        
        st.markdown("---")
        st.info("""
        **v2 Düzeltmeleri:**
        - ✅ Delta fonksiyonu düzeltildi
        - ✅ Matris yönü düzeltildi
        - ✅ Example 1 ile doğrulandı
        """)
    
    # Ana içerik
    if uploaded_file is not None:
        try:
            # Dosyayı oku
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, index_col=0)
            else:
                df = pd.read_excel(uploaded_file, index_col=0)
            
            # Format bilgisi
            if rows_are_params:
                st.info("📊 Format: Satırlar=Parametreler, Sütunlar=Elemanlar (Hocanın formatı)")
                st.success(f"✅ Dosya yüklendi: {uploaded_file.name} ({df.shape[0]} parametre × {df.shape[1]} eleman)")
            else:
                st.success(f"✅ Dosya yüklendi: {uploaded_file.name} ({df.shape[0]} eleman × {df.shape[1]} parametre)")
            
            # Veri önizleme
            with st.expander("📋 Yüklenen Veri (Girdi Matrisi)", expanded=False):
                st.dataframe(df, use_container_width=True)
            
            # RMVC Analizi
            with st.spinner("🔄 RMVC analizi yapılıyor..."):
                U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df, rows_are_params=rows_are_params)
                
                # Filtreleme
                if bos_filtrele:
                    E_named = {k: v for k, v in E_named.items() if len(v) > 0}
                    E_info = {k: v for k, v in E_info.items() if k in E_named}
                
                if len(E_named) < 2:
                    st.error("❌ En az 2 boş olmayan parametre kümesi gerekli!")
                    return
                
                # Hesaplamalar
                membership_matrix = create_membership_matrix(E_named, U)
                scores = calculate_scores(membership_matrix, U)
                
                # Skorları sırala
                sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
                best_score = float(sorted_scores[0][1])
                best_choices = [u for u, s in sorted_scores if float(s) == best_score]
            
            # Sonuç Tabları
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🏆 Sonuçlar", 
                "🔢 Üyelik Matrisi",
                "📊 Grafikler",
                "📈 Parametre Analizi",
                "🔍 Detaylı Analiz",
                "🔄 İteratif Analiz"
            ])
            
            # TAB 1: Sonuçlar
            with tab1:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Toplam Eleman (|U|)", len(U))
                with col2:
                    st.metric("Toplam Parametre (m)", len(E_named))
                with col3:
                    avg_score = sum(float(s) for s in scores.values()) / len(scores)
                    st.metric("Ortalama Skor", f"{avg_score:.3f}")
                with col4:
                    st.metric("Max Skor", f"{best_score:.3f}")
                
                # En iyi seçim
                st.markdown(f"""
                <div class="best-choice">
                    🏆 <b>Optimal Seçim:</b> {', '.join(best_choices)}<br>
                    <small>Skor: {best_score:.4f}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Skor tablosu
                st.markdown("### 📋 Eleman Skorları (Sıralı)")
                
                score_data = []
                for i, (u, s) in enumerate(sorted_scores, 1):
                    score_data.append({
                        'Sıra': i,
                        'Eleman': u,
                        'Skor (Kesir)': str(s) if kesir_goster else '-',
                        'Skor (Ondalık)': round(float(s), 4),
                        'Durum': '⭐ EN İYİ' if float(s) == best_score else ''
                    })
                
                score_df = pd.DataFrame(score_data)
                st.dataframe(score_df, use_container_width=True, height=400)
            
            # TAB 2: Üyelik Matrisi
            with tab2:
                st.markdown("### 🔢 MEMBERSHIP VALUE MATRIX (BAĞIL ÜYELİK MATRİSİ)")
                st.markdown("**Satırlar:** Parametreler (SETS) | **Sütunlar:** Elemanlar (1, 2, 3, ...)")
                
                # Matrisi DataFrame'e dönüştür
                matrix_df = matrix_to_dataframe(membership_matrix, U, E_info)
                
                # Sayısal sütunları al (SETS hariç)
                numeric_cols = [c for c in matrix_df.columns if c != 'SETS']
                
                # Görüntüleme için kopyala
                display_df = matrix_df.copy()
                for col in numeric_cols:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")
                
                # SETS sütununu index yap (hocanın formatı gibi)
                display_df = display_df.set_index('SETS')
                st.dataframe(display_df, use_container_width=True)
                
                # SUM satırı ekle
                st.markdown("### 📊 SUM s(x) - Sütun Toplamları")
                col_sums = matrix_df[numeric_cols].sum()
                sum_df = pd.DataFrame([col_sums.values], columns=numeric_cols, index=['SUM s(x)'])
                sum_df = sum_df.applymap(lambda x: f"{x:.4f}")
                st.dataframe(sum_df, use_container_width=True)
                
                # CSV Export butonu
                st.markdown("### 📥 CSV İndir")
                
                # Export için tam matris (SUM dahil)
                export_df = matrix_df.copy()
                export_df = export_df.set_index('SETS')
                sum_row = pd.DataFrame([matrix_df[numeric_cols].sum().values], 
                                       columns=numeric_cols, index=['SUM s(x)'])
                export_df = pd.concat([export_df, sum_row])
                
                csv_data = export_df.to_csv()
                st.download_button(
                    label="📥 Üyelik Matrisini CSV olarak indir",
                    data=csv_data,
                    file_name="membership_matrix.csv",
                    mime="text/csv"
                )
                
                # Heatmap
                st.markdown("### 🗺️ Üyelik Matrisi Heatmap")
                
                heatmap_data = matrix_df[numeric_cols].values
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    x=numeric_cols,
                    y=matrix_df['SETS'].tolist(),
                    title='Üyelik Değerleri (Sarı=1, Mor=0)',
                    color_continuous_scale='Viridis',
                    aspect='auto',
                    text_auto='.2f'
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # TAB 3: Grafikler
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bar chart - Skorlar
                    fig_bar = px.bar(
                        score_df.head(20),
                        x='Eleman',
                        y='Skor (Ondalık)',
                        title='🏅 Eleman Skorları (Top 20)',
                        color='Skor (Ondalık)',
                        color_continuous_scale='Viridis'
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Histogram
                    fig_hist = px.histogram(
                        score_df,
                        x='Skor (Ondalık)',
                        nbins=15,
                        title='📈 Skor Dağılımı',
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig_hist.add_vline(x=best_score, line_dash="dash", line_color="red",
                                       annotation_text=f"Max: {best_score:.2f}")
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                # Box plot
                fig_box = px.box(
                    score_df,
                    y='Skor (Ondalık)',
                    title='📦 Skor Box Plot',
                    points='all'
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # TAB 4: Parametre Analizi
            with tab4:
                st.markdown("### 📈 Parametre (Kriter) Analizi")
                
                param_data = []
                for e_i in sorted(E_info.keys(), key=param_sort_key):
                    info = E_info[e_i]
                    param_data.append({
                        'Parametre': e_i,
                        'Orijinal ID': info['orijinal_ad'],
                        'Eleman Sayısı |Φ(eᵢ)|': info['eleman_sayisi'],
                        'γ(eᵢ)': info['eleman_sayisi'] * (len(E_named) - 1),
                        'Elemanlar': ', '.join(sorted(info['elemanlar'], key=safe_sort_key))
                    })
                
                param_df = pd.DataFrame(param_data)
                st.dataframe(param_df, use_container_width=True)
                
                # Parametre boyutları grafiği
                fig_param = px.bar(
                    param_df,
                    x='Parametre',
                    y='Eleman Sayısı |Φ(eᵢ)|',
                    title='Parametre Küme Boyutları',
                    color='Eleman Sayısı |Φ(eᵢ)|',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_param, use_container_width=True)
            
            # TAB 5: Detaylı Analiz
            with tab5:
                st.markdown("### 🔍 Eleman Detaylı Analizi")
                
                selected_u = st.selectbox(
                    "Analiz edilecek elemanı seçin:",
                    options=sorted(U, key=lambda x: -float(scores.get(x, 0))),
                    format_func=lambda x: f"{x} (Skor: {float(scores.get(x, 0)):.3f})"
                )
                
                if selected_u:
                    u_score = scores.get(selected_u, Fraction(0, 1))
                    u_rank = [i for i, (u, s) in enumerate(sorted_scores, 1) if u == selected_u][0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Skor", f"{float(u_score):.4f}")
                    with col2:
                        st.metric("Sıralama", f"{u_rank}/{len(U)}")
                    with col3:
                        percentile = (1 - u_rank/len(U)) * 100
                        st.metric("Yüzdelik", f"%{percentile:.1f}")
                    
                    # Detay tablosu
                    detail_df = get_element_detail(selected_u, membership_matrix, E_info)
                    st.dataframe(detail_df, use_container_width=True)
                    
                    # Radar chart
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=detail_df['Üyelik (Ondalık)'].tolist(),
                        theta=detail_df['Parametre'].tolist(),
                        fill='toself',
                        name=selected_u
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        title=f'Eleman {selected_u} - Parametre Üyelik Profili'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
            
            # TAB 6: İteratif Analiz
            with tab6:
                st.markdown("### 🔄 İteratif RMVC Analizi")
                st.markdown("""
                Bu bölümde üyelik matrisini eşikleyerek yeni bir binary matris oluşturabilir 
                ve RMVC algoritmasını tekrar çalıştırarak sıralama değişimlerini gözlemleyebilirsiniz.
                """)
                
                # Session state başlat
                if 'iterations' not in st.session_state:
                    st.session_state.iterations = [{
                        'iteration': 0,
                        'membership_matrix': membership_matrix,
                        'scores': scores,
                        'threshold': None,
                        'binary_matrix': None
                    }]
                
                current_iter = len(st.session_state.iterations) - 1
                current_data = st.session_state.iterations[current_iter]
                
                # Mevcut iterasyon bilgisi
                st.info(f"📍 Şu anda İterasyon {current_iter} üzerindesiniz.")
                
                # Üyelik matrisi istatistikleri
                st.markdown("#### 📊 Mevcut Üyelik Matrisi İstatistikleri")
                
                col1, col2, col3, col4 = st.columns(4)
                
                all_values = []
                for row in current_data['membership_matrix'].values():
                    all_values.extend([float(v) for v in row.values()])
                
                with col1:
                    st.metric("Min Değer", f"{min(all_values):.4f}")
                with col2:
                    st.metric("Max Değer", f"{max(all_values):.4f}")
                with col3:
                    st.metric("Ortalama", f"{np.mean(all_values):.4f}")
                with col4:
                    st.metric("Std Sapma", f"{np.std(all_values):.4f}")
                
                # Değer dağılımı histogram
                st.markdown("#### 📈 Değer Dağılımı")
                fig_dist = px.histogram(
                    x=all_values,
                    nbins=20,
                    title='Üyelik Değerlerinin Dağılımı',
                    labels={'x': 'Üyelik Değeri', 'y': 'Frekans'}
                )
                fig_dist.add_vline(x=np.mean(all_values), line_dash="dash", line_color="red", 
                                   annotation_text="Ortalama")
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Eşik değer seçimi
                st.markdown("#### 🎯 Eşik Değer Seçimi")
                
                threshold = st.slider(
                    "Eşik değeri belirleyin (bu değerin üzerindeki değerler 1, altındakiler 0 olacak):",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.01,
                    help="Seçilen eşik değerine göre yeni bir binary matris oluşturulur"
                )
                
                # Eşik analizi
                values_above = sum(1 for v in all_values if v > threshold)
                values_below = len(all_values) - values_above
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"1'e Dönüşecek ({threshold:.2f} üzeri)", values_above)
                with col2:
                    st.metric(f"0'a Dönüşecek ({threshold:.2f} ve altı)", values_below)
                
                # Eşikleme uygula butonu
                if st.button("🔄 Eşikleme Uygula ve Yeni İterasyon Başlat", type="primary"):
                    with st.spinner("Yeni iterasyon hesaplanıyor..."):
                        # Eşikleme uygula
                        binary_matrix = threshold_matrix(current_data['membership_matrix'], U, threshold)
                        
                        # Binary matrisi soft set formatına dönüştür
                        new_E_named = {}
                        for e_key in binary_matrix.keys():
                            new_E_named[e_key] = set()
                            for u, val in binary_matrix[e_key].items():
                                if val == 1:
                                    new_E_named[e_key].add(u)
                        
                        # Yeni RMVC hesapla
                        new_membership_matrix = create_membership_matrix(new_E_named, U)
                        new_scores = calculate_scores(new_membership_matrix, U)
                        
                        # Yeni iterasyonu kaydet
                        st.session_state.iterations.append({
                            'iteration': current_iter + 1,
                            'membership_matrix': new_membership_matrix,
                            'scores': new_scores,
                            'threshold': threshold,
                            'binary_matrix': binary_matrix
                        })
                        
                        st.success(f"✅ İterasyon {current_iter + 1} oluşturuldu!")
                        st.rerun()
                
                # İterasyon karşılaştırması
                if current_iter > 0:
                    st.markdown("---")
                    st.markdown("#### 📊 İterasyon Karşılaştırması")
                    
                    # Hangi iterasyonları karşılaştıracak
                    col1, col2 = st.columns(2)
                    with col1:
                        iter_a = st.selectbox(
                            "İterasyon A:",
                            range(len(st.session_state.iterations)),
                            index=max(0, current_iter - 1),
                            format_func=lambda x: f"İterasyon {x}"
                        )
                    with col2:
                        iter_b = st.selectbox(
                            "İterasyon B:",
                            range(len(st.session_state.iterations)),
                            index=current_iter,
                            format_func=lambda x: f"İterasyon {x}"
                        )
                    
                    if iter_a != iter_b:
                        data_a = st.session_state.iterations[iter_a]
                        data_b = st.session_state.iterations[iter_b]
                        
                        # Sıralama karşılaştırma
                        comparison_df = compare_rankings(data_a['scores'], data_b['scores'])
                        
                        st.markdown(f"##### 🔄 İterasyon {iter_a} → İterasyon {iter_b} Sıralama Değişimleri")
                        
                        # İstatistikler
                        num_up = len(comparison_df[comparison_df['Durum'] == '🟢 Yükseldi'])
                        num_down = len(comparison_df[comparison_df['Durum'] == '🔴 Düştü'])
                        num_same = len(comparison_df[comparison_df['Durum'] == '⚪ Aynı'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🟢 Yükselenler", num_up)
                        with col2:
                            st.metric("🔴 Düşenler", num_down)
                        with col3:
                            st.metric("⚪ Aynı Kalanlar", num_same)
                        
                        # Karşılaştırma tablosu
                        st.dataframe(comparison_df, use_container_width=True, height=400)
                        
                        # Skor değişimi grafiği
                        st.markdown("##### 📈 Skor Değişimleri")
                        
                        fig_change = go.Figure()
                        
                        elements = comparison_df['Eleman'].tolist()
                        old_scores = comparison_df['Eski Skor'].tolist()
                        new_scores = comparison_df['Yeni Skor'].tolist()
                        
                        fig_change.add_trace(go.Scatter(
                            x=elements,
                            y=old_scores,
                            mode='markers+lines',
                            name=f'İterasyon {iter_a}',
                            marker=dict(size=8)
                        ))
                        
                        fig_change.add_trace(go.Scatter(
                            x=elements,
                            y=new_scores,
                            mode='markers+lines',
                            name=f'İterasyon {iter_b}',
                            marker=dict(size=8)
                        ))
                        
                        fig_change.update_layout(
                            title='Elemanların Skor Değişimleri',
                            xaxis_title='Eleman',
                            yaxis_title='Skor',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_change, use_container_width=True)
                
                # İterasyon geçmişi
                if len(st.session_state.iterations) > 1:
                    st.markdown("---")
                    st.markdown("#### 📜 İterasyon Geçmişi")
                    
                    history_data = []
                    for i, iter_data in enumerate(st.session_state.iterations):
                        sorted_iter = sorted(iter_data['scores'].items(), 
                                           key=lambda x: float(x[1]), reverse=True)
                        top_3 = [u for u, _ in sorted_iter[:3]]
                        
                        history_data.append({
                            'İterasyon': i,
                            'Eşik Değer': iter_data['threshold'] if iter_data['threshold'] is not None else 'N/A',
                            'Top 1': top_3[0] if len(top_3) > 0 else '',
                            'Top 2': top_3[1] if len(top_3) > 1 else '',
                            'Top 3': top_3[2] if len(top_3) > 2 else ''
                        })
                    
                    history_df = pd.DataFrame(history_data)
                    st.dataframe(history_df, use_container_width=True)
                    
                    # Sıfırla butonu
                    if st.button("🔄 Tüm İterasyonları Sıfırla"):
                        st.session_state.iterations = [{
                            'iteration': 0,
                            'membership_matrix': membership_matrix,
                            'scores': scores,
                            'threshold': None,
                            'binary_matrix': None
                        }]
                        st.success("✅ İterasyonlar sıfırlandı!")
                        st.rerun()
            
            # İndirme butonları
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_scores = score_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Skorları İndir", csv_scores, "rmvc_skorlar.csv", "text/csv")
            
            with col2:
                csv_matrix = matrix_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Matrisi İndir", csv_matrix, "rmvc_matris.csv", "text/csv")
            
            with col3:
                csv_param = param_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Parametreleri İndir", csv_param, "rmvc_parametreler.csv", "text/csv")
        
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.exception(e)
    
    else:
        # Dosya yüklenmemişse
        st.info("👆 Lütfen sol panelden bir CSV veya Excel dosyası yükleyin.")
        
        # Example 1 gösterimi
        st.markdown("### 📝 Makaledeki Example 1 Formatı")
        
        example_df = pd.DataFrame({
            'e1': [1, 1, 1, 0, 1],
            'e2': [0, 1, 0, 1, 1],
            'e3': [1, 0, 1, 1, 0],
            'e4': [1, 1, 0, 0, 1]
        }, index=['1', '2', '3', '4', '5'])
        
        st.markdown("**Girdi Matrisi (Binary Soft Set):**")
        st.dataframe(example_df)
        
        st.markdown("""
        **Açıklama:**
        - **Satırlar:** Elemanlar (1, 2, 3, 4, 5) = U
        - **Sütunlar:** Parametreler (e1, e2, e3, e4) = E
        - **Değerler:** 1 = eleman parametreye ait, 0 = ait değil
        
        **Beklenen Sonuçlar (Makaleden):**
        - e₁ için 4. eleman: **0.333** (1/3)
        - e₂ için 1. eleman: **0.556** (5/9)
        - e₂ için 3. eleman: **0.333** (1/3)
        - e₃ için 2. eleman: **0.444** (4/9)
        - e₄ için 4. eleman: **0.333** (1/3)
        """)
        
        # Demo butonu
        if st.button("🚀 Example 1 ile Test Et"):
            # Example 1 verisini kullan
            U = {'1', '2', '3', '4', '5'}
            E_named = {
                'e_1': {'1', '2', '3', '5'},
                'e_2': {'2', '4', '5'},
                'e_3': {'1', '3', '4'},
                'e_4': {'1', '2', '5'}
            }
            E_info = {
                'e_1': {'orijinal_ad': 'e1', 'eleman_sayisi': 4, 'toplam_deger': 4, 'elemanlar': {'1', '2', '3', '5'}},
                'e_2': {'orijinal_ad': 'e2', 'eleman_sayisi': 3, 'toplam_deger': 3, 'elemanlar': {'2', '4', '5'}},
                'e_3': {'orijinal_ad': 'e3', 'eleman_sayisi': 3, 'toplam_deger': 3, 'elemanlar': {'1', '3', '4'}},
                'e_4': {'orijinal_ad': 'e4', 'eleman_sayisi': 3, 'toplam_deger': 3, 'elemanlar': {'1', '2', '5'}}
            }
            
            membership_matrix = create_membership_matrix(E_named, U)
            
            st.markdown("### ✅ Example 1 Sonuçları")
            
            # Sonuç matrisi
            st.markdown("**Üyelik Matrisi:**")
            result_data = []
            for e_i in ['e_1', 'e_2', 'e_3', 'e_4']:
                row = {'Parametre': e_i}
                for u in ['1', '2', '3', '4', '5']:
                    val = membership_matrix[e_i][u]
                    row[u] = f"{float(val):.3f} ({val})"
                result_data.append(row)
            
            result_df = pd.DataFrame(result_data)
            st.dataframe(result_df, use_container_width=True)
            
            # Doğrulama
            st.markdown("**Doğrulama (Makaledeki değerlerle karşılaştırma):**")
            checks = [
                ('e_1', '4', Fraction(1, 3), 0.333),
                ('e_2', '1', Fraction(5, 9), 0.556),
                ('e_2', '3', Fraction(1, 3), 0.333),
                ('e_3', '2', Fraction(4, 9), 0.444),
                ('e_3', '5', Fraction(4, 9), 0.444),
                ('e_4', '3', Fraction(4, 9), 0.444),
                ('e_4', '4', Fraction(1, 3), 0.333),
            ]
            
            for e_i, u, expected_frac, expected_dec in checks:
                actual = membership_matrix[e_i][u]
                match = "✅" if actual == expected_frac else "❌"
                st.write(f"{match} M({u}, {e_i}) = {float(actual):.3f} (Beklenen: {expected_dec})")


if __name__ == "__main__":
    main()
