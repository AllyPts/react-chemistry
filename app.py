import streamlit as st
import re
import matplotlib.pyplot as plt
from io import BytesIO

class ReactChemistry:
    def __init__(self):
        self.setup_session()
        self.setup_page()

    def setup_session(self):
        if 'historico' not in st.session_state:
            st.session_state.historico = []

    def setup_page(self):
        st.set_page_config(page_title="React Chemistry", page_icon="🧪", layout="wide")
        st.markdown("""
            <style>
            .stTextArea textarea { 
                font-family: 'Courier New', monospace; 
                font-size: 18px !important; 
                color: #ffffff !important; 
                background-color: #1e1e1e !important; 
            }
            .history-box { 
                padding: 20px; 
                border-radius: 10px; 
                border: 1px solid #333; 
                margin-bottom: 20px; 
                background-color: #0e1117;
            }
            </style>
        """, unsafe_allow_html=True)

    def chemical_engine(self, text):
        if not text: return ""

        # 1. PROTEÇÃO E ESPAÇAMENTO DO SINAL DE ADIÇÃO
        text = text.replace(" + ", " {PLUS_TAG} ")

        # 2. DICIONÁRIO DE SÍMBOLOS COMPLETO (CONFORME SOLICITADO)
        subs = {
            # Setas e Processos
            "luz": r"\xrightarrow{\text{luz}}",
            "pirolise": r"\xrightarrow{\Delta}",
            "eletrolise": r"\xrightarrow{e^{-}}",
            "combustao": r"\xrightarrow{+O_{2}}",
            "<=>": r"\leftrightarrow", 
            "<->": r"\rightleftharpoons", 
            "->": r"\rightarrow",
            "longa": r"\longrightarrow",
            "inversa": r"\longleftarrow",
            "==>": r"\Longrightarrow",
            # Energia, Cargas e Radiação
            "deltaH<0": r"\Delta H < 0",
            "deltaH>0": r"\Delta H > 0",
            "deltaH": r"\Delta H",
            "E0": r"E^{\circ}",
            "delta+": r"\delta^{+}",
            "delta-": r"\delta^{-}",
            "e-": r"e^{-}",
            "hv": r"h\nu",
            "lambda": r"\lambda",
            "delta": r"\Delta",
            # Sinais
            "!=": r"\neq",
            "gas!!": r"\uparrow\uparrow",
            "gas": r"\uparrow",
            "sol": r"\downarrow"
        }
        
        # Substituição por ordem de tamanho para evitar conflitos
        for key in sorted(subs.keys(), key=len, reverse=True):
            text = text.replace(key, subs[key])

        # 3. FORÇAR ESPAÇAMENTO NAS SETAS (Usando micro-espaços LaTeX \,)
        text = text.replace(r"\rightarrow", r" \, \rightarrow \, ")
        text = text.replace(r"\leftrightarrow", r" \, \leftrightarrow \, ")
        text = text.replace(r"\rightleftharpoons", r" \, \rightleftharpoons \, ")

        # 4. ESTADOS FÍSICOS E CONCENTRAÇÃO
        for est in ["(s)", "(l)", "(g)", "(aq)", "dil.", "conc."]:
            text = text.replace(est, f" \, _{{{est}}}")
        
        # 5. COEFICIENTES E ÍNDICES
        text = re.sub(r'(^|\s|\+)(\d+)([A-Z][a-z]?)', r'\1 \2 \3', text)
        text = re.sub(r'([a-zA-Z\)])(\d+)', r'\1_{\2}', text)
        
        # 6. CARGAS IÔNICAS
        text = re.sub(r'(?<!\{)(\d?[\+\-])(?!\d)', r'^{\1}', text)

        # 7. CONDIÇÃO CUSTOMIZADA NA SETA [texto]->
        match_seta = re.search(r'\[(.*?)\]\s*\\,\s*\\rightarrow', text)
        if match_seta:
            cond = match_seta.group(1)
            text = text.replace(f"[{cond}] \, \\rightarrow \, ", f" \, \\xrightarrow{{{cond}}} \, ")

        # 8. RESTAURA O SINAL DE MAIS COM ESPAÇO
        text = text.replace("{PLUS_TAG}", r" \, + \, ")
        
        return text

    def generate_image(self, latex_lines, color):
        try:
            fig, ax = plt.subplots(figsize=(12, max(1.5, len(latex_lines) * 1.3)))
            fig.patch.set_alpha(0)
            ax.axis('off')
            
            clean_lines = []
            for l in latex_lines:
                # Adaptação para o Matplotlib (overset)
                c = l.replace(r'\xrightarrow', r'\overset').replace(r'\huge', '').replace(r'\large', '')
                clean_lines.append(f"${c}$")
            
            full_content = "\n".join(clean_lines)
            ax.text(0.5, 0.5, full_content, size=28, color=color, 
                    ha='center', va='center', transform=ax.transAxes)
            
            buf = BytesIO()
            plt.savefig(buf, format="png", bbox_inches='tight', transparent=True, dpi=300)
            plt.close(fig)
            return buf
        except:
            if 'fig' in locals(): plt.close(fig)
            return None

    def run(self):
        with st.sidebar:
            st.title("🎨 Customização")
            escolha_cor = st.color_picker("Cor da Fonte (Download)", "#FFFFFF")
            st.divider()
            st.subheader("📚 Dicionário de Atalhos")
            with st.expander("➡️ Setas e Processos", expanded=True):
                st.code("luz : luz na seta\npirolise : Δ na seta\neletrolise : e- na seta\ncombustao : +O2 na seta\n-> : Seta comum\n<-> : Equilíbrio\n<=> : Reversível\n[cat]-> : Cat. na seta")
            with st.expander("⚡ Energia e Cargas"):
                st.code("deltaH : ΔH\nE0 : Potencial E°\ndelta+ / - : Cargas Parciais\ne- : Elétron\nhv : hν\nlambda : λ")
            with st.expander("🧪 Estados e Sinais"):
                st.code("(s) (l) (g) (aq)\ndil. / conc.\ngas / gas!! : ↑ / ↑↑\nsol : ↓\n!= : ≠\n[ ] : Concentração")

        st.title("React Chemistry")
        
        col_in, col_out = st.columns([1, 1], gap="large")

        with col_in:
            st.subheader("Editor Científico")
            input_text = st.text_area("Entrada:", value="2H2 + O2 -> 2H2O", height=250)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Registrar"):
                    if input_text and input_text not in st.session_state.historico:
                        st.session_state.historico.append(input_text)
            with c2:
                if st.button("🗑️ Limpar"):
                    st.session_state.historico = []
                    st.rerun()

        with col_out:
            st.subheader("Preview Profissional")
            if input_text:
                linhas = input_text.split('\n')
                preview_latex = [self.chemical_engine(l) for l in linhas if l.strip()]
                for pl in preview_latex:
                    st.latex(rf"\huge {pl}")
                
                st.divider()
                img_data = self.generate_image(preview_latex, escolha_cor)
                if img_data:
                    st.download_button(
                        label="📥 Baixar PNG (300 DPI)",
                        data=img_data,
                        file_name="quimica_react_chemistry.png",
                        mime="image/png"
                    )
            else:
                st.info("Aguardando entrada...")

        if st.session_state.historico:
            st.divider()
            st.subheader("📜 Resultados Anteriores")
            for item in reversed(st.session_state.historico):
                st.markdown(f'<div class="history-box">', unsafe_allow_html=True)
                st.latex(rf"\large {self.chemical_engine(item)}")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    ReactChemistry().run()