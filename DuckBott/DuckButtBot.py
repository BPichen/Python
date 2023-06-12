import tweepy, telebot, json, time, threading, TelegramConstants, requests, random
from telegram import ParseMode

twitter_bearer_token = TelegramConstants.twitter_bearer_token
bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
bot_chat_id = TelegramConstants.bot_chat_id
read_file = TelegramConstants.read_file

bot = telebot.TeleBot(token=bot_token)
auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)

searchArray = ['dubu', 'duckbutt', ' dao ']

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
            try:  
                shill_post = threading.Thread(target=shillPost, args=[tweet.id])
                shill_post.start()     
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

def shillPost(tweet):
    message_id = 0
    times_looped = 0
    while True:
        try:
            tweet_data = api.get_status(tweet)
            duckbot_level = loaddata()  
            likes = int(duckbot_level['duckbot_level'] * 5 / 2)
            retweets = int(duckbot_level['duckbot_level'] / 2) + 1
        except Exception as e:
            print(e)
            break

        if (tweet_data.favorite_count >= likes) and (tweet_data.retweet_count >= retweets):
            duckbot_level['duckbot_level'] += 1
            savedata(duckbot_level)
            bot.delete_message(bot_chat_id, message_id)
            bot_message ='⭐️ DuckBott level up! DuckBott is now level ' + str(duckbot_level['duckbot_level']) + '! ⭐️\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) +'\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '   Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)                
            bot.send_message(bot_chat_id, bot_message)
            break

        else:
            bot_message = '🟩 DuckBott level ' + str(duckbot_level['duckbot_level']) + '! Like and retweet to level up! 🟩\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) + '\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '  Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)
            if message_id == 0:
                message_id = bot.send_message(bot_chat_id, bot_message).message_id
            else:
                bot.delete_message(bot_chat_id, message_id)
                message_id = bot.send_message(bot_chat_id, bot_message).message_id

        if times_looped > 4:
            bot.delete_message(bot_chat_id, message_id)
            bot_message = '🟥 Tweet goal not achieved. Try harder next time! 🟥\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) + '\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '  Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)
            bot.send_message(bot_chat_id, bot_message)
            break

        times_looped = times_looped + 1

        time.sleep(60)

@bot.message_handler(commands=['quack'])
def quack(message): 
   increaseQuacks(message, 1, "quack") 

@bot.message_handler(commands=['unquack'])
def unquack(message): 
    decreaseQuacks(message, 1, "unquack")

@bot.message_handler(commands=['superquack'])
def superquack(message): 
    if(checklevel(message, 50)):
        increaseQuacks(message, 2, "superquack") 

@bot.message_handler(commands=['sneakaquack'])
def sneakaquack(message):
    if(checklevel(message, 50)):
        decreaseQuacks(message, 2, "sneakaquack")

@bot.message_handler(commands=['megaquack'])
def superquack(message): 
    if(checklevel(message, 100)):
        increaseQuacks(message, 3, "superquack") 

@bot.message_handler(commands=['monitor'])
def monitor(message): 
   if(checkadmin(message)):
       if(message.reply_to_message is None):
            user = ((message.text).replace('/monitor ', ''))
            bot_message = "Okay, currently monitoring " + user
            bot.send_message(message.chat.id, bot_message)                   
       else:
            user = message.reply_to_message.from_user.username
            bot_message = "Okay, currently monitoring @" + user
            bot.send_message(message.chat.id, bot_message)

