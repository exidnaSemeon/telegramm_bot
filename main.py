import telebot
import sqlite3
import json
import re
import schedule
import time
from info_structure import *
#start_notification_system()

from telebot import types
bot=telebot.TeleBot('6600443788:AAE4dA8vLdHeW306IpkuCGVeNIFvA8pJpWY')
week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
litle_week=['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
litle_week_dict={}
time_pattern1 = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]$')  # 10:00-9:00
time_pattern2 = re.compile(r'^([01][0-9]|2[0-3])[0-5][0-9]$') # 1000
time_pattern3 = re.compile(r'^([01]?[0-9]|2[0-3])[0-5][0-9]-([01]?[0-9]|2[0-3])[0-5][0-9]$') #1000-1100
notification_pattern = re.compile(r'^\d{1,2}$|^[1][0-1]\d$|^120$')# проверяет что меньше 120 и подхоит под шаблон
for i in range(len(week)):
    litle_week_dict[litle_week[i]]=week[i]



@bot.message_handler(commands=['commands_list'])
def show_comand_list(message):
    print(message.from_user.first_name)
    chat_id = message.chat.id
    bot.send_message(chat_id,'''  
/show_my_timetable - с помощью этой команды вы можете увидеть своё расписание
/change_my_timetable - с помощью этой команды можно как добавить новое время, так и удалить старое
add day/time/note- с помощью такой записи можно добавить нужное время \n к примеру: вт/0830/завтрак с помощью такой записи вы запланируете событие на час\n или понедельник/1500-1600/обед так можно запланировать событие на определенный промежуток времени 
 ''')



@bot.message_handler(commands=['start'])
def start(message):
    print(message.from_user.first_name)
    markup=types.InlineKeyboardMarkup()
    button1 = (types.InlineKeyboardButton('список команд', callback_data='command_list'))
    button2 = (types.InlineKeyboardButton('информация о боте', callback_data='info'))
    markup.add(button1, button2)
    register(message)
    msg=bot.send_message(message.chat.id,'Вас приветствует meeting_planner\nНиже можете ознакомится с командами и функциями бота ',reply_markup=markup)

@bot.message_handler(commands=['register'])
def register(message):
    db = sqlite3.connect('databaze.db')
    my_dict = {}
    for x in week:
        my_dict[x]=[]
    json_dict = json.dumps(my_dict)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(user_id int,slovar text) ")
    c.execute("SELECT user_id FROM users")
    users=c.fetchall()
    for x in users:
        if x[0]==message.chat.id:
            print('user_already_registered')
            db.commit()
            db.close()
            # bot.send_message(message.chat.id,'Вы уже зарегистрированы')
            return True
    c.execute('INSERT INTO users (user_id, slovar) VALUES (? , ?)', (message.chat.id, json_dict))
    c.execute("SELECT * FROM users ")
    db.commit()  # обновление самой базы данных
    db.close()
    bot.send_message(message.chat.id, 'Регистрация прошла успешно, можете приступать к использованию!')
    return True
@bot.message_handler(commands=['change_my_timetable'])
def change_diolog(message):
    print(message.from_user.first_name)
    markup = types.InlineKeyboardMarkup()
    button1 = (types.InlineKeyboardButton('добавить новое время в расписание', callback_data='add_time'))
    button2 = (types.InlineKeyboardButton('убрать старые записи', callback_data='del_time_day'))
    markup.add(button1)
    markup.add(button2)
    msg = bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',reply_markup=markup)


@bot.message_handler(commands=['show_my_timetable'])
def show_timetable(message):
    chat_id=message.chat.id
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={chat_id}")
    slovar = c.fetchall()[0][0]
    dictionary=json.loads(slovar)

    otv=''
    for day in dictionary:
        if dictionary[day]==[]:
            otv+=f'{day}: \n полностью свободен \n'
        else:
            otv+=f'в {day} заняты следующие часы: \n'
            for hours in dictionary[day]:

                otv+=f'{hours[0]} - {hours[1]} -- {hours[2]}\n'
            otv+='\n'
    bot.send_message(chat_id,otv)
    db.commit()
    db.close()

@bot.message_handler(commands=['add_notifications']) #to_do
def notification_add_choose_day(message):
    markup = show_week(message, 'notification')
    bot.send_message(message.chat.id,'выберите день недели, в котором хотите включить уведомления',reply_markup=markup)

def notification_add_choose_time(callback): #to_do
    chat_id=callback.message.chat.id
    markup = choose_time(callback, 'notification_time')
    if markup == 'этот день свободен': bot.send_message(chat_id, 'этот день свободен')
    bot.send_message(chat_id, 'выберите время, для которого хотите включить уведомления', reply_markup=markup)
def notification_add_choose_time_2(callback):
    print(callback.data,123123)
    '''
    :param callback: callback.data= time/day
    :return: callback.data= time/day/notification_time
    '''
    time,day=callback.data[0],callback.data[1]
    markup=buttons_for_notification(callback)
    bot.send_message(callback.message.chat.id,'за какое количество времени вас предупретить?',reply_markup=markup)



@bot.callback_query_handler(func= lambda callback: True)
def callbackmessage(callback):
        print(callback.data)
        command= callback.data.split('//')[-1]
        if command=='info':
            bot.send_message(callback.message.chat.id,'на данный момент в этом боте вы можете составить своё расписание')
        elif command=='command_list':
            show_comand_list(callback.message)
        elif command=='add_time':
            change_timetable_add(callback.message)
        elif command=='del_time_day':
            choose_day(callback.message)
        elif command=='notification':
            callback.data = callback.data.split('//')[0]
            notification_add_choose_time(callback)
        elif command == 'notification_time':
            callback.data = callback.data.split('//')[:2]
            notification_add_choose_time_2(callback)
        elif command=='del' :
            callback.data=callback.data.split('//')[0]
            choose_time_del(callback)
        elif command =='del1':
            callback.data=callback.data.split('//')
            finaly_delete_data(callback)
        elif command=='not_ad':
            callback.data = callback.data.split('//')[:-1]
            add_to_schedule_jobs(callback)
            pass


