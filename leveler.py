####################################################################
#                                                                  #
#    Credit: therealOri  |  https://github.com/therealOri          #
#                                                                  #
####################################################################

####################################################################################
#                                                                                  #
#                            Imports & definitions                                 #
#                                                                                  #
####################################################################################
import asyncio
import discord
import os
from discord import app_commands
import datetime
from libs import rnd
import tomllib
import time
import logging
import sqlite3



#Load our config for main
with open('config.toml', 'rb') as fileObj:
    config = tomllib.load(fileObj) #dictionary/json




__authors__ = '@therealOri'
token = config["TOKEN"]
guild_id = config["guild_id"]
MY_GUILD = discord.Object(id=guild_id)
bot_logo = config["bot_logo"]
author_logo = None



hex_red=0xFF0000
hex_green=0x0AC700
hex_yellow=0xFFF000 # I also like -> 0xf4c50b

# +++++++++++ Imports and definitions +++++++++++ #














####################################################################################
#                                                                                  #
#                             Normal Functions                                     #
#                                                                                  #
####################################################################################
def clear():
    os.system("clear||cls")



def random_hex_color():
    hex_digits = '0123456789abcdef'
    hex_digits = rnd.shuffle(hex_digits)
    color_code = ''
    nums = rnd.randint(0, len(hex_digits)-1, 6)
    for _ in nums:
        color_code += hex_digits[_]
    value =  int(f'0x{color_code}', 16)
    return value



def load_config():
    #Load our config when we want.
    with open('config.toml', 'rb') as fileObj:
        config = tomllib.load(fileObj) #dictionary/json
    return config
# +++++++++++ Normal Functions +++++++++++ #













####################################################################################
#                                                                                  #
#                Async Functions, buttons, modals, classes, etc.                   #
#                                                                                  #
####################################################################################
async def status():
    while True:
        status_messages = ['my internals', '/help for help', 'your navigation history', 'myself walking on the grass', 'Global Global Global', 'base all your 64', 'your security camera footage', 'myself walking on the moon', 'your browser search history']
        smsg = rnd.choice(status_messages)
        activity = discord.Streaming(type=1, url='https://www.youtube.com/watch?v=4xDzrJKXOOY', name=smsg)
        await lvler.change_presence(status=discord.Status.online, activity=activity)
        await asyncio.sleep(60) #Seconds




