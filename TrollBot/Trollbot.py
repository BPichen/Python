import tweepy, telebot, json, time, threading, TelegramConstants, requests, random, re
from telegram import ParseMode
from PIL import Image

twitter_bearer_token = TelegramConstants.twitter_bearer_token
twitter_consumer_token = TelegramConstants.twitter_consumer_token
twitter_consumer_secret = TelegramConstants.twitter_consumer_secret
bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
bot_chat_id = TelegramConstants.bot_chat_id
read_file = TelegramConstants.read_file

bot = telebot.TeleBot(token=bot_token)
auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)

pic_generating = False

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
            if tweet.in_reply_to_status_id is not None: 
                return
            else:
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
            trollbot_level = loaddata()  
            likes = int(trollbot_level['trollbot_level'] * 3 / 2)
            retweets = int(trollbot_level['trollbot_level'] / 2) + 1
        except Exception as e:
            print(e)
            break

        if (tweet_data.favorite_count >= likes) and (tweet_data.retweet_count >= retweets):
            trollbot_level['trollbot_level'] += 1
            savedata(trollbot_level)
            bot.delete_message(bot_chat_id, message_id)
            bot_message ='⭐️ Trollbot getting stronger? Trollbot is now level ' + str(trollbot_level['trollbot_level']) + '! ⭐️\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) +'\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '   Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)                
            bot.send_message(bot_chat_id, bot_message)
            break

        else:
            bot_message = '🟩 Trollbot level ' + str(trollbot_level['trollbot_level']) + '! Troll the post! 🟩\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) + '\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '  Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)
            if message_id == 0:
                message_id = bot.send_message(bot_chat_id, bot_message).message_id
            else:
                bot.delete_message(bot_chat_id, message_id)
                message_id = bot.send_message(bot_chat_id, bot_message).message_id

        if times_looped > 4:
            bot.delete_message(bot_chat_id, message_id)
            bot_message = '🟥 Probem, not trying hard enough? Try harder next time 🟥\n\nhttps://twitter.com/' + tweet_data.user.screen_name + '/status/' + str(tweet_data.id) + '\n\nLike goal: ' + str(tweet_data.favorite_count) + '/' + str(likes) + '  Retweet goal: ' + str(tweet_data.retweet_count) + '/' + str(retweets)
            bot.send_message(bot_chat_id, bot_message)
            break

        times_looped = times_looped + 1

        time.sleep(60)
    
@bot.message_handler(commands=['troll'])
def quack(message): 
    increaseScore(message, 1, "troll") 

@bot.message_handler(commands=['fuuu'])
def unquack(message): 
    decreaseScore(message, 1, "fuuu")

def increaseScore(message, score, function):
    reply = message.reply_to_message

    try:
        reply.photo[-1].file_id
        reply_id = message.reply_to_message.from_user.id
        sender_id = message.from_user.id
        sender_first_name = message.from_user.first_name
        first_name = message.reply_to_message.from_user.first_name

        if reply_id == sender_id:
            bot.reply_to(message, "You can't " + function + " yourself!")
            return
        
        data = loaddata() 
        
        if(str(reply_id) in data['users']):      
            data['users'][str(reply_id)]['times_trolled'] += score
            data['users'][str(reply_id)]['user_name'] = first_name
            savedata(data)

        else:
            data['users'][str(reply_id)] = {"user_name": first_name, "times_trolled": 1, "times_trollee": 0}
            savedata(data)

        if(str(sender_id) in data['users']):
            data['users'][str(sender_id)]['times_trollee'] += score
            data['users'][str(sender_id)]['user_name'] = sender_first_name
            savedata(data)
        
        else:
            data['users'][str(sender_id)] = {"user_name": sender_first_name, "times_trolled": 0, "times_trollee": 1}
            savedata(data)
            
        bot_message = (sender_first_name + ' has ' + function + 'ed ' + first_name + ' to level ' + str(data['users'][str(reply_id)]['times_trolled']) + '!')
        bot_reply = bot.reply_to(reply, bot_message)
        try:
            auto_delete(message, bot_reply) 
        except:
            pass
    except:
        bot.reply_to(reply, "Not an image, problem?")


