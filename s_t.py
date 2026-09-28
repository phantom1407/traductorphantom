import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# ---------------------------------------------------------
# ESTILOS CSS PARA EL TEMA LILA / MORADO
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal de la aplicación */
    .stApp {
        background-color: #F5EEF8; /* Lila muy claro */
    }
    
    /* Color del texto para títulos y subtítulos */
    h1, h2, h3 {
        color: #6C3483 !important; /* Morado oscuro */
    }
    
    /* Color de los textos normales */
    p, span, label {
        color: #5B2C6F !important;
    }
    
    /* Estilizar los botones nativos de Streamlit */
    div.stButton > button:first-child {
        background-color: #AF7AC5; /* Lila vibrante */
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #8E44AD; /* Morado más intenso al pasar el mouse */
        color: white !important;
    }

    /* Estilizar el botón de Bokeh (el de escuchar) */
    .bk-btn {
        background-color: #AF7AC5 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    .bk-btn:hover {
        background-color: #8E44AD !important;
    }
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------


st.title("💜 Traductor Mágico")
st.subheader("Dime lo que quieres traducir...")

try:
    image = Image.open('OIG7.jpg')
    st.image(image, width=300)
except FileNotFoundError:
    st.warning("No se encontró la imagen 'OIG7.jpg'. Asegúrate de tenerla en la misma carpeta.")

with st.sidebar:
    st.subheader("✨ Opciones del Traductor")
    st.write("Presiona el botón principal. Cuando escuches la señal, "
             "habla con claridad lo que deseas traducir. Luego selecciona "   
             "los idiomas de entrada y salida.")

st.write("Toca el botón abajo y empieza a hablar 🎙️")

# Botón de Bokeh para el reconocimiento de voz
stt_button = Button(label="🎙️ Escuchar Voz", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;  
    recognition.interimResults = true;
    recognition.lang = 'es-ES';  // Lenguaje base del navegador
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    
    recognition.onend = function() {
        console.log("Reconocimiento detenido");
    }
    
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.info(f"Escuché: **{result.get('GET_TEXT')}**")
        
    try:
        os.mkdir("temp")
    except FileExistsError:
        pass
        
    st.title("🎧 Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    
    # Columnas para organizar mejor la selección de idiomas
    col1, col2 = st.columns(2)
    
    with col1:
        in_lang = st.selectbox(
            "Idioma de Entrada",
            ("Español", "Inglés", "Bengali", "Coreano", "Mandarín", "Japonés"),
        )
        
    with col2:
        out_lang = st.selectbox(
            "Idioma de Salida",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
        )
        
    # Diccionario de idiomas para limpiar los if/elif
    lang_dict = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    
    input_language = lang_dict[in_lang]
    output_language = lang_dict[out_lang]
    
    english_accent = st.selectbox(
        "Acento (Para inglés/español)",
        (
            "Defecto",
            "Español (México)",
            "Reino Unido",
            "Estados Unidos",
            "Canadá",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )
    
    # Asignar tld según el acento
    if english_accent == "Defecto": tld = "com"
    elif english_accent == "Español (México)": tld = "com.mx"
    elif english_accent == "Reino Unido": tld = "co.uk"
    elif english_accent == "Estados Unidos": tld = "com"
    elif english_accent == "Canadá": tld = "ca"
    elif english_accent == "Australia": tld = "com.au"
    elif english_accent == "Irlanda": tld = "ie"
    elif english_accent == "Sudáfrica": tld = "co.za"
    
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20].replace(" ", "_")
        except:
            my_file_name = "audio_traducido"
            
        filepath = f"temp/{my_file_name}.mp3"
        tts.save(filepath)
        return my_file_name, trans_text
    
    display_output_text = st.checkbox("Mostrar texto traducido escrito")
    
    if st.button("🪄 Traducir y Convertir"):
        with st.spinner('Traduciendo con magia...'):
            result_file, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result_file}.mp3", "rb")
            audio_bytes = audio_file.read()
            
            st.markdown(f"### 🎵 Tu audio listo:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
            if display_output_text:
                st.markdown(f"### 📝 Texto traducido:")
                st.success(f"{output_text}")
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(7)
