import streamlit as st
import openai

# Configura OpenAI/OpenRouter
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="ECOAI", layout="centered")

st.title("🌱 ECOAI")
st.subheader("Un LLM per risparmiare energia e risorse!")

# Inizializza la cronologia nella sessione
if "history" not in st.session_state:
    st.session_state.history = []

# Input dell'utente
input_text = st.text_input("Inserisci un prompt:", placeholder="Scrivi qui la tua domanda...")

# Scelta tipo di risposta
col1, col2, col3 = st.columns(3)
with col1:
    standard = st.button("RISPOSTA STANDARD")
with col2:
    completo = st.button("RISPOSTA RIASSUNTIVA")
with col3:
    bullet = st.button("RISPOSTA BULLET")

# Funzione per generare prompt
def genera_prompt(testo, tipo):
    if tipo == "completo":
        return (
            "Rispondi in modo chiaro e completo, ma con il minor numero possibile di parole, "
            "senza tralasciare informazioni importanti: " + testo
        )
    elif tipo == "bullet":
        return "Rispondi in modo brevissimo, poche parole, no frasi lunghe: " + testo
    return testo

# Gestione invio prompt
tipo_prompt = None
if input_text:
    if standard:
        tipo_prompt = "standard"
    elif completo:
        tipo_prompt = "completo"
    elif bullet:
        tipo_prompt = "bullet"

    if tipo_prompt:
        try:
            prompt_completo = genera_prompt(input_text, tipo_prompt)
            risposta = openai.ChatCompletion.create(
                model="mistralai/mistral-7b-instruct",
                messages=[{"role": "user", "content": prompt_completo}]
            ).choices[0].message.content

            # Aggiunge alla cronologia
            st.session_state.history.append({
                "domanda": input_text,
                "risposta": risposta,
                "tipo": tipo_prompt
            })

            st.markdown("### ✅ Risposta:")
            st.markdown(f"**Tipo:** {tipo_prompt.capitalize()}")
            st.markdown(risposta)

        except Exception as e:
            st.error(f"Errore durante la richiesta a OpenRouter: {e}")

# Visualizza cronologia
if st.session_state.history:
    st.markdown("---")
    st.markdown("## 🕘 Cronologia")
    if st.button("🗑️ Cancella Cronologia"):
        st.session_state.history = []

    for item in reversed(st.session_state.history):
        colore = {
            "standard": "lightblue",
            "completo": "lightgreen",
            "bullet": "khaki"
        }.get(item["tipo"], "lightgray")

        st.markdown(
            f"""
            <div style="background-color:{colore};padding:10px;border-radius:8px;margin-bottom:10px">
                <strong>Domanda:</strong> {item["domanda"]}<br>
                <strong>Risposta:</strong> {item["risposta"]}
            </div>
            """, unsafe_allow_html=True
        )
