# concentration_bot
Chatbot for Telegram messenger, which sets a timer, asks about distractions and success of a task and uploads this info to a google spreadsheet.

I used:
1. AsyncTelebot and a couple of other classes from pyTelegramBotAPI package for connecting to Telegram API
2. wraps from functools for creating private access mode (idea is not mine, I used code from stackoverflow user "S.D." (https://stackoverflow.com/questions/55437732/how-to-restrict-the-acess-to-a-few-users-in-pytelegrambotapi/68229442#68229442)
3. aioschedule for creating a timer
4. asyncio for gathering two tasks - bot.infinity_polling and scheduler
5. google.oauth2 and gspread for connecting to a google spreadsheet

This bot has three commands: set, unset and stats. When you press "set", you get 3 options of concentration period: 20, 30 and 40 minutes. When the time is up, you get notification and then could rate your focus and completion of the task. This info uploads to Google spreadsheet. "unset" - discards a timer. "stats" - shows you info from a spreadsheet in a compact style (for a message).
