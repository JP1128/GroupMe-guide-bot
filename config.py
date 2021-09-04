import configparser as cp

c = cp.ConfigParser()
c.read('bot.ini')

# GroupMe API
groupme_image_url = 'https://image.groupme.com/pictures'
groupme_base_url = 'https://api.groupme.com/v3'
bot_url = groupme_base_url + '/bots'
post_message = bot_url + '/post'


# Database
dbname = c['DATABASE']['DBNAME']
host = c['DATABASE']['HOST']
user = c['DATABASE']['USER']
password = c['DATABASE']['PASSWORD']


# Bot Settings
prefix = c['BOT']['PREFIX']
access_token = c['BOT']['ACCESS_TOKEN']
max_guide_name = 32


# Image Settings
min_width = 800
padding = 100
ratio = 5

empty_character = "\u200B"
