#imports for packages. Tweepy is to interact with Twitter, telebot is to interact with telegram, threading is for multithreading, and TelegramConstants is for API keys and other secret stuff
#any print statements print to console for testing/debug stuff
import tweepy, json, telebot, time, threading, TelegramConstants

#load secret variables from TelegramContants py file and save them locally
twitter_bearer_token = TelegramConstants.twitter_bearer_token
bot_token = TelegramConstants.bot_token
bot_admin_chat_id = TelegramConstants.bot_admin_chat_id
read_file = TelegramConstants.read_file

#assign telegram bot token to make the telegram bot work and set up tweepy to use the Twitter API key. api is used to interact with twitter and bot is used to interact with telegram
bot = telebot.TeleBot(token=bot_token)
auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)

#connectStream is called to connnect the Twitter API filtered stream. If the stream fails it tries to reconnect
def connectStream():
        try:
            stream.filter()#tweet_fields=["referenced_tweets"]
        except:
            connectStream()
            print("Error connecting. Retrying...")

#MyStream class for all the twitter handlers. on_connect is when the stream connects (connectStream above), on_tweet is when a tweet comes in that matches the filters, etc. This class handles anything that happens while the stream is running
class MyStream(tweepy.StreamingClient):
    def on_connect(self):
        #when the Twitter API stream connects send the admin chat a message and print to console
        bot.send_message(bot_admin_chat_id, "Connected!")
        print("Connected")
        return True
    
    #this function gets called when a tweet matching the filters is tweeted. Ex. I tweet #test and this function would get called
    def on_tweet(self, tweet):   
        if(contestrunning() == "true"):#if a contest is currently running, do the following
            if('RT' not in tweet.text[:2]): #Checks if the tweet is a retweet. Tweets need to be original to be counted
                try:
                    user_list = loaddata() #load JSON data. See loaddata function way below
                    tmp_tweet = api.get_status(tweet.id) #load the new tweets data using the Twitter API and the tweets ID.                   
                    
                    if(tmp_tweet.user.screen_name in user_list['banned_users']): #if the username that just tweeted is in the banned list ignore it
                        print("Banned user tried to tweet.")
                        return                 
                    else:    #if not in the banned list (most users)                   
                        if(tmp_tweet.user.screen_name in user_list['users']): #if the user has already been entered in the contest and exists in JSON data (already tweeted once with #competition)
                            print("Existing user: " + tmp_tweet.user.screen_name) #print in console that an existing user just tweeted with their Twitter screen name
                            try:
                                #the users last known tweet ID gets saved to JSON. If the users last tweet is identical to the one that just came in it doesn't get counted.
                                #this makes it so someone can't tweet the same thing over and over again and like/retweet them all for free points. Back to back tweets need to be unique
                                last_tweet = api.get_status(user_list['users_last_tweet'][tmp_tweet.user.screen_name])#load data for their last known tweet
                                if(tmp_tweet.text) == (last_tweet.text): #if the tweets text matches their last known tweets text, ignore it as a duplicate
                                    print("Duplicate tweet. Do not add.")                           
                                else: #else, add the tweet ID to their list of tweets, last known tweet, and save
                                    print("New tweet. Adding.")
                                    user_list['users'][tmp_tweet.user.screen_name].append(tmp_tweet.id) #add the users screen name and use it as a key for an array of tweet IDs
                                    user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id #add the users screen name and use it as a key for their last tweet ID
                                    savedata(user_list) #save JSON data
                            except:#error handling
                                #if the users last known tweet can't be loaded it probably got deleted. Add the tweet that just came in as their last known tweet and save
                                print("Last known Tweet deleted. Adding.")
                                user_list['users'][tmp_tweet.user.screen_name].append(tmp_tweet.id) #add to user's array of tweets
                                user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id#add tweet id to user's last known tweet
                                savedata(user_list)#save data to JSON file

                        elif('#trololo' in tweet.text.lower()):#if the username does not exist in JSON and #competition is in the tweet
                            #competition only has to be used to enter the contest. Once registered, they can use any of the contests hashtags
                            print("New user: " + tmp_tweet.user.screen_name)  #print to console that a new user tweeted along with their screen name                   
                            user_list['users'][tmp_tweet.user.screen_name] = ([tmp_tweet.id]) #add users screen name and use it as a key for an array of tweet ids. "testusername": {[123, 124, 125]}
                            user_list['users_last_tweet'][tmp_tweet.user.screen_name] = tmp_tweet.id #add users screen name and use it as a key for their last known tweet. "testusername": {125}
                            user_list['users_score'][tmp_tweet.user.screen_name] = 0 #set users score to 0 so that it isn't blank in JSON. "testusername": {0}
                            savedata(user_list)#save JSON data
                            tweet_link = 'https://twitter.com/' + tmp_tweet.user.screen_name + '/status/' + str(tmp_tweet.id) #creates a Tweet URL for the new competitor using their username and tweet ID
                            s = tmp_tweet.user.screen_name + " has joined the competition! Here's their first tweet:\n\n" + tweet_link #creates a string for a message to the current active telegram chat. New user has joined the competition
                            bot.send_message(getchatid(), s) #sends message to current active telegram chat
                except Exception: #if there is an issue pulling a tweet, rest for small time because Twitter doesn't like constant spamming and might disconnect the stream
                    time.sleep(0.2)
            time.sleep(0.2)
    
    #all of the below are exceptions that Twitter sends if the stream has an error. If the stream gets disconnected in any of these cases it will send the admin chat a message to let me know that the stream has been disconnected and will reconnect in 15 seconds
    #too fast of a reconnect might trigger twitter to block the bot for 15+ minutes
    def on_connection_error(status):
        bot.send_message(bot_admin_chat_id, "Connection error. Reconnecting in 15 seconds") #send message to telegram admin chat that the stream disconnected
        time.sleep(15) #sleep 60 seconds
        bot.send_message(bot_admin_chat_id, "Trying to Reconnect..") #send reconnecting message
        connectStream() #reconnect

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
    #end of stream disconnect handling

