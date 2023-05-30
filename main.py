
import postgre
import aphavantage
from aiogram import  Bot,types
from aiogram.dispatcher import Dispatcher,FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aioschedule
import config

storage =MemoryStorage()

dataBase = postgre.PostgeHelper()


bot = Bot(config.bot_key)
dp = Dispatcher(bot,storage=storage)

apiHelper = aphavantage.AlphaApiHelper(config.api_key)


class FSM(StatesGroup):
  #none = State()
  sheet = State()


@dp.message_handler(commands=['new_sheet'],state=None)
async def new_sheet(message):
  await FSM.sheet.set()
  await bot.send_message(message.chat.id,"Введите имя ценной бумаги")
  
@dp.message_handler(commands=['status'],state=None)
async def status(message):
  base_data = dataBase.get_all_sheets_by_name(str(message.chat.id))
  
  result='Показатели для ваших бумаг:\n'
  for i in base_data:
    name = i[0]
    stat = apiHelper.analyze(apiHelper.get_sheet_status(name)["Time Series (Daily)"])
    dataBase.update_statistic_by_name(stat,name)
    result +=f"Для бумаги {name} показатели равны: {stat}\n"

  await bot.send_message(message.chat.id,result)
  #for i in base_data:

@dp.message_handler(content_types=['text'],state=FSM.sheet)
async def add_sheet(message,state :FSMContext):
  data = apiHelper.get_sheet_status(message.text)
  if 'Error Message' in data:
    await bot.send_message(message.chat.id,f"Для ценной бумаги {message.text} не найдено значений")
    await state.set_state(None)
    return;
  dataBase.insert_sheet(message.text,str(message.chat.id))
  await state.set_state(None)
  await bot.send_message(message.chat.id,f"Ценная бумага {message.text} добавлена к отслеживаемым")

async def refresh_statistics():
  base_data = dataBase.get_all_sheets()
  
  result='Показатели для ваших бумаг:\n'
  for i in base_data:
    name = i[0]
    stat = apiHelper.analyze(apiHelper.get_sheet_status(name)["Time Series (Daily)"])
    dataBase.update_statistic_by_name(stat,name)
    result +=f"Для бумаги {name} показатели равны: {stat}\n"


async def scheduler():
    aioschedule.every().day.at("12:00").do(refresh_statistics)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
  asyncio.create_task(scheduler())

executor.start_polling(dp,skip_updates=True,on_startup=on_startup)

