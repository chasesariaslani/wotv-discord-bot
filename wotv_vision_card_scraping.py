import requests
from bs4 import BeautifulSoup
import mysql.connector

#### Database #####
# Initialize MySQL Database
def connect_to_DB():
    mydb = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net",
                                   user="b92e20fe30b01e",
                                   passwd=input("Please input password. \n"))
    mycursor = mydb.cursor()
    return (mydb, mycursor)


#### Scraping ####
website = 'https://warofthevisions.gamepedia.com/Category:Vision_Cards'  # Website to find links 
source = requests.get(website).text
soup = BeautifulSoup(source, 'html.parser')


vision_card_webpage_portion = []
vision_card_name = []
vision_card_webpage_total = []

vision_card_html = soup.find_all(class_="CharacterNavBoxImage2")
for items in vision_card_html:
    for attributes in items:
        try:
            vision_card_webpage_portion.append(attributes['href'])  # Locates links
        except:
            pass


#### Cleaning Data ####
for page in vision_card_webpage_portion:
    vision_card_webpage_total.append('https://warofthevisions.gamepedia.com' + page)


website = vision_card_webpage_total
all_vision_card_information = []
for site in website:
    source = requests.get(site).text
    soup = BeautifulSoup(source, 'html.parser')

    try:
        vision_card_name = soup.find(class_='firstHeading').text.replace('\u200b', '')
        URL = site
        table_stats = soup.find(class_='wikitable').find_all('td')
        table_abilities = soup.find(class_='wikitable').find_all('th')
        self_buff_name = table_abilities[7].text.replace('\xa0Res', '').strip()
        group_buff_name = table_abilities[9].text.replace('\xa0Res', '').strip()
        lvl = table_stats[28].text.strip()
        hp = table_stats[29].text.strip()
        atk = table_stats[30].text.strip()
        mag = table_stats[31].text.strip()
        self_buff_stat = table_stats[32].text.strip()
        group_buff_stat = table_stats[34].text.strip()
        vision_card_information = [vision_card_name, URL, self_buff_name,
                                   group_buff_name, lvl, hp, atk,
                                   mag, self_buff_stat, group_buff_stat]
        all_vision_card_information.append(vision_card_information)

    except AttributeError:
        self_buff_name = '0'  # Zeroes for easy removal in sql database
        group_buff_name = '0'
        lvl = '0'
        hp = '0'
        atk = '0'
        mag = '0'
        self_buff_stat = '0'
        group_buff_stat = '0'
        vision_card_information = [vision_card_name, URL, self_buff_name,
                                   group_buff_name, lvl, hp, atk,
                                   mag, self_buff_stat, group_buff_stat]
        all_vision_card_information.append(vision_card_information)


##### Uploading to SQL Database ####
mydb, mycursor = connect_to_DB()
sql_check = "SELECT * FROM heroku_60221c8fe47759d.vision_cards;"
mycursor.execute(sql_check)
vision_card_check = mycursor.fetchall()
all_vision_card_names_sql = []
for vision_card_name_sql in vision_card_check:
    all_vision_card_names_sql.append(vision_card_name_sql[0])  # Fetches the data from the SQL server as a check


for vision_card_python in all_vision_card_information:  # If data does not exist, send data up to server.
    if vision_card_python in all_vision_card_names_sql:
        print('no insert')
    else:
        upload_vision_cards = "INSERT INTO heroku_60221c8fe47759d.vision_cards\
    (name, url, group_buff, self_buff, vc_level, hp, attack, magic) VALUES\
    (%s, %s, %s, %s, %s, %s, %s, %s);"
        val = (vision_card_python[0], vision_card_python[1],
               vision_card_python[2] + ' + ' + vision_card_python[9],
               vision_card_python[3] + ' + ' + vision_card_python[8],
               vision_card_python[4], vision_card_python[5],
               vision_card_python[6], vision_card_python[7])
        mycursor.execute(upload_vision_cards, val)
        mydb.commit()