#This is the start of Telegram bot commands. Anything that starts with the @bot.message_handler syntax below is a function that can be called with a /command. This one below is /startcontest to start competitions
@bot.message_handler(commands=['startcontest'])#commands=['telegramcommandname']
def start_contest(message):
    if(checkadmin(message)): #user needs to be an admin to run this command
        if(contestrunning() == "true"): #if the contest is already running send a message that there's already a contest running
            bot.reply_to(message, 'A contest is already running. Please use /endcontest to manually end the current contest.')
        else:
            hours = ((message.text).replace('/startcontest ', '')) #dumb way of grabbing message content after the command. Ex. /startcontest 5. Grabs the 5 from the command
            end_time = int(time.time()) + (int(hours) * 3600) #converts hours to seconds and sets an endtime variable
            saveconteststate("true")  #set contest running to true     
            setendtime(end_time) #set the end time for a contest
            bot_message = hours + ' hour contest started!'    
            bot.reply_to(message, bot_message) #send a message to active telegram chat that an n hour contest started
            print("Contest started.")   
            check_score = threading.Thread(target=check_scoreboard) #set up check_score thread
            check_timer = threading.Thread(target=check_time)  #set up check_timer thread
            check_score.start() #start above thread. Thread will close when complete
            check_timer.start() #start above thread. Thread will close when complete
        
#ends a contest early. User needs to be a superadmin to run this command (I am the only superadmin, if not any admin could accidentally use this and end the contest early)
@bot.message_handler(commands=['endcontest'])
def end_contest(message):
    if(checksuperadmin(message)):#check if message sender is a superadmin
        if(contestrunning() == "true"):#contest must be running
            results = threading.Thread(target=send_results) #set up a thread to send results. If not a thread, a /command might interrupt the score tallying
            results.start() #starts the thread created above. When done it will print the message below to console and close the thread
            print("Contest ended manually.")
        else:
            bot.reply_to(message, 'There are currently no running contests. Please use /startcontest to start a new contest.') #reply that a contest is not running
        
#generic bot command /start tells them to use /shillbot to see a list of commands    
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Please use /shillbot to view this bots commands.')

#replies to the command senders message with how to score points
@bot.message_handler(commands=['scoring'])
def send_welcome(message):
    bot.reply_to(message, 'Scoring is based on likes and retweets received by your tweet. The current scoring standards are as follows:\n\nLike: 1 point\nRetweet: 4 points\n\nDuplicate Tweets will not be scored.')

#replies to the command senders message with how to register
@bot.message_handler(commands=['register'])
def register(message):
    bot.reply_to(message, 'To register, create a Tweet tagged with #trololo and one of the /tags. After you have been registered, any tweet with one of the tags will count.')

