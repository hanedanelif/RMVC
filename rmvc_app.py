# -*- coding: utf-8 -*-
"""
RMVC Web Arayüzü - Streamlit Uygulaması
=======================================
CSV/Excel dosyasından RMVC analizi yapan interaktif web arayüzü.

Çalıştırma:
    streamlit run rmvc_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from fractions import Fraction
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Konfigürasyonu
st.set_page_config(
    page_title="RMVC Analiz Aracı",
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# RMVC FONKSİYONLARI
# ============================================================

def csv_to_soft_set(df):
    """CSV verisini Soft Set formatına dönüştürür."""
    satir_ids = df.index.tolist()
    sutun_ids = df.columns.tolist()
    
    U = set(str(sid) for sid in satir_ids)
    
    E_named = {}
    E_info = {}  # Ek bilgiler için
    
    for i, sutun_id in enumerate(sutun_ids):
        e_key = f"e_{i+1}"
        sutun_verisi = df[sutun_id]
        
        alt_kume = set()
        toplam_deger = 0
        
        for satir_id, deger in sutun_verisi.items():
            try:
                numeric_val = pd.to_numeric(deger, errors='coerce')
                if numeric_val > 0:
                    alt_kume.add(str(satir_id))
                    toplam_deger += numeric_val
            except:
                pass
        
        E_named[e_key] = alt_kume
        E_info[e_key] = {
            'orijinal_ad': str(sutun_id),
            'eleman_sayisi': len(alt_kume),
            'toplam_deger': toplam_deger
        }
    
    return U, E_named, E_info, satir_ids, sutun_ids


def delta_function(e_name, E_named, U):
    """Delta fonksiyonu hesaplama."""
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    
    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            for other_e_set in E_named.values():
                if {element, other_element}.issubset(other_e_set):
                    total_sum += 1
                    break
        results[element] = total_sum
    
    return results


def create_membership_matrix(E_named, U):
    """Üyelik matrisini oluşturur."""
    membership_matrix = {e_key: {} for e_key in E_named.keys()}
    m = len(E_named)
    
    for e_key in E_named.keys():
        e_set = E_named[e_key]
        delta_results = delta_function(e_key, E_named, U)
        g_coeff = len(e_set) * (m - 1) if len(e_set) > 0 and m > 1 else 1
        
        for element in U:
            if element in e_set:
                membership_value = 1.0
            elif element in delta_results and g_coeff > 0:
                membership_value = float(Fraction(delta_results[element], g_coeff))
            else:
                membership_value = 0.0
            
            membership_matrix[e_key][element] = membership_value
    
    return membership_matrix


def calculate_scores(membership_matrix):
    """Skorları hesaplar."""
    elements = set()
    for row in membership_matrix.values():
        elements.update(row.keys())
    
    scores = {}
    for element in elements:
        total = sum(row.get(element, 0) for row in membership_matrix.values())
        scores[element] = round(total, 4)
    
    return scores


def get_element_criteria_membership(element, membership_matrix, E_info):
    """Bir elemanın tüm kriterlerdeki üyelik değerlerini döndürür."""
    memberships = []
    for e_key, row in membership_matrix.items():
        memberships.append({
            'Kriter': e_key,
            'Orijinal Ad': E_info[e_key]['orijinal_ad'],
            'Üyelik Değeri': row.get(element, 0)
        })
    return pd.DataFrame(memberships)


# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

def main():
    # Başlık
    st.markdown('<div class="main-header">📊 RMVC Analiz Aracı</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Rough Multi-Valued Choice - Çok Kriterli Karar Verme Sistemi</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/analytics.png", width=150)
        st.markdown("### 📁 Veri Yükleme")
        
        uploaded_file = st.file_uploader(
            "CSV veya Excel dosyası yükleyin",
            type=['csv', 'xlsx', 'xls'],
            help="İlk sütun ID, ilk satır başlıklar olmalı. Değerler: 0=ilişki yok, >0=ilişki var"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Ayarlar")
        
        bos_kumeleri_filtrele = st.checkbox("Boş kümeleri filtrele", value=True)
        min_eleman = st.slider("Min. eleman sayısı", 0, 10, 0)
        
        st.markdown("---")
        st.markdown("### 📖 Hakkında")
        st.info("""
        **RMVC Yöntemi**
        
        Rough Set Theory tabanlı çok kriterli karar verme algoritması.
        
        - CSV/Excel'den veri okuma
        - Otomatik Soft Set dönüşümü
        - Üyelik matrisi hesaplama
        - Optimal seçim belirleme
        """)
    
    # Ana içerik
    if uploaded_file is not None:
        # Dosyayı oku
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, index_col=0)
            else:
                df = pd.read_excel(uploaded_file, index_col=0)
            
            st.success(f"✅ Dosya başarıyla yüklendi: {uploaded_file.name}")
            
            # Veri önizleme
            with st.expander("📋 Yüklenen Veri Önizlemesi", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Toplam: {df.shape[0]} satır × {df.shape[1]} sütun")
            
            # RMVC Analizi
            with st.spinner("🔄 RMVC analizi yapılıyor..."):
                U, E_named, E_info, satir_ids, sutun_ids = csv_to_soft_set(df)
                
                # Filtreleme
                if bos_kumeleri_filtrele:
                    E_named = {k: v for k, v in E_named.items() if len(v) >= min_eleman}
                    E_info = {k: v for k, v in E_info.items() if k in E_named}
                
                if len(E_named) < 2:
                    st.error("❌ En az 2 boş olmayan kriter kümesi gerekli!")
                    return
                
                # Hesaplamalar
                membership_matrix = create_membership_matrix(E_named, U)
                scores = calculate_scores(membership_matrix)
                sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
                best_score = sorted_scores[0][1]
                best_choices = [elem for elem, score in sorted_scores if score == best_score]
            
            # Sonuç Tabları
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏆 Sonuçlar", 
                "📊 Grafikler", 
                "🔢 Üyelik Matrisi",
                "📈 Kriter Analizi",
                "🔍 Detaylı Analiz"
            ])
            
            # TAB 1: Sonuçlar
            with tab1:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Toplam Eleman", len(U))
                with col2:
                    st.metric("Toplam Kriter", len(E_named))
                with col3:
                    st.metric("Ortalama Skor", f"{np.mean(list(scores.values())):.2f}")
                with col4:
                    st.metric("Max Skor", f"{best_score:.2f}")
                
                # En iyi seçim
                st.markdown(f"""
                <div class="best-choice">
                    🏆 <b>Optimal Seçim:</b> {', '.join(best_choices)}<br>
                    <small>Skor: {best_score:.4f}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Skor tablosu
                st.markdown("### 📋 Eleman Skorları")
                
                score_df = pd.DataFrame(sorted_scores, columns=['Eleman', 'Skor'])
                score_df['Sıra'] = range(1, len(score_df) + 1)
                score_df['Durum'] = score_df['Skor'].apply(
                    lambda x: '⭐ EN İYİ' if x == best_score else ('✅ İyi' if x > np.mean(list(scores.values())) else ''))
                score_df = score_df[['Sıra', 'Eleman', 'Skor', 'Durum']]
                
                st.dataframe(score_df, use_container_width=True, height=400)
            
            # TAB 2: Grafikler
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bar chart - Skorlar
                    fig_bar = px.bar(
                        score_df.head(20),
                        x='Eleman',
                        y='Skor',
                        title='🏅 En Yüksek Skorlu Elemanlar (Top 20)',
                        color='Skor',
                        color_continuous_scale='Viridis'
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Pie chart - Skor dağılımı
                    bins = [0, 1, 2, 3, 4, 5, float('inf')]
                    labels = ['0-1', '1-2', '2-3', '3-4', '4-5', '5+']
                    score_df['Skor Aralığı'] = pd.cut(score_df['Skor'], bins=bins, labels=labels)
                    dist = score_df['Skor Aralığı'].value_counts()
                    
                    fig_pie = px.pie(
                        values=dist.values,
                        names=dist.index,
                        title='📊 Skor Dağılımı',
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Histogram
                fig_hist = px.histogram(
                    score_df,
                    x='Skor',
                    nbins=20,
                    title='📈 Skor Histogramı',
                    color_discrete_sequence=['#1f77b4']
                )
                fig_hist.add_vline(x=best_score, line_dash="dash", line_color="red",
                                   annotation_text=f"Max: {best_score:.2f}")
                fig_hist.add_vline(x=np.mean(list(scores.values())), line_dash="dash", line_color="green",
                                   annotation_text=f"Ort: {np.mean(list(scores.values())):.2f}")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # TAB 3: Üyelik Matrisi
            with tab3:
                st.markdown("### 🔢 Üyelik Matrisi")
                
                # Matrisi DataFrame'e dönüştür
                matrix_df = pd.DataFrame(membership_matrix).T
                matrix_df = matrix_df.round(3)
                
                # Heatmap
                fig_heatmap = px.imshow(
                    matrix_df.values,
                    x=matrix_df.columns.tolist(),
                    y=matrix_df.index.tolist(),
                    title='Üyelik Matrisi Heatmap',
                    color_continuous_scale='RdYlGn',
                    aspect='auto'
                )
                fig_heatmap.update_layout(height=600)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Tablo
                with st.expander("📋 Matris Tablosu"):
                    st.dataframe(matrix_df, use_container_width=True)
            
            # TAB 4: Kriter Analizi
            with tab4:
                st.markdown("### 📈 Kriter (Ürün) Analizi")
                
                # Kriter bilgileri
                kriter_df = pd.DataFrame([
                    {
                        'Kriter': k,
                        'Orijinal ID': v['orijinal_ad'],
                        'Eleman Sayısı': v['eleman_sayisi'],
                        'Toplam Değer': v['toplam_deger']
                    }
                    for k, v in E_info.items()
                ])
                kriter_df = kriter_df.sort_values('Eleman Sayısı', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Popüler kriterler
                    fig_kriter = px.bar(
                        kriter_df.head(15),
                        x='Orijinal ID',
                        y='Eleman Sayısı',
                        title='🔥 En Popüler Kriterler (Ürünler)',
                        color='Eleman Sayısı',
                        color_continuous_scale='Reds'
                    )
                    fig_kriter.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_kriter, use_container_width=True)
                
                with col2:
                    # Toplam değer
                    fig_deger = px.bar(
                        kriter_df.sort_values('Toplam Değer', ascending=False).head(15),
                        x='Orijinal ID',
                        y='Toplam Değer',
                        title='💰 En Yüksek Değerli Kriterler',
                        color='Toplam Değer',
                        color_continuous_scale='Greens'
                    )
                    fig_deger.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_deger, use_container_width=True)
                
                # Kriter tablosu
                st.dataframe(kriter_df, use_container_width=True)
            
            # TAB 5: Detaylı Analiz
            with tab5:
                st.markdown("### 🔍 Eleman Detaylı Analizi")
                
                selected_element = st.selectbox(
                    "Analiz edilecek elemanı seçin:",
                    options=sorted(U, key=lambda x: -scores.get(x, 0)),
                    format_func=lambda x: f"{x} (Skor: {scores.get(x, 0):.2f})"
                )
                
                if selected_element:
                    elem_score = scores.get(selected_element, 0)
                    elem_rank = [i for i, (e, s) in enumerate(sorted_scores, 1) if e == selected_element][0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Skor", f"{elem_score:.4f}")
                    with col2:
                        st.metric("Sıralama", f"{elem_rank}/{len(U)}")
                    with col3:
                        percentile = (1 - elem_rank/len(U)) * 100
                        st.metric("Yüzdelik Dilim", f"%{percentile:.1f}")
                    
                    # Kriterlerdeki üyelik değerleri
                    elem_memberships = get_element_criteria_membership(selected_element, membership_matrix, E_info)
                    elem_memberships = elem_memberships.sort_values('Üyelik Değeri', ascending=False)
                    
                    # Radar chart
                    top_criteria = elem_memberships.head(10)
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=top_criteria['Üyelik Değeri'].tolist(),
                        theta=top_criteria['Orijinal Ad'].tolist(),
                        fill='toself',
                        name=selected_element
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        title=f'{selected_element} - Kriter Üyelik Profili (Top 10)'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # Üyelik tablosu
                    st.markdown("#### Tüm Kriter Üyelik Değerleri")
                    st.dataframe(elem_memberships, use_container_width=True)
            
            # İndirme butonu
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_scores = score_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Skorları İndir (CSV)",
                    csv_scores,
                    "rmvc_skorlar.csv",
                    "text/csv"
                )
            
            with col2:
                csv_matrix = pd.DataFrame(membership_matrix).T.to_csv().encode('utf-8')
                st.download_button(
                    "📥 Matrisi İndir (CSV)",
                    csv_matrix,
                    "rmvc_matris.csv",
                    "text/csv"
                )
            
            with col3:
                csv_kriter = kriter_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Kriter Analizini İndir (CSV)",
                    csv_kriter,
                    "rmvc_kriterler.csv",
                    "text/csv"
                )
        
        except Exception as e:
            st.error(f"❌ Hata oluştu: {str(e)}")
            st.exception(e)
    
    else:
        # Dosya yüklenmemişse bilgi göster
        st.info("👆 Lütfen sol panelden bir CSV veya Excel dosyası yükleyin.")
        
        # Örnek format
        st.markdown("### 📝 Beklenen Dosya Formatı")
        
        ornek_df = pd.DataFrame({
            'Ürün_1': [100, 0, 50, 0],
            'Ürün_2': [0, 200, 0, 75],
            'Ürün_3': [30, 0, 0, 100]
        }, index=['Firma_A', 'Firma_B', 'Firma_C', 'Firma_D'])
        
        st.dataframe(ornek_df)
        
        st.markdown("""
        **Açıklama:**
        - **Satırlar:** Elemanlar (Firmalar, Adaylar vb.)
        - **Sütunlar:** Kriterler (Ürünler, Özellikler vb.)
        - **Değerler:** 0 = ilişki yok, >0 = ilişki var (değer büyüklüğü)
        """)
        
        # Demo butonu
        if st.button("🚀 Demo Veri ile Dene"):
            st.session_state['demo'] = True
            st.rerun()


if __name__ == "__main__":
    main()
