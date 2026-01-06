import os, tempfile, datetime as dt, json
import csv
import matplotlib.pyplot as plt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from .database import insert_gasto, get_gastos, get_gastos_por_categoria
from .audio_transcription import preprocess_audio, transcribe_audio_with_whisper
from .llm_agent import extract_gasto_data
from .relatorio_pdf import gerar_relatorio_pdf
from .gerar_grafico import gerar_grafico_gastos_por_categoria

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = context.user_data.get("pending_gasto")
    if not data:
        await query.edit_message_text("❌ Não há gasto pendente para confirmar.")
        return
    if query.data == "confirmar_gasto":
        insert_gasto(
            query.from_user.id,
            data["Valor"],
            data["Categoria"],
            dt.datetime.now().isoformat(),
            data["transcript"]
        )
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
        
        data = extract_gasto_data(transcript)

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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📥 Recebendo sua mensagem...")
        transcript = update.message.text
        
        await update.message.reply_text("🔎 Analisando o gasto e classificando a categoria...")
        
        data = extract_gasto_data(transcript)

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
        print(e)
        await update.message.reply_text("❌ Ocorreu um erro e o gasto não foi registrado corretamente. Por favor, tente novamente.")

async def handle_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        rows = get_gastos(user_id)

        if not rows:
            await update.message.reply_text("Nenhum gasto encontrado para este usuário.")
            return

        await update.message.reply_text("📄 Gerando o relatório PDF dos seus gastos...")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            pdf_path = pdf_file.name

        gerar_relatorio_pdf(rows, pdf_path)

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(
                f,
                filename="relatorio_gastos.pdf"
            )

        os.remove(pdf_path)
    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ocorreu um erro ao gerar o relatório. Por favor, tente novamente.")

async def handle_grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        data = get_gastos_por_categoria(user_id)

        if not data:
            await update.message.reply_text("Nenhum gasto encontrado para este usuário.")
            return
        await update.message.reply_text("📊 Gerando o gráfico dos seus gastos por categoria...")
        img_path = gerar_grafico_gastos_por_categoria(data)

        with open(img_path, "rb") as f:
            await update.message.reply_photo(
                f,
                caption="📊 Gastos por categoria — ByteGasto"
            )

        os.remove(img_path)
    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ocorreu um erro ao gerar o gráfico. Por favor, tente novamente.")


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Olá! Eu sou o ByteGasto 🤖\n\n"
        "Envie uma mensagem de voz dizendo o valor e a categoria do seu gasto, por exemplo:\n"
        "\"Gastei 20 reais com mercado\"\n\n"
        "Eu vou transcrever, extrair os dados e registrar para você.\n"
    )
    await update.message.reply_text(msg)

def setup_bot():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "SEU_TOKEN_AQUI")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CommandHandler("relatorio", handle_relatorio))
    app.add_handler(CommandHandler("grafico", handle_grafico))
    app.add_handler(
        CallbackQueryHandler(handle_confirm, pattern="^(confirmar_gasto|cancelar_gasto)$")
    )
    return app

def main():
    app = setup_bot()
    print("ByteGasto bot rodando...")
    app.run_polling()   

if __name__ == "__main__":
    main()