#replies with a list of commands
@bot.message_handler(commands=['shillbot'])
def send_commands(message):
    bot.reply_to(message, 'User commands:\n\n/leaderboard - Show the current leaderboard\n/points twitterhandle - Show a handles points\n/tags - Display a list of scored hashtags\n/register - Information on how to register\n/scoring - Display the points awarded for liking/retweets\n\nAdmin Commands:\n\n/startcontest n - Starts an n hour shill contest\n/addtag #yourtag - Adds a hashtag\n/resettags - Clears the list of hashtags\n/banish - Bans an existing Twitter handle from the competition and removes their Tweets\n/unbanish - Unbans a Twitter handle')

#/points "username" will loop through all the provided users tweets and tally their score, then send it as a reply to their message. If the user isn't in the JSON data it tells them the user isn't registered
@bot.message_handler(commands=['points'])
def points(message):
    if(contestrunning() == "true"):#contest needs to be running to run this command
        user = ((message.text).replace('/points ', '')) #dumb way to grab message content. /points exampleuser will strip to exampleuser
        user_list = loaddata()#load JSON data into a variable       
        for tmp_user in user_list['users']: #loop through each user in the JSON data and check for matches on the name provided     
            if(user.lower() == tmp_user.lower()):
                tmp_score = 0 #temp score starts at zero
                for tweet in user_list['users'][tmp_user]:    
                    try:     
                        tweet_data = api.get_status(tweet) #use twitter API to get a tweet IDs data
                        tmp_score += (tweet_data.retweet_count * 4) #retweets are 4 points. Add to tmp_score
                        tmp_score += (tweet_data.favorite_count) #likes(favorites) are 1 point. Add to tmp_score                            
                    except:
                        continue #if an exception occurs (tweet probably deleted). Skip this tweet ID
                if(tmp_score == 1): #if user has 1 point. Make point singular
                    bot_message = tmp_user + ' has ' + str(tmp_score) + ' point.'
                else: #user has more than one point. Make it plural
                    bot_message = tmp_user + ' has ' + str(tmp_score) + ' points.'
                bot.reply_to(message, bot_message) #reply to the command sender
                return

            else:
                bot.reply_to(message, "That user is not registered") #user was not found in JSON data  
    else:
        bot.reply_to(message, "Contest is not running") #contest isn't running

#/learderboard pulls the top 10 scores and the top tweet
@bot.message_handler(commands=['leaderboard'])
def send_leaderboard(message):
    if(contestrunning() == "true"):#contest needs to be running
        user_list = loaddata()#load JSON data into a variable   
        tmp_scores = {}#empty data for temp
        for user in user_list['users_score']:#for each user in JSON data, loop
            tmp_scores[user] = user_list['users_score'][user]#add each users score to the temp dataset
        if(int(user_list['top_tweet_points']) != 0):#if the top_tweet_points does not = 0 a best tweet exists. Grab it's points
            try:
                best_tweet = api.get_status(int(user_list['top_tweet'])) #get tweet information for the best tweet using the Twitter API. Feed it the Tweet ID
            except:
                print("Best tweet deleted?")#tweet ID no longer exists(probbly deleted)
        else:
            bot.send_message(getchatid(), "No points have been scored yet. Go tweet! (Points are scored every 10 minutes)")#sends a message to the bots active telegram group
            return
        formatted_scores = sorted(tmp_scores.items(), key=lambda x: x[1], reverse=True)[:10]#sorts the temp data from greatest to least

        #this is all a bunch of magic and string formatting to make it print nicely in Telegram
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

#/tags returns the Twitter API filters current rules/hashtags
@bot.message_handler(commands=['tags'])
def send_tags(message):
    hashtags = stream.get_rules()#save the filters rules to a variable
    hashtags_array = []
    if(hashtags.data is None): #if there are no rules added, reply to message      
            bot.reply_to(message, "There are currently no hashtags added. To add a hashtag, type /addtag #yourhashtag")                                      
    else:#else, loop through each rule and grab the value variable for each
        for x in range(len(hashtags.data)):
            hashtags_array.append(hashtags.data[x].value)

        #magic to make it display in telegram nicely
        s = '\n'.join(str(x) for x in hashtags_array) 
        text = ['Current hashtags: ', s]
        sf = '\n\n'.join(str(x) for x in text)

        bot.reply_to(message, sf)#reply to the message sender with the active tags

