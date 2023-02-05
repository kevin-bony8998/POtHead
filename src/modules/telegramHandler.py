import telebot
import requests
from telebot import types
from googleSheetHandler import googleSheetUpdater

BOT_TOKEN = "5914370761:AAFhHez9-JBphU1cNz4WQ-uBDonTduUDm_k"

bot = telebot.TeleBot(BOT_TOKEN)

customInputRequired = False
ticketDetailEntry = False
POTicketNumber = ""
POTicketDescription = ""
POTicketStatus = ""
userName = ""

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

@bot.message_handler(func=lambda call: (customInputRequired and not ticketDetailEntry))
def POTicketHandler(message):
    global customInputRequired, POTicketNumber
    print("[telegramHandler][POTicketHandler] Entered the POTicketHandler function! Here is the message value:", message)
    customInputRequired = False
    if message.text.isdigit():
        customKeyBoardOptions = {
            "chatId": message.chat.id,
            "message": f'Got the ticket number: {message.text} and it looks great! Is this the right ticket number?',
            "options": [
                [
                    {
                        "text": "Yes",
                        "callback_data": "ticketConfirmed"
                    },
                    {
                        "text": "No",
                        "callback_data": "ticketReenter"
                    }
                ]
            ]
        }
        POTicketNumber = message.text
        print("[telegramHandler][POTicketHandler] This is the chat id that we are sending: ",message.chat.id)
        userOption = telSendInlinebutton(customKeyBoardOptions)
        print("[telegramHandler][POTicketHandler] Status of user menu selection: ", userOption)
    else:
        errorReply = "Oops! Looks like there might have been some non-digits that snuck in! Please enter just the ticket number!"
        bot.reply_to(message, errorReply)

@bot.message_handler(func=lambda call: (customInputRequired and ticketDetailEntry))
def POTicketDescriptionHandler(message):
    global customInputRequired, ticketDetailEntry,POTicketDescription
    print("[telegramHandler][POTicketDescriptionHandler] Entered the POTicketDescriptionHandler function! Here is the message value:", message)
    acknowlegmentReply = "Got the description!"
    POTicketDescription = message.text
    bot.reply_to(message, acknowlegmentReply)
    customInputRequired = False
    ticketDetailEntry = False
    print("[telegramHandler][POTicketDescriptionHandler] Final PO ticket number and description:", POTicketNumber, POTicketDescription)
    customKeyBoardOptions = {
        "chatId": message.chat.id,
        "message": "Finally, what's the status of the ticket?",
        "options": [
            [
                {
                    "text": "To Do",
                    "callback_data": "To Do"
                },
                {
                    "text": "In Progress",
                    "callback_data": "In Progress"
                },
                {
                    "text": "Closed",
                    "callback_data": "Closed"
                }
            ]
        ]
    }
    print("[telegramHandler][sendWelcome] This is the chat id that we are sending: ",message.chat.id)
    userOption = telSendInlinebutton(customKeyBoardOptions)
    print("[telegramHandler][sendWelcome] Status of user menu selection: ", userOption)

def updateTicketStatus(status, chatId):
    global POTicketStatus
    print("[telegramHandler][updateTicketStatus] Entered the ticket status handler! Here is the complete data: ", status, chatId)
    acknowlegmentReply = "Got the ticket staus! I'll handle the rest! Thank you for your time!"
    POTicketStatus = status
    bot.send_message(chatId, acknowlegmentReply)
    googleSheetUpdater(POTicketNumber, POTicketDescription, POTicketStatus, userName)

def startUserFlow(chatId):
    global customInputRequired
    print("[telegramHandler][startUserFlow] Received a start user flow message from the user! Here is it's chatId:", chatId)
    bot.send_message(chatId, 'Please enter the PO ticket number!')
    customInputRequired = True
    #Code for a custom reply keyboard
    # markup = types.ReplyKeyboardMarkup(row_width=2)
    # itembtn1 = types.KeyboardButton('a')
    # itembtn2 = types.KeyboardButton('v')
    # itembtn3 = types.KeyboardButton('d')
    # markup.add(itembtn1, itembtn2, itembtn3)
    # bot.send_message(chatId, "Choose one letter:", reply_markup=markup)

def getTicketDetails(chatId):
    global customInputRequired, ticketDetailEntry
    print("[telegramHandler][getTicketDetails] Received a confirmation on ticket number from the user! Here is it's chatId:", chatId)
    bot.send_message(chatId, 'Please enter the PO ticket description!')
    customInputRequired = True
    ticketDetailEntry = True

def endUserFlow(chatId):
    bot.send_message(chatId, 'Thanks for talking to me!')

@bot.callback_query_handler(func=lambda call: True)
def handleQuery(userOptionData):
    global userName
    print("[telegramHandler][handleQuery] Entered the callBackQueryHandler! Here is the complete data: ", userOptionData)
    print("[telegramHandler][handleQuery] Entered the callBackQueryHandler! Here is the selected option: ", userOptionData.data)
    userOption = userOptionData.data
    if (userOption == "userFlowStart") or (userOption == "ticketReenter"): 
        startUserFlow(userOptionData.message.chat.id)
    elif userOption == "ticketConfirmed":
        getTicketDetails(userOptionData.message.chat.id)
    elif (userOption == "To Do") or (userOption == "In Progress") or (userOption == "Closed"):
        userName = userOptionData.message.chat.first_name
        updateTicketStatus(userOption, userOptionData.message.chat.id)
    else: 
        endUserFlow(userOptionData.message.chat.id)

@bot.message_handler(func=lambda call: (not customInputRequired))
def errorReplyHandler(message):
    print("[telegramHandler][errorReplyHandler] Entered the echo all function! Here is the message value:", message)
    errorReply = "Oops! I didn't get that! To start a PO ticket registration/updation process, try typing '/hello','/start' or (my personal favourite) '/wassaapppp'"
    bot.reply_to(message, errorReply)

bot.infinity_polling()