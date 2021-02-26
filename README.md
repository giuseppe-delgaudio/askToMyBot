# AskToMyBot

This bot has been created using [Bot Framework](https://dev.botframework.com) v4.11, this bot allows to analyse a human face to obtain many face information.
The bot has different modes and functionalities : 
* *Face Analyse* : this mode consent, after a photo upload to obtain a user's face age, the result can be saved
* *Face Compare* : this mode consent , after a first photo upload to compare your image with another image, the second image can be uploded or can be searched on web, the result can be saved.
* *Compare face with stars* : this mode consent : after a photo upload and a VIP group selected, the bot returns a most resembling VIP, if exists, the result can be saved.
* *Show and manage results* : this mode consent : this mode shows all results and if the users want, is possible to delete one or all results

In any conversation is possible to interrupt action with '''/fine''' command
The bot has a secret menu for insert and manage person groups, the developer can access them with the command '''developerMode''' after '''/fine'''

## To try this sample

- Clone the repository
- Open repository folder
- Activate your desired virtual environment
- In the terminal, type `pip install -r requirements.txt`
- Run your bot with `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the latest Bot Framework Emulator from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- File -> Open Bot
- Enter a Bot URL of `http://localhost:3978/api/messages`
- Add into Bot Framework Emulator AppID : '''51bd055d-b570-4266-bef7-8920cf7a9708'''  AppPassword : '''OT~P8yU59xr~L~sado2A_.RFREr3aA155q'''
- Start emulator

## Deploy the bot to Azure

- Create Azure Web App in powershell CLI , Portal or Visual Studio Code
- In portal open Azure Web app configuration and copy in *General Settings* -> *Startup Command* this string : '''python3.7 -m aiohttp.web -H 0.0.0.0 -P 8000 app:init_func'''
- In portal open Azure Web app configuration and deploy app with github binding or deploy zip file from powershell CLI see Documentation for details
- Create Bot Channel registration and insert the URL of Azure App in *Bot Channel Regitration* -> *Settings* add URL adding /api/messages -> '''URL/api/messages'''  

## Documentation

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)

### Note ### 
-This bot use [Python 3.7 version](https://www.python.org/downloads/release/python-3710/)
-For DB functions create [Azure Function App](https://github.com/giuseppe-delgaudio/functionAppDB)