#/addtag "tag" adds a hashtag to the Twitter API filter
@bot.message_handler(commands=['addtag'])
def addtag(message):
    if(checkadmin(message)):#need to be an admin
        rule = ((message.text).replace('/addtag ', '')) #dumb way to grab input. /addtag #test strips it down to #test
        stream.add_rules(tweepy.StreamRule(rule)) #add #test to the Twitter API rules
        bot.reply_to(message, "Hashtag added!") #success! User just added a hashtag, send them a reply  

#/resettags resets the current hashtags. Will clear any saved rules in the filter
@bot.message_handler(commands=['resettags'])
def resettags(message):
    if(checkadmin(message)):#need to be an admin
        rules = stream.get_rules() #gets all the current Twitter API rules
        bot.reply_to(message, "Hashtags cleared!")
        for rule in rules: #for each rule, delete
            stream.delete_rules(rule)

#bans a twitter username from the contest and deletes their tweet data
@bot.message_handler(commands=['banish'])
def ban(message):
    if(checkadmin(message)):#need to be an admin
        user = ((message.text).replace('/banish ', '')) #more dumb to strip command from text. '/banish test' gives test
        user_list = loaddata() #load JSON data
        for tmp_user in user_list['users']:  #loop through the user list 
            if(user.lower() == tmp_user.lower()): #if a match is found
                user_list['users_last_tweet'].pop(tmp_user, None) #remove their last known tweet id
                user_list['users'].pop(tmp_user, None) #remove them from the user list            
                user_list['banned_users'][tmp_user] = ("true") #add them to the banned list
                savedata(user_list) #save JSON data
                bot.reply_to(message, "User has been banned!") #success! send command sender a reply in chat
                return #done
            else:
                continue #if not a match, keep searching
        bot.reply_to(message, "That user does not exist!") #no user found

#unbans a twitter username from the contest. Does not restore tweet data
@bot.message_handler(commands=['unbanish'])
def unban(message):
    if(checkadmin(message)):#need to be an admin
        user = ((message.text).replace('/unbanish ', '')) #even more dumb to strip command from text. '/unbanish test' gives test
        user_list = loaddata() #load JSON
        for tmp_user in user_list['banned_users']: #loop through banned users list
            if(user.lower() == tmp_user.lower()): #if the username exists in the ban list, remove them      
                user_list['banned_users'].pop(tmp_user, None)
                savedata(user_list) #save data
                bot.reply_to(message, "User has been unbanned!")
                return
            else:
                continue #not found yet, keep looking
        bot.reply_to(message, "That user does not exist!") #nada

#/setchatid sets this bots active chat. It can only be used by my Telegram account. If I run this command in a Telegram chat it's chat ID gets saved to JSON for admin checks and other stuff      
@bot.message_handler(commands=['setchatid'])
def setchatid(message):
    if(checksuperadmin(message)): #check if command sender is a superadmin
        try:
            data = loaddata() #load JSON data
            data['other']['chat_id'] = message.chat.id#adds whatever chat ID this message came from
            savedata(data) #save JSON data
            bot.send_message(getchatid(), "Bot initialized!")#send a message to the now active Telegram chat
        except Exception as e:
            bot.send_message(getchatid(), e)#error handling

#the below are all functions that cannot be called via Telegram commands. They're used internally by the bot

