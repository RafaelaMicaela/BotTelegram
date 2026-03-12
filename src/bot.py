import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from config import TELEGRAM_TOKEN
import asyncio

# Lista de aniversariantes
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
    ("Pablo", None),
    ("Thiago", "29 de Dezembro"),
]

MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}

def get_birthdays_for_month(month: int):
    aniversariantes = []
    for nome, data in BIRTHDAYS:
        if data:
            try:
                dia, mes_nome = data.split(' de ')
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Olá! Eu sou o bot de aniversariantes da eSigma 🎉.\n\n"
        "Comandos disponíveis:\n"
        "/aniversariantes - Mostra os aniversariantes do mês atual.\n\n"
        "Eu também envio automaticamente a lista de aniversariantes do mês no início de cada mês!"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# Função para notificar aniversariantes do mês em todos os chats conhecidos
async def notify_birthdays_monthly(app):
    while True:
        now = datetime.datetime.now()
        # Notifica no primeiro dia do mês às 09:00
        next_run = now.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            # Se já passou do horário, agenda para o próximo mês
            if next_run.month == 12:
                next_run = next_run.replace(year=now.year+1, month=1)
            else:
                next_run = next_run.replace(month=now.month+1)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        # Envia para todos os chats conhecidos
        aniversariantes_mes = get_birthdays_for_month(next_run.month)
        if aniversariantes_mes:
            msg = (
                "Eita que esse mês tem Bolo! 🎂\n"
                "Aniversariantes do mês:\n" + "\n".join(aniversariantes_mes)
            )
        else:
            msg = "Não há aniversariantes cadastrados para este mês."
        # Recupera todos os chats salvos
        for chat_id in app.chat_ids:
            try:
                await app.bot.send_message(chat_id=chat_id, text=msg)
            except Exception:
                continue

# Handler para salvar chat_id de quem interagir
async def save_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in context.application.chat_ids:
        context.application.chat_ids.add(chat_id)
    # Não responde nada, só salva

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # Set para guardar os chats que interagiram
    app.chat_ids = set()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aniversariantes", aniversariantes))
    # Salva chat_id de qualquer mensagem recebida
    app.add_handler(MessageHandler(filters.ALL, save_chat_id))
    # Inicia a tarefa de notificação automática
    loop = asyncio.get_event_loop()
    loop.create_task(notify_birthdays_monthly(app))
    print("Bot rodando. Envie /start ou /aniversariantes no Telegram.")
    app.run_polling()
