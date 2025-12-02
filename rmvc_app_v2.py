# -*- coding: utf-8 -*-
"""
RMVC Web Arayüzü v2 - Düzeltilmiş Versiyon
==========================================
Makaledeki (mathematics-13-02693-v3) formüllere uygun hesaplama.

Düzeltmeler:
1. Delta fonksiyonu: Tüm kümelerde ikili sayımı (break kaldırıldı)
2. Matris yönü: Satırlar=Parametreler, Sütunlar=Elemanlar
3. Formül doğrulaması: Example 1 ile test edildi

Çalıştırma:
    streamlit run rmvc_app_v2.py --server.port 8510
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

def csv_to_soft_set(df):
    """
    CSV verisini Soft Set formatına dönüştürür.
    
    Makaledeki notasyon:
    - U: Evrensel küme (satırlar = elemanlar/adaylar)
    - E: Parametre kümesi (sütunlar = kriterler)
    - Φ(e_i): e_i parametresine ait elemanlar kümesi
    """
    # Satırlar = Elemanlar (U), Sütunlar = Parametreler (E)
    eleman_ids = df.index.tolist()
    parametre_ids = df.columns.tolist()
    
    # U: Evrensel küme
    U = set(str(eid) for eid in eleman_ids)
    
    # E: Parametre kümeleri - Φ(e_i) = {u ∈ U : değer > 0}
    E_named = {}
    E_info = {}
    
    for i, param_id in enumerate(parametre_ids):
        e_key = f"e_{i+1}"
        sutun_verisi = df[param_id]
        
        # Φ(e_i): Bu parametreye ait elemanlar
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
    Satırlar = Parametreler, Sütunlar = Elemanlar (Makaledeki format)
    """
    # Elemanları sırala
    sorted_elements = sorted(U, key=lambda x: int(x) if x.isdigit() else x)
    
    data = []
    for e_i in sorted(membership_matrix.keys(), key=lambda x: int(x.split('_')[1])):
        row = {'Parametre': e_i, 'Orijinal': E_info[e_i]['orijinal_ad']}
        for u in sorted_elements:
            val = membership_matrix[e_i].get(u, Fraction(0, 1))
            row[u] = float(val)
        data.append(row)
    
    return pd.DataFrame(data)


def get_element_detail(u, membership_matrix, E_info):
    """Bir elemanın tüm parametrelerdeki üyelik değerlerini döndürür."""
    details = []
    for e_i in sorted(membership_matrix.keys(), key=lambda x: int(x.split('_')[1])):
        val = membership_matrix[e_i].get(u, Fraction(0, 1))
        details.append({
            'Parametre': e_i,
            'Orijinal Ad': E_info[e_i]['orijinal_ad'],
            'Üyelik (Kesir)': str(val),
            'Üyelik (Ondalık)': round(float(val), 4)
        })
    return pd.DataFrame(details)


# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

def main():
    # Başlık
    st.markdown('<div class="main-header">📊 RMVC Analiz Aracı v2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Rough Multi-Valued Choice - Makaledeki Formüllere Uygun</div>', unsafe_allow_html=True)
    
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
        
        transpose_matrix = st.checkbox(
            "Matrisi transpose et", 
            value=False,
            help="Eğer dosyanızda Satırlar=Parametreler, Sütunlar=Elemanlar ise işaretleyin"
        )
        bos_filtrele = st.checkbox("Boş kümeleri filtrele", value=True)
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
            
            # Transpose seçeneği
            if transpose_matrix:
                df = df.T
                st.info("ℹ️ Matris transpose edildi (Satırlar↔Sütunlar)")
            
            st.success(f"✅ Dosya yüklendi: {uploaded_file.name} ({df.shape[0]} eleman × {df.shape[1]} parametre)")
            
            # Veri önizleme
            with st.expander("📋 Yüklenen Veri (Girdi Matrisi)", expanded=False):
                st.dataframe(df, use_container_width=True)
            
            # RMVC Analizi
            with st.spinner("🔄 RMVC analizi yapılıyor..."):
                U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df)
                
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
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏆 Sonuçlar", 
                "🔢 Üyelik Matrisi",
                "📊 Grafikler",
                "📈 Parametre Analizi",
                "🔍 Detaylı Analiz"
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
                st.markdown("### 🔢 Üyelik Matrisi M(u, eᵢ)")
                st.markdown("**Satırlar:** Parametreler (eᵢ) | **Sütunlar:** Elemanlar (u)")
                
                # Matrisi DataFrame'e dönüştür
                matrix_df = matrix_to_dataframe(membership_matrix, U, E_info)
                
                # Sayısal sütunları al
                numeric_cols = [c for c in matrix_df.columns if c not in ['Parametre', 'Orijinal']]
                
                # Kesir veya ondalık gösterim
                if kesir_goster:
                    display_df = matrix_df.copy()
                    for col in numeric_cols:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if x != 1.0 else "1")
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.dataframe(matrix_df.round(4), use_container_width=True)
                
                # Heatmap
                st.markdown("### 🗺️ Üyelik Matrisi Heatmap")
                
                heatmap_data = matrix_df[numeric_cols].values
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    x=numeric_cols,
                    y=matrix_df['Parametre'].tolist(),
                    title='Üyelik Değerleri (Sarı=1, Mor=0)',
                    color_continuous_scale='Viridis',
                    aspect='auto',
                    text_auto='.2f'
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Sütun toplamları (Skorlar)
                st.markdown("### 📊 Sütun Toplamları = Skorlar")
                col_sums = matrix_df[numeric_cols].sum()
                col_sums_df = pd.DataFrame({
                    'Eleman': col_sums.index,
                    'Toplam Skor': col_sums.values.round(4)
                }).sort_values('Toplam Skor', ascending=False)
                st.dataframe(col_sums_df, use_container_width=True)
            
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
                for e_i in sorted(E_info.keys(), key=lambda x: int(x.split('_')[1])):
                    info = E_info[e_i]
                    param_data.append({
                        'Parametre': e_i,
                        'Orijinal ID': info['orijinal_ad'],
                        'Eleman Sayısı |Φ(eᵢ)|': info['eleman_sayisi'],
                        'γ(eᵢ)': info['eleman_sayisi'] * (len(E_named) - 1),
                        'Elemanlar': ', '.join(sorted(info['elemanlar'], key=lambda x: int(x) if x.isdigit() else x))
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
