## Telegram bot for analyzing the Hotels.com website and searching hotels suitable for the user

----
The bot is written using the library
[Pytelegrambotapi](https://pypi.org/project/pyTelegramBotAPI/)

Bot uses [API сайта Hotels.com](https://rapidapi.com/apidojo/api/hotels4)

---
### What a bot can do:

- accepts mandatory data - city name, arrival / departure dates and the desired currency to be displayed in offers;
- city name input is possible in Russian and English;
- search for the most expensive / the cheapest offers by stated dates in the specified city;
- search for offers in the specified price range, taking into account the maximum distance from the city center;
- saves the history of user requests and can display it in messages;
- processes only text messages. When receiving a message of a different type, the bot will inform the user about the impossibility of processing this message;

---
### Commands:

- /help — help command,
- /start — the beginning of user input of the information necessary for the search,
- /lowprice — listing of the cheapest hotels in the city,
- /highprice — listing of the most expensive hotels in the city,
- /bestdeal — listing of hotels that are most suitable for the price and location from the center,
- /history — hotel search history display,
- /hello_world — test command,

---
### Work description:
After entering the first message, the user receives a response from the bot with a 
proposal to start searching for offers. After that, the bot awaits further commands from the user.

<br/><br/>
#### Command /start
After entering the command, the user is prompted for:
1. City where the search will be carried out
2. Choosing a city from the possible proposed options.
3. Check-in date
4. Departure date
5. Currency for displaying the cost of offers
6. The maximum number of offers required by the user
7. List of commands to select the sorting method ** (if /bestdeal - see the description of this command)

<br/><br/>
#### Command /lowprice
After entering the command, the user is prompted for:
1. City where the search will be carried out
2. Choosing a city from the possible proposed options.
3. Check-in date
4. Departure date
5. Currency for displaying the cost of offers
6. The maximum number of offers required by the user

<br/><br/>
#### Command /highprice
After entering the command, the user is prompted for:
1. City where the search will be carried out
2. Choosing a city from the possible proposed options.
3. Check-in date
4. Departure date
5. Currency for displaying the cost of offers
6. The maximum number of offers required by the user

<br/><br/>
#### Command /bestdeal
After entering the command, the user is prompted for:
1. City where the search will be carried out
2. Choosing a city from the possible proposed options.
3. Check-in date
4. Departure date
5. Currency for displaying the cost of offers
6. The maximum number of offers required by the user
7. Suitable price range (two numbers separated by a separator)
8. Maximum distance from the city center.




---
### Bot response:
After completing the processing of the command, the bot sends the found number of proposals to the user. Each offer is sent in a separate message.
#### The structure of the offer:
- hotel photo;
- the name of the hotel;
- distance from the city center;
- the cost of the entire stay;
- link to the hotel in the Hotels.com system for booking;

---
### Installation and setup:
1. Install [python >= 3.9](https://www.python.org/downloads/)
2. Install dependencies with PIP by running the following command in
command line:
```
pip install -r requirements.txt
```
3. Clone the given repository to yourself
4. Talk to @botfather in telegram and create your own bot.
You need to get a TOKEN for your bot;
5. Add the token received from @botfather to the _config_example.py file;
6. Register at [rapidapi.com] (https://rapidapi.com);
7. Follow the direct link to the [Hotels API Documentation] (https://rapidapi.com/apidojo/api/hotels4/);
8. Click the Subscribe to Test button;
9. Choose a free package (Basic);
10. You need to get TOKEN and HOST from rapidapi.com and add them to
_config_example.py file;
11. Rename _config_example.py to _config.py

The bot is ready to go!

In the command line, change to the directory where
files of the given project and enter the command:
```
python main.py
```