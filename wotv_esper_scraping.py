from bs4 import BeautifulSoup
import pandas as pd
import requests
import mysql.connector


# Initialize MySQL Database
def connect_to_DB():
    mydb = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net",
                                   user="b92e20fe30b01e",
                                   passwd=input("Please input password. \n"))
    mycursor = mydb.cursor()
    return (mydb, mycursor)


#### Scraping ####
webpage = 'http://wotvffbe.gamea.co'
source = requests.get('http://wotvffbe.gamea.co/c/hzpwnmyd').text
soup = BeautifulSoup(source, 'html.parser')

esper_page = []
esper_name = []
webpage_and_name = []
esper_stat_tables = []
stat_table = {}


esper_url_location = soup.find(class_='at-md').find_all('a')
for url in esper_url_location:
    esper_page.append(webpage + url.get('href'))  # finds url to combine to find esper page
    esper_name.append(url.find('img').get('alt'))  # finds names of espers

for webpage, name in zip(esper_page, esper_name):
    webpage_and_name.append((name, webpage))

for url in esper_page:
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    for table in soup.find_all('table'):
        try:
            if table.tr.th.text == 'HP':
                esper_stat_tables.append([url, table.text])  # finds 1 star and 2 star tables
        except (AttributeError, ValueError):
            print("Value Missing")
            pass


#### Data Cleaning ####
data = {'webpage': esper_page, 'name': esper_name}

esper_df = pd.DataFrame(data=data, columns=['webpage', 'name'])  # I did this to use the order of the rows as a tool. Probably a much better way.


for item in esper_stat_tables:

    esp_name = esper_df.loc[esper_df['webpage'] == item[0]]['name'].values[0]  # finds location of name based on url
    item.append(esp_name)

# print(esper_stat_tables)

for item in esper_stat_tables:
    stat_table[item[2]] = {}

    esp_url = esper_df.loc[esper_df['name'] == item[2]]['webpage'].values[0]
    stat_table[item[2]]['URL'] = esp_url

    strip_hp = item[1].lower().replace('hp', '')
    if strip_hp[0].isdigit():
        stat_table[item[2]]['HP'] = strip_hp[0:3]  # Always in hundreds.
        strip_atk = strip_hp[3:].replace('atk', '')
    else:
        stat_table[item[2]]['HP'] = 'empty'
        strip_atk = strip_hp


    if strip_atk[2].isdigit():
        stat_table[item[2]]['ATK'] = strip_atk[0:3]
        strip_tp = strip_atk[3:].replace('tp', '')
    elif strip_atk[1].isdigit():
        stat_table[item[2]]['ATK'] = strip_atk[0:2]
        strip_tp = strip_atk[2:].replace('tp', '')
    elif strip_atk[0].isdigit():
        stat_table[item[2]]['ATK'] = strip_atk[0:1]
        strip_tp = strip_atk[1:].replace('tp', '')
    else:
        stat_table[item[2]]['ATK'] = 'empty'
        strip_tp = strip_atk

    if strip_tp[1].isdigit():
        stat_table[item[2]]['TP'] = strip_tp[0:2]
        strip_mag = strip_tp[2:].replace('mag', '')

    elif strip_tp[0].isdigit():
        stat_table[item[2]]['TP'] = strip_tp[0:1]
        strip_mag = strip_tp[1:].replace('mag', '')
    else:
        stat_table[item[2]]['TP'] = 'empty'
        strip_mag = strip_tp

    if strip_mag[2].isdigit():
        stat_table[item[2]]['MAG'] = strip_mag[0:3]
        strip_ap = strip_mag[3:].replace('ap', '')
    elif strip_mag[1].isdigit():
        stat_table[item[2]]['MAG'] = strip_mag[0:2]
        strip_ap = strip_mag[2:].replace('ap', '')
    elif strip_mag[0].isdigit():
        stat_table[item[2]]['MAG'] = strip_mag[0:1]
        strip_ap = strip_mag[1:].replace('ap', '')        
    else:
        stat_table[item[2]]['MAG'] = 'empty'
        strip_ap = strip_mag

    if strip_ap[0].isdigit():
        stat_table[item[2]]['AP'] = strip_ap[0:2]  # Always in 10's
        strip_agi = strip_ap[2:].replace('agi', '')
    else:
        stat_table[item[2]]['AP'] = 'empty'
        strip_agi = strip_ap

    if strip_agi[1].isdigit():
        stat_table[item[2]]['AGI'] = strip_agi[0:2]
        strip_dex = strip_agi[2:].replace('dex', '')
    elif strip_agi[0].isdigit():
        stat_table[item[2]]['AGI'] = strip_agi[0:1]
        strip_dex = strip_agi[1:].replace('dex', '')
    else:
        stat_table[item[2]]['AGI'] = 'empty'
        strip_dex = strip_agi

    if strip_dex[0].isdigit():
        stat_table[item[2]]['DEX'] = strip_dex[0:2]  # Always in 10's
        strip_luck = strip_dex[2:].replace('luck', '')
    else:
        stat_table[item[2]]['DEX'] = 'empty'
        strip_luck = strip_dex

    if strip_luck[0].isdigit():
        stat_table[item[2]]['LUCK'] = strip_luck[0:2]  # Always in 10's
        strip_cost = strip_luck[2:].replace('cost','')
    else:
        stat_table[item[2]]['LUCK'] = 'empty'
        strip_cost = strip_luck

    if strip_cost is not None and strip_cost[0:3] != 'atk':
        stat_table[item[2]]['COST'] = strip_cost
    else:
        stat_table[item[2]]['COST'] = 'empty'


