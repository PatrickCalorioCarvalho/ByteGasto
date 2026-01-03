from src.database import init_db
from src.telegram_bot import setup_bot
from dotenv import load_dotenv


def main():
    load_dotenv()
    init_db()
    app = setup_bot()
    print("ByteGasto bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()