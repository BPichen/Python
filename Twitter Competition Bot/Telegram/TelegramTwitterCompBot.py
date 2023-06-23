import tweepy, json, telebot, time, threading, TelegramConstants

twitter_bearer_token = TelegramConstants.twitter_bearer_token
bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
read_file = TelegramConstants.read_file

bot = telebot.TeleBot(token=bot_token)
auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)

def connectStream():
        try:
            stream.filter()
        except:
            connectStream()
            print("Error connecting. Retrying...")

# Twitter stream handling

class MyStream(tweepy.StreamingClient):
    def on_connect(self):
        bot.send_message(bot_admin_chat_id, "Connected!")
        print("Connected")
        return True
    
    def on_tweet(self, tweet):   
        if(contestrunning() == "true"):
            if('RT' not in tweet.text[:2]):
                try:
                    user_list = loaddata()
                    tmp_tweet = api.get_status(tweet.id)                   
                    
                    if(tmp_tweet.user.screen_name in user_list['banned_users']):
                        print("Banned user tried to tweet.")
                        return                 
                    else:                   
                        if(tmp_tweet.user.screen_name in user_list['users']):
                            print("Existing user: " + tmp_tweet.user.screen_name) 
                            try:
                                last_tweet = api.get_status(user_list['users_last_tweet'][tmp_tweet.user.screen_name])
                                if(tmp_tweet.text) == (last_tweet.text):
                                    print("Duplicate tweet. Do not add.")                           
                                else:
                                    print("New tweet. Adding.")
                                    user_list['users'][tmp_tweet.user.screen_name].append(tmp_tweet.id) 
                                    user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id 
                                    savedata(user_list) 
                            except:
                                print("Last known Tweet deleted. Adding.")
                                user_list['users'][tmp_tweet.user.screen_name].append(tmp_tweet.id)
                                user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id
                                savedata(user_list)

                        elif('#trololo' in tweet.text.lower()):
                            print("New user: " + tmp_tweet.user.screen_name)                  
                            user_list['users'][tmp_tweet.user.screen_name] = ([tmp_tweet.id]) 
                            user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id
                            user_list['users_score'][tmp_tweet.user.screen_name] = 0 
                            savedata(user_list)
                            tweet_link = 'https://twitter.com/' + tmp_tweet.user.screen_name + '/status/' + str(tmp_tweet.id)
                            s = tmp_tweet.user.screen_name + " has joined the competition! Here's their first tweet:\n\n" + tweet_link
                            bot.send_message(getchatid(), s)
                except Exception:
                    time.sleep(0.2)
            time.sleep(0.2)

    def on_connection_error(status):
        bot.send_message(bot_admin_chat_id, "Connection error. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..") 
        connectStream()

    def on_closed(status):
        bot.send_message(bot_admin_chat_id, "Connection closed. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_exception(status):
        bot.send_message(bot_admin_chat_id, "Exception received. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_disconnect(status):
        bot.send_message(bot_admin_chat_id, "Disconnected. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_error(status):
        bot.send_message(bot_admin_chat_id, "Error. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

    def on_limit(status):
        bot.send_message(bot_admin_chat_id, "Twitter limit. Reconnecting in 15 seconds")
        time.sleep(15)
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..")
        connectStream()

# Telegram bot commands

@bot.message_handler(commands=['startcontest'])
def start_contest(message):
    if(checkadmin(message)): 
        if(contestrunning() == "true"): 
            bot.reply_to(message, 'A contest is already running. Please use /endcontest to manually end the current contest.')
        else:
            hours = ((message.text).replace('/startcontest ', ''))
            end_time = int(time.time()) + (int(hours) * 3600) 
            saveconteststate("true")   
            setendtime(end_time)
            bot_message = hours + ' hour contest started!'    
            bot.reply_to(message, bot_message)  
            check_score = threading.Thread(target=check_scoreboard) 
            check_timer = threading.Thread(target=check_time)
            check_score.start()
            check_timer.start() 
        
@bot.message_handler(commands=['endcontest'])
def end_contest(message):
    if(checksuperadmin(message)):
        if(contestrunning() == "true"):
            results = threading.Thread(target=send_results)
            results.start()
            print("Contest ended manually.")
        else:
            bot.reply_to(message, 'There are currently no running contests. Please use /startcontest to start a new contest.')
          
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Please use /shillbot to view this bots commands.')

@bot.message_handler(commands=['scoring'])
def send_welcome(message):
    bot.reply_to(message, 'Scoring is based on likes and retweets received by your tweet. The current scoring standards are as follows:\n\nLike: 1 point\nRetweet: 4 points\n\nDuplicate Tweets will not be scored.')

@bot.message_handler(commands=['register'])
def register(message):
    bot.reply_to(message, 'To register, create a Tweet tagged with #trololo and one of the /tags. After you have been registered, any tweet with one of the tags will count.')

@bot.message_handler(commands=['shillbot'])
def send_commands(message):
    bot.reply_to(message, 'User commands:\n\n/leaderboard - Show the current leaderboard\n/points twitterhandle - Show a handles points\n/tags - Display a list of scored hashtags\n/register - Information on how to register\n/scoring - Display the points awarded for liking/retweets\n\nAdmin Commands:\n\n/startcontest n - Starts an n hour shill contest\n/addtag #yourtag - Adds a hashtag\n/resettags - Clears the list of hashtags\n/banish - Bans an existing Twitter handle from the competition and removes their Tweets\n/unbanish - Unbans a Twitter handle')

@bot.message_handler(commands=['points'])
def points(message):
    if(contestrunning() == "true"):
        user = ((message.text).replace('/points ', '')) 
        user_list = loaddata()    
        for tmp_user in user_list['users']:  
            if(user.lower() == tmp_user.lower()):
                tmp_score = 0 
                for tweet in user_list['users'][tmp_user]:    
                    try:     
                        tweet_data = api.get_status(tweet) 
                        tmp_score += (tweet_data.retweet_count * 4) 
                        tmp_score += (tweet_data.favorite_count)                            
                    except:
                        continue 
                if(tmp_score == 1): 
                    bot_message = tmp_user + ' has ' + str(tmp_score) + ' point.'
                else: 
                    bot_message = tmp_user + ' has ' + str(tmp_score) + ' points.'
                bot.reply_to(message, bot_message) 
                return

            else:
                bot.reply_to(message, "That user is not registered") 
    else:
        bot.reply_to(message, "Contest is not running") 

@bot.message_handler(commands=['leaderboard'])
def send_leaderboard(message):
    if(contestrunning() == "true"):
        user_list = loaddata()  
        tmp_scores = {}
        for user in user_list['users_score']:
            tmp_scores[user] = user_list['users_score'][user]
        if(int(user_list['top_tweet_points']) != 0):
            try:
                best_tweet = api.get_status(int(user_list['top_tweet']))
            except:
                print("Best tweet deleted?")
        else:
            bot.send_message(getchatid(), "No points have been scored yet. Go tweet! (Points are scored every 10 minutes)")
            return
        formatted_scores = sorted(tmp_scores.items(), key=lambda x: x[1], reverse=True)[:10]

        bot_message = "Current Top 10:\n\n"
        s = '\n'.join(str(x) for x in formatted_scores) 
        bot_message += s
        bot_message = bot_message.replace("('", '')
        bot_message = bot_message.replace("',", ': ')
        bot_message = bot_message.replace(")", '')
        bot_message = bot_message + '\n\n' + 'Top Tweet:\n\n' + 'https://twitter.com/' + best_tweet.user.screen_name + '/status/' + str(best_tweet.id)
        bot.reply_to(message, bot_message)
    else:
        bot.reply_to(message, "Contest is not running")

@bot.message_handler(commands=['tags'])
def send_tags(message):
    hashtags = stream.get_rules()
    hashtags_array = []
    if(hashtags.data is None):      
            bot.reply_to(message, "There are currently no hashtags added. To add a hashtag, type /addtag #yourhashtag")                                      
    else:
        for x in range(len(hashtags.data)):
            hashtags_array.append(hashtags.data[x].value)

        s = '\n'.join(str(x) for x in hashtags_array) 
        text = ['Current hashtags: ', s]
        sf = '\n\n'.join(str(x) for x in text)

        bot.reply_to(message, sf)

@bot.message_handler(commands=['addtag'])
def addtag(message):
    if(checkadmin(message)):
        rule = ((message.text).replace('/addtag ', '')) 
        stream.add_rules(tweepy.StreamRule(rule)) 
        bot.reply_to(message, "Hashtag added!") 

@bot.message_handler(commands=['resettags'])
def resettags(message):
    if(checkadmin(message)):
        rules = stream.get_rules()
        bot.reply_to(message, "Hashtags cleared!")
        for rule in rules: 
            stream.delete_rules(rule)

@bot.message_handler(commands=['banish'])
def ban(message):
    if(checkadmin(message)):
        user = ((message.text).replace('/banish ', ''))
        user_list = loaddata() 
        for tmp_user in user_list['users']:  
            if(user.lower() == tmp_user.lower()): 
                user_list['users_last_tweet'].pop(tmp_user, None) 
                user_list['users'].pop(tmp_user, None)             
                user_list['banned_users'][tmp_user] = ("true") 
                savedata(user_list) 
                bot.reply_to(message, "User has been banned!")
                return #done
            else:
                continue 
        bot.reply_to(message, "That user does not exist!") 

@bot.message_handler(commands=['unbanish'])
def unban(message):
    if(checkadmin(message)):
        user = ((message.text).replace('/unbanish ', '')) 
        user_list = loaddata() 
        for tmp_user in user_list['banned_users']:
            if(user.lower() == tmp_user.lower()):      
                user_list['banned_users'].pop(tmp_user, None)
                savedata(user_list) 
                bot.reply_to(message, "User has been unbanned!")
                return
            else:
                continue 
        bot.reply_to(message, "That user does not exist!")
     
@bot.message_handler(commands=['setchatid'])
def setchatid(message):
    if(checksuperadmin(message)): 
        try:
            data = loaddata() 
            data['other']['chat_id'] = message.chat.id
            savedata(data) 
            bot.send_message(getchatid(), "Bot initialized!")
        except Exception as e:
            bot.send_message(getchatid(), e)

# send_results is called when a contest ends. Gather scores for each entered user and send to active chat.

def send_results():
    user_list = loaddata()
    tmp_scores = {}
    best_tweet_points = 0 
    best_tweet_id = 0 
    for user in user_list['users']:
        tmp_score = 0 
        for tweet in user_list['users'][user]:
            tmp_best_tweet_points = 0 
            try:
                tweet_data = api.get_status(tweet) 
                tmp_score += (tweet_data.retweet_count * 4)
                tmp_score += (tweet_data.favorite_count)
                tmp_best_tweet_points += (tweet_data.retweet_count * 4) 
                tmp_best_tweet_points += (tweet_data.favorite_count)
                    
                if(tmp_best_tweet_points > best_tweet_points):
                    best_tweet_id = tweet
                    best_tweet_points = tmp_best_tweet_points                      
            except:
                continue
        tmp_scores[user] = tmp_score
    if(best_tweet_points != 0): 
        best_tweet = api.get_status(best_tweet_id) 
        formatted_scores = sorted(tmp_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        bot_message = "Contest ended. Here were the top 10:\n\n"

        s = '\n'.join(str(x) for x in formatted_scores) 

        bot_message += s
        bot_message = bot_message.replace("('", '')
        bot_message = bot_message.replace("',", ': ')
        bot_message = bot_message.replace(")", '')
        bot_message = bot_message + '\n\n' + 'Top Tweet:\n\n' + 'https://twitter.com/' + best_tweet.user.screen_name + '/status/' + str(best_tweet_id)
        bot.send_message(getchatid(), bot_message)
    else: 
        bot.send_message(getchatid(), "Contest ended with no points scored. Pathetic.")

    wipelist() 

# wipelist is called after a contest is scored to clear JSON reuslts.

def wipelist():
    data = loaddata() 

    data['users'] = {}
    data['users_score'] = {}
    data['users_last_tweet'] = {}
    data['top_tweet'] = {}
    data['top_tweet_points'] = 0
    data['banned_users'] = {}
    data['other']['end_time'] = 0
    savedata(data)
    saveconteststate("false")

# checkadmin checks if the function caller is an admin in the active chat.
   
def checkadmin(message):
    admins = bot.get_chat_administrators(getchatid())
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array):
        return True
    else:
        bot.reply_to(message, "You need to be an admin to do this.")
        return False
     
# checksuperadmin checks if a function caller is an admin in the secret admin chat.

def checksuperadmin(message):
    admins = bot.get_chat_administrators(bot_admin_chat_id)
    admin_array = []
    for admin in admins:
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array): 
        return True
    else: 
        bot.reply_to(message, "You need to be a superadmin to do this.")
        return False
    
# Saving and loading JSON data.
    
def savedata(data):
    with open(read_file, 'w') as f:
        json.dump(data, f) 

def loaddata():
    file = open(read_file)
    data = json.load(file)
    return(data)

def saveconteststate(is_running):
    data = loaddata() 
    data['other']['is_running'] = is_running 
    savedata(data) 

def saveuserscore(user, score):
    data = loaddata() 
    data['users_score'][user] = score 
    savedata(data) 

def savebesttweet(tweet, points):
    data = loaddata() 
    data['top_tweet'] = tweet 
    data['top_tweet_points'] = points 
    savedata(data) 

def contestrunning():
    req = loaddata()
    contest_running = req['other']['is_running'] 
    return contest_running 

def setendtime(end_time):
    data = loaddata()
    data['other']['end_time'] = str(end_time) 
    savedata(data)

def getendtime():
    req = loaddata()
    end_time = req['other']['end_time']
    return(end_time)

def getchatid():
    req = loaddata()
    chat_id = req['other']['chat_id']
    return chat_id

# check_scoreboard runs on it's own thread when a contest is started. Checks every 10 minutes and saves the current score.

def check_scoreboard():
    while(contestrunning() == 'true'): 
        print("Checking score..")
        user_list = loaddata() 
        best_tweet_points = 0
        for user in user_list['users']:
            tmp_score = 0
            for tweet in user_list['users'][user]: 
                tmp_best_tweet_points = 0    
                try: 
                    tweet_data = api.get_status(tweet) 
                    tmp_score += (tweet_data.retweet_count * 4)
                    tmp_score += (tweet_data.favorite_count)
                    tmp_best_tweet_points += (tweet_data.retweet_count * 4) 
                    tmp_best_tweet_points += (tweet_data.favorite_count)

                    if(tmp_best_tweet_points > best_tweet_points):
                        best_tweet_id = tweet
                        best_tweet_points = tmp_best_tweet_points  
                        try:
                            savebesttweet(best_tweet_id, best_tweet_points) 
                        except:
                            continue                   
                except:
                    continue 
            saveuserscore(user, tmp_score)
            
        time.sleep(600)

# bot_polling runs on it's own thread to handle telegram commands

def bot_polling():
    while True:
        try:
            bot.polling(True)
        except Exception:
            time.sleep(5)

# timed_end is called when a contest ends. Starts a new send_results thread to gather results.

def timed_end():
        bot.send_message(getchatid(), "Shill contest ended! Gathering results, one moment please..") 
        results = threading.Thread(target=send_results)
        results.start() 
        print("Contest ended.")

# check_time runs on it's own thread when a contest is started to check time versus end time.

def check_time():    
        end_time = getendtime() 
        while((int(end_time) > int(time.time()))):  
            print("Comparing time..")          
            time.sleep(5)

        timed_end()

# Initialize threads and check if a contest was running (bot may have crashed or reset) resume contest if True.

if __name__ == "__main__":  
    stream = MyStream(bearer_token=TelegramConstants.twitter_bearer_token)
    check_score = threading.Thread(target=check_scoreboard)
    check_timer = threading.Thread(target=check_time)
    polling = threading.Thread(target=bot_polling)
    connect_stream = threading.Thread(target=connectStream)
    if(contestrunning() == 'true'):
        check_score.start()
        check_timer.start()
    try:       
        polling.start()
        connect_stream.start() 
    except Exception as e:
        print("Exception received: " + e)