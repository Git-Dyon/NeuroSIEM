import streamlit as st
import pandas as pd
import json
import subprocess
import time
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="NeuroSIEM - Centro de Comando",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILO CSS (Tema Escuro/Hacker) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #4B4B4B;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3 { color: #00FFAA !important; }
    [data-testid="stMetricValue"] { color: #FAFAFA !important; }
    [data-testid="stMetricLabel"] { color: #CCCCCC !important; }
    
    /* Estilo do botão de download para destaque */
    .stDownloadButton button {
        background-color: #262730;
        color: #00FFAA;
        border: 1px solid #00FFAA;
        font-weight: bold;
    }
    .stDownloadButton button:hover {
        background-color: #00FFAA;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CLASSE DE RELATÓRIO PDF ---
class PDFReport(FPDF):
    def header(self):
        # Título do Documento
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'NeuroSIEM - Relatorio de Incidente', 0, 1, 'C')
        self.ln(5)
        # Linha separadora
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()} - Gerado por NeuroSIEM AI', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'  {title}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Tratamento simples para caracteres especiais (latin-1)
        safe_body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, safe_body)
        self.ln()

def generate_pdf(incident_data):
    pdf = PDFReport()
    pdf.add_page()
    
    # Cabeçalho do Evento
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, f"Data do Relatorio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(5)
    
    # 1. Detalhes do Incidente
    pdf.chapter_title(f"Evento: {incident_data.get('tipo_ataque', 'N/A')}")
    
    # Cor vermelha se for risco alto
    if incident_data.get('risco') == 'Alto':
        pdf.set_text_color(220, 50, 50)
    pdf.chapter_body(f"Nivel de Risco Identificado: {incident_data.get('risco', 'N/A').upper()}")
    pdf.set_text_color(0, 0, 0) # Volta para preto
    
    # 2. Análise da IA
    pdf.chapter_title("Analise da Inteligencia Artificial")
    pdf.chapter_body(incident_data.get('explicacao_curta', 'Sem analise disponivel.'))
    
    # 3. Mitigação
    pdf.chapter_title("Recomendacao de Mitigacao")
    pdf.chapter_body(incident_data.get('mitigacao', 'Verificar logs manuais.'))
    
    # 4. Evidência Técnica (JSON)
    pdf.chapter_title("Evidencia Tecnica (JSON Bruto)")
    pdf.set_font('Courier', '', 9)
    json_str = json.dumps(incident_data, indent=2, ensure_ascii=False)
    pdf.multi_cell(0, 5, json_str.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. FUNÇÃO: PESCAR LOGS DO CONTAINER ---
def get_logs_from_docker():
    container_names = ["single-node-wazuh.manager-1", "wazuh.manager"]
    for container in container_names:
        cmd = f"docker exec {container} cat /var/ossec/logs/integrations.log"
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8')
        except subprocess.CalledProcessError:
            continue
    return ""

# --- 5. FUNÇÃO: TRADUZIR LOGS PARA DADOS ---
def parse_logs(raw_data):
    logs = []
    lines = raw_data.split('\n')
    buffer = ""
    is_json = False
    
    for line in lines:
        if line.strip() == "{":
            is_json = True
            buffer = "{"
        elif line.strip() == "}" and is_json:
            buffer += "}"
            is_json = False
            try:
                log_obj = json.loads(buffer)
                log_obj['timestamp'] = datetime.now().strftime("%H:%M")
                logs.append(log_obj)
            except:
                pass
        elif is_json:
            buffer += line
            
    return logs[::-1]

# --- 6. INTERFACE DO DASHBOARD ---
st.title("🛡️ NeuroSIEM: Centro de Comando")
st.caption("Monitoramento de Ameaças em Tempo Real com Inteligência Artificial")

with st.sidebar:
    st.header("Status do Sistema")
    st.success("✅ Wazuh Manager: ONLINE")
    st.success("✅ Ollama AI (Local): CONECTADO")
    st.info("Painel atualiza a cada 5s.")
    if st.button("🔄 Forçar Atualização"):
        st.rerun()

raw_logs = get_logs_from_docker()
data = parse_logs(raw_logs)

if not data:
    st.warning("⏳ Aguardando detecção de ameaças...")
else:
    # Métricas
    col1, col2, col3 = st.columns(3)
    high_risk = len([x for x in data if x.get('risco') == 'Alto'])
    medium_risk = len([x for x in data if x.get('risco') == 'Médio'])
    
    with col1: st.metric("Total Analisado", len(data))
    with col2: st.metric("Risco CRÍTICO", high_risk, delta_color="inverse")
    with col3: st.metric("Risco Médio", medium_risk)

    st.divider()
    st.subheader("📡 Feed de Inteligência")
    
    for i, item in enumerate(data):
        icon = "🔴" if item.get('risco') == 'Alto' else "🟠" if item.get('risco') == 'Médio' else "🟢"
        
        with st.expander(f"{icon} [{item.get('risco')}] {item.get('tipo_ataque')} - {item.get('timestamp')}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("### 🤖 Análise")
                st.write(item.get('explicacao_curta'))
                st.markdown("### 🛡️ Ação Recomendada")
                st.info(item.get('mitigacao'))
            with c2:
                st.write("### 📄 Documentação")
                
                # --- BOTÃO DE PDF ---
                pdf_bytes = generate_pdf(item)
                st.download_button(
                    label="📥 Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name=f"Relatorio_Incidente_{i}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_{i}"
                )
                
                with st.expander("Ver JSON Técnico"):
                    st.json(item)

time.sleep(5)
st.rerun()
