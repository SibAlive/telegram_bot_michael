import logging
from aiogram import Router, F, Bot
from aiogram.enums import BotCommandScopeType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (Message, BotCommandScopeChat, Contact, ReplyKeyboardRemove, CallbackQuery)
from aiogram.filters import CommandStart, Command, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from bot.services import (UserService, PointService, StatisticService,
                          DoctorService, get_user_data, convert_times,
                          convert_str_to_time)
from bot import keyboards
from bot.filters import (IsCorrectFullNameMessage, IsCorrectAgeMessage, ChooseTime)
from bot.FSM import DataForm, ServiceFrom
from bot.lexicon import RU


logger = logging.getLogger(__name__)

# Инициализируем роутер модуля
user_router = Router()


# Команда /start
@user_router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(
        message: Message,
        bot: Bot,
        session: AsyncSession,
        state: FSMContext,
):
    logger.debug("Вошли в хэндлер, обрабатывающий команду /start")
    user_id = message.from_user.id
    user_service = UserService(session)

    # Проверяем, зарегистрирован ли пользователь
    is_registered = await user_service.get_user(user_id=user_id)

    # Если не зарегистрирован, запрашиваем данные (ФИО, телефон, возраст)
    if not is_registered:
        await state.set_state(DataForm.fill_full_name)    # Запрашиваем ФИО
        await message.answer(text=RU.get('enter_name'))
    # Если зарегистрирован, уведомляем
    else:
        user_data = await user_service.get_user(user_id=user_id)
        user_data = get_user_data(user_data)
        await message.answer(text=RU.get('already_registered') + user_data)

    # Создаем главное меню
    commands = keyboards.create_main_menu(user_id)
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.chat.id,
        )
    )
    logger.debug("Выходим из хэндлера, обрабатывающего команду /start")


# Команда /finance
@user_router.message(Command("finance"), StateFilter(default_state))
async def process_finance_command(message, session):
    point_service = PointService(session)
    total_points = await point_service.get_user_points(telegram_id=message.from_user.id)
    # Преобразуем None в 0
    total_points = 0 if total_points is None else total_points
    await message.answer(text=RU.get('your_points') + str(total_points))


# Команда /call
@user_router.message(Command("call"), StateFilter(default_state))
async def process_call_command(message, session):
    user_id = message.from_user.id
    user_service = UserService(session)
    statistics_service = StatisticService(session)

    # Получаем данные о пользователе
    user_data = await user_service.get_user(user_id=user_id)
    # Получаем номер телефона пользователя
    phone_number = user_data[0].get('phone_number')

    text = RU.get("/call_desc")
    # Делаем запись в БД об обратном звонке
    await statistics_service.get_call_back(telegram_id=user_id, message=text, phone_number=phone_number)

    await message.answer(text=RU.get('we_call_you'))


# Команда /appoint (запись на прием)
@user_router.message(Command("appoint"), StateFilter(default_state))
async def process_call_command(message, session):
    user_id = message.from_user.id
    user_service = UserService(session)
    statistics_service = StatisticService(session)

    # Получаем данные о пользователе
    user_data = await user_service.get_user(user_id=user_id)
    # Получаем номер телефона пользователя
    phone_number = user_data[0].get('phone_number')

    text = RU.get("appoint_for_bd")
    # Делаем запись в БД о записи на прием
    await statistics_service.get_call_back(telegram_id=user_id, message=text, phone_number=phone_number)

    await message.answer(
        text='К кому Вы хотите попасть на прием?',
        reply_markup=keyboards.create_keyboard_employee()
    )


# Нажатие инлайн кнопки любого специалиста
@user_router.callback_query(F.data.in_(["Лор", "Окулист", "Невролог", "Хирург"]))
async def process_doctor(callback_query: CallbackQuery, state):
    doctor = callback_query.data
    await state.update_data(doctor=doctor)
    await callback_query.message.edit_text(
        text="Выберите день посещения",
        reply_markup=keyboards.create_keyboard_day()
    )


# Нажатие инлайн кнопки Сегодня или Завтра
@user_router.callback_query(F.data.in_(['Сегодня', 'Завтра']))
async def process_day_choose(callback_query, session, state):
    dt = date.today() if callback_query.data == 'Сегодня' else date.today() + timedelta(days=1)
    data = await state.get_data()
    await state.update_data(dt=dt.isoformat())
    doctor = data.get('doctor')
    doctor_service = DoctorService(session)

    date_times = await doctor_service.get_schedule(doctor=doctor, dt=dt)
    times = convert_times(date_times)

    kb = keyboards.create_keyboard_time(times)
    text = "Выберите время приема" if times else "Извините, свободного времени на выбранный день нет"

    await callback_query.message.edit_text(
        text=text,
        reply_markup=kb
    )


# Нажатие инлайн кнопки с выбором времени записи
@user_router.callback_query(ChooseTime())
async def process_time_choose(callback_query, state):
    data = await state.get_data()
    dt = data.get('dt')
    # date_time = convert_str_to_time(dt=dt, time_str=callback_query.data)
    date_time = dt + callback_query.data
    print(date_time)
    await state.update_data(date_time=date_time)

    await state.set_state(ServiceFrom.fill_service)
    await callback_query.message.edit_text(
        text="Напишите вкратце причину обращения или услугу",
        reply_markup=None
    )