def increaseQuacks(message, quacks, function):
    message_id = message.message_id
    reply = message.reply_to_message
    reply_id = message.reply_to_message.from_user.id
    sender_id = message.from_user.id
    sender_first_name = message.from_user.first_name
    first_name = message.reply_to_message.from_user.first_name

    if reply_id == sender_id:
        bot.reply_to(message, "You can't " + function + " yourself!")
        return
    
    data = loaddata() 
    
    if(str(reply_id) in data['users']):      
        data['users'][str(reply_id)]['times_quacked'] += quacks
        data['users'][str(reply_id)]['user_name'] = first_name
        savedata(data)

    else:
        data['users'][str(reply_id)] = {"user_name": first_name, "times_quacked": 1, "times_quackee": 0}
        savedata(data)

    if(str(sender_id) in data['users']):
        data['users'][str(sender_id)]['times_quackee'] += quacks
        data['users'][str(sender_id)]['user_name'] = first_name
        savedata(data)
    
    else:
        data['users'][str(sender_id)] = {"user_name": sender_first_name, "times_quacked": 0, "times_quackee": 1}
        savedata(data)

    bot.delete_message(message.chat.id, message_id)
        
    bot_message = (sender_first_name + ' has ' + function + 'ed ' + first_name + ' to level ' + str(data['users'][str(reply_id)]['times_quacked']) + '!')
    bot.reply_to(reply, bot_message) 


def decreaseQuacks(message, quacks, function):
    message_id = message.message_id
    reply = message.reply_to_message
    reply_id = message.reply_to_message.from_user.id
    sender_id = message.from_user.id
    sender_first_name = message.from_user.first_name
    first_name = message.reply_to_message.from_user.first_name

    if(reply_id == sender_id):
        bot.reply_to(message, "You can't " + function + " yourself!")
        return
  
    data = loaddata()  

    if(str(reply_id) in data['users']):      
        data['users'][str(reply_id)]['times_quacked'] -= quacks
        data['users'][str(reply_id)]['user_name'] = first_name
        savedata(data)

    else:
        data['users'][str(reply_id)] = {"user_name": first_name, "times_quacked": -1, "times_quackee": 0}
        savedata(data)
    
    bot.delete_message(message.chat.id, message_id)
        
    bot_message = (sender_first_name + ' has ' + function + "ed " + first_name + ' to level ' + str(data['users'][str(reply_id)]['times_quacked']) + '!')
    bot.reply_to(reply, bot_message)


@bot.message_handler(commands=['quacklist'])
def quacklist(message):
    quack_list = threading.Thread(target=quackers, args=[message])
    quack_list.start()  

def quackers(message):
    users = loaddata()
    tmp_scores = {}
    for user in users['users']:
        if users['users'][user]['user_name'] in tmp_scores:
            key = users['users'][user]['user_name'] + '(' + user + ')'
            tmp_scores[key] = users['users'][user]['times_quacked']
        else:
            tmp_scores[users['users'][user]['user_name']] = users['users'][user]['times_quacked']
    
    formatted_scores = sorted(tmp_scores.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)[:10]
    
    bot_message = "Top 10 quackheads:\n\n"
    s = '*\n'.join(str(x) for x in formatted_scores) 
    bot_message += s
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("',", ': ')
    bot_message = bot_message.replace(")*", '')
    bot_message = bot_message[:-1] + ''
    bot.reply_to(message, bot_message)

@bot.message_handler(commands=['uglyducklings'])
def antiquacklist(message):
    quack_list = threading.Thread(target=antiquackers, args=[message])
    quack_list.start()  

def antiquackers(message):
    users = loaddata()
    tmp_scores = {}
    for user in users['users']:
        if users['users'][user]['user_name'] in tmp_scores:
            key = users['users'][user]['user_name'] + '(' + user + ')'
            tmp_scores[key] = users['users'][user]['times_quacked']
        else:
            tmp_scores[users['users'][user]['user_name']] = users['users'][user]['times_quacked']       
    
    formatted_scores = sorted(tmp_scores.items(), key=lambda kv:(kv[1], kv[0]), reverse=False)[:10]
    
    bot_message = "Top 10 ugly ducklings:\n\n"
    s = '*\n'.join(str(x) for x in formatted_scores) 
    bot_message += s
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("',", ': ')
    bot_message = bot_message.replace(")*", '')
    bot_message = bot_message[:-1] + ''
    bot.reply_to(message, bot_message)

@bot.message_handler(commands=['quackdealers'])
def quackdealers(message):
    quack_list = threading.Thread(target=quackees, args=[message])
    quack_list.start()  