def finaly_delete_data(callback):
    '''
    :param callback: callback.data=['время','день недели']
    :return:
    '''
    day = callback.data[1]
    time=eval(callback.data[0])
    chat_id = callback.message.chat.id
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={chat_id}")

    slovar = c.fetchall()[0][0]
    dictionary = json.loads(slovar)  # разшифровали
    for i in range(len(dictionary[day])):
        if dictionary[day][i][0]==time[0]:
            dictionary[day].pop(i)
            bot.send_message(chat_id, 'запись удалена')
            json_dict = json.dumps(dictionary)  # шифруем обратно
            c.execute("UPDATE users SET slovar=? WHERE user_id=?", (json_dict, chat_id))
            db.commit()
            db.close()
            return
    bot.send_message(chat_id, 'эта запись уже удалена')
    db.commit()
    db.close()
    return

def choose_time_del(callback):
    chat_id=callback.message.chat.id
    markup=choose_time(callback,'del1')
    if markup=='этот день свободен': bot.send_message(chat_id, 'этот день свободен')
    else: bot.send_message(chat_id,'какое время хотите удалить?',reply_markup=markup)

def choose_day(message):
    markup = show_week(message,'del')# создает кнопки с callbackdata в виде команджы del и днем недели
    print(markup)
    bot.send_message(message.chat.id,'выберите день недели, в котором хотите убрать время',reply_markup=markup)

def change_timetable_add(message): #следующе сообщение будет воспринято как добавление нового времени
    bot.send_message(message.chat.id,'Введи день недели и время которое хочешь добавить через / так же вы можете ввести событие которым занято это время а также установить напминание\n пример: понедельник/10:00-12:00/обед/15 такая запись добавит в ваше расписание обытие обед с 10-12 и напомнит вам о нем за 15 минут')
    bot.register_next_step_handler(message, change_timetable_add123)
def change_timetable_add123(message): #to_do
    '''
    :param message:
    :return: добавляет время в нашще распиание
    '''
    chat_id=message.chat.id
    note, day, time,notification= split_add(message.text)
    if any([note==None,day==None,time==None,notification==None]):
        print(note==None,day==None,time==None,notification==None)
        bot.send_message(chat_id,'некоректно введены данные')
        return
    # try:
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={chat_id}")
    slovar = c.fetchall()[0][0]
    dictionary=json.loads(slovar) # расшифровали
    time=time.split('-')
    if not check_if_overlaps(dictionary[day],time):
            time=sorted(time)
            time.append(note)
            if notification=='':
                time.append(((time_data(None).to_json())))
            else:
                time.append(((time_data(notification).to_json())))
            print(time,day,123123123123)
            dictionary[day].append(time)
            dictionary[day]=sorted(dictionary[day], key=lambda x: (int(x[1].replace(':',''))))
            json_dict = json.dumps(dictionary) #шифруем обратно
            print(json_dict)
            c.execute("UPDATE users SET slovar=? WHERE user_id=?",(json_dict,chat_id))
            db.commit()
            db.close()

            bot.send_message(message.chat.id, 'время успешно добавлено')
    else:
        db.commit()
        db.close()
        bot.send_message(message.chat.id,'это время накладывается на другое в вашем расписании')

    # except:
        bot.send_message(message.chat.id, 'что то пошло не так, поробуйте снова')

def split_add(text): #обработка текста который ввел пользователь при добавлении времени #to_do
    text = text.split('/') #
    text = [litle_week_dict[x] if x in litle_week else x for x in text]
    note,week_day,time,notification=None,None,None,None
    for x in text:
        x=x.lower()

        if time_pattern1.match(x) and time==None:
            time=x
        elif time_pattern2.match(x) and time==None:
            time = x[:2] + ':' + x[2:] + '-'
            if x[1] == '9' and x[0] != 2:


                x = str(int(x[0]) + 1)+'0'+':'+x[2:]
                time+=x
            else:
                time += x[0] + str(int(x[1]) + 1) + ':' + x[2:]
        elif time_pattern3.match(x) and time == None:
            x=x.replace('-','')

            x=f'{x[:2]}:{x[2:4]}-{x[4:6]}:{x[6:]}'

            time=x
        elif notification_pattern.match(x) and notification==None:
            notification=x
        elif x in week or x in litle_week and week_day==None:
            week_day=x
        else:
            note=x

    if note==None: note=''
    if notification==None: notification=''

    return note,week_day,time,notification


def check_if_overlaps(day,new_time):
    '''
    :param day: mas         тут записано всё время занятое в конкретный день
    :param new_time: mas         время которое мы хотим добавить
    :return: bool        выводим накладывается или нет
    '''
    start= int(new_time[0].replace(':', ''))
    end = int(new_time[1].replace(':', ''))
    for x in day:
        current_start=int(x[0].replace(':', ''))
        current_end=int(x[1].replace(':', ''))
        if end <= current_start or current_end <= start:
            continue
        else:
            return True
    return False




@bot.message_handler(content_types=['text']) #
def define_a_command(message):
    command=message.text.split(' ', 1)[0].strip() #смотрим какая команда
    message.text=message.text.split(' ', 1)[1]
    print(command)
    if command=='add':
        change_timetable_add123(message)



bot.polling(none_stop=True)#чтобы всегда работало

while True:#
    schedule.run_pending()
    time.sleep(1)