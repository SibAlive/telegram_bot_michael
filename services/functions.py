import logging
from datetime import datetime

from lexicon import RU


logger = logging.getLogger(__name__)


def get_user_data(data: dict | list[dict]) -> str:
    """Возвращает строку данных пользователя для подтверждения"""
    if type(data) is list:
        data = data[0]

    full_name = data.get("full_name")
    phone_number = data.get("phone_number")
    age = data.get("age")

    result = RU.get('user_data').format(full_name, phone_number, age)
    return result


# Функция конвертирует общую сумму корзины
def convert_total(total: int, i18n: dict) -> str:
    return i18n.get("calculate_cart").format(total).replace(',', ' ')


# Функция формирует текст сообщения, при нажатии на кнопку оформить заказ
async def create_text_order(i18n: dict, products: list[dict]) -> tuple | str:
    text = ""
    total = 0

    for product in products:
        name = product.get('name')
        qnty = product.get('qnty')
        price = product.get('price')
        total += price * qnty
        text += (f"{name}: {qnty} * {price:,.2f} сум = {total:,.2f} сум;\n"
                   .replace(',', ' '))

    if text:
        result_1 = i18n.get("your_order_total").format(total).replace(',', ' ')
        result_2 = text
        # result_3 = i18n.get('write_name')
        return result_1, result_2

    text = i18n.get("order_cart_empty")
    return text


# Функция, формирующая текст подтверждения ввода данных
def get_confirm_text(data: dict, i18n: dict) -> str:
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address")
    result = i18n.get("confirm_text").format(name, phone, address)
    return result


async def get_confirm_text_from_db(user_service, user_id: int, i18n: dict) -> str:
    user_data = await user_service.get_user_name_phone_address(user_id=user_id)
    name = user_data[0].get("name")
    phone = user_data[0].get("phone")
    address = user_data[0].get("address")
    result = i18n.get("confirm_text").format(name, phone, address)
    return result


def convert_times(date_times):
    result = []
    for date_time in date_times:
        time = date_time.strftime("%H:%M")
        result.append(time)
    return result


def convert_str_to_time(dt, time_str: str):
    tm = datetime.strptime(time_str, "%H:%M").time()
    result = datetime.combine(dt, tm)
    return result


async def send_test_message_broadcast(*, bot, chat_id, file_type, file_id, caption=None):
    """Функция отправляет тестовое сообщение с файлом админу"""
    if file_type == "photo":
        return await bot.send_photo(
            chat_id=chat_id,
            photo=file_id,
            caption=caption
        )
    elif file_type == "video":
        return await bot.send_video(
            chat_id=chat_id,
            video=file_id,
            caption=caption
        )
    elif file_type == "document":
        return await bot.send_document(
            chat_id=chat_id,
            document=file_id,
            caption=caption
        )