def quackees(message):
    users = loaddata()
    tmp_scores = {}
    for user in users['users']:

        if users['users'][user]['user_name'] in tmp_scores:
            key = users['users'][user]['user_name'] + '(' + user + ')'
            tmp_scores[key] = users['users'][user]['times_quackee']
        else:
            tmp_scores[users['users'][user]['user_name']] = users['users'][user]['times_quackee'] 
        
    
    formatted_scores = sorted(tmp_scores.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)[:10]
    
    bot_message = "Top 10 quack dealers:\n\n"
    s = '*\n'.join(str(x) for x in formatted_scores) 
    bot_message += s
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("',", ': ')
    bot_message = bot_message.replace(")*", '')
    bot_message = bot_message[:-1] + ''
    bot.reply_to(message, bot_message)

@bot.message_handler(commands=['getchatid'])
def getchatid(message):
    bot.reply_to(message, message.chat.id)

@bot.message_handler(commands=['biz'])
def biz(message):
    biz_search = threading.Thread(target=bizThread, args=[message])
    biz_search.start() 

def bizThread(message):
    message_id = bot.reply_to(message, 'Checking for duck based biz threads, one moment please.').message_id
    webURL = 'https://a.4cdn.org/biz/catalog.json'
    r = requests.get(webURL).json()

    i=0
    threadArray = []
    
    for index in r: 
        for threads in r[i]['threads']:  
            webURL = 'https://a.4cdn.org/biz/thread/' + str(threads['no']) + '.json'
            t = requests.get(webURL).json()
            try:
                threadFound = False
                for variable in searchArray:                               
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
    bot.delete_message(bot_chat_id, message_id)
    bot.reply_to(message, sf, parse_mode=ParseMode.HTML)

def checkadmin(message):
    admins = bot.get_chat_administrators(bot_chat_id)
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array):
        return True
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.reply_to(message, "You need to be an admin to do this.")        
        return False

def checklevel(message, levelRequirement):
    data = loaddata()
    if(data['users'][str(message.from_user.id)]['times_quacked'] < levelRequirement):
        bot.reply_to(message, "You need to be level " + str(levelRequirement) + " to do that!")
        return False
    return True

def savedata(data):
    with open(read_file, 'w') as f:
        json.dump(data, f) 

def loaddata():
    file = open(read_file)
    data = json.load(file)
    return(data)

def autoQuack():
    message_id = 0
    while True:
        if(message_id != 0):
            bot.delete_message(bot_chat_id, message_id)
        data = loaddata()
        user_id = random.choice(tuple(data['users']))
        
        data['users'][str(user_id)]['times_quacked'] += 1
        savedata(data)

        message_id = bot.send_message(bot_chat_id, 'DuckBott has randomly quacked ' + data['users'][str(user_id)]['user_name'] + ' to level ' + str(data['users'][str(user_id)]['times_quacked']) + '!').message_id
        time.sleep(7200)

def timedmessages():
    messages = loaddata()['duck_quotes']
    while True:
        x = random.randint(0, len(messages) - 1)
        bot.send_message(bot_chat_id, messages[x]['quote'])    
        time.sleep(21600)
    
@bot.message_handler(commands=['addaccount'])
def addaccount(message):
    if(checkadmin(message)):
        accounts = ['DuckButtCrypto']

        for account in accounts:
            rule = "from:" + account
            stream.add_rules(tweepy.StreamRule(rule))
        bot.reply_to(message, "Default account added!") 

def main():
    while True:
        try:
            bot.polling(True)
        except Exception:
            time.sleep(5) 

if __name__ == "__main__":  
    stream = MyStream(bearer_token=TelegramConstants.twitter_bearer_token)
    polling = threading.Thread(target=main)
    timed_messages = threading.Thread(target=timedmessages)
    autoquack = threading.Thread(target=autoQuack)
    connect_stream = threading.Thread(target=connectStream)
    try:       
        polling.start()
        timed_messages.start()
        autoquack.start()
        connect_stream.start()        
    except:
        print("Exception received")