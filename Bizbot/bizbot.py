import telebot, json, time, threading, TelegramConstants, requests
from telegram import ParseMode

bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
bot_chat_id = TelegramConstants.bot_chat_id
read_file = TelegramConstants.read_file

bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id

bot = telebot.TeleBot(token=bot_token)

@bot.message_handler(commands=['start'])
def biz(message):
    bot_message = "Add this bot to your chat, make it an admin, and use command /bizbot to get started."
    bot.reply_to(message, bot_message)

@bot.message_handler(commands=['biz'])
def biz(message):
    biz_search = threading.Thread(target=bizThread, args=[message])
    biz_search.start() 

@bot.message_handler(commands=['bizfilters'])
def filters(message):
    biz_search = threading.Thread(target=filters, args=[message])
    biz_search.start() 

@bot.message_handler(commands=['addbizfilter'])
def addbizfilter(message):
    biz_search = threading.Thread(target=addfilter, args=[message])
    biz_search.start() 

@bot.message_handler(commands=['removebizfilter'])
def removebizfilter(message):
    biz_search = threading.Thread(target=removefilter, args=[message])
    biz_search.start() 

@bot.message_handler(commands=['bizbot'])
def bizbot(message):
    bot_message = "BizBot commands:\n\n/biz - searches biz\n/bizfilters - displays added filters\n/addbizfilter xxxx - adds a custom biz filter\n/removebizfilter xxxx = removes a custom biz filter"
    bot.reply_to(message, bot_message)

def bizThread(message):
    bot.reply_to(message, 'Filtering biz threads, one moment please ser')
    webURL = 'https://a.4cdn.org/biz/catalog.json'
    r = requests.get(webURL).json()

    i=0
    threadArray = []
    
    for index in r: 
        for threads in r[i]['threads']:  
            webURL = 'https://a.4cdn.org/biz/thread/' + str(threads['no']) + '.json'
            t = requests.get(webURL).json()
            try:
                group_list = loaddata()
                threadFound = False
                for variable in group_list['groups'][str(message.chat.id)]:                               
                    for posts in t['posts']:
                        if variable in posts['com'].lower():
                            s = 'https://dereferer.me/?https%3A//boards.4channel.org/biz/thread/' + str(threads['no'])
                            s = "<a href='" + s + "'>" + str(threads['no']) + "</a>"
                            threadArray.append(s)  
                            threadFound = True
                            break
                    if threadFound:
                        break         
            except KeyError:
                  pass
        i = i + 1

    if not threadArray:
        s = 'No active threads'
    else:     
        s = '\n'.join(str(x) for x in threadArray)   
    text = ['Current active threads: ', s]
    sf = '\n\n'.join(str(x) for x in text)
    bot.reply_to(message, sf, parse_mode=ParseMode.HTML)

def filters(message):   
    try:
        group_list = loaddata()
        for variable in group_list['groups'][str(message.chat.id)]:                               
            s = '\n'.join(str(x) for x in group_list['groups'][str(message.chat.id)]) 
        text = ['Current filters: ', s]
        bot_message = '\n\n'.join(str(x) for x in text)
        bot.reply_to(message, bot_message)
    except:
        bot.reply_to(message, "You do not have any active filters. Please use /addbizfilter to add a new filter.")


def addfilter(message):
    if(checkadmin(message)):
        filter = ((message.text).replace('/addbizfilter ', '')) 
        group_list = loaddata()
        if(str(message.chat.id) in group_list['groups']):
            group_list['groups'][str(message.chat.id)].append(filter)           
        else:
            group_list['groups'][str(message.chat.id)] = [filter]
        savedata(group_list)
        bot.reply_to(message, "Filter added!")
    else:
        bot.reply_to(message, "You need to be an admin to do this.")

def removefilter(message):
    if(checkadmin(message)):
        filter = ((message.text).replace('/removebizfilter ', '')) 
        group_list = loaddata()
        try:
            group_list['groups'][str(message.chat.id)].remove(filter)
            bot.reply_to(message, "Filter removed!")
            savedata(group_list)
        except:
            bot.reply_to(message, "Filter does not exist")
    else:
        bot.reply_to(message, "You need to be an admin to do this.")
        

def checkadmin(message):
    admins = bot.get_chat_administrators(message.chat.id)
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array):
        return True
    else:
        bot.reply_to(message, "You need to be an admin to do this.")
        return False

def savedata(data):
    with open(read_file, 'w') as f:
        json.dump(data, f) 

def loaddata():
    file = open(read_file)
    data = json.load(file)
    return(data)

def main():
    while True:
        try:
            bot.polling(True)
        except Exception:
            time.sleep(5) 

if __name__ == "__main__":  
    polling = threading.Thread(target=main)
    try:       
        polling.start()      
    except:
        print("Exception received")