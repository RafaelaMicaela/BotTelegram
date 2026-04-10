import datetime
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from config import TELEGRAM_TOKEN

BIRTHDAYS = [
    ("Arthur Melo", "29 de Janeiro"),
    ("Dennis", "3 de Janeiro"),
    ("Douglas", "6 de Junho"),
    ("Felipe Xavier", "9 de Agosto"),
    ("Filipe Araújo", "13 de Outubro"),
    ("Gabriel", "5 de Abril"),
    ("George", "22 de Fevereiro"),
    ("Hilquias", "13 de Dezembro"),
    ("Lucas Nithael", "4 de Abril"),
    ("Marcos", "13 de Setembro"),
    ("Renan Lisboa", "11 de Dezembro"),
    ("Rafaela", "23 de Maio"),
    ("Pablo", "17 de Fevereiro"),
    ("Thiago", "29 de Dezembro"),
]

MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}

CHAT_IDS_FILE = "chat_ids.json"

def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return set(data)
            except Exception:
                pass
    return set()

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(chat_ids), f)

def get_birthdays_for_month(month: int):
    aniversariantes = []
    for nome, data in BIRTHDAYS:
        if data:
            try:
                dia_str, mes_nome = data.split(' de ')
                if MONTHS[mes_nome.strip().lower()] == month:
                    aniversariantes.append(f"{nome}: {data}")
            except Exception:
                continue
    return aniversariantes

async def aniversariantes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.datetime.now()
    mes_atual = hoje.month
    aniversariantes_mes = get_birthdays_for_month(mes_atual)
    if aniversariantes_mes:
        msg = (
            "Eita que esse mês tem comemoração! 🎂🍕🥐\n"
            "Aniversariantes do mês:\n" + "\n".join(aniversariantes_mes)
        )
    else:
        msg = "Não há aniversariantes cadastrados para este mês."
    await update.message.reply_text(msg)

async def pizza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Atenção, pessoal! Passando para avisar que hoje é DIA DE PIZZA! 🍕🍕🍕"
    await update.message.reply_text(msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_chat_id(update, context) # Salva o ID ao iniciar
    msg = (
        "Olá! Eu sou o bot de aniversariantes da eSigma 🎉.\n\n"
        "Comandos disponíveis:\n"
        "/aniversariantes - Mostra os aniversariantes do mês atual.\n"
        "/pizza - Avisa que hoje é dia de pizza!\n\n"
        "Eu também envio automaticamente os aniversariantes do mês e do dia!"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def save_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat:
        chat_id = update.effective_chat.id
        chat_ids = load_chat_ids()
        if chat_id not in chat_ids:
            chat_ids.add(chat_id)
            save_chat_ids(chat_ids)

async def send_daily_notifications(context: ContextTypes.DEFAULT_TYPE):
    chat_ids = load_chat_ids()
    if not chat_ids:
        return

    hoje = datetime.datetime.now()
    
    # 1. Verifica se hoje é o primeiro dia do mês para listar todos do mês
    if hoje.day == 1:
        aniversariantes_mes = get_birthdays_for_month(hoje.month)
        if aniversariantes_mes:
            msg_mes = "Eita que esse mês tem Bolo! 🎂\nAniversariantes do mês:\n" + "\n".join(aniversariantes_mes)
            for cid in chat_ids:
                try: 
                    await context.bot.send_message(chat_id=cid, text=msg_mes)
                except Exception as e: 
                    print(f"Erro ao enviar para {cid}: {e}")

    # 2. Verifica se hoje tem algum aniversariante do dia
    aniversariantes_hoje = []
    for nome, data in BIRTHDAYS:
        if data:
            try:
                dia_str, mes_nome = data.split(' de ')
                dia = int(dia_str.strip())
                mes_num = MONTHS[mes_nome.strip().lower()]
                if dia == hoje.day and mes_num == hoje.month:
                    aniversariantes_hoje.append(nome)
            except Exception:
                continue
    
    if aniversariantes_hoje:
        if len(aniversariantes_hoje) == 1:
            msg_hoje = f"🎉 Hoje é aniversário de {aniversariantes_hoje[0]}! Parabéns! 🎈🍰🎂"
        else:
            nomes_str = ", ".join(aniversariantes_hoje[:-1]) + " e " + aniversariantes_hoje[-1]
            msg_hoje = f"🎉 Hoje é aniversário de {nomes_str}! Parabéns a todos! 🎈🍰🎂"
            
        for cid in chat_ids:
            try: 
                await context.bot.send_message(chat_id=cid, text=msg_hoje)
            except Exception: 
                pass

async def send_pizza_notification(context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.datetime.now()
    # Verifica se hoje é dia 14
    if hoje.day != 14:
        return

    chat_ids = load_chat_ids()
    if not chat_ids:
        return
    msg = "Atenção, pessoal! Passando para avisar que hoje é DIA DE PIZZA! 🍕🍕🍕"
    for cid in chat_ids:
        try: 
            await context.bot.send_message(chat_id=cid, text=msg)
        except Exception: 
            pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aniversariantes", aniversariantes))
    app.add_handler(CommandHandler("pizza", pizza))
    # Captura qualquer mensagem e salva o chat_id silenciosamente
    app.add_handler(MessageHandler(filters.ALL, save_chat_id))

    # Obtém o fuso horário local
    try:
        local_tz = datetime.datetime.now().astimezone().tzinfo
    except Exception:
        local_tz = None

    # Agenda a notificação diária (aniversariantes) para as 09:00
    t_09 = datetime.time(hour=9, minute=0, tzinfo=local_tz)
    app.job_queue.run_daily(send_daily_notifications, time=t_09)

    # Agenda a notificação da pizza todos os dias às 12:00 (a lógica interna filtra pro dia 14)
    t_12 = datetime.time(hour=12, minute=0, tzinfo=local_tz)
    app.job_queue.run_daily(send_pizza_notification, time=t_12)

    print("Bot rodando com agendamento ativo. Envie /start no Telegram para o bot registrar o chat.")
    app.run_polling()
