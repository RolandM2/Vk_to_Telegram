import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import gspread
import datetime
import telebot


ID_users = ID_users       # user_id for send message Telegram
token_vk = 'TOKEN'
group_ID = 'group_ID'     # VK group ID
telegram_token = 'token'  # API Telegram token

# VK
# listen to the community, if a new message arrives, trigger an event

def get_user_name(vk_session, link_to_user):
    vk = vk_session.get_api()
    screen_name = link_to_user.split('/')[-1]
    user_id = vk_session.method('users.get', {'user_ids': screen_name})[0]['id']
    user_get = vk.users.get(user_ids=user_id)
    user_get1 = user_get[0]
    first_name = user_get1['first_name']
    last_name = user_get1['last_name']
    full_name = first_name + " " + last_name
    return full_name


def get_vk_message():
    while 1:
        try:
            vk_session = vk_api.VkApi(token=token_vk)
            longpoll = VkBotLongPoll(vk_session, "201763111")
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_REPLY:
                    splitter = event.object.text.split()
                    # print(splitter)
                    link_to_user = splitter[splitter.index('Пользователь:') + 1]  # link for VK page
                    name_parents = get_user_name(vk_session, link_to_user)        # Name VK page
                    forms = splitter[splitter.index('форме:') + 1]                # form
                    time_lid = splitter[splitter.index('отправки:') + 3]          # time user

                    if splitter[splitter.index('Город,') + 3] == 'Вопрос:':       # if no city
                        city = 'н/д'
                    elif splitter[splitter.index('Город,') + 3] == 'Россия,':
                        city = splitter[splitter.index('Город,') + 4]
                    else:
                        city = splitter[splitter.index('Город,') + 3]

                    # find name and age
                    if 0 < len(splitter[splitter.index('ребёнка') + 2]) <= 2:
                        age = splitter[splitter.index('ребёнка') + 2]
                    elif 0 < len(splitter[splitter.index('ребёнка') + 3]) <= 2:
                        age = splitter[splitter.index('ребёнка') + 3]
                    else:
                        age = splitter[splitter.index('ребёнка') + 3]

                    if len(splitter[splitter.index('ребёнка') + 2]) > 2:
                        name = splitter[splitter.index('ребёнка') + 2]
                    elif len(splitter[splitter.index('ребёнка') + 3]) > 2 \
                            and splitter[splitter.index('ребёнка') + 3] != 'Вопрос:':
                        name = splitter[splitter.index('ребёнка') + 3]
                    else:
                        name = 'н/д'

                    phone = splitter[splitter.index('связи') + 2]

                    send_google_sheets_telebot(name, phone, city, link_to_user, age, name_parents, forms, time_lid)

        except Exception as e:                  # Errors
            print("Reconnection", datetime.datetime.now(), e)
            time.sleep(1)
            pass

# write data to Google table
def send_google_sheets_telebot(name='', phone='', city='', link_to_user='', age='', name_parents='', forms='', time_lid=''):
    gc = gspread.service_account('service_account.json')
    sh = gc.open('Name table')

    worksheet = sh.get_worksheet(0)                        # connect sheet
    empty_acell = str(len(worksheet.col_values(1)) + 1)    # find the first empty cell
    # add data 
    worksheet.update('A' + empty_acell, f"{datetime.datetime.now():%d.%m.%Y}")
    worksheet.update('C' + empty_acell, str(name_parents))
    worksheet.update('F' + empty_acell, str(phone.replace("-", '')))
    worksheet.update('D' + empty_acell, str(age))
    worksheet.update('E' + empty_acell, str(name.replace(",", '')))
    worksheet.update('B' + empty_acell, str(city))
    worksheet.update('G' + empty_acell, str(link_to_user))
    worksheet.update('V' + empty_acell, str(forms))
    worksheet.update('W' + empty_acell, str(time_lid))

    # send data to Telegram
    bot = telebot.TeleBot(telegram_token)
    bot.send_message(ID_users, 'New application!\n' 
                               + 'Time: ' + time_lid + '\n' 
                               + 'Name parents: ' + name_parents + '\n' 
                               + 'Name child: ' + name + '\n' 
                               + 'Age: ' + age + '\n' 
                               + 'City: ' + city)
    
    bot.send_message(ID_users, 'Phone: ' + phone.replace('8', '+7', 1))  # replace 8 to +7


if __name__ == '__main__':
    while 1:
        get_vk_message()
