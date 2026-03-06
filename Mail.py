import streamlit as st
import google.generativeai as genai
import urllib.parse
import os
import base64
from PIL import Image
import PyPDF2
from st_img_pastebutton import paste  # <-- LIBRERIA MAGICA PER INCOLLARE
import io

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
st.set_page_config(page_title="Key Account Manager AI", page_icon="🛠️", layout="wide")

# Funzione per resettare i campi
def reset_fields():
    st.session_state.distributore = ""
    st.session_state.bozza = ""
    st.session_state.obiettivo = "Follow up ordine / stato consegna"

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
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942784.png", width=70)
    st.title("Strategia Mail KAM")
    
    profilo = st.selectbox("👤 Profilo Interlocutore", [
        "Ufficio Acquisti", "Responsabile Tecnico", "Key Account Storico", "Nuovo Cliente Direzionale", "Amministrazione"
    ])
    allocuzione = st.radio("🗣️ Allocuzione", ["Tu", "Lei"], horizontal=True, index=1)
    tipo_destinatario = st.radio("🏢 Tipo Destinatario", ["Azienda Cliente", "Partner Fornitore"], index=0, horizontal=True)
    tono_scelto = st.select_slider("🎭 Tono", options=["Risolutivo/Informale", "Cordiale", "Istituzionale/Professionale"], value="Cordiale")
    lunghezza = st.select_slider("📏 Lunghezza", options=["Sintetica", "Standard", "Articolata"], value="Standard")
    
    st.divider()
    if st.button("🗑️ SVUOTA CAMPI"):
        reset_fields()
        st.rerun()
    st.caption("KAM Assistant v6.0 - Utensiltecnica")

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
            <h1 style="margin: 0; padding: 0;">🛠️ Generatore Mail KAM</h1>
            <img src="data:image/jpeg;base64,{img_b64}" style="width: 70px; height: auto; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='margin-bottom: 20px;'>🛠️ Generatore Mail KAM</h1>", unsafe_allow_html=True)

