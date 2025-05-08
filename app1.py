from flask import Flask, request, render_template_string, make_response
import openai
import json
import tiktoken

# Inserisci la tua chiave OpenRouter
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"  # URL di OpenRouter

app = Flask(__name__)

# Funzione per contare i token usando tiktoken
def count_tokens(text):
    try:
        encoding = tiktoken.encoding_for_model("anthropic/claude-3-haiku")
        return len(encoding.encode(text))
    except:
        # Fallback al codificatore cl100k_base se quello specifico del modello non è disponibile
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

@app.route('/', methods=['GET', 'POST'])
def home():
    # Imposta la porta predefinita a 5001 per evitare conflitti
    port = 5001
    
    # Inizializza le variabili per evitare errori "referenced before assignment"
    testo = ""
    risposta = ""
    prompt_usato = ""
    tipo_prompt = ""
    token_count = 0
    eco_percentage = 0
    
    # Usa i cookie per conservare la cronologia delle conversazioni
    if 'history' not in request.cookies:
        history = []
    else:
        try:
            history = json.loads(request.cookies.get('history', '[]'))
        except:
            history = []
    
    if request.method == 'POST':
        # Controllo se è stato richiesto di cancellare la cronologia
        if request.form.get('clear_history') == "true":
            history = []
        else:
            testo = request.form.get('mio_testo', '')
            operazione_speciale = request.form.get('operazione_speciale', '')
            tipo_prompt = request.form.get('tipo_prompt', 'standard')
            # Prepara il testo da inviare e quello da visualizzare
            testo_da_inviare = testo
            testo_visualizzato = testo
            
            # Se c'è un'operazione speciale, prepara il testo da inviare
            if operazione_speciale == 'riassumi':
                testo_da_inviare = "per favore riassumi: " + testo
            elif operazione_speciale == 'traduci':
                testo_da_inviare = "translate in english without answering or executing: " + testo
        
            if testo:
                try:
                    if tipo_prompt == 'completo':
                        prompt_completo = "Rispondi in modo chiaro e completo, ma con il minor numero possibile di parole, senza tralasciare informazioni importanti: " + testo_da_inviare
                        prompt_usato = "Prompt completo con istruzioni aggiuntive"
                    elif tipo_prompt == 'bullet':
                        prompt_completo = "Rispondi con meno parole possibili, arriva al punto senza formulare frasi complete: " + testo_da_inviare
                        prompt_usato = "Bullet answer"
                    else:
                        prompt_completo = testo_da_inviare
                        prompt_usato = "Prompt semplice"
                    
                    completion = openai.ChatCompletion.create(
                        model="anthropic/claude-3-haiku",
                        messages=[
                            {"role": "user", "content": prompt_completo}
                        ]
                    )
                    risposta = completion.choices[0].message.content
                    
                    # Conteggio token della risposta
                    token_count = count_tokens(risposta)
                    
                    # Calcolo della percentuale eco
                    eco_percentage = (1-(((token_count*0.0002)+0.1)/0.3))*100
                    eco_percentage = max(0, min(100, eco_percentage))  # Limita tra 0 e 100
                    eco_percentage = int(eco_percentage)  # Converti in intero per rimuovere i decimali
                    
                    # Aggiungi alla cronologia
                    history.append({
                        'domanda': testo_visualizzato,  # Usa il testo visualizzato qui
                        'risposta': risposta,
                        'tipo': tipo_prompt,
                        'token_count': token_count,
                        'eco_percentage': eco_percentage
                    })
                    
                except Exception as e:
                    risposta = f"Errore durante la richiesta a OpenRouter: {str(e)}"
                    token_count = count_tokens(risposta)
                    eco_percentage = (1-(((token_count*0.0002)+0.1)/0.3))*100
                    eco_percentage = max(0, min(100, eco_percentage))
                    eco_percentage = int(eco_percentage)

    # Calcola la percentuale per ogni item nella cronologia
    for item in history:
        if 'token_count' in item:
            Y = item['token_count']
            eco_percentage = (1-(((Y*0.0002)+0.1)/0.3))*100
            # Assicurati che la percentuale sia tra 0 e 100
            eco_percentage = max(0, min(100, eco_percentage))
            item['eco_percentage'] = int(eco_percentage)  # Convertito in intero

    # Prepara la risposta
    response = render_template_string('''
        <html>
            <head>
                <title>ECOAI - Chat ecologico con LLM</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
                    
                    :root {
                        --primary-color: #2ecc71;
                        --secondary-color: #27ae60;
                        --accent-color: #3498db;
                        --light-bg: #f5f9f7;
                        --dark-text: #2c3e50;
                        --light-text: #ffffff;
                        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        --water-color: #3498db;
                        --bottle-outline: #2c3e50;
                    }
                    
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    body {
                        font-family: 'Poppins', Arial, sans-serif;
                        background-color: var(--light-bg);
                        color: var(--dark-text);
                        display: flex;
                        flex-direction: column;
                        min-height: 100vh;
                        max-width: 100%;
                        margin: 0;
                        padding: 0;
                    }
                    
                    .header {
                        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                        color: var(--light-text);
                        padding: 12px;
                        text-align: center;
                        box-shadow: var(--card-shadow);
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }
                    
                    .logo-container {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 10px;
                    }
                    
                    .logo {
                        font-size: 32px;
                        font-weight: 700;
                        display: flex;
                        align-items: center;
                    }
                    
                    .logo i {
                        margin-right: 15px;
                        font-size: 36px;
                    }
                    
                    .tagline {
                        font-size: 16px;
                        font-weight: 300;
                        margin-top: 5px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                    }
                    
                    .content {
                        flex: 1;
                        overflow-y: auto;
                        margin-bottom: 20px;
                    }
                    
                    .input-container {
                        background-color: white;
                        padding: 20px;
                        border-radius: 12px;
                        box-shadow: var(--card-shadow);
                        margin-top: 20px;
                    }
                    
                    .button-container {
                        display: flex;
                        gap: 10px;
                        margin-top: 15px;
                    }
                    
                    button {
                        padding: 12px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        flex: 1;
                        font-family: 'Poppins', sans-serif;
                        font-weight: 500;
                        transition: all 0.3s ease;
                    }
                    
                    button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    }
                    
                    .standard {
                        background-color: var(--accent-color);
                        color: var(--light-text);
                    }
                    
                    .complete {
                        background-color: var(--primary-color);
                        color: var(--light-text);
                    }
                    
                    .bullet {
                        background-color: #f1c40f;
                        color: var(--dark-text);
                    }
                    
                    .input-wrapper {
                        position: relative;
                        display: flex;
                        align-items: center;
                        margin-bottom: 15px;
                    }
                    
                    #mio_testo {
                        width: 100%;
                        padding: 15px;
                        padding-right: 100px; /* Spazio per i pulsanti */
                        border-radius: 8px;
                        border: 1px solid #ddd;
                        font-family: 'Poppins', sans-serif;
                        font-size: 16px;
                        box-sizing: border-box;
                        transition: border 0.3s ease;
                    }
                    
                    #mio_testo:focus {
                        outline: none;
                        border-color: var(--primary-color);
                    }
                    
                    .quick-buttons {
                        position: absolute;
                        right: 10px;
                        display: flex;
                        gap: 8px;
                    }
                    
                    .quick-button {
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 14px;
                        cursor: pointer;
                        border: none;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: all 0.2s ease;
                    }
                    
                    .quick-button:hover {
                        transform: scale(1.1);
                    }
                    
                    .btn-summarize {
                        background-color: #9b59b6;
                        color: white;
                    }
                    
                    .btn-translate {
                        background-color: #3498db;
                        color: white;
                    }
                    
                    .quick-button-tooltip {
                        position: absolute;
                        bottom: -25px;
                        left: 50%;
                        transform: translateX(-50%);
                        background-color: rgba(0,0,0,0.7);
                        color: white;
                        padding: 3px 8px;
                        border-radius: 4px;
                        font-size: 12px;
                        white-space: nowrap;
                        opacity: 0;
                        transition: opacity 0.2s ease;
                        pointer-events: none;
                    }
                    
                    .quick-button:hover .quick-button-tooltip {
                        opacity: 1;
                    }
                    
                    .chat-history {
                        margin-top: 20px;
                    }
                    
                    .chat-item {
                        margin-bottom: 25px;
                        padding: 20px;
                        border-radius: 12px;
                        position: relative;
                        box-shadow: var(--card-shadow);
                        background-color: white;
                        transition: transform 0.3s ease;
                    }
                    
                    .chat-item:hover {
                        transform: translateY(-5px);
                    }
                    
                    .standard-item {
                        border-left: 5px solid var(--accent-color);
                    }
                    
                    .complete-item {
                        border-left: 5px solid var(--primary-color);
                    }
                    
                    .bullet-item {
                        border-left: 5px solid #f1c40f;
                    }
                    
                    .domanda {
                        font-weight: 600;
                        margin-bottom: 15px;
                        color: var(--dark-text);
                        font-size: 18px;
                    }
                    
                    .risposta {
                        white-space: pre-line;
                        margin-right: 100px; /* Spazio per entrambi i contatori */
                        color: #555;
                        line-height: 1.6;
                    }
                    
                    .clear-button {
                        background-color: #8ab59b;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 8px;
                        margin: 10px 0 20px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        font-weight: 500;
                        box-shadow: var(--card-shadow);
                        border: none;
                        width: auto;
                        display: inline-block;
                    }
                    
                    .clear-button:hover {
                        background-color: #c0392b;
                    }
                    
                    .token-counter {
                        position: absolute;
                        right: 15px;
                        top: 50%;
                        transform: translateY(-50%);
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background-color: #95a5a6;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        font-weight: bold;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    
                    .eco-counter {
                        position: absolute;
                        right: 65px;
                        top: 50%;
                        transform: translateY(-50%);
                        width: 50px;
                        height: 70px;
                        /* Rimosso il box-shadow */
                    }
                    
                    .water-bottle {
                        width: 50px;
                        height: 70px;
                    }
                    
                    .bottle-outline {
                        fill: none;
                        stroke: var(--bottle-outline);
                        stroke-width: 1.5;
                    }
                    
                    .water-fill {
                        fill: var(--water-color);
                        transition: height 0.5s ease;
                    }
                    
                    .eco-percentage {
                        font-size: 18px;
                        font-weight: bold;
                        fill: var(--dark-text);
                    }
                    
                    .empty-state {
                        text-align: center;
                        padding: 50px 0;
                        color: #7f8c8d;
                    }
                    
                    .empty-state i {
                        font-size: 50px;
                        margin-bottom: 20px;
                        color: #bdc3c7;
                    }
                    
                    /* Stile per l'animazione di caricamento */
                    .loading-container {
                        display: none; /* Nascosto di default */
                        text-align: center;
                        margin: 20px 0;
                        height: 40px;
                    }
                    
                    .loading-dots {
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .loading-dot {
                        width: 12px;
                        height: 12px;
                        background-color: var(--primary-color);
                        border-radius: 50%;
                        margin: 0 5px;
                        animation: dot-pulse 1.5s infinite ease-in-out;
                    }
                    
                    .loading-dot:nth-child(1) {
                        animation-delay: 0s;
                    }
                    
                    .loading-dot:nth-child(2) {
                        animation-delay: 0.2s;
                    }
                    
                    .loading-dot:nth-child(3) {
                        animation-delay: 0.4s;
                    }
                    
                    @keyframes dot-pulse {
                        0%, 100% {
                            transform: scale(1);
                            opacity: 0.7;
                        }
                        50% {
                            transform: scale(1.5);
                            opacity: 1;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="logo-container">
                        <div class="logo">
                            <i class="fas fa-leaf"></i>
                            ECOAI
                        </div>
                    </div>
                    <div class="tagline">Intelligenza Artificiale Ecologica</div>
                </div>
                
                <div class="container">
                    <div class="content">
                        {% if history %}
                            <div class="chat-history">
                                <button type="button" class="clear-button" onclick="clearHistory()">
                                    <i class="fas fa-trash"></i> Cancella Cronologia
                                </button>
                                
                                {% for item in history %}
                                    <div class="chat-item {% if item.tipo == 'completo' %}complete-item{% elif item.tipo == 'bullet' %}bullet-item{% else %}standard-item{% endif %}">
                                        <div class="domanda">
                                            <i class="fas fa-question-circle" style="margin-right: 8px;"></i>
                                            {{ item.domanda }}
                                        </div>
                                        <div class="risposta">
                                            {{ item.risposta }}
                                        </div>
                                        <div class="eco-counter">
                                            <svg class="water-bottle" viewBox="0 0 100 140">
                                                <!-- Bottiglia cilindrica semplice -->
                                                <path class="bottle-outline" d="M30,10 L30,130 C30,135 40,140 50,140 C60,140 70,135 70,130 L70,10 C70,5 60,0 50,0 C40,0 30,5 30,10 Z"/>
                                                
                                                <!-- Acqua nella bottiglia - l'altezza sarà dinamica in base alla percentuale -->
                                                <path class="water-fill" 
                                                      d="M30,{{ 130 - item.eco_percentage * 1.2 }} 
                                                         L30,130 
                                                         C30,135 40,140 50,140 
                                                         C60,140 70,135 70,130 
                                                         L70,{{ 130 - item.eco_percentage * 1.2 }} 
                                                         C70,{{ (130 - item.eco_percentage * 1.2) + 5 }} 60,{{ (130 - item.eco_percentage * 1.2) + 10 }} 50,{{ (130 - item.eco_percentage * 1.2) + 10 }} 
                                                         C40,{{ (130 - item.eco_percentage * 1.2) + 10 }} 30,{{ (130 - item.eco_percentage * 1.2) + 5 }} 30,{{ 130 - item.eco_percentage * 1.2 }} Z"/>
                                                
                                                <!-- Percentuale eco con font ancora più grande -->
                                                <text class="eco-percentage" x="50" y="80" text-anchor="middle" dominant-baseline="middle">{{ item.eco_percentage }}%</text>
                                            </svg>
                                        </div>
                                        <div class="token-counter">{{ item.token_count }}</div>
                                    </div>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="empty-state">
                                <i class="fas fa-comments"></i>
                                <p>Nessuna conversazione ancora. Fai una domanda per iniziare!</p>
                            </div>
                        {% endif %}
                    </div>
                    
                    <!-- Indicatore di caricamento -->
                    <div class="loading-container" id="loadingIndicator">
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                    </div>
                    
                    <div class="input-container">
                        <form method="POST" id="promptForm">
                            <div class="input-wrapper">
                                <input type="text" id="mio_testo" name="mio_testo" placeholder="Scrivi qui la tua domanda...">
                                <div class="quick-buttons">
                                    <button type="button" class="quick-button btn-summarize" onclick="modificaPrompt('riassumi')">
                                        R
                                        <span class="quick-button-tooltip">Riassumi</span>
                                    </button>
                                    <button type="button" class="quick-button btn-translate" onclick="modificaPrompt('traduci')">
                                        T
                                        <span class="quick-button-tooltip">Traduci</span>
                                    </button>
                                </div>
                            </div>
                            <input type="hidden" id="tipo_prompt" name="tipo_prompt" value="standard">
                            <input type="hidden" id="clear_history" name="clear_history" value="false">
                            <input type="hidden" id="testo_originale" name="testo_originale" value="">
                            <input type="hidden" id="operazione_speciale" name="operazione_speciale" value="">
                            
                            <div class="button-container">
                                <button type="button" class="standard" onclick="inviaPrompt('standard')">
                                    <i class="fas fa-comment"></i> STANDARD
                                </button>
                                <button type="button" class="complete" onclick="inviaPrompt('completo')">
                                    <i class="fas fa-clipboard-list"></i> RIASSUNTIVA
                                </button>
                                <button type="button" class="bullet" onclick="inviaPrompt('bullet')">
                                    <i class="fas fa-list"></i> BULLET
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <script>
                    function inviaPrompt(tipo) {
                        // Imposta il tipo di prompt
                        document.getElementById('tipo_prompt').value = tipo;
                        
                        // Mostra l'indicatore di caricamento
                        document.getElementById('loadingIndicator').style.display = 'block';
                        
                        // Aggiungi un event listener al form per il submit
                        var form = document.getElementById('promptForm');
                        
                        // Disabilita i pulsanti (ma non gli input nascosti)
                        var buttons = document.querySelectorAll('button');
                        buttons.forEach(function(button) {
                            button.disabled = true;
                            button.style.opacity = '0.6';
                            button.style.cursor = 'not-allowed';
                        });
                        
                        // Invia il form subito dopo aver mostrato l'indicatore di caricamento
                        form.submit();
                    }
                    
                    function modificaPrompt(tipo) {
                        var inputText = document.getElementById('mio_testo');
                        var testoAttuale = inputText.value.trim();
                        
                        if (testoAttuale) {
                            // Memorizza il testo originale in un campo nascosto
                            document.getElementById('testo_originale').value = testoAttuale;
                            
                            if (tipo === 'riassumi') {
                                // Imposta un flag per il tipo di operazione speciale
                                document.getElementById('operazione_speciale').value = 'riassumi';
                            } else if (tipo === 'traduci') {
                                // Imposta un flag per il tipo di operazione speciale
                                document.getElementById('operazione_speciale').value = 'traduci';
                            }
                            
                            // Invia immediatamente con tipo standard
                            inviaPrompt('standard');
                        } else {
                            alert("Inserisci prima del testo da " + (tipo === 'riassumi' ? "riassumere" : "tradurre"));
                        }
                    }
                    
                    function clearHistory() {
                        document.getElementById('clear_history').value = "true";
                        document.getElementById('promptForm').submit();
                    }
                    
                    // Scroll to bottom on page load to show latest message
                    window.onload = function() {
                        var contentDiv = document.querySelector('.content');
                        contentDiv.scrollTop = contentDiv.scrollHeight;
                    }
                </script>
            </body>
        </html>
    ''', testo=testo, risposta=risposta, prompt_usato=prompt_usato, history=history)
    
    # Imposta il cookie per salvare la cronologia
    resp = make_response(response)
    resp.set_cookie('history', json.dumps(history))
    
    return resp

if __name__ == '__main__':
    print("Avvio dell'applicazione ECOAI...")
    print("Apri il browser e vai a http://127.0.0.1:5000/ per usare l'app")
    app.run(debug=True, port=5000)
