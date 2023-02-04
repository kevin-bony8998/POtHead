import telebot
import requests

BOT_TOKEN = "5914370761:AAFhHez9-JBphU1cNz4WQ-uBDonTduUDm_k"

bot = telebot.TeleBot(BOT_TOKEN)

def telSendInlinebutton(customKeyBoardOptions):
    print("[telegramHandler][telSendInlinebutton] Entered the custom option keyboard function! Here are the custom keyboard options: ", customKeyBoardOptions)
    print("[telegramHandler][telSendInlinebutton] Entered the custom option keyboard function! Here is the chat id: ", customKeyBoardOptions["chatId"])
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
 
    payload = {
        'chat_id': customKeyBoardOptions["chatId"],
        'text': customKeyBoardOptions["message"],
        'reply_markup': {
            "inline_keyboard": customKeyBoardOptions["options"]
        }
    }
    r = requests.post(url, json=payload)
    return r

@bot.message_handler(commands=['start', 'hello', 'wassaapppp'])
def sendWelcome(message):
    print("[telegramHandler][sendWelcome] Received a start message from the user! Here it is")
    customKeyBoardOptions = {
        "chatId": message.chat.id,
        "message": "Hello, do you have a PO ticket you'd like to register/update with me?",
        "options": [
            [
                {
                    "text": "Yes",
                    "callback_data": "userFlowStart"
                },
                {
                    "text": "No",
                    "callback_data": "userFlowEnd"
                }
            ]
        ]
    }
    print("[telegramHandler][sendWelcome] This is the chat id that we are sending: ",message.chat.id)
    userOption = telSendInlinebutton(customKeyBoardOptions)
    print("[telegramHandler][sendWelcome] Status of user menu selection: ", userOption)

def startUserFlow(chatId):
    print("[telegramHandler][startUserFlow] Received a start message from the user! Here is it's chatId:", chatId)
    bot.send_message(chatId, 'Please enter the PO ticket number!')

def endUserFlow(chatId):
    bot.send_message(chatId, 'Thanks for talking to me!')

@bot.callback_query_handler(func=lambda call: True)
def handleQuery(userOptionData):
    print("[telegramHandler][handleQuery] Entered the callBackQueryHandler! Here is the complete data: ", userOptionData)
    print("[telegramHandler][handleQuery] Entered the callBackQueryHandler! Here is the selected option: ", userOptionData.data)
    userOption = userOptionData.data
    if (userOption == "userFlowStart"): 
        startUserFlow(userOptionData.message.chat.id)
    else: 
        endUserFlow(userOptionData.message.chat.id)

@bot.message_handler(func=lambda msg: True)
def errorReplyHandler(message):
    print("[telegramHandler][errorReplyHandler] Entered the echo all function! Here is the message value:", message)
    errorReply = "Oops! I didn't get that! To start a PO ticket process, try typing '/hello','/start' or (my personal favourite) '/wassaapppp'"
    bot.reply_to(message, errorReply)
    

bot.infinity_polling()