def decreaseScore(message, score, function):
    reply = message.reply_to_message

    try:
        reply.photo[-1].file_id
        reply_id = message.reply_to_message.from_user.id
        sender_id = message.from_user.id
        sender_first_name = message.from_user.first_name
        first_name = message.reply_to_message.from_user.first_name

        if(reply_id == sender_id):
            bot.reply_to(message, "You can't " + function + " yourself!")
            return
    
        data = loaddata()  

        if(str(reply_id) in data['users']):      
            data['users'][str(reply_id)]['times_trolled'] -= score
            data['users'][str(reply_id)]['user_name'] = first_name
            savedata(data)

        else:
            data['users'][str(reply_id)] = {"user_name": first_name, "times_trolled": -1, "times_trollee": 0}
            savedata(data)
           
        bot_message = (sender_first_name + ' has ' + function + "ed " + first_name + ' to level ' + str(data['users'][str(reply_id)]['times_trolled']) + '!')
        bot_reply = bot.reply_to(reply, bot_message)
        try:
            auto_delete(message, bot_reply) 
        except:
            pass
    except:
        bot.reply_to(reply, "Not an image, problem?")

def auto_delete(message, reply):
    time.sleep(10)
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(reply.chat.id, reply.message_id)

@bot.message_handler(commands=['trolllist'])
def trolllist(message):
    troll_list = threading.Thread(target=gen_list, args=[message])
    troll_list.start()  

def gen_list(message):
    users = loaddata()
    tmp_scores = {}
    for user in users['users']:
        if users['users'][user]['user_name'] in tmp_scores:
            key = users['users'][user]['user_name'] + '(' + user + ')'
            tmp_scores[key] = users['users'][user]['times_trolled']
        else:
            tmp_scores[users['users'][user]['user_name']] = users['users'][user]['times_trolled']
    
    formatted_scores = sorted(tmp_scores.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)[:10]
    
    bot_message = "Top 10 trolls:\n\n"
    s = '*\n'.join(str(x) for x in formatted_scores) 
    bot_message += s
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("('", '')
    bot_message = bot_message.replace("',", ': ')
    bot_message = bot_message.replace(")*", '')
    bot_message = bot_message[:-1] + ''
    bot.reply_to(message, bot_message)

@bot.message_handler(commands=['fuuulist'])
def fuulist(message):
    troll_list = threading.Thread(target=antitrollers, args=[message])
    troll_list.start()  

def antitrollers(message):
    users = loaddata()
    tmp_scores = {}
    for user in users['users']:
        if users['users'][user]['user_name'] in tmp_scores:
            key = users['users'][user]['user_name'] + '(' + user + ')'
            tmp_scores[key] = users['users'][user]['times_trolled']
        else:
            tmp_scores[users['users'][user]['user_name']] = users['users'][user]['times_trolled']       
    
    formatted_scores = sorted(tmp_scores.items(), key=lambda kv:(kv[1], kv[0]), reverse=False)[:10]
    
    bot_message = "Bottom 10 trolls:\n\n"
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

def bizThread(message):
    message_id = bot.reply_to(message, 'Checking for biz threads, one moment please.').message_id
    webURL = 'https://a.4cdn.org/biz/catalog.json'
    r = requests.get(webURL).json()

    i=0
    threadArray = []
    
    for index in r: 
        for threads in r[i]['threads']:  
            webURL = 'https://a.4cdn.org/biz/thread/' + str(threads['no']) + '.json'
            t = requests.get(webURL).json()
            try:
                filters = loaddata()
                threadFound = False
                for variable in filters['bizfilters']:                               
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
    try:
        bot.delete_message(message.chat.id, message_id)
        bot.reply_to(message, sf, parse_mode=ParseMode.HTML)
    except:
        bot.reply_to(message, sf, parse_mode=ParseMode.HTML)

