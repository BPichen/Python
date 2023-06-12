import tweepy, time
import requests
from tweepy import OAuthHandler
from datetime import datetime

TOKEN = '5632953101:AAFkJzaE62b6ulZuooD8MTt7VBDvdYMvOPc'

auth = tweepy.OAuth2BearerHandler("AAAAAAAAAAAAAAAAAAAAAO4CiQEAAAAADHHp85eQAFwyYSrMh0H1CszGiY4%3DX6t2i4ABmG9gOnRLTi8fm9rnYCdBrMxhTKXI2N59QkiApcVLFP")


tier1 = ['jimcramer', 'elonmusk', 'jack', 'cz_binance','1goonrich', 'mattwallace888', 'bitboy_crypto', 'prothedoge', 'WatcherGuru', 'SBF_FTX']
tier2 = ['milesdeutscher', 'jackniewold', 'kucoincom', 'gate_io', 'somecrypt0guy']

def getTweets():

    for user in tier1: 
        currenttime = datetime.utcnow()
        currenttime = time.mktime(currenttime.timetuple())

        tweets = []
        tmpTweets = api.user_timeline(screen_name=user)
        for tweet in tmpTweets:
            tweets.append(tweet)


        for tweet in tweets:
            tweettime = time.mktime((tweet.created_at).timetuple())
            if (tweettime + 12 > currenttime) and ('RT' not in tweet.text[:2]):
                if(tweet.in_reply_to_status_id is None):
                    telegram_bot_sendTwitter(user, str(tweet.id), 0, tweet.text)
                else:
                    telegram_bot_sendTwitter(user, str(tweet.id), 1, tweet.text)

    for user in tier2: 
        currenttime = datetime.utcnow()
        currenttime = time.mktime(currenttime.timetuple())

        tweets = []
        tmpTweets = api.user_timeline(screen_name=user)
        for tweet in tmpTweets:
            tweets.append(tweet)


        for tweet in tweets:
            tweettime = time.mktime((tweet.created_at).timetuple())
            if (tweettime + 12 > currenttime) and ('RT' not in tweet.text[:2] and tweet.in_reply_to_status_id is None):
                telegram_bot_sendTwitter(user, str(tweet.id), 0, tweet.text)
    print("Looping..")


        
def telegram_bot_sendTwitter(username, tweetid, tweetType, tweetText):

    if tweetType == 0:
        time.sleep(1)
        bot_message = 'NEW TWEET (@' + username + ')\n' + tweetText + '\n\nhttps://twitter.com/' + username + '/status/' + tweetid
        bot_message = bot_message.replace("#", '$')
        bot_chatID = '-1001556614034'
        send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()

    elif tweetType == 1:
        time.sleep(1)
        bot_message = 'NEW REPLY (@' + username + ')\n' + tweetText + '\n\nhttps://twitter.com/' + username + '/status/' + tweetid
        bot_message = bot_message.replace("#", '$')
        bot_chatID = '-1001556614034'
        send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()

print("Bot initializing..")

while True:
    api = tweepy.API(auth, retry_count=5, timeout=None)

    try:
        getTweets()
    except Exception as e:
        print(e)
        continue

    time.sleep(8)