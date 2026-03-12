import os
from dotenv import load_dotenv

# Isso aqui é o que "puxa" as variáveis do arquivo .env para a memória do seu PC
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")