def addfilter(message):
    if(checkadmin(message)):
        filter = ((message.text).replace('/addbizfilter ', '')) 
        filters = loaddata()
        filters['bizfilters'].append(filter)           
        savedata(filters)
        bot.reply_to(message, "Filter added!")

def removefilter(message):
    if(checkadmin(message)):
        filter = ((message.text).replace('/removebizfilter ', '')) 
        filters = loaddata()
        try:
            filters['bizfilters'].remove(filter)
            bot.reply_to(message, "Filter removed!")
            savedata(filters)
        except:
            bot.reply_to(message, "Filter does not exist")

def filters(message):   
    try:
        filters = loaddata()
        for variable in filters['bizfilters']:                               
            s = '\n'.join(str(x) for x in filters['bizfilters']) 
        text = ['Current filters: ', s]
        bot_message = '\n\n'.join(str(x) for x in text)
        bot.reply_to(message, bot_message)
    except:
        bot.reply_to(message, "You do not have any active filters. Please use /addbizfilter to add a new filter.")

def checkadmin(message):
    admins = bot.get_chat_administrators(bot_chat_id)
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array):
        return True
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.reply_to(message, "Problem, not an admin?")        
        return False

def savedata(data):
    with open(read_file, 'w') as f:
        json.dump(data, f) 

def loaddata():
    file = open(read_file)
    data = json.load(file)
    return(data)
           
@bot.message_handler(commands=['addaccount'])
def addaccount(message):
    if(checkadmin(message)):
        accounts = ['trollfaceth']

        for account in accounts:
            rule = "from:" + account
            stream.add_rules(tweepy.StreamRule(rule))
        bot.reply_to(message, "Default account added!") 

@bot.message_handler(commands=['refresh'])
def troll(message):
    global pic_generating 
    pic_generating = False
    bot.reply_to(message, "Wow I'm feeling refreshed now. Thanks")

@bot.message_handler(commands=['trollify'])
def troll(message):
    troll = threading.Thread(target=trollify, args=[message])
    troll.start() 

def trollify(message):
    global pic_generating
    if not pic_generating:
        pic_generating = True
        try:
            trolls = loaddata()
            x = random.randint(1, trolls['trolls'])
            troll = r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\trollface" + str(x) + ".png"
            reply = message.reply_to_message
            fileID = reply.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\image.png", 'wb') as new_file:
                new_file.write(downloaded_file)
            im1 = Image.open(r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\image.png").convert('RGBA').resize((500,500))
            
            im2 = Image.open(troll).convert('RGBA').resize((500,500))

            im3 = Image.blend(im1, im2, 0.35)

            im3.save(r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\image.png")
            
            bot.send_photo(message.chat.id, photo=open(r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\image.png", 'rb'))
            pic_generating = False
        except:
            bot.reply_to(message, "Not an image, problem?")
            pic_generating = False
    else:
        bot.reply_to(message, "Busy generating, problem?")

@bot.message_handler(func=lambda message: True)
def filter_message(message):
    if 'https://boards.4channel.org/biz/thread/' in message.text:
        x = re.sub('https://boards.4channel.org/biz/thread/', 'BUMP TO DUMP THIS 4CHAN THREAD\n\nhttps://dereferer.me/?https%3A//boards.4channel.org/biz/thread/', message.text)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, x)
        return
    if "wen renounce" in (message.text).lower():
        try:
            bot.send_photo(message.chat.id, photo=open(r"C:\Users\Brandon\Documents\Coding\Troll\Python\images\wenrenounce.png", 'rb'), reply_to_message_id=message.id)
        except Exception as e:
            print(e)
        return



def main():
    while True:
        try:
            bot.polling(True)
        except Exception:
            time.sleep(5) 

if __name__ == "__main__":  
    stream = MyStream(bearer_token=TelegramConstants.twitter_bearer_token)
    polling = threading.Thread(target=main)
    #timed_messages = threading.Thread(target=timedmessages)
    #connect_stream = threading.Thread(target=connectStream)
    try:       
        polling.start()
        #timed_messages.start()
        #connect_stream.start()        
    except:
        print("Exception received")