st.markdown('<div class="hint-box">👈 <b>Imposta il tono a sinistra, carica appunti o immagini a destra!</b></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    distributore = st.text_input("📍 Nome Key Account / Azienda", key="distributore", placeholder="Es. Industrie Meccaniche SpA")
    obiettivo = st.selectbox("🎯 Obiettivo della Mail", [
        "Risposta a email/messaggio",
        "Follow up ordine / stato consegna", 
        "Invio preventivo / offerta dedicata", 
        "Aggiornamento listino prezzi", 
        "Risoluzione anomalia / problema di fornitura", 
        "Gestione reso o sostituzione", 
        "Pianificazione ordini continuativi (contratti quadro)", 
        "Presentazione nuovo catalogo/utensili", 
        "Sollecito amministrativo / verifica pagamenti"
    ], key="obiettivo")

with col2:
    bozza = st.text_area("📝 Appunti veloci (dati tecnici, nr. ordine, ecc.)", key="bozza", placeholder="Scrivi qui i dettagli dell'ordine, l'articolo o il problema da risolvere...", height=130)
    
    st.markdown("<br><b>📎 Allegati (Opzionale)</b>", unsafe_allow_html=True)
    
    # 1. IL NUOVO BOTTONE MAGICO PER GLI SCREENSHOT
    st.caption("Hai fatto uno screenshot (Stamp / Win+Shift+S)? Clicca qui sotto:")
    pasted_image_data = paste(label="📋 INCOLLA DA APPUNTI", key="image_clipboard")
    
    # 2. CARICAMENTO NORMALE PER PDF o FILE SALVATI
    st.caption("Oppure carica un file già salvato sul PC (Immagine o PDF):")
    uploaded_file = st.file_uploader("Trascina qui o sfoglia", type=['png', 'jpg', 'jpeg', 'pdf'], label_visibility="collapsed")

    # Gestione dell'immagine incollata dal bottone magico
    pasted_image = None
    if pasted_image_data is not None:
        header, encoded = pasted_image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        pasted_image = Image.open(io.BytesIO(binary_data))
        st.success("✅ Screenshot catturato con successo!")
        st.image(pasted_image, width=150)

def create_outlook_link(subject, body):
    clean_body = body.replace("#", "").replace("*", "") 
    query = urllib.parse.quote(clean_body)
    subject_query = urllib.parse.quote(subject)
    return f"mailto:?subject={subject_query}&body={query}"

st.write("") 

if st.button("🚀 GENERA VERSIONI STRATEGICHE"):
    if distributore and (bozza or uploaded_file is not None or pasted_image is not None):
        with st.spinner('Elaboro i dati tecnici e redigo le varianti...'):
            prompt = f"""
            Sei il Responsabile Contatti con i Key Account della 'Cipriani Utensiltecnica' (situata a Pomezia, RM). 
            Lavori dall'ufficio (back-office) e gestisci le relazioni commerciali, operative e tecniche con i grandi clienti nel settore dell'utensileria. 
            Scrivi DUE varianti di email diverse per il contatto/azienda: {distributore}.
            
            REGOLE TASSATIVE:
            1. Destinatario: Un {tipo_destinatario.upper()}.
            2. Allocuzione: Dai del {allocuzione.upper()}.
            3. Tono: {tono_scelto}.
            4. Lunghezza: {lunghezza.upper()}.
            5. Profilo interlocutore: {profilo}. 
            6. Obiettivo della mail: {obiettivo}.
            7. Note e dettagli da inserire: {bozza}.
            8. FIRMA: NESSUNA firma o segnaposto tipo [Il Tuo Nome] o [Tuo Ruolo]. Chiudi solo con i saluti adeguati.
            9. OGGETTO: NON scrivere l'oggetto nel testo della mail.
            10. TITOLI: NON scrivere MAI "VERSIONE 1", "Variante", "Taglio professionale" o altre intestazioni. Inizia subito con il saluto al cliente.
            """
            
            contents = []
            
            # 1. Se hai incollato uno screenshot con il bottone magico:
            if pasted_image is not None:
                prompt += "\n\n11. SCREENSHOT ALLEGATO: Ti ho fornito un'immagine con un messaggio scritto o un dettaglio tecnico. La tua email DEVE ESSERE UNA RISPOSTA DIRETTA e pertinente a quanto mostrato nello screenshot, integrando le mie note se presenti."
                contents = [prompt, pasted_image]
                
            # 2. Se hai caricato un file/PDF tradizionale:
            elif uploaded_file is not None:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                if file_extension == 'pdf':
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    testo_pdf = ""
                    for page in pdf_reader.pages:
                        testo_pdf += page.extract_text() + "\n"
                    prompt += f"\n\n11. DOCUMENTO ALLEGATO: Ti ho fornito un PDF di cui ho estratto il testo qui sotto. Leggilo attentamente e formula un'email di risposta o gestione pertinente, integrando le mie note se presenti.\n[TESTO PDF]:\n{testo_pdf}"
                    contents = [prompt]
                else:
                    img = Image.open(uploaded_file)
                    prompt += "\n\n11. SCREENSHOT ALLEGATO: Ti ho fornito un'immagine con un messaggio scritto o un dettaglio tecnico. La tua email DEVE ESSERE UNA RISPOSTA DIRETTA e pertinente a quanto mostrato nello screenshot, integrando le mie note se presenti."
                    contents = [prompt, img]
                    
            # 3. Solo testo:
            else:
                contents = [prompt]
            
            prompt += "\n\nIMPORTANTE: Separa le due mail SOLO con la stringa esatta: SEPARA_QUI"
            
            try:
                # Assicuriamoci che il prompt sia aggiornato nei contents
                contents[0] = prompt
                
                response = model.generate_content(contents).text
                
                if "SEPARA_QUI" in response:
                    v1, v2 = response.split("SEPARA_QUI")
                else:
                    v1, v2 = response, ""

                st.divider()
                res_col1, res_col2 = st.columns(2)
                mail_subject = f"{obiettivo} - {distributore}"

                with res_col1:
                    st.info("📌 **Variante Diretta / Operativa**")
                    st.write(v1.strip())
                    st.markdown(f'[📧 Apri in Outlook Classico]({create_outlook_link(mail_subject, v1.strip())})')
                
                with res_col2:
                    st.success("🤝 **Variante Diplomatica / Commerciale**")
                    st.write(v2.strip())
                    st.markdown(f'[📧 Apri in Outlook Classico]({create_outlook_link(mail_subject, v2.strip())})')
            except Exception as e:
                st.error(f"Errore di connessione o generazione: {e}")
    else:
        st.warning("Compila il nome dell'Azienda e inserisci almeno una bozza di testo o un file allegato (Immagine/PDF)!")
