import streamlit as st
import google.generativeai as genai
import urllib.parse
import os
import base64

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop()

# Modello Gemini 2.5 Flash
model = genai.GenerativeModel('gemini-2.5-flash')

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Area Manager AI", page_icon="👞", layout="wide")

# Funzione per resettare i campi
def reset_fields():
    st.session_state.distributore = ""
    st.session_state.bozza = ""
    st.session_state.obiettivo = "Follow up"

# Inizializzazione session state per il reset
if 'distributore' not in st.session_state: st.session_state.distributore = ""
if 'bozza' not in st.session_state: st.session_state.bozza = ""

# CSS: Sfondo neutro, bottoni moderni e casella info AZZURRA
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-image: linear-gradient(to right, #0078d4, #00bcf2);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.01);
        box-shadow: 0 4px 15px rgba(0,0,128,0.2);
    }
    .hint-box {
        background-color: #e1f5fe; 
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0078d4;
        margin-bottom: 20px;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #01579b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2950/2950057.png", width=70)
    st.title("Strategia Mail")
    
    profilo = st.selectbox("👤 Profilo Partner", [
        "Partner Storico", "Nuovo Lead", "Recupero Rapporto", "Agente", "Collega"
    ])
    allocuzione = st.radio("🗣️ Allocuzione", ["Tu", "Lei"], horizontal=True)
    tipo_destinatario = st.radio("🏢 Tipo Destinatario", ["Distributore", "Utilizzatore"], index=0, horizontal=True)
    tono_scelto = st.select_slider("🎭 Tono", options=["Amichevole", "Cordiale", "Professionale"], value="Cordiale")
    lunghezza = st.select_slider("📏 Lunghezza", options=["Corta", "Standard", "Lunga"], value="Standard")
    
    st.divider()
    # TASTO RESET
    if st.button("🗑️ SVUOTA CAMPI"):
        reset_fields()
        st.rerun()
    st.caption("Assistant Area Manager v2.6")

# --- AREA PRINCIPALE ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

img_b64 = get_image_base64("michelone.jpg")

if img_b64:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <h1 style="margin: 0; padding: 0;">👞 Generatore Mail AI</h1>
            <img src="data:image/jpeg;base64,{img_b64}" style="width: 70px; height: auto; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='margin-bottom: 20px;'>👞 Generatore Mail AI</h1>", unsafe_allow_html=True)

st.markdown('<div class="hint-box">👈 <b>Usa la barra laterale a sinistra!</b></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    distributore = st.text_input("📍 Nome Contatto / Azienda", key="distributore", placeholder="Es. Rossi Calzature")
    obiettivo = st.selectbox("🎯 Obiettivo", [
        "Follow up", "Richiesta appuntamento", "Ringraziare e presentare offerta", 
        "Comunicazione generica", "Svuotare Magazzino", "Inserimento Nuovo Articolo", 
        "Aumento Sell-out", "Fissare Formazione"
    ], key="obiettivo")

with col2:
    bozza = st.text_area("📝 Appunti veloci", key="bozza", placeholder="Scrivi qui i dettagli...", height=250)

def create_outlook_link(subject, body):
    clean_body = body.replace("#", "").replace("*", "") 
    query = urllib.parse.quote(clean_body)
    subject_query = urllib.parse.quote(subject)
    return f"mailto:?subject={subject_query}&body={query}"

st.write("") 

if st.button("🚀 GENERA VERSIONI STRATEGICHE"):
    if distributore and bozza:
        with st.spinner('Pulisco i testi e separo le varianti...'):
            prompt = f"""
            Sei un Area Manager esperto di calzature antinfortunistiche e guanti da lavoro. 
            Scrivi DUE varianti di email diverse per il contatto: {distributore}.
            
            REGOLE TASSATIVE:
            1. Destinatario: Un {tipo_destinatario.upper()}.
            2. Allocuzione: Dai del {allocuzione.upper()}.
            3. Tono: {tono_scelto}.
            4. Lunghezza: {lunghezza.upper()}.
            5. Profilo relazione: {profilo}. 
            6. Obiettivo: {obiettivo}.
            7. Note: {bozza}.
            8. FIRMA: NESSUNA firma o segnaposto tipo [Il Tuo Nome].
            9. OGGETTO: NON scrivere l'oggetto nel testo della mail.
            10. TITOLI: NON scrivere MAI "VERSIONE 1", "Variante", "Taglio professionale" o altre intestazioni. Inizia subito con il saluto.
            
            IMPORTANTE: Separa le due mail SOLO con la stringa: SEPARA_QUI
            """
            try:
                response = model.generate_content(prompt).text
                if "SEPARA_QUI" in response:
                    v1, v2 = response.split("SEPARA_QUI")
                else:
                    v1, v2 = response, ""

                st.divider()
                res_col1, res_col2 = st.columns(2)
                mail_subject = f"{obiettivo} - {distributore}"

                with res_col1:
                    st.info("📌 **Variante Professionale**")
                    st.write(v1.strip())
                    st.markdown(f'[📧 Apri in Outlook Classico]({create_outlook_link(mail_subject, v1.strip())})')
                
                with res_col2:
                    st.success("🤝 **Variante Relazionale**")
                    st.write(v2.strip())
                    st.markdown(f'[📧 Apri in Outlook Classico]({create_outlook_link(mail_subject, v2.strip())})')
            except Exception as e:
                st.error(f"Errore: {e}")
    else:
        st.warning("Compila il nome e gli appunti per procedere!")