#send_results is called when a competition comes to an end. Once scoring is complete bot will send a message to the active telegram chat with results
def send_results():
    user_list = loaddata() #load JSON data
    tmp_scores = {} #temp score list data
    best_tweet_points = 0 #temp best tweet points data 
    best_tweet_id = 0 #temp best tweet id
    for user in user_list['users']:#loop through each user in the JSON data
        tmp_score = 0 #individual user score
        for tweet in user_list['users'][user]:#loop through the users list of tweets
            tmp_best_tweet_points = 0 #used to temporarily check the users best tweet   
            try: #try to get the tweets data and add it's retweets and likes for points. If the tweet cannot be loaded it was probably deleted. Tweet ID is ignored if an error occurs
                tweet_data = api.get_status(tweet) #check tweet data using Twitter API. tweet variable is a tweet ID
                tmp_score += (tweet_data.retweet_count * 4) #add score for this tweets retweets
                tmp_score += (tweet_data.favorite_count) #add score for this tweets likes(favorites)
                tmp_best_tweet_points += (tweet_data.retweet_count * 4) #add this tweets likes/retweets to temp variable to check their best tweet
                tmp_best_tweet_points += (tweet_data.favorite_count)
                    
                if(tmp_best_tweet_points > best_tweet_points): #if the just checked tweet has more points than the overall current best tweet, rewrite best tweet. If not, keep counting tweets
                    best_tweet_id = tweet
                    best_tweet_points = tmp_best_tweet_points                      
            except:
                continue
        tmp_scores[user] = tmp_score #save the individual users score to a dictionary keyed with their Twitter user ID
    if(best_tweet_points != 0): #if there is a best tweet, get it's status and display the leaderboard
        best_tweet = api.get_status(best_tweet_id) #get tweet data for the current best tweet
        formatted_scores = sorted(tmp_scores.items(), key=lambda x: x[1], reverse=True)[:10] #format scores so that they are best to worst (10 max entries)

        #fancy formatting so that the string prints in Telegram nicely
        bot_message = "Contest ended. Here were the top 10:\n\n"
        s = '\n'.join(str(x) for x in formatted_scores) 

        bot_message += s
        bot_message = bot_message.replace("('", '')
        bot_message = bot_message.replace("',", ': ')
        bot_message = bot_message.replace(")", '')
        bot_message = bot_message + '\n\n' + 'Top Tweet:\n\n' + 'https://twitter.com/' + best_tweet.user.screen_name + '/status/' + str(best_tweet_id)
        bot.send_message(getchatid(), bot_message) #send active chat a message with the results
    else: #there wasn't a best tweet because no points were scored. Scold them
        bot.send_message(getchatid(), "Contest ended with no points scored. Pathetic.")

    wipelist() #call wipelist below to reset JSON data

def wipelist(): #this gets called when a contest is ended (manually or automatically). It opens the JSON file and sets everything back to default.
    data = loaddata() #loads JSON file
    #default data
    data['users'] = {}
    data['users_score'] = {}
    data['users_last_tweet'] = {}
    data['top_tweet'] = {}
    data['top_tweet_points'] = 0
    data['banned_users'] = {}
    data['other']['end_time'] = 0
    savedata(data)#saves the JSON file
    saveconteststate("false") #set contest state to false. No contest is running

#function called for any command that needs an admin check. Bot checks the active chat ID's admins and compares. If the user who used the command is not an admin, tell them they need to be an admin   
def checkadmin(message):
    admins = bot.get_chat_administrators(getchatid())#get active chats admin IDs
    admin_array = []
    for admin in admins: #add each admin ID to an array for comparison
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array): #if the command sender exists in the admin array, return True
        return True
    else: #not in admin array, return False
        bot.reply_to(message, "You need to be an admin to do this.")
        return False
    
#function called for any command that needs a superadmin check. Bot checks the bot admin chat ID's admins and compares. If the user who used the command is not a superadmin, tell them they need to be an superadmin    
def checksuperadmin(message):
    admins = bot.get_chat_administrators(bot_admin_chat_id)#get admin chats admin IDs
    admin_array = []
    for admin in admins:#add each admin ID to an array for comparison
        admin_array.append(admin.user.id)
    
    if(message.from_user.id in admin_array): #if the command sender exists in the admin array, return True
        return True
    else: #not in admin array, return False
        bot.reply_to(message, "You need to be a superadmin to do this.")
        return False

#reusable function used to save JSON data. Dumps data dictionary to file
def savedata(data):
    with open(read_file, 'w') as f:
        json.dump(data, f) 

#reusable function used to load JSON data. Saves JSON data to local data variable
def loaddata():
    file = open(read_file)
    data = json.load(file)
    return(data)

#sets the contest state
def saveconteststate(is_running):
    data = loaddata() #load JSON data
    data['other']['is_running'] = is_running #sets the is_running variable to true or false
    savedata(data) #save JSON data

#saves a users score when check_scoreboard is running. JSON data saving
def saveuserscore(user, score):
    data = loaddata() #load JSON data
    data['users_score'][user] = score #sets the provided users score variable 
    savedata(data) #save JSON data

#saves best tweet. JSON data saving
def savebesttweet(tweet, points):
    data = loaddata() #load JSON data
    data['top_tweet'] = tweet #sets the best tweet ID
    data['top_tweet_points'] = points #sets the best tweets current points
    savedata(data) #save JSON data

#checks if a contest is running. Variable is saved via JSON in case the bot crashes
def contestrunning():
    req = loaddata()#load JSON
    contest_running = req['other']['is_running'] #grab is_running variable
    return contest_running #is the contest running? True or False

#sets the end time when starting a contest. Variable is saved via JSON in case the bot crashes
def setendtime(end_time):
    data = loaddata()#load JSON
    data['other']['end_time'] = str(end_time) #set contest end time
    savedata(data) #save JSON

