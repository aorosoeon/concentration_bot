from functools import wraps
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup
from telebot.types import KeyboardButton
from telebot.types import Message
import aioschedule as schedule
import asyncio
import datetime as dt
import gspread
from google.oauth2 import service_account

bot = AsyncTeleBot("API_KEY")

credentials = service_account.Credentials.from_service_account_file("CREDENTIALS_JSON")
scoped_credentials = credentials.with_scopes(["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"])
client = gspread.authorize(scoped_credentials)
sheet = client.open("NAME_OF_SPREADSHEET").sheet1

resultsRow = []

tw = "20 min"
th = "30 min"
fo = "40 min"
focusMarks = ["0", "1", "2", "3", "4", "5+"]
completionMarks = ["25%", "50%", "75%", "100%", "125%", "150%"]

markupDuration = ReplyKeyboardMarkup(one_time_keyboard=True)
dButton1 = KeyboardButton(tw)
dButton2 = KeyboardButton(th)
dButton3 = KeyboardButton(fo)
markupDuration.add(dButton1, dButton2, dButton3)

markupFocus = ReplyKeyboardMarkup(one_time_keyboard=True)
fButton1 = KeyboardButton("0")
fButton2 = KeyboardButton("1")
fButton3 = KeyboardButton("2")
fButton4 = KeyboardButton("3")
fButton5 = KeyboardButton("4")
fButton6 = KeyboardButton("5+")
markupFocus.add(fButton1, fButton2, fButton3, fButton4, fButton5, fButton6)

markupCompletion = ReplyKeyboardMarkup(one_time_keyboard=True)
fButton1 = KeyboardButton("25%")
fButton2 = KeyboardButton("50%")
fButton3 = KeyboardButton("75%")
fButton4 = KeyboardButton("100%")
fButton5 = KeyboardButton("125%")
fButton6 = KeyboardButton("150%")
markupCompletion.add(fButton1, fButton2, fButton3, fButton4, fButton5, fButton6)

def is_known_username(username):
	known_usernames = ["CHAT_ID"] #chat id needs to be int, I use string here as a placeholder
	return username in known_usernames

def private_access():
	def deco_restrict(f):
		@wraps(f)
		async def f_restrict(message, *args, **kwargs):
			username1 = message.chat.id
			if is_known_username(username1):
				return await f(message, *args, **kwargs)
			else:
				await bot.send_message(message.chat.id, "Who are you? Keep on walking...")
		return f_restrict
	return deco_restrict

@bot.message_handler(commands=["start", "set"])
@private_access()
async def send_welcome(message: Message):
	await bot.send_message(message.chat.id, "Hey! Which interval suits you better?", reply_markup=markupDuration)

@bot.message_handler(commands=['unset'])
@private_access()
async def unset_timer(message: Message):
	await bot.send_message(message.chat.id, "Sure, see you later then.")
	schedule.clear(message.chat.id)
	resultsRow.clear()

@bot.message_handler(commands=['stats'])
@private_access()
async def getStats(message: Message):
	statsStr = ""
	statsValues = sheet.get_all_values()
	for i in range(1, len(statsValues)):
		statsStr += str(i)
		statsStr += ". "
		for j in range(4):
			statsStr += f"{statsValues[i][j]}, "
		statsStr = statsStr[:-2]
		statsStr += "\n"
	await bot.send_message(message.chat.id, statsStr)

async def timeIsUp(chatId, duration):
	await bot.send_message(chatId, "Time is up. How many times have you been distracted during the last {}utes?".format(duration), reply_markup=markupFocus)
	schedule.clear(chatId)
	timeAndDateNow = str(dt.datetime.now())
	resultsRow.append(timeAndDateNow)
	resultsRow.append(duration)

@bot.message_handler()
@private_access()
async def optionsOfTime(message: Message):
	if message.text == tw:
		schedule.every(20).minutes.do(timeIsUp, message.chat.id, tw).tag(message.chat.id)
	if message.text == th:
		schedule.every(30).minutes.do(timeIsUp, message.chat.id, th).tag(message.chat.id)
	if message.text == fo:
		schedule.every(40).minutes.do(timeIsUp, message.chat.id, fo).tag(message.chat.id)
	if message.text in focusMarks:
		await bot.send_message(message.chat.id, "How would you rate the completion of the task?", reply_markup=markupCompletion)
		resultsRow.append(message.text)
	if message.text in completionMarks:
		await bot.send_message(message.chat.id, "Thanks!")
		resultsRow.append(message.text)
		numCycles = int(sheet.cell(2, 6).value)
		for number in range(4):
			sheet.update_cell(numCycles + 2, number + 1, resultsRow[number])
		sheet.update_cell(2, 6, numCycles + 1)
		resultsRow.clear()

async def scheduler():
	while True:
		await schedule.run_pending()
		await asyncio.sleep(1)

async def main():
	await asyncio.gather(bot.infinity_polling(), scheduler())

if __name__ == '__main__':
	asyncio.run(main())