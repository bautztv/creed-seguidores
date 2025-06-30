import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import asyncio

API_SMM_URL = "https://painelsmm.com/api/v2/"
API_SMM_KEY = "1c918..."  # substitua pelo seu token SMMOFICIAL
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-767b6330-80f6-465c-b830-e0bb3..."  # seu token Mercado Pago
BOT_TOKEN = "8065012229:AAGB..."  # seu token bot Telegram

markup_lucro = 10.0

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Estado simples para exemplo
user_states = {}

async def get_services():
    """Pega os serviços da API SMM"""
    url = f"{API_SMM_URL}?key={API_SMM_KEY}&action=services"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if data["status"] == "success":
                return data["services"]
            else:
                return []

def build_services_keyboard(services):
    kb = InlineKeyboardBuilder()
    for srv in services:
        label = f"{srv['service']} - R${float(srv['rate']) + markup_lucro:.2f}"
        kb.button(text=label, callback_data=f"service_{srv['service']}_{srv['service_id']}_{srv['rate']}")
    kb.button(text="🔙 Voltar", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Olá! Bem-vindo ao CREED SEGUIDORES.\nDigite /services para ver os serviços disponíveis.")

@dp.message(Command("services"))
async def services_cmd(message: types.Message):
    services = await get_services()
    if not services:
        await message.answer("Erro ao buscar serviços. Tente novamente mais tarde.")
        return
    kb = build_services_keyboard(services)
    await message.answer("Escolha um serviço para comprar:", reply_markup=kb)

@dp.callback_query(Text(startswith="service_"))
async def service_select(query: types.CallbackQuery):
    _, name, service_id, rate = query.data.split("_", 3)
    user_states[query.from_user.id] = {
        "service_id": service_id,
        "service_name": name,
        "rate": float(rate)
    }
    await query.message.answer(f"Você escolheu *{name}*.\nDigite a quantidade desejada:")
    await query.answer()

@dp.message()
async def quantity_input(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or "service_id" not in user_states[user_id]:
        return  # ignorar mensagens que não estejam no fluxo
    try:
        quantity = int(message.text)
        if quantity < 1:
            await message.answer("Quantidade deve ser um número inteiro positivo.")
            return
    except:
        await message.answer("Digite um número válido para a quantidade.")
        return

    user_states[user_id]["quantity"] = quantity
    price = user_states[user_id]["rate"] * quantity + markup_lucro
    user_states[user_id]["price"] = price
    await message.answer(f"Total: R$ {price:.2f}\nPara pagar via PIX, use o comando /pay")

@dp.message(Command("pay"))
async def pay_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or "price" not in user_states[user_id]:
        await message.answer("Você precisa escolher um serviço e quantidade antes.")
        return
    price = user_states[user_id]["price"]

    # Aqui você deve criar o pagamento via Mercado Pago API (PIX) e retornar o QR code ou link
    # Vou colocar exemplo simples com link fictício, substitua pela integração real

    payment_link = f"https://www.mercadopago.com.br/pagar?amount={price:.2f}"

    await message.answer(f"Para pagar R$ {price:.2f}, clique no link:\n{payment_link}\n\nApós pagar, aguarde a confirmação automática.")

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    # Simples senha hardcoded para exemplo
    if message.text.strip() != "/admin 1234":
        await message.answer("Acesso negado. Use /admin 1234 para entrar.")
        return
    # Exemplo de estatísticas simples
    await message.answer("Painel Admin:\n- Pedidos feitos: 10\n- Vendas totais: R$ 500,00")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())