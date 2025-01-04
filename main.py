import discord
from discord.ext import commands
from discord import app_commands
import json
import scraper
import translators as ts 
import requests

_ = ts.preaccelerate_and_speedtest()

with open('config.json') as f:
    config = json.load(f)
    print("Config Loaded!")

with open('country_map.json', encoding='utf-8') as f:
    country_map = json.load(f)
    print("Country Map Loaded!")

bot_token = config["bot_token"]

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("------------------------------------")
    print("Bot Name: " + bot.user.name)
    print("Discord Version: " + discord.__version__)
    print("Bot created by Yukio")
    print("------------------------------------")
    await bot.change_presence(activity=discord.Game(name='doorzo kart'))
    await bot.tree.sync()
    print("Commands synced!")

def create_embed(productname,price,img,desc,url):
    embed = discord.Embed(
        title=f"{productname}",
        color=discord.Color.red(), description=desc,url=url
    )
    embed.set_thumbnail(url=img)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1310713923640754238/1312078202360959006/rainbow-line.gif")
    embed.add_field(name="Price", value=f"{price}", inline=True)
    #embed.footer(text="Doorzo Bot Created By Yukio | ALPHA1.0")
    return embed

# Translation function using translators library
def translate(text):
    try:
        return ts.translate_text(text, translator="google", to_language="en")
    except Exception as e:
        return f"Translation error: {e}"

@bot.tree.command(name="doorzo", description="Send funny info about a product page.")
@app_commands.describe(url="The URL of the product page.")
async def doorzo(interaction: discord.Interaction, url: str):
    await interaction.response.defer()  # Acknowledge the interaction immediately
    print("Starting scrape process...")
    user_id = interaction.user.id
    view = DoorzoView(user_id,url)
    try:
        # Call your scraper to get the product data
        scape = await scraper.scrape_product(url)
        if isinstance(scape, str):  # Handle errors from the scraper
            await interaction.followup.send(f"Error: {scape}")
            return

        # Extract and translate data
        productname = scape["product_name"]
        price = scape["price"]
        img = scape["product_image_url"]
        desc = scape["description"]

        print("Scrape process complete. Sending embed...")

        # Create and send the embed
        embed = create_embed(productname=productname, price=price, desc=desc, img=img,url=url)
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send(f"An error occurred: {e}")