#loads end time from JSON
def getendtime():
    req = loaddata()
    end_time = req['other']['end_time']
    return(end_time)

#loads active chat ID from JSON
def getchatid():
    req = loaddata()
    chat_id = req['other']['chat_id']
    return chat_id

#function for checking the scoreboard. This is it's own thread that gets started when a contest starts. Will check scores every 10 minutes 
def check_scoreboard():
    while(contestrunning() == 'true'): #While the contest is running. If the contest ends this thread is killed
        print("Checking score..")
        user_list = loaddata() #load JSON data
        best_tweet_points = 0
        for user in user_list['users']: #for each user in dataset
            tmp_score = 0
            for tweet in user_list['users'][user]: #for each tweet the user has
                tmp_best_tweet_points = 0    
                try:  #try getting tweet data
                    tweet_data = api.get_status(tweet) #use Tweet ID (tweet) and Twitter API to grab individual tweet data
                    tmp_score += (tweet_data.retweet_count * 4) #add retweet points
                    tmp_score += (tweet_data.favorite_count) #add like(favorite) points
                    tmp_best_tweet_points += (tweet_data.retweet_count * 4) #tmp for best tweet comparison later
                    tmp_best_tweet_points += (tweet_data.favorite_count)

                    if(tmp_best_tweet_points > best_tweet_points): #if the tweet just checked has more points than the current best overall tweet, overwrite it
                        best_tweet_id = tweet
                        best_tweet_points = tmp_best_tweet_points  
                        try:
                            savebesttweet(best_tweet_id, best_tweet_points) #save best tweet id and points
                        except:
                            continue                   
                except:
                    continue #exception occured (tweet probably deleted). Continue checking other tweets
            saveuserscore(user, tmp_score) #Have checked all the users tweets, save the users score so it can be checked with /leaderboard
            
        time.sleep(600)#wait 10 minutes between each check to keep the twitter API from overloading

#main is used for bot polling. Bot polling is what listens for / commands. Ex. /shillbot gets used in a telegram group. This is started as a thread so that other functions don't get interrupted   
def main():
    while True:
        try:
            bot.polling(True)#bot is listening to commands
        except Exception:
            time.sleep(5)#if an exception happens, wait 5 seconds and try to poll again 

#timed_end is called when a contest reaches it's end time
def timed_end():
        bot.send_message(getchatid(), "Shill contest ended! Gathering results, one moment please..") #send a message to the active chat ID
        results = threading.Thread(target=send_results) #ready a thread for sending results
        results.start() #start the thread
        print("Contest ended.")

#check_time runs every 5 seconds as it's own thread once a contest is started. If the end time is less than current time, call the timed_end function above. Used to keep track of the contest time
def check_time():    
        end_time = getendtime() #get end time for a competition
        while((int(end_time) > int(time.time()))):  #while end time is greater than current time
            print("Comparing time..")          
            time.sleep(5) #sleep 5 seconds

        timed_end()#once the while loop breaks, call a timed_end

#This function is called once the bot script is started. Starts processes for everything to work
if __name__ == "__main__":  
    stream = MyStream(bearer_token=TelegramConstants.twitter_bearer_token)#sets up a Twitter stream variable using the class defined above
    check_score = threading.Thread(target=check_scoreboard)#sets up a check_score thread using the check_scoreboard function (periodically check the scoreboard when a contest starts). Uninterruptable because multithreading. This does not start the thread
    check_timer = threading.Thread(target=check_time)#sets up a check_timer thread using the check_time function (periodically check the time when a contest starts). Uninterruptable because multithreading. This does not start the thread
    polling = threading.Thread(target=main)#sets up a polling thread using the main function (waits for user input via Telegram). Uninterruptable because multithreading. This does not start the thread
    connect_stream = threading.Thread(target=connectStream)#sets up a Twitter stream thread using the connect_stream function (waits for Tweets to come in). Uninterruptable because multithreading. This does not start the thread
    if(contestrunning() == 'true'):#if a contest is already running, restart the check_score and check_timer threads. Bot probably crashed or PC reset
        check_score.start()#multithreading, start periodic score check
        check_timer.start()#multithreading, start periodic timer check
    try:       
        polling.start()#multithreading, start bot polling (waiting for telegram commands)
        connect_stream.start()#multithreading, start Twitter stream (waiting for tweets)  
    except Exception as e:
        print("Exception received: " + e)#bot broke