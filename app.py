import streamlit as st
import pandas as pd
import scraper
import io

# Page Config
st.set_page_config(
    page_title="Busca Candidato X-Ray | Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional UI/UX Design System
st.markdown("""
<style>
    /* Global Font */
    html, body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Primary Button - Custom Styling to match Pro Theme */
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }
    
    /* Result Cards */
    .candidate-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: all 0.2s;
        position: relative;
        overflow: hidden;
    }
    .candidate-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #BFDBFE;
        transform: translateY(-2px);
    }
    .candidate-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background-color: #2563EB;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E293B;
        text-decoration: none;
        margin-bottom: 0.5rem;
        display: block;
    }
    .card-title:hover {
        color: #2563EB;
    }
    .card-url {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 0.8rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-snippet {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.5;
    }
    
    /* Metrics/Info Box */
    .metric-box {
        background: #EFF6FF;
        border: 1px solid #DBEAFE;
        border-radius: 8px;
        padding: 1rem;
        color: #1E40AF;
        font-weight: 500;
        text-align: center;
    }
    
</style>
""", unsafe_allow_html=True)

# Main Header
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<div style='font-size: 4rem; text-align: center;'>🎯</div>", unsafe_allow_html=True)
with col_title:
    st.title("Busca Candidato X-Ray")
    st.markdown("##### Ferramenta avançada de sourcing para Recrutadores Tech")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔍 Configuração")
    
    search_mode = st.selectbox(
        "Modo de Busca",
        ["LinkedIn", "Portais de Emprego", "PDF/DOCX - Currículos", "Redes Sociais", "Listas de RH"],
        index=0,
        help="Define a estratégia de X-Ray Search."
    )
    source_website = search_mode

    st.markdown("### 👤 Perfil Ideal")
    role = st.text_input("Cargo", placeholder="Ex: Desenvolvedor Full Stack")
    location = st.text_input("Localidade", value="São José do Rio Preto")
    seniority = st.selectbox("Senioridade", ["Qualquer", "Junior", "Pleno", "Senior", "Especialista", "Manager"])
    skills = st.text_area("Skills Obrigatórias", placeholder="Ex: React, Node.js, AWS")

    st.markdown("### 🎛️ Preferências")
    num_results = st.slider("Resultados por busca", 10, 50, 15)

    with st.expander("🕵️ Filtros Avançados"):
        target_company = st.text_input("Empresa Alvo", placeholder="Ex: Nubank, Google")
        exclude_terms = st.text_input("⛔ Excluir Termos", placeholder="Ex: recruiter, consultoria")
        open_to_work = st.checkbox("Apenas 'Open to Work'")
        use_intitle = st.checkbox("Forçar cargo no Título")
        exact_match = st.checkbox("Busca Exata (Aspas em tudo)")

    st.markdown("---")
    search_btn = st.button("� Buscar Candidatos")

# Main Logic
if search_btn:
    if not role or not location:
        st.error("⚠️ Preencha **Cargo** e **Localidade** para iniciar.")
    else:
        # 1. Generate Query
        query = scraper.generate_search_query(
            role, location, seniority, skills,
            exact_match=exact_match, exclude_terms=exclude_terms,
            target_company=target_company, use_intitle=use_intitle,
            open_to_work=open_to_work, site=source_website
        )

        # 2. Results Header
        st.markdown(f"""
        <div style="background-color: #F1F5F9; padding: 1rem; border-radius: 8px; border-left: 4px solid #64748B; margin-bottom: 2rem;">
            <code style="color: #475569; font-family: monospace;">{query}</code>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Active Filters Display
        filters = []
        if active := exclude_terms: filters.append(f"⛔ -{active}")
        if active := target_company: filters.append(f"� {active}")
        if open_to_work: filters.append("🟢 OpenToWork")
        if use_intitle: filters.append("🎯 inTitle")
        
        if filters:
            st.caption("Filtros: " + "  •  ".join(filters))

        # 4. Search Execution
        with st.spinner("🤖 Varrendo a web em busca de talentos..."):
            try:
                data = scraper.scrape_smart(query, num_results=int(num_results), site=source_website, expected_location=location)
                
                if data:
                    count = len(data)
                    st.markdown(f"""
                    <div class="metric-box">
                        ✅ {count} candidatos encontrados
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 📋 Resultados")
                    
                    # Layout selection
                    tab_cards, tab_table = st.tabs(["📇 Visualização Cards", "📊 Tabela / Exportar"])
                    
                    with tab_cards:
                        for item in data:
                            title = item.get('Nome/Titulo', 'Sem Título')
                            link = item.get('Link Perfil', '#')
                            snippet = item.get('Resumo', 'Clique para ver o perfil completo.')
                            
                            st.markdown(f"""
                            <div class="candidate-card">
                                <a href="{link}" target="_blank" class="card-title">{title} ↗</a>
                                <div class="card-url">{link}</div>
                                <div class="card-snippet">{snippet}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    with tab_table:
                        df = pd.DataFrame(data)
                        st.dataframe(
                            df,
                            column_config={"Link Perfil": st.column_config.LinkColumn("URL")},
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        col1, col2 = st.columns(2)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        col1.download_button("📥 Baixar CSV", csv, "candidatos.csv", "text/csv")
                        
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        col2.download_button("📥 Baixar Excel", buffer.getvalue(), "candidatos.xlsx")

                else:
                    st.warning("⚠️ Nenhum resultado encontrado. Tente remover alguns filtros ou usar termos mais genéricos.")
                    st.markdown("💡 **Dica:** Desmarque 'Busca Exata' ou remova Skills obrigatórias.")

            except Exception as e:
                st.error(f"❌ Erro na busca: {e}")
else:
    # Empty State - Welcome Screen
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #64748B;">
        <h2>Pronto para encontrar o próximo talento?</h2>
        <p>Defina o perfil na barra lateral e dispare o X-Ray.</p>
        <div style="font-size: 5rem; opacity: 0.2;">🔍</div>
    </div>
    """, unsafe_allow_html=True)