#### Pushing Data ####
mydb, mycursor = connect_to_DB()
sql_check = "SELECT * FROM heroku_60221c8fe47759d.espers;"
mycursor.execute(sql_check)
esper_check = mycursor.fetchall()
all_esper_names_sql = []
for esper_name_sql in esper_check:
    all_esper_names_sql.append(esper_name_sql[0])  # Fetches the data from the SQL server as a check


for esper_name_python in stat_table:  # Checks if data scraped is different from the SQL data.
    if esper_name_python in all_esper_names_sql:
        print('no insert')
    else:
        sql1 = "INSERT INTO heroku_60221c8fe47759d.espers (name, hp) VALUES (%s, %s);"
        val = (esper_name, 1)  # added a 1 because I could not get it to work UNLESS I had two values. Will look into.
        mycursor.execute(sql1, val)
        mydb.commit()


for esper_name_python in stat_table:
    url = stat_table[esper_name_python]['URL']
    if url == 'empty':
        url = 0

    hp = stat_table[esper_name_python]['HP']
    if hp == 'empty':
        hp = 0

    attack = stat_table[esper_name_python]['ATK']
    if attack == 'empty':
        attack = 0

    tp = stat_table[esper_name_python]['TP']
    if tp == 'empty':
        tp = 0

    agility = stat_table[esper_name_python]['AGI']
    if agility == 'empty':
        agiltiy = 0

    magic = stat_table[esper_name_python]['MAG']
    if magic == 'empty':
        magic = 0

    ap = stat_table[esper_name_python]['AP']
    if ap == 'empty':
        ap = 0

    dexterity = stat_table[esper_name_python]['DEX']
    if dexterity == 'empty':
        dexterity = 0

    luck = stat_table[esper_name_python]['LUCK']
    if luck == 'empty':
        luck = 0

    cost = stat_table[esper_name_python]['COST']
    if cost == 'empty':
        cost = 0

    sql_update_stats = "UPDATE heroku_60221c8fe47759d.espers SET url=%s, hp=%s,\
        attack=%s, tp=%s, agility=%s, magic=%s, ap=%s, dexterity=%s,\
        luck=%s, cost=%s WHERE name = %s;"
    val = (url, hp, attack, tp, agility, magic, ap, dexterity, luck, cost, esper_name_python)
    mycursor.execute(sql_update_stats, val)
    mydb.commit()