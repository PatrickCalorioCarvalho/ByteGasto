import os, tempfile, datetime as dt, json, sqlite3, ffmpeg, ollama
import whisper
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
import re
import csv
import matplotlib.pyplot as plt
import subprocess

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "carteira.db")
DB_PATH = os.path.abspath(DB_PATH)

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS Gastos (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Valor REAL,
            Categoria TEXT,
            Data TEXT,
            raw_texto TEXT
        )""")

def preprocess_audio(input_path):
    output_path = input_path.replace('.oga', '_clean.wav')

    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-ac', '1',
        '-ar', '16000',
        '-af', 'loudnorm',
        output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def transcribe_audio_with_whisper(audio_path):
    model = whisper.load_model("tiny") 
    result = model.transcribe(audio_path, language="pt")
    return result["text"]

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = context.user_data.get("pending_gasto")
    if not data:
        await query.edit_message_text("❌ Não há gasto pendente para confirmar.")
        return
    if query.data == "confirmar_gasto":
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""INSERT INTO Gastos
                        (UserId, Valor, Categoria, Data, Raw_texto)
                        VALUES (?, ?, ?, ?, ?)""",
                        (query.from_user.id,
                        data["Valor"],
                        data["Categoria"],
                        dt.datetime.now().isoformat(),
                        data["transcript"]))
        await query.edit_message_text(
            f"✅ Gasto cadastrado!\n"
            f"💸 Valor: <b>R$ {data['Valor']:.2f}</b>\n"
            f"🏷️ Categoria: <b>{data['Categoria']}</b>",
            parse_mode="HTML"
        )
    else:
        await query.edit_message_text("Cadastro do gasto cancelado. Envie novamente o áudio se desejar registrar outro gasto.")
    context.user_data.pop("pending_gasto", None)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📥 Recebendo seu áudio...")
        voice = update.message.voice
        file = await voice.get_file()
        ogg_path = os.path.join(tempfile.gettempdir(), f"{file.file_id}.oga")
        await file.download_to_drive(ogg_path)
        
        await update.message.reply_text("🔊 Convertendo e processando o áudio...")
        wav_path = preprocess_audio(ogg_path)
       
        await update.message.reply_text("📝 Transcrevendo o áudio para texto...")
        transcript = transcribe_audio_with_whisper(wav_path)
        
        await update.message.reply_text(f"🗒️ Transcrição: \"{transcript}\"")
        
        await update.message.reply_text("🔎 Analisando o gasto e classificando a categoria...")
        
        prompt = f"""Você é um extrator de gastos. Retorne somente um JSON no formato:
                    {{
                    "Valor": float,
                    "Categoria": str,
                    }}
                    Classifique a categoria do gasto de acordo com estas opções padronizadas:
                    - "alimentacao" (ex: mercado, lanche, restaurante, comida, padaria)
                    - "bebida" (ex: cerveja, vinho, bar, refrigerante)
                    - "transporte" (ex: uber, gasolina, ônibus, metrô, passagem)
                    - "moradia" (ex: aluguel, condomínio, luz, água, internet)
                    - "lazer" (ex: cinema, show, viagem, festa)
                    - "outros" (caso não se encaixe nas anteriores)
                    Retorne apenas os campos que existem no texto no Formato JSON.
                    Não retorne nada mais.
                    Não adicione comentários.
                    O texto é em português.
                    Texto: \"{transcript}\""""
        
        completion = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": prompt}]
        )["message"]["content"]
       
        match = re.search(r'\{.*\}', completion, re.DOTALL)
        if not match:
            await update.message.reply_text("❌ Não foi possível extrair o JSON da resposta. O gasto não foi registrado. Tente novamente.")
            return
        
        data = json.loads(match.group(0))

        context.user_data["pending_gasto"] = {
            "Valor": data["Valor"],
            "Categoria": data["Categoria"],
            "transcript": transcript
        }
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_gasto"),
                InlineKeyboardButton("🔄 Cancelar", callback_data="cancelar_gasto"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Confirme o cadastro do gasto:\n"
            f"💸 Valor: <b>R$ {data['Valor']:.2f}</b>\n"
            f"🏷️ Categoria: <b>{data['Categoria']}</b>\n"
            f"🗒️ Descrição: \"{transcript}\"",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text("❌ Ocorreu um erro e o gasto não foi registrado corretamente. Por favor, tente novamente.")

async def handle_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.execute(
            "SELECT Valor, Categoria, Data, raw_texto FROM Gastos WHERE UserId = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
    if not rows:
        await update.message.reply_text("Nenhum gasto encontrado para este usuário.")
        return

    with tempfile.NamedTemporaryFile("w+", newline='', suffix=".csv", delete=False) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Valor", "Categoria", "Data", "Raw_texto"])
        writer.writerows(rows)
        csvfile_path = csvfile.name

    with open(csvfile_path, "rb") as f:
        await update.message.reply_document(f, filename="relatorio_gastos.csv")
    os.remove(csvfile_path)

async def handle_grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.execute(
            "SELECT Categoria, SUM(Valor) FROM Gastos WHERE UserId = ? GROUP BY Categoria",
            (user_id,)
        )
        data = cursor.fetchall()
    if not data:
        await update.message.reply_text("Nenhum gasto encontrado para este usuário.")
        return
    

    categorias = [row[0] if row[0] is not None else "Sem categoria" for row in data]
    valores = [row[1] if row[1] is not None else 0 for row in data]
    plt.figure(figsize=(8, 5))
    plt.bar(categorias, valores, color='skyblue')
    plt.xlabel('Categoria')
    plt.ylabel('Total Gasto')
    plt.title('Gastos por Categoria')
    plt.tight_layout()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as imgfile:
        plt.savefig(imgfile.name)
        imgfile_path = imgfile.name
    plt.close()
    with open(imgfile_path, "rb") as f:
        await update.message.reply_photo(f, caption="Gráfico de gastos por categoria")
    os.remove(imgfile_path)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Olá! Eu sou o ByteGasto 🤖\n\n"
        "Envie uma mensagem de voz dizendo o valor e a categoria do seu gasto, por exemplo:\n"
        "\"Gastei 20 reais com mercado\"\n\n"
        "Eu vou transcrever, extrair os dados e registrar para você.\n"
    )
    await update.message.reply_text(msg)

def main():
    init_db()
    token = "SEUU_TOKEN_AQUI"  # Substitua pelo seu token do bot
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CommandHandler("relatorio", handle_relatorio))
    app.add_handler(CommandHandler("grafico", handle_grafico))
    app.add_handler(
        CallbackQueryHandler(handle_confirm, pattern="^(confirmar_gasto|cancelar_gasto)$")
    )
    print("ByteGasto bot rodando...")
    app.run_polling()   

if __name__ == "__main__":
    main()
