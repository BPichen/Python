import tweepy, telebot, time, threading, TelegramConstants

twitter_bearer_token = TelegramConstants.twitter_bearer_token
bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
bot_chat_id = TelegramConstants.bot_chat_id

bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id

bot = telebot.TeleBot(token=bot_token)
auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)

def connectStream():
        try:
            stream.filter()
        except:
            connectStream()
            print("Error connecting. Retrying...")

class MyStream(tweepy.StreamingClient):
    def on_connect(self):
        bot.send_message(bot_admin_chat_id, "Connected!")
        print("Connected")
        return True
    
    def on_tweet(self, tweet):
        tweet = api.get_status(tweet.id)
        if('RT' not in tweet.text[:2]): 
            if(tweet.in_reply_to_status_id is not None):
                lead = 'New Reply!'
            else:
                lead = "New Tweet!"
            try:       
                bot_message = lead + ' (@' + tweet.user.screen_name + ')\n' + tweet.text + '\n\nhttps://twitter.com/' + tweet.user.screen_name + '/status/' + str(tweet.id)
                bot.send_message(bot_chat_id, bot_message)
            except Exception as e:
                print(e)
                time.sleep(0.5)
        time.sleep(0.5)
    
    def on_connection_error(status):
        bot.send_message(bot_admin_chat_id, "Connection error. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_closed(status):
        bot.send_message(bot_admin_chat_id, "Connection closed. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_exception(status):
        bot.send_message(bot_admin_chat_id, "Exception received. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_disconnect(status):
        bot.send_message(bot_admin_chat_id, "Stream disconnected. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_error(status):
        bot.send_message(bot_admin_chat_id, "Error received. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_limit(status):
        bot.send_message(bot_admin_chat_id, "Twitter limit. Reconnecting in 60 seconds")
        print(status.text)
        time.sleep(60)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

@bot.message_handler(commands=['add'])
def addaccounts(message):
    if(checkadmin(message)):
        account = ((message.text).replace('/add ', ''))
        rule = "from:" + account
        stream.add_rules(tweepy.StreamRule(rule))
        bot_message = '@' + account + ' has been added to the shill list!'
        bot.send_message(bot_chat_id, bot_message)
        bot.reply_to(message, "Account added!") 

@bot.message_handler(commands=['addaccounts'])
def removeaccounts(message):
    if(checkadmin(message)):
        accounts = ['jimcramer', 'elonmusk', 'jack', 'cz_binance','1goonrich', 'mattwallace888', 'bitboy_crypto', 'prothedoge', 'WatcherGuru', 'cryptogodjohn']

        for account in accounts:
            rule = "from:" + account
            stream.add_rules(tweepy.StreamRule(rule))
        bot.reply_to(message, "Default accounts added!")   

@bot.message_handler(commands=['resetaccounts'])
def resettaccounts(message):
    if(checkadmin(message)):
        rules = stream.get_rules()     
        for rule in rules:
            stream.delete_rules(rule)
        bot.reply_to(message, "Accounts cleared!")

@bot.message_handler(commands=['accounts'])
def accounts(message):
    accounts = stream.get_rules()
    accounts_array = []
    if(accounts.data is None):       
            bot.reply_to(message, "There are currently no accounts added. To add an account, type /add ")                                      
    else:
        for x in range(len(accounts.data)):
            accounts_array.append(accounts.data[x].value)
        s = '\n'.join(str(x) for x in accounts_array) 
        text = ['Current accounts: ', s]
        sf = '\n\n'.join(str(x) for x in text)

        bot.reply_to(message, sf)  

def checkadmin(message):
    admins = bot.get_chat_administrators(TelegramConstants.bot_admin_chat_id)
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array):
        return True
    else:
        bot.reply_to(message, "You need to be an admin to do this.")
        return False

def main():
    while True:
        try:
            bot.polling(True)
        except Exception:
            time.sleep(5) 

if __name__ == "__main__":  
    stream = MyStream(bearer_token=TelegramConstants.twitter_bearer_token)
    polling = threading.Thread(target=main)
    connect_stream = threading.Thread(target=connectStream)
    try:       
        polling.start()
        connect_stream.start()        
    except:
        print("Exception received")