class DoorzoView(discord.ui.View):
    def __init__(self, user_id, url):
        super().__init__()
        self.user_id = user_id
        self.url = url
    #TODO: (maybe) add a button to open up the link to the product page from doorzo
    #@discord.ui.button(label="Check it out on Doorzo!", style=discord.ButtonStyle.link)
    #async def checkout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Open the URL for the Doorzo product link
        #button.url = self.url  # Set the button's URL to the one stored in the class
        #await interaction.response.defer()  # Optionally defer the response if you want to acknowledge it
        #print(f"Redirecting to Doorzo URL: {self.url}")

    @discord.ui.button(label="Translate",style=discord.ButtonStyle.primary)
    async def translate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # Acknowledge the interaction immediately
        try:
        # Call your scraper to get the product data
            scape = await scraper.scrape_product(self.url)
            if isinstance(scape, str):  # Handle errors from the scraper
                await interaction.followup.send(f"Error: {scape}")
                return

            # Extract and translate data
            productname = translate(scape["product_name"])
            price = scape["price"]
            img = scape["product_image_url"]
            desc = translate(scape["description"])

            print("Scrape process complete. Sending embed...")
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.edit_message(f"An error occurred: {e}")
        # Create and send the embed
        embed = create_embed(productname=productname, price=price, desc=desc, img=img,url=self.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1310713923640754238/1312078202360959006/rainbow-line.gif")
        await interaction.edit_original_response(embed=embed, view=self)

# The API endpoint to fetch shipment data
API_ENDPOINT = "https://sig.doorzo.com/?n=Sig.Front.Front.ShipmentCalculatorApiWeb&from=INTERNATIONAL&isNew=15&Weight={weight}&Country={country}&T=2&Sort=price_asc"

# Define the slash command
@bot.tree.command(name="shippingcalculator", description="Get shipment price based on country and weight")
@app_commands.describe(weight="The weight of the product in grams.", country="Write the name of your country, start with capital letter for example 'United States'")
async def get_shipment_price(interaction: discord.Interaction, country: str, weight: float):
    # Get the Chinese simplified country name from the country_map
    chinese_country = country_map.get(country, None)
    
    # If the country isn't found in the map, send an error message
    if not chinese_country:
        await interaction.response.send_message(f"Sorry, we couldn't find that country in the list. Please try again with a valid country.")
        return

    # Format the API URL with the correct country and weight
    url = API_ENDPOINT.format(weight=weight, country=chinese_country)

    # Make the request to the API
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()

            # Extract data from the API response
            if 'data' in result and 'info' in result['data']:
                shipment_info = result['data']['info']
                
                # Prepare the response to show prices and carriers
                response_text = f"**Shipment prices for {country} ({chinese_country}) weighing {weight} grams:**\n"
                embed = discord.Embed(title=response_text,color=discord.Color.red(),description="Please keep in mind this is an estimate! prices might change depending on things beyond our control.")
                embed.set_image(url="https://www.doorzo.com/_nuxt/calc_en.35d674cc.png")
                # Loop through each shipping option and format the result
                for shipping in shipment_info:
                    name = shipping['Name']
                    total = shipping['Total']
                    embed.add_field(name=name, value=f"{total} ¥", inline=True)

                    # Format the price information
                    #response_text += f"\n**{name}:** {total} YEN\n"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1310713923640754238/1312078202360959006/rainbow-line.gif")
                await interaction.response.send_message(embed=embed)

            else:
                await interaction.response.send_message("Sorry, no shipment information found for this query.")
        else:
            await interaction.response.send_message("Error fetching data from the API. Please try again later.")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while fetching data: {str(e)}")

# Define the slash command for currency conversion
@bot.tree.command(name="currencyconverter", description="Convert from Japanese Yen to another currency")
@discord.app_commands.describe(amount="Amount in Japanese Yen", target_currency="Target currency (e.g., USD, EUR, GBP)")
async def currency_converter(interaction: discord.Interaction, amount: float, target_currency: str):
    # Define the HexaRate API URL template
    HEXARATE_API_URL = "https://hexarate.paikama.co/api/rates/latest/JPY?target={target_currency}"

    try:
        # Format the API URL with the target currency
        url = HEXARATE_API_URL.format(target_currency=target_currency.upper())
        
        # Fetch the exchange rate from HexaRate API
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Ensure the 'data' and 'mid' are in the response
            if "data" in data and "mid" in data["data"]:
                rate = data["data"]["mid"]
                converted_amount = amount * rate
                
                # Send the conversion result to the user
                #response_text = f"**Currency Conversion:**\n{amount} JPY = {converted_amount:.2f} {target_currency.upper()}"
                embed = discord.Embed(title="Currency Conversion",color=discord.Color.green(), description="Dont know your currency short name? check it here! https://hexarate.paikama.co/iso-code-histories")
                embed.add_field(name="Conversion Rate", value=f"{amount} JPY = {converted_amount:.2f} {target_currency.upper()}", inline=True)
                embed.set_image(url="https://cdn.discordapp.com/attachments/1310713923640754238/1312078202360959006/rainbow-line.gif")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Sorry, conversion for {target_currency.upper()} is not available.")
        else:
            await interaction.response.send_message(f"Error fetching exchange rates. HTTP Status Code: {response.status_code}")
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# About command
@bot.tree.command(name="about", description="Displays information about the bot")
async def about(interaction: discord.Interaction):
    # Bot's ping
    ping = bot.latency * 1000  # Convert to ms

    # Create the embed
    embed = discord.Embed(
        title="Doorzo Bot",
        description="This bot is not affiliated with or owned by Doorzo. It uses data provided through scraping the website for informational purposes only. This bot was created in order to connect doorzo with the discord server and bring better overall user experience to the community",
        color=discord.Color.green()
    )
    embed.add_field(name="Bot Version", value="ALPHA1.0.1", inline=False)
    embed.add_field(name="Ping", value=f"{ping:.2f} ms", inline=True)
    embed.set_image(url="https://media.tenor.com/SYvxuKcTpEUAAAAi/cat-cats.gif")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1311989530689142825/1312347539818676266/botlogodoorzo.png?ex=674c2a63&is=674ad8e3&hm=136a48a0f7f5e90910e93f46c1f470abc2005218ccd9fc071c705b645497c8d6&")
    embed.set_footer(text="Created by Yukio Koito", icon_url="https://i.imgur.com/96n5Juo.png")
    
    await interaction.response.send_message(embed=embed)

#support command
@bot.tree.command(name="support", description="Displays information about doorzo's support")
async def support(interaction: discord.Interaction):
    embed = discord.Embed(title="Need help? - Doorzo is here for you!",description="There isn't much we can do on discord beside answering common knowledge and troubleshooting so for better customer support we suggest you try contacting doorzo's official support by creating a ticket.",colour=0x00b0f4)

    embed.add_field(name="Keep in mind!",value="Doorzo's customer support works between Monday to Friday, 10:30 to 18:30 (JST) or for your timezone from <t:1735954200:t> to <t:1735983000:t>",inline=False)
    embed.add_field(name="How do I open a customer support ticket?",value="keep in mind there is a different between customer support (which is a chatbot that gives you common answers for simple questions) and customer ticket support (which is given to you by a person and not a bot)",inline=False)
    embed.add_field(name="Mobile",value="Go to your account section and scroll down, you will see customer ticket, click on it and you will see the option to create a new ticket.",inline=True)
    embed.add_field(name="Website",value="on doorzo's website look to your right and you will see a small menu with a few options, click on customer ticket and then it will open a new page.\nthere you will be able to create a new customer ticket.",inline=True)
    embed.add_field(name="here is an image that shows how to do it.",value=".",inline=False)

    embed.set_image(url="https://cdn.discordapp.com/attachments/1307950009215488010/1325044894414278758/supportvisual.png?ex=677a5bb8&is=67790a38&hm=eae23a486cb28552f7a4044b20700126b0c78d83e90abb22dac179ad398cb431&")

    embed.set_footer(text="Doorzo Bot")
    await interaction.response.send_message(embed=embed)

# Define the /help command
@bot.tree.command(name="help", description="Display all available commands")
async def help_command(interaction: discord.Interaction):
    # Create an embed for the help message
    embed = discord.Embed(title="Help - Bot Commands", color=discord.Color.blue())
    embed.add_field(name="/help", value="Show this page!", inline=False)
    embed.add_field(name="/about", value="show information about the bot", inline=False)
    embed.add_field(name="/doorzo (url)", value="Show information about doorzo listing", inline=False)
    embed.add_field(name="/currencyconverter (amount) (currency)", value="Convert from Japanese Yen to another currency (e.g., USD, EUR, GBP).", inline=False)
    embed.add_field(name="/shippingcalculator (weight(g)) (country(first letter capital!))", value="Get shipment price based on country and weight.", inline=False)
    embed.add_field(name="/support", value="show information about doorzo support and how to open a customer support ticket")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1310713923640754238/1312078202360959006/rainbow-line.gif")
    # Send the embed with all the available commands
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run(bot_token)
