from aiogram.fsm.state import StatesGroup, State


# Форма заполнения данных при регистрации
class DataForm(StatesGroup):
    fill_full_name = State() # Ожидаем ФИО
    fill_phone = State() # Ожидаем телефон
    fill_age = State() # Ожидаем возраст
    fill_correct = State() # Ожидаем подтверждение


 # Форма заполнения услуги при обращении к врачу
class ServiceFrom(StatesGroup):
    fill_service = State()


# Форма массовой рассылки
class BroadcastForm(StatesGroup):
    choose = State() # Ожидаем выбор типа сообщения
    message = State() # Ожидаем сообщение/описание
    file = State() # Ожидаем фото, видео или документ
    caption = State() # Ожидаем описание (опционально)
    confirm = State()  # Ожидаем подтверждения отправки