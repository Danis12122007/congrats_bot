from aiogram.fsm.state import State, StatesGroup


class Congrat(StatesGroup):
    user_id = State()
    congrat_type = State()
    congrat_recipient_role = State()
    congrat_style = State()
    reciever_name = State()
    promocode = State()
    achieve = State()
    holiday = State()
    anniversary = State()
    broadcast = State()
    confirm_broadcast = State()
