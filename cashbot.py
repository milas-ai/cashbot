import telebot, json, os, re, sys
from datetime import datetime

API_TOKEN = "<BOT-TOKEN>"

data_json = {}

bot = telebot.TeleBot(API_TOKEN)

def writeJson(data_json):
    with open("data.json", "w") as json_file:
        json.dump(data_json, json_file, ensure_ascii=False)

def loadJson():
    global data_json
    try:
        with open("data.json") as json_file:
            data_json = json.load(json_file)
    except FileNotFoundError:
        print("File data.json not found!")

# handle the "/start" command
@bot.message_handler(commands=["start"])
def command_start(message):
    loadJson()
    bot.send_message(message.chat.id, "Bem vinde ao <Bot-name>)!\nPosso te ajudar a registrar suas despesas do mês, precisando de qualquer ajuda basta digitar /help")

# handle the "/help" command
@bot.message_handler(commands=["help"])
def command_help(message):
    bot.send_message(message.chat.id, "Para anotar uma nova despesa é só me mandar:\nR$0.00 - descrição\n\nSe quiser ver seu histórico de despesas utilize /resume\nSe quiser resetar o histórico de despesas utilize /reset\nSe quiser calcular a soma das despesas utilize /boleto")

# handle the "/resume" command
@bot.message_handler(commands=["resume"])
def command_resume(message):
    global data_json
    loadJson()
    Id = message.chat.id
    if (str(Id) in data_json):
        ret = "*Histórico:*\n"
        for regist in data_json[str(Id)]:
            ret = ret + regist.replace(","," / R$",1).replace(","," / ") + "\n"
    else:
        ret = "Opa, parece que você não tem gastos anotados!"
    bot.send_message(Id, ret, "Markdown")

# handle the "/reset" command
@bot.message_handler(commands=["reset"])
def command_reset(message):
    global data_json
    loadJson()
    ret = ""
    if (str(message.chat.id) in data_json):
        del data_json[str(message.chat.id)]
        writeJson(data_json)
        ret = "Histórico limpinho!"
    else:
        ret = "Opa, parece que você não tem gastos anotados!"
    bot.send_message(message.chat.id, ret)

# handle the "/boleto" command
@bot.message_handler(commands=["boleto"])
def command_boleto(message):
    global data_json
    loadJson()
    Id = message.chat.id
    if (str(Id) in data_json):
        ret = "*Seu total é:*\nR$"
        tot = 0
        for regist in data_json[str(Id)]:
            content = regist.split(",")
            tot = tot + float(content[1])
        ret = ret + str(tot)
    else:
        ret = "Opa, parece que você não tem gastos anotados!"
    bot.send_message(Id, ret, "Markdown")


# handle normal messages
@bot.message_handler(func=lambda message: True)
def new_message(message):
    if re.match("^R?\$[0-9][0-9]*\.?[0-9]* - ", message.text):
        global data_json
        loadJson()
        content = message.text.split(" - ")
        amountText = content[0].replace("R","").replace("$","")
        descText = content[1]
        dateText = datetime.today().strftime("%d/%m/%y"+" - "+"%H:%M")
        writeJson(addToHistory(message.chat.id, "{},{},{}".format(dateText,amountText,descText)))
        bot.send_message(message.chat.id, "Anotado! R${} em {}".format(amountText,dateText))
    else:
        bot.send_message(message.chat.id, "Alguma nova despesa? Atente-se para a formatação da mensagem, se precisar de ajuda digite /help")

def addToHistory(chatId, array):
    global data_json
    if not (str(chatId) in data_json):
        data_json[str(chatId)] = []
    data_json[str(chatId)].append(array)
    return data_json

bot.infinity_polling()