# Написание причины обращения
@user_router.message(ServiceFrom.fill_service, F.text)
async def process_service(message, session, state):
    data = await state.get_data()
    date_time = data.get('date_time')
    speciality = data.get('doctor')
    doctor_service = DoctorService(session)

    # Проверяем, свободно ли время
    if await doctor_service.check_sign_up(speciality=speciality, date_time=date_time):
        await doctor_service.sign_up_to_doctor(
            telegram_id=message.from_user.id,
            speciality=speciality,
            service=message.text,
            date_time=date_time,
        )
        await message.answer(text="Спасибо за обращение. Вы успешно записаны")
    else:
        # Уведомляем пользователя, что его время заняли пока он думал
        await message.answer(text="Извините, но пока Вы писали причину посещения, выбранное время уже заняли")
    await state.set_state()


# Нажатие инлайн кнопки Назад к дате
@user_router.callback_query(F.data == "Назад к дате")
async def process_back_to_date(callback_query):
    await callback_query.message.edit_text(
        text="Выберите день посещения",
        reply_markup=keyboards.create_keyboard_day()
    )


# Нажатие инлайн кнопки назад
@user_router.callback_query(F.data == 'Назад')
async def process_back(callback_query):
    await callback_query.message.edit_text(
        text='К кому Вы хотите попасть на прием?',
        reply_markup=keyboards.create_keyboard_employee()
    )


# Нажатие инлайн кнопки отмена
@user_router.callback_query(F.data == 'Отмена')
async def process_cancel(callback_query):
    await callback_query.message.edit_text(
        text="Для записи на прием нажмите /appoint",
        reply_markup=None
    )


# Ввод ФИО
@user_router.message(DataForm.fill_full_name, IsCorrectFullNameMessage())
async def enter_name(message, state, session, full_name):
    logger.debug("Вошли в хэндлер ввода ФИО")
    # Проверяем, есть ли введенное ФИО в базе данных
    user_service = UserService(session)
    if await user_service.check_user_by_full_name(telegram_id=message.from_user.id, full_name=full_name):
        await user_service.update_user_id_by_full_name(full_name=full_name, telegram_id=message.from_user.id)
        await message.answer(text=RU.get('this_name_already_exist'))
    else:
        await state.update_data(full_name=full_name)    # Временно сохраняем данные внутри контекста
        await message.answer(text=RU.get('enter_phone'),
                             reply_markup=keyboards.create_share_phone_keyboard()
                             )
        await state.set_state(DataForm.fill_phone)  # Запрашиваем номер телефона


# Некорректный ввод ФИО
@user_router.message(DataForm.fill_full_name)
async def wrong_enter_name(message):
    logger.debug("Вошли в хэндлер некорректного ввода ФИО")
    await message.answer(text=RU.get('wrong_enter_name'))


# Обработка отправленного номера телефона
@user_router.message(DataForm.fill_phone, lambda message: message.contact)
async def process_phone_from_keyboard(message, state):
    logger.debug("Вошли в хэндлер обработки номера телефона")
    # Получаем номер телефона
    contact: Contact = message.contact
    phone_number = contact.phone_number

    # Проверяем, что номер принадлежит именно этому пользователю
    user_id = contact.user_id
    if user_id != message.from_user.id:
        await message.answer(
            text=RU.get('not_your_phone'),
            reply_markup=keyboards.create_share_phone_keyboard()
        )
    else:
        await state.update_data(phone_number=phone_number)
        await message.answer(
            text=RU.get('enter_age'),
            reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру
        )
        await state.set_state(DataForm.fill_age)    # Запрашиваем возраст


# Ввод возраста
@user_router.message(DataForm.fill_age, IsCorrectAgeMessage())
async def enter_age(message, state, age):
    logger.debug("Вошли в хэндлер ввода возраста")
    await state.update_data(age=age)  # Временно сохраняем данные внутри контекста
    data = await state.get_data()
    user_data = get_user_data(data) # Получаем данные пользователя
    await message.answer(
        text=RU.get('check_your_data') + user_data,
        reply_markup=keyboards.create_keyboard_confirm()
    )
    await state.set_state(DataForm.fill_correct)  # Запрашиваем подтверждение данных


# Некорректный ввод возраста
@user_router.message(DataForm.fill_age)
async def wrong_enter_age(message, state):
    logger.debug("Вошли в хэндлер некорректного ввода возраста")
    await message.answer(text=RU.get('wrong_enter_age'))


# Подтверждение данных
@user_router.callback_query(DataForm.fill_correct, F.data == "confirm")
async def process_confirm_data(callback, state, session):
    logger.debug("Вошли в хэндлер подтверждения данных")
    user_id = callback.from_user.id
    user_service = UserService(session)
    data = await state.get_data()
    await state.set_state()

    # Регистрируем нового пользователя
    if all(data.get(detail) for detail in ('full_name', 'phone_number', 'age')):
        await user_service.add_user(
            telegram_id=user_id,
            full_name=data.get('full_name'),
            phone_number=int(data.get('phone_number')),
            age=int(data.get('age'))
        )
        await callback.message.answer(text=RU.get('wellcome'))
    else:
        await callback.message.answer(text=RU.get('error_registration'))

    await callback.answer()


# Исправление данных
@user_router.callback_query(DataForm.fill_correct, F.data == "correct")
async def process_correct_data(callback, state):
    logger.debug("Вошли в хэндлер исправления данных")
    await state.set_state(DataForm.fill_full_name)
    await callback.answer() # Убираем мерцание инлайн кнопки
    await callback.message.answer(text=RU.get('enter_name'))


