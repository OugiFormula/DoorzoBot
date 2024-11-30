<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/OugiFormula/DoorzoBot/">
    <img src="https://github.com/OugiFormula/DoorzoBot/blob/main/botlogodoorzo.png" alt="Logo">
  </a>

  <h3 align="center">Doorzo bot</h3>

  <p align="center">
    Doorzo lookup and utility bot!
    <br />
    <br />
    <br />
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Instructions](#instructions)



<!-- ABOUT THE PROJECT -->
## About The Project

This bot is not affiliated with or owned by Doorzo. It uses data scrapped off doorzo website for informational purposes only.
<br />
<br />
This bot was created in order to display useful information for users on discord related to doorzo and enchance the experience of doorzo's official discord server.
<br />
<br />

### Built With
* [Python](https://python.org)
* [Playwright](https://playwright.dev/)
* [Doorzo](https://www.doorzo.com/?lang=en)

<!-- GETTING STARTED -->
## Instructions

Step 1 | install all requirements, can be found on requirements.txt.

step 2 | open cmd, type the following command
py -m playwright install

Step 2 | setup your bot token in the config

go to config.json and you will see there bot_token replace YOUR_BOT_TOKEN, make sure you don't remove the "

## Command List

* /help
the command will show the list of all commands
* /doorzo (url)
the command will generate an embed with information about the doorzo listing scrapping the data from the site.
* /currencyconverter (amount) (currency)
The command will convert from Japanese Yen to another currency (e.g., USD, EUR, GBP). using https://hexarate.paikama.co/ api.
* /shippingcalculator (weight(g)) (country(first letter capital!))
The command will send information about estimated shipping prices.
* /about
The command will send information about the bot.

## Have fun!
(keep in mind I dont have time to maintain this so feel free to play around with it and feel free to contribute)
