from aiogram.dispatcher.filters.state import State, StatesGroup


class Product(StatesGroup):
    Name = State()
    Describe = State()
    Cost = State()
    Image = State()
    Confirm = State()


class Purchase(StatesGroup):
    Item = ""
    EnterQuantity = State()
    Approval = State()
    Payment = State()
