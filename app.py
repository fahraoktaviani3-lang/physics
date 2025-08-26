import streamlit as st
import google.generativeai as genai
import os

# --- KONFIGURASI APLIKASI STREAMLIT ---
st.set_page_config(
    page_title="Chatbot Ahli Fisika ⚛️",
    page_icon="⚛️"
)

# Judul utama aplikasi
st.title("⚛️ Chatbot Ahli Fisika")
st.caption("Aplikasi ini dibuat menggunakan Google Gemini 1.5 Flash.")

# --- PENGATURAN API KEY DAN MODEL (SEBAGAI SECRET) ---

# Mengambil API Key dari Streamlit Secrets.
# Pastikan Anda telah mengaturnya di Streamlit Cloud sebagai 'GEMINI_API_KEY'.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ API Key tidak ditemukan. Harap atur 'GEMINI_API_KEY' di Streamlit Secrets.")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# --- KONTEKS AWAL CHATBOT ---
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli fisika. Tuliskan rumus tentang Fisika. Jawaban singkat. Tolak pertanyaan non-fisika."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan rumus yang ingin Anda ketahui."]
    }
]

# --- INISIALISASI MODEL DAN SESI CHAT ---
# Cek apakah model sudah diinisialisasi di session state
if "model" not in st.session_state:
    genai.configure(api_key=API_KEY)
    st.session_state.model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

# Cek apakah riwayat chat sudah ada di session state
if "messages" not in st.session_state:
    # Inisialisasi riwayat chat dengan konteks awal
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

    # Inisialisasi sesi chat
    st.session_state.chat = st.session_state.model.start_chat(history=INITIAL_CHATBOT_CONTEXT)

# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["parts"][0])
    elif message["role"] == "model":
        st.chat_message("assistant").markdown(message["parts"][0])

# --- PROSES INPUT PENGGUNA ---
if prompt := st.chat_input("Tanyakan sesuatu tentang Fisika..."):
    # Tambahkan input pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    st.chat_message("user").markdown(prompt)

    # Kirim pesan ke model dan dapatkan respons
    try:
        with st.spinner("Sedang membalas..."):
            response = st.session_state.chat.send_message(prompt, request_options={"timeout": 60})

        # Tambahkan respons model ke riwayat chat
        if response and response.text:
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            st.chat_message("assistant").markdown(response.text)
        else:
            st.chat_message("assistant").markdown("Maaf, saya tidak bisa memberikan balasan.")

    except Exception as e:
        error_message = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}"
        st.error(error_message)
        st.info("Kemungkinan penyebab: Masalah koneksi internet, API Key tidak valid, atau melebihi kuota.")
