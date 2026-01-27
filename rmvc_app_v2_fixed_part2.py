# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

def main():
    # Başlık
    st.markdown('<div class="main-header">📊 RMVC Analiz Aracı v2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Relational Membership Value Calculation - Soft Set Teorisi Tabanlı</div>', unsafe_allow_html=True)
    
    # Ana sayfa açıklama metni
    st.markdown("""
    Bu araç, Relational Membership Value Calculation (RMVC) algoritmasını kullanarak soft set tabanlı karar verme
    sürecini kolaylaştırmak için tasarlanmıştır.
    
    **Kullanım:**
    1. Sol panelden bir CSV veya Excel dosyası yükleyin
    2. Formatı doğru seçin (Satırlar=Parametreler veya Satırlar=Elemanlar)
    3. Sonuçları görüntüleyin ve analiz edin
    
    **Özellikler:**
    - Üyelik matrisi hesaplama ve görüntüleme
    - Eleman skorları ve sıralama
    - Grafiksel analiz ve görselleştirme
    - İteratif RMVC analizi
    - Detaylı parametre ve eleman incelemesi
    
    **Referans:**
    > Dayioglu, A.; Erdogan, F.O.; Celik, B. "RMVC: A Validated Algorithmic Framework for Decision-Making Under Uncertainty". Mathematics 2025, 13, 2693.
    """)
    
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
                    sum_row = pd.DataFrame([col_sums], columns=numeric_cols, index=['SUM s(x)'])
                    export_df = pd.concat([export_df, sum_row])
                    
                    csv = export_df.to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Üyelik Matrisini İndir",
                        data=csv,
                        file_name="rmvc_membership_matrix.csv",
                        mime="text/csv",
                    )
                
                # TAB 3: Grafikler
                with tab3:
                    st.markdown("### 📊 Skor Dağılımı")
                    
                    # Skor grafiği
                    fig_scores = px.bar(
                        score_data, 
                        x='Eleman', 
                        y='Skor (Ondalık)',
                        color='Skor (Ondalık)',
                        color_continuous_scale='Blues',
                        title='Eleman Skorları',
                        labels={'Eleman': 'Eleman', 'Skor (Ondalık)': 'Skor'}
                    )
                    fig_scores.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_scores, use_container_width=True)
                    
                    # Heatmap
                    st.markdown("### 🔥 Üyelik Matrisi Heatmap")
                    
                    # Heatmap için veri hazırla
                    heatmap_df = matrix_df.set_index('SETS')
                    
                    fig_heatmap = px.imshow(
                        heatmap_df,
                        color_continuous_scale='Blues',
                        title='Üyelik Değerleri Heatmap',
                        labels=dict(x="Eleman", y="Parametre", color="Üyelik Değeri")
                    )
                    fig_heatmap.update_xaxes(side="top")
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # TAB 4: Parametre Analizi
                with tab4:
                    st.markdown("### 📈 Parametre Analizi")
                    
                    # Parametre seçimi
                    selected_param = st.selectbox(
                        "Parametre seçin:",
                        sorted(E_named.keys(), key=param_sort_key),
                        format_func=lambda x: f"{x} ({E_info[x]['orijinal_ad']})"
                    )
                    
                    if selected_param:
                        st.markdown(f"#### {selected_param} - {E_info[selected_param]['orijinal_ad']}")
                        
                        # Parametre bilgileri
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Eleman Sayısı", E_info[selected_param]['eleman_sayisi'])
                        with col2:
                            st.metric("Toplam Değer", E_info[selected_param]['toplam_deger'])
                        with col3:
                            st.metric("Ortalama Değer", 
                                     f"{E_info[selected_param]['toplam_deger']/max(1, E_info[selected_param]['eleman_sayisi']):.2f}")
                        
                        # Elemanlar
                        st.markdown("#### 📋 Parametreye Ait Elemanlar")
                        elements = sorted(E_info[selected_param]['elemanlar'], key=safe_sort_key)
                        st.write(", ".join(elements))
                        
                        # Üyelik değerleri
                        st.markdown("#### 📊 Üyelik Değerleri")
                        
                        param_values = []
                        for u in sorted(U, key=safe_sort_key):
                            val = membership_matrix[selected_param].get(u, Fraction(0, 1))
                            param_values.append({
                                'Eleman': u,
                                'Üyelik (Kesir)': str(val) if kesir_goster else '-',
                                'Üyelik (Ondalık)': float(val),
                                'Durum': '✅ Tam Üye' if float(val) == 1 else ('❌ Üye Değil' if float(val) == 0 else '🔶 Kısmi Üye')
                            })
                        
                        param_df = pd.DataFrame(param_values)
                        st.dataframe(param_df, use_container_width=True)
                        
                        # Üyelik grafiği
                        fig_param = px.bar(
                            param_df,
                            x='Eleman',
                            y='Üyelik (Ondalık)',
                            color='Üyelik (Ondalık)',
                            color_continuous_scale='Blues',
                            title=f'{selected_param} - Üyelik Değerleri',
                            labels={'Eleman': 'Eleman', 'Üyelik (Ondalık)': 'Üyelik Değeri'}
                        )
                        fig_param.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_param, use_container_width=True)
                
                # TAB 5: Detaylı Analiz
                with tab5:
                    st.markdown("### 🔍 Detaylı Eleman Analizi")
                    
                    # Eleman seçimi
                    selected_u = st.selectbox(
                        "Eleman seçin:",
                        sorted(U, key=safe_sort_key)
                    )
                    
                    if selected_u:
                        st.markdown(f"#### Eleman {selected_u} - Detaylı Analiz")
                        
                        # Eleman skoru
                        st.metric("Toplam Skor", f"{float(scores[selected_u]):.4f} ({scores[selected_u]})")
                        
                        # Üyelik değerleri
                        st.markdown("#### 📊 Parametrelere Üyelik Değerleri")
                        
                        elem_values = []
                        for e_i in sorted(E_named.keys(), key=param_sort_key):
                            val = membership_matrix[e_i].get(selected_u, Fraction(0, 1))
                            elem_values.append({
                                'Parametre': e_i,
                                'Orijinal Ad': E_info[e_i]['orijinal_ad'],
                                'Üyelik (Kesir)': str(val) if kesir_goster else '-',
                                'Üyelik (Ondalık)': float(val),
                                'Durum': '✅ Tam Üye' if float(val) == 1 else ('❌ Üye Değil' if float(val) == 0 else '🔶 Kısmi Üye')
                            })
                        
                        elem_df = pd.DataFrame(elem_values)
                        st.dataframe(elem_df, use_container_width=True)
                        
                        # Üyelik grafiği
                        fig_elem = px.bar(
                            elem_df,
                            x='Parametre',
                            y='Üyelik (Ondalık)',
                            color='Üyelik (Ondalık)',
                            color_continuous_scale='Blues',
                            title=f'Eleman {selected_u} - Parametre Üyelik Değerleri',
                            labels={'Parametre': 'Parametre', 'Üyelik (Ondalık)': 'Üyelik Değeri'}
                        )
                        fig_elem.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_elem, use_container_width=True)
                        
                        # Radar grafiği
                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[float(membership_matrix[e_i].get(selected_u, Fraction(0, 1))) for e_i in sorted(E_named.keys(), key=param_sort_key)],
                            theta=[e_i for e_i in sorted(E_named.keys(), key=param_sort_key)],
                            fill='toself',
                            name=selected_u
                        ))
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                            title=f'Eleman {selected_u} - Parametre Üyelik Profili'
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