class LevelingSystem:
    def __init__(self, db_name, lvler):
        self.conn = sqlite3.connect(db_name)
        self.lvler = lvler

    def __del__(self):
        self.conn.close()

    def get_cursor(self, guild_id, table_name):
        self.create_table(self.conn, guild_id, table_name)
        return self.conn.cursor()

    def load_config(self):
        return load_config()

    async def on_message(self, message):
        config = self.load_config()
        channel = message.channel.id
        ignore_channels = config["leveling"]["ignore_channels"]

        if channel in ignore_channels: #ignore messages sent in certain channels in your guild.
            return

        guild_id = message.guild.id
        table_name = f"guild_{guild_id}"
        c = self.get_cursor(guild_id, table_name)
        level = 0
        exp = 0

        user = message.author.id
        xp = config["leveling"]["xp"]
        if message.author == self.lvler.user:  # Ignores itself
            self.conn.close()
            return


        try:
            res = c.execute(f"SELECT user_id, level, exp FROM {table_name} WHERE user_id=?", (user,))
            user_data = res.fetchone()
        except sqlite3.Error as e:
            user_data = None

        if user_data is None:
            row = [user, level, exp]  # defaults
            c.execute(f"INSERT INTO {table_name} VALUES (?, ?, ?)", row)
            self.conn.commit()
            return
        else:
            try:
                c.execute("BEGIN TRANSACTION")
                user_id, current_level, current_exp = user_data

                updated_exp = current_exp + xp

                # This can be modified. (Add levels, change levels, exp required, etc.)
                milestones = {
                    "level 1": 3750,
                    "level 5": 20250,
                    "level 10": 52500,
                    "level 15": 78750,
                    "level 20": 105000,
                    "level 30": 178500,
                    "level 40": 303450,
                    "level 50": 515865,
                    "level 60": 876961,
                    "level 70": 1492831,
                    "level 80": 2537611,
                    "level 90": 5072221,
                    "level 100": 10144445
                }

                for milestone_lvl, milestone_exp in milestones.items():
                    if updated_exp >= milestone_exp:
                        new_level = int(milestone_lvl.split()[1])
                        if new_level > current_level:
                            c.execute(f"UPDATE {table_name} SET exp=?, level=? WHERE user_id=?", (updated_exp, new_level, user,))
                            self.conn.commit()

                            rnd_hex = self.random_hex_color()
                            level_embed = discord.Embed(
                                title=f'🎉 Level up!! 🪅\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n**@{message.author}** has leveled up to **{milestone_lvl}**!',
                                colour=rnd_hex,
                                timestamp=datetime.datetime.now(datetime.timezone.utc)
                            )
                            level_embed.set_thumbnail(url=message.author.display_avatar)
                            level_embed.add_field(name='\u200B\n', value='-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
                            level_embed.set_footer(text=__authors__, icon_url=author_logo)
                            channel = self.lvler.get_channel(channel)
                            await channel.send(embed=level_embed)
                            break
                else:
                    c.execute(f"UPDATE {table_name} SET exp=? WHERE user_id=?", (updated_exp, user,))
                    self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error updating database: {e}")
                self.conn.rollback()
                return


    @staticmethod #to be used in this class
    def random_hex_color():
        hex_digits = '0123456789abcdef'
        hex_digits = rnd.shuffle(hex_digits)
        color_code = ''
        nums = rnd.randint(0, len(hex_digits)-1, 6)
        for _ in nums:
            color_code += hex_digits[_]
        value =  int(f'0x{color_code}', 16)
        return value


    @staticmethod
    def create_table(conn, guild_id, table_name):
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                user_id TEXT,
                level INTEGER,
                exp INTEGER
            )
        """)
        conn.commit()
# +++++++++++ Async Functions, buttons, modals, etc. +++++++++++ #












####################################################################################
#                                                                                  #
#                                Client Setup                                      #
#                                                                                  #
####################################################################################
class LVR(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        #self.tree.copy_global_to(guild=MY_GUILD)  # This copies your commands over to your guild for immediate access for testing while you wait for discord to register all of the commands.
        await self.tree.sync(guild=None)



intents = discord.Intents.default()
intents.messages = True
lvler = LVR(intents=intents)
# +++++++++++ Client Setup +++++++++++ #










####################################################################################
#                                                                                  #
#                                   Events                                         #
#                                                                                  #
####################################################################################
@lvler.event
async def on_ready():
    global author_logo
    me = await lvler.fetch_user(254148960510279683)
    author_logo = me.avatar
    lvler.loop.create_task(status())

    clear()
    print(f'Logged in as {lvler.user} (ID: {lvler.user.id})')
    print('------')





@lvler.event
async def on_message(message):
    leveling_system = LevelingSystem('user_levels.db', lvler)
    await leveling_system.on_message(message)
# +++++++++++ Events +++++++++++ #













####################################################################################
#                                                                                  #
#                             Regular Commands                                     #
#                                                                                  #
####################################################################################
@lvler.tree.command(description='Shows you what commands you can use.')
async def help(interaction: discord.Interaction):
    rnd_hex = random_hex_color()
    embed = discord.Embed(title='Commands  |  Help\n-=-=-=-=-=-=-=-=-=-=-=-=-=-', colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=bot_logo)
    embed.add_field(name='\u200B\n/help', value="Shows you this help message.", inline=True)
    embed.add_field(name='\u200B\n/ping ', value="Checks the bots connection & if it is responsive.", inline=True)
    embed.add_field(name="\u200B\n", value="\u200B\n-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)
    embed.set_footer(text=__authors__, icon_url=author_logo)
    await interaction.response.send_message(embed=embed, ephemeral=True)




@lvler.tree.command(description='Test to see if the bot is responsive.')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"⏱️ Pong! ⏱️\nConnection speed is {round(lvler.latency * 1000)}ms", ephemeral=True)

# +++++++++++ Regular Commands +++++++++++ #


















if __name__ == '__main__':
    clear()
    lvler.run(token, reconnect=True, log_level=logging.INFO) #log_handler is also an option for if you have your own way of handling logging, etc.
