import mysql.connector
import discord
from discord.ext import commands


# Initialize MySQL Database
def connect_to_DB():
    mydb = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net",
                                   user="b92e20fe30b01e",
                                   passwd=input("Please input password. \n"))
    mycursor = mydb.cursor()
    return (mydb, mycursor)


mydb, mycursor = connect_to_DB()


def esper_name_generator(array):
    new_array = []
    for names in array:
        new_array.append(names[0].lower().strip())  # Name is in different location for esper compared to characters
    return(new_array)


def character_name_generator(array):
    new_array = []
    for names in array:
        if names[2] is None:
            new_array.append(names[1].lower().strip())
        else:
            new_array.append(names[1].lower().strip() + ' ' + names[2].lower().strip())  # Need to add last name as certain characters have the same first name
    return(new_array)


def vision_card_name_generator(array):
    new_array = []
    for names in array:
        name = names[0]
        # print(name)
        name = name.split(',')[0]
        # print(name)
        name = name.split('<')[0]
        # print(name)
        name = name.replace('«', '')
        name = name.replace('»', '')
        name = name.lower()
        new_array.append(name)
    return(new_array)


def last_name(array, i):
    if array[i][2] is not None:  # Certain characters have null values
        return(array[i][2])
    else:
        return('')


def character_names(array, i):  # adds description of character.
    return(f'{array[i][0]}\
    \n Name: {array[i][1]} {last_name(array, i)}\
    \n Jobs: {array[i][4]}, {array[i][5]}, {array[i][6]}\
    \n Master Ability: {array[i][3]}\
    \n HP: {array[i][7]} Attack: {array[i][8]}\
    \n TP: {array[i][9]} Magic: {array[i][10]}\
    \n AP: {array[i][11]} Speed: {array[i][12]}\
    \n Move: {array[i][13]} Dexterity: {array[i][14]}\
    \n Jump: {array[i][15]} Range: {array[i][16]}\
    \n Luck: {array[i][17]} Cost: {array[i][18]}')


# Espers
esper_info = "SELECT * FROM heroku_60221c8fe47759d.espers;"
mycursor.execute(esper_info)
espers = mycursor.fetchall()


def esper_name(array, i):  # adds description of espers
    return(f'{array[i][0]}\
    \n URL: {array[i][1]}\
    \n HP: {array[i][2]} Attack: {array[i][3]}\
    \n TP: {array[i][4]} Magic: {array[i][5]}\
    \n AP: {array[i][6]} Agility: {array[i][7]}\
    \n Dexterity: {array[i][8]} Luck: {array[i][9]}\
    \n Cost: {array[i][9]}')


def vision_card_name(array, i):  # adds description of vision cards
    return(f'{array[i][0]}\
    \n URL: {array[i][1]}\
    \n Group Buff: {array[i][2]}\
    \n Self Buff: {array[i][3]}\
    \n Level: {array[i][4]} HP: {array[i][5]}\
    \n Attack: {array[i][6]} Magic: {array[i][7]}')

# UR characters from DB
ur_info = "SELECT * FROM heroku_60221c8fe47759d.ur_characters;"
mycursor.execute(ur_info)
ur_characters = mycursor.fetchall()


# MR characters from DB
mr_info = "SELECT * FROM heroku_60221c8fe47759d.mr_characters;"
mycursor.execute(mr_info)
mr_characters = mycursor.fetchall()


# SR characters from DB
sr_info = "SELECT * FROM heroku_60221c8fe47759d.sr_characters;"
mycursor.execute(sr_info)
sr_characters = mycursor.fetchall()


# Other characters from DB
other_info = "SELECT * FROM heroku_60221c8fe47759d.other_characters;"
mycursor.execute(other_info)
other_characters = mycursor.fetchall()


# Vision Cards from DB
vision_cards_info = "SELECT * FROM heroku_60221c8fe47759d.vision_cards;"
mycursor.execute(vision_cards_info)
vision_cards = mycursor.fetchall()
# print(vision_cards)


# Creates lists to sift through.
esper_names = esper_name_generator(espers)
ur_names = character_name_generator(ur_characters)
mr_names = character_name_generator(mr_characters)
sr_names = character_name_generator(sr_characters)
other_names = character_name_generator(other_characters)
vision_card_names = vision_card_name_generator(vision_cards)
# print(vision_card_names)

# Discord Bot
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game('WOTV Trial'))
    print('Bot is ready.')


# Pushes messages to discord based on lists.
@client.event
async def on_message(message):
    wotv_content = message.content.lower().replace('wotv', '').strip()
    # print(wotv_content)
    if wotv_content in esper_names:
        esper_location = esper_names.index(wotv_content)
        await message.channel.send(esper_name(espers, esper_location))

    elif wotv_content in ur_names:
        ur_location = ur_names.index(wotv_content)
        await message.channel.send(character_names(ur_characters, ur_location))

    elif wotv_content in mr_names:
        mr_location = mr_names.index(wotv_content)
        await message.channel.send(character_names(mr_characters, mr_location))

    elif wotv_content in sr_names:
        sr_location = sr_names.index(wotv_content)
        await message.channel.send(character_names(sr_characters, sr_location))

    elif wotv_content in other_names:
        other_location = other_names.index(wotv_content)
        await message.channel.send(character_names(other_characters, other_location))

    elif wotv_content in vision_card_names:
        vision_card_location = vision_card_names.index(wotv_content)
        await message.channel.send(vision_card_name(vision_cards, vision_card_location))

    elif wotv_content == 'help':
        author = message.author

        embed = discord.Embed(
        colour=discord.Colour.orange()
        )

        embed.set_author(name='Help')
        embed.add_field(name="Characters", value="Type in wotv and a character's name:\
                        \n Example: wotv vinera fennes", inline=False)
        embed.add_field(name="Espers", value="Type in wotv and an esper's name:\
                        \n Example: wotv ifrit", inline=False)
        embed.add_field(name="Vision Cards", value="Type in wotv and the name*\
                        \n Note: special characters and anything after a comma has been removed.\
                        \n Example: wotv 'rock cliff titan\
                        \n Example: freezer of all\
                        \n Example: long-distance communication device earth" , inline=False)

        await author.send(embed=embed)

    else:
        pass


# Runs the Bot in Discord
client.run('NzEzOTIyMzg4MDIyMDAxNzU0.XsnKCQ.ST7nz7cp1wSs6eVoEIgA5LZzSes')
