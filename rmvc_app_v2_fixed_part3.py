                # TAB 6: İteratif Analiz
                with tab6:
                    # Profesyonel başlık ve açıklama
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               padding: 2rem; border-radius: 10px; margin: -1rem -1rem 2rem -1rem; 
                               color: white; text-align: center;'>
                        <h1 style='margin: 0; font-size: 2.5rem;'>🔄 İteratif RMVC Analizi</h1>
                        <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
                            Üyelik matrisini eşikleyerek binary matris oluşturun ve RMVC algoritmasını tekrar çalıştırın
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Session state başlat
                    if 'iterations' not in st.session_state:
                        st.session_state.iterations = [{
                            'iteration': 0,
                            'membership_matrix': membership_matrix,
                            'scores': scores,
                            'threshold': None,
                            'keep_below': None,
                            'thresholded_matrix': None
                        }]
                    
                    current_iter = len(st.session_state.iterations) - 1
                    current_data = st.session_state.iterations[current_iter]
                    
                    # İterasyon durumu kartı
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style='background: #f0f2f6; padding: 1rem; border-radius: 10px; 
                                   border-left: 4px solid #667eea;'>
                            <h3 style='margin: 0; color: #2d3748;'>📍 Mevcut İterasyon</h3>
                            <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: #667eea;'>
                                İterasyon {current_iter}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if current_iter > 0:
                            if st.button("🔄 Tümünü Sıfırla", type="secondary", use_container_width=True):
                                st.session_state.iterations = [{
                                    'iteration': 0,
                                    'membership_matrix': membership_matrix,
                                    'scores': scores,
                                    'threshold': None,
                                    'keep_below': None,
                                    'thresholded_matrix': None
                                }]
                                st.rerun()
                    
                    # Ana içerik için iki kolon
                    col_left, col_right = st.columns([1, 1])
                    
                    with col_left:
                        # 📊 Matris İstatistikleri
                        st.markdown("""
                        <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                            <h3 style='margin: 0 0 1rem 0; color: #2d3748;'>📊 Matris İstatistikleri</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Tüm değerleri topla
                        all_values = []
                        for row in current_data['membership_matrix'].values():
                            all_values.extend([float(v) for v in row.values()])
                        
                        fractional_values = [v for v in all_values if 0 < v < 1]
                        count_zeros = sum(1 for v in all_values if v == 0.0)
                        count_ones = sum(1 for v in all_values if v == 1.0)
                        
                        # İstatistik kartları
                        stats_grid = st.columns(2)
                        with stats_grid[0]:
                            st.markdown("""
                            <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                       border-left: 3px solid #48bb78; margin-bottom: 0.5rem;'>
                                <p style='margin: 0; font-size: 0.9rem; color: #718096;'>Toplam Değer</p>
                                <p style='margin: 0; font-size: 1.5rem; font-weight: bold; color: #2d3748;'>{}</p>
                            </div>
                            """.format(len(all_values)), unsafe_allow_html=True)
                        with stats_grid[1]:
                            st.markdown("""
                            <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                       border-left: 3px solid #4299e1; margin-bottom: 0.5rem;'>
                                <p style='margin: 0; font-size: 0.9rem; color: #718096;'>Ortalama</p>
                                <p style='margin: 0; font-size: 1.5rem; font-weight: bold; color: #2d3748;'>{:.4f}</p>
                            </div>
                            """.format(np.mean(all_values)), unsafe_allow_html=True)
                        
                        # Değer dağılımı
                        st.markdown("""
                        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                   border-left: 3px solid #9f7aea; margin-bottom: 0.5rem;'>
                            <p style='margin: 0; font-size: 0.9rem; color: #718096;'>Değer Dağılımı</p>
                            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                                <div style='text-align: center;'>
                                    <p style='margin: 0; font-size: 1.2rem; font-weight: bold; color: #e53e3e;'>{}</p>
                                    <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Sıfır</p>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='margin: 0; font-size: 1.2rem; font-weight: bold; color: #38a169;'>{}</p>
                                    <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Bir</p>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='margin: 0; font-size: 1.2rem; font-weight: bold; color: #3182ce;'>{}</p>
                                    <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Ondalıklı</p>
                                </div>
                            </div>
                        </div>
                        """.format(count_zeros, count_ones, len(fractional_values)), unsafe_allow_html=True)
                        
                        # Ondalıklı değerler detayı
                        if fractional_values:
                            st.markdown("""
                            <div style='background: #fef5e7; padding: 1rem; border-radius: 8px; 
                                       border-left: 3px solid #f39c12; margin-bottom: 0.5rem;'>
                                <p style='margin: 0; font-size: 0.9rem; color: #718096;'>Ondalıklı Değerler (0 ve 1 hariç)</p>
                                <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                                    <div style='text-align: center;'>
                                        <p style='margin: 0; font-size: 1rem; font-weight: bold; color: #2d3748;'>{:.4f}</p>
                                        <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Min</p>
                                    </div>
                                    <div style='text-align: center;'>
                                        <p style='margin: 0; font-size: 1rem; font-weight: bold; color: #2d3748;'>{:.4f}</p>
                                        <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Max</p>
                                    </div>
                                    <div style='text-align: center;'>
                                        <p style='margin: 0; font-size: 1rem; font-weight: bold; color: #2d3748;'>{:.4f}</p>
                                        <p style='margin: 0; font-size: 0.8rem; color: #718096;'>Ortalama</p>
                                    </div>
                                </div>
                            </div>
                            """.format(min(fractional_values), max(fractional_values), np.mean(fractional_values)), unsafe_allow_html=True)
                    
                    with col_right:
                        # 🎯 Eşikleme Kontrol Paneli
                        st.markdown("""
                        <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                            <h3 style='margin: 0 0 1rem 0; color: #2d3748;'>🎯 Eşikleme Kontrol Paneli</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Eşik değeri seçimi
                        default_threshold = round(np.mean(fractional_values), 4) if fractional_values else 0.5
                        
                        st.markdown("""
                        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                   margin-bottom: 1rem;'>
                            <p style='margin: 0 0 0.5rem 0; font-weight: bold; color: #2d3748;'>Eşik Değeri</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        threshold = st.slider(
                            "Eşik değeri:",
                            min_value=0.0,
                            max_value=1.0,
                            value=default_threshold,
                            step=0.0001,
                            format="%.4f",
                            help=f"Önerilen: {default_threshold:.4f} (ondalıklı değerlerin ortalaması)"
                        )
                        
                        # Operatör seçimi
                        st.markdown("""
                        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                   margin-bottom: 1rem;'>
                            <p style='margin: 0 0 0.5rem 0; font-weight: bold; color: #2d3748;'>Karşılaştırma Operatörü</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        threshold_operator = st.radio(
                            "Operatör:",
                            options=[">", ">="],
                            index=1,
                            horizontal=True,
                            help="> : Eşikten büyük olanlar 1 olur<br>>= : Eşike eşit ve büyük olanlar 1 olur"
                        )
                        
                        # Mod seçimi
                        st.markdown("""
                        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; 
                                   margin-bottom: 1rem;'>
                            <p style='margin: 0 0 0.5rem 0; font-weight: bold; color: #2d3748;'>Eşikleme Modu</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        keep_below = st.radio(
                            "Mod:",
                            options=["Binary", "Mixed"],
                            index=0,
                            horizontal=True,
                            help="Binary: Eşik altı 0'a dönüşür<br>Mixed: Eşik altı aynı kalır"
                        )
                        
                        # Etki analizi
                        affected_count = sum(1 for v in all_values 
                                            if (threshold_operator == ">=" and v >= threshold - 1e-4) or 
                                               (threshold_operator == ">" and v > threshold + 1e-4))
                        conversion_rate = (affected_count / len(all_values)) * 100
                        
                        st.markdown(f"""
                        <div style='background: #e6fffa; padding: 1rem; border-radius: 8px; 
                                   border-left: 3px solid #38b2ac; margin-bottom: 1rem;'>
                            <p style='margin: 0; font-size: 0.9rem; color: #2d3748;'>Eşikleme Etkisi</p>
                            <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: bold; color: #38b2ac;'>
                                {affected_count} değer 1'e dönüşecek ({conversion_rate:.1f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Uygula butonu
                        if st.button("🚀 Eşikleme Uygula ve Yeni İterasyon Başlat", 
                                    type="primary", use_container_width=True):
                            with st.spinner("Yeni iterasyon hesaplanıyor..."):
                                # Eşikleme uygula
                                thresholded_matrix = threshold_matrix(
                                    current_data['membership_matrix'], 
                                    U, 
                                    threshold, 
                                    keep_below == "Mixed",
                                    threshold_operator
                                )
                                
                                # Eşiklenmiş matrisi soft set formatına dönüştür
                                new_E_named = {}
                                for e_key in thresholded_matrix.keys():
                                    new_E_named[e_key] = set()
                                    for u, val in thresholded_matrix[e_key].items():
                                        if val == 1 or (keep_below == "Mixed" and val > 0):
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
                                    'threshold_operator': threshold_operator,
                                    'keep_below': keep_below == "Mixed",
                                    'thresholded_matrix': thresholded_matrix
                                })
                                
                                st.success(f"✅ İterasyon {current_iter + 1} başarıyla oluşturuldu!")
                                st.rerun()
                    
                    # İterasyon Geçmişi
                    if len(st.session_state.iterations) > 1:
                        st.markdown("""
                        <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 2rem;'>
                            <h3 style='margin: 0 0 1rem 0; color: #2d3748;'>📜 İterasyon Geçmişi</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Geçmiş tablosu
                        history_data = []
                        for i, iter_data in enumerate(st.session_state.iterations):
                            if iter_data.get('threshold') is not None:
                                history_data.append({
                                    "İterasyon": iter_data['iteration'],
                                    "Eşik": f"{iter_data['threshold']:.4f}",
                                    "Operatör": iter_data.get('threshold_operator', '-'),
                                    "Mod": "Mixed" if iter_data.get('keep_below') else "Binary",
                                    "Durum": "✅ Tamamlandı"
                                })
                        
                        if history_data:
                            history_df = pd.DataFrame(history_data)
                            st.dataframe(history_df, use_container_width=True, hide_index=True)
                        
                        # Detaylı geçmiş
                        st.markdown("##### 📋 Detaylı İterasyonlar")
                        
                        for idx, iter_data in enumerate(st.session_state.iterations):
                            with st.expander(f"🔄 İterasyon {iter_data['iteration']} - Detaylar", 
                                           expanded=(idx == len(st.session_state.iterations) - 1)):
                                
                                # Eşik bilgisi
                                if iter_data.get('threshold') is not None:
                                    st.markdown(f"""
                                    <div style='background: #f0f4f8; padding: 1rem; border-radius: 8px; 
                                               margin-bottom: 1rem;'>
                                        <p style='margin: 0; font-weight: bold; color: #2d3748;'>
                                            🎯 Eşik: {iter_data['threshold']:.4f} | 
                                            Operatör: {iter_data.get('threshold_operator', '-')} | 
                                            Mod: {'Mixed' if iter_data.get('keep_below') else 'Binary'}
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div style='background: #f0f4f8; padding: 1rem; border-radius: 8px; 
                                               margin-bottom: 1rem;'>
                                        <p style='margin: 0; font-weight: bold; color: #2d3748;'>
                                            📍 Başlangıç iterasyonu (orijinal üyelik matrisi)
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # İstatistikler
                                iter_values = []
                                for row in iter_data['membership_matrix'].values():
                                    iter_values.extend([float(v) for v in row.values()])
                                
                                iter_fractional = [v for v in iter_values if 0 < v < 1]
                                iter_zeros = sum(1 for v in iter_values if v == 0.0)
                                iter_ones = sum(1 for v in iter_values if v == 1.0)
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Toplam", len(iter_values))
                                with col2:
                                    st.metric("Sıfır", iter_zeros)
                                with col3:
                                    st.metric("Bir", iter_ones)
                                with col4:
                                    st.metric("Ondalıklı", len(iter_fractional))
                                
                                # Matris göster
                                st.markdown("**Üyelik Matrisi:**")
                                iter_matrix_df = matrix_to_dataframe(iter_data['membership_matrix'], U, E_info)
                                st.dataframe(iter_matrix_df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.exception(e)
            return
    else:
        # Dosya yüklenmemişse
        st.info("👆 Lütfen sol panelden bir CSV veya Excel dosyası yükleyin.")


if __name__ == "__main__":
    main()
