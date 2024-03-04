import telebot
import sqlite3
import json
import re
import schedule #время at_time #как часто period # время и дата next_run
import time
from telebot import types
from datetime import datetime, timedelta
bot=telebot.TeleBot('6600443788:AAE4dA8vLdHeW306IpkuCGVeNIFvA8pJpWY')
days_of_week = {
    'monday': 'понедельник',
    'tuesday': 'вторник',
    'wednesday': 'среда',
    'thursday': 'четверг',
    'friday': 'пятница',
    'saturday': 'суббота',
    'sunday': 'воскресенье'}
class time_data:
    def __init__(self,notification=None,is_postponed=False):
        self.notification=notification #
        self.is_postponed=False # да нет
    def to_json(self):
        '''
        convert the instance of this class to json
        time_data(obj).to_json() #шифруем
        obj=as_time_data(obj) # обратно расшифрорываем
        '''
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)
def set_notofication(day, time, chat_id):
    obj=None
    if day == 'понедельник':
        obj = schedule.every().monday.at(time).do(send_message, chat_id)
    if day == 'вторник':
        obj= schedule.every().tuesday.at(time).do(send_message, chat_id)
    if day == 'среда':
        obj= schedule.every().wednesday.at(time).do(send_message, chat_id)
    if day == 'четверг':
        obj = schedule.every().thursday.at(time).do(send_message, chat_id)
    if day == 'пятница':
        obj = schedule.every().friday.at(time).do(send_message, chat_id)
    if day == 'суббота':
        obj= schedule.every().saturday.at(time).do(send_message, chat_id)
    if day == 'воскресенье':
        obj = schedule.every().sunday.at(time).do(send_message, chat_id)
    return obj
def as_time_data(dct):
    return time_data(dct['notification'], dct['is_postponed'])
# abc=time_data()
# abc.notification=schedule.every().sunday.at('10:00').do(f,'123123') разочарование
# print(schedule.get_jobs())
# print(abc.notification.next_run)
#
# print(json.dumps(abc.notification.__dict__) )
week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
week_dict={week[i]: i for i in range(len(week))}

def find_nearest_weekday(day_of_week):
    '''  0 до 6, где 0 - понедельник, 1 - вторник и т.д.
    :param day_of_week: int(0-6)
    :return: date(2024-02-19)
    '''
    today = datetime.now().date()
    days_ahead = (day_of_week - today.weekday()) % 7
    nearest_date = today + timedelta(days=days_ahead)
    return nearest_date

def substract(times,pred):
    '''
    :param times: ВРЕМЯ НАЧАЛА
    :param pred:  насколько минут надо перенести
    :return: новое время
    '''
    print(pred,123123)
    time=[]
    for time_str in times:
        time_obj = datetime.strptime(time_str, '%H:%M')
        new_time_obj = time_obj - timedelta(minutes=int(pred))
        new_time_str = new_time_obj.strftime('%H:%M')
        time.append(new_time_str)
    return time
def get_day(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')
    return day_of_week
def show_week(message,ind): #added
    '''
    :param message:
    :param ind: параметр который определяет какой callback будет
    :return: день//callback
    '''
    markup = types.InlineKeyboardMarkup()
    dobav_now=()
    button3 = None
    button1 = None
    button2 = None
    for i in range(len(week)):
        if i!=0 and i%3==0:
            markup.add(button1,button2,button3)
            button1 = (types.InlineKeyboardButton(week[i], callback_data=f'{week[i]}//{ind}'))
        if i==len(week)-1:
            button1 = (types.InlineKeyboardButton(week[i], callback_data=f'{week[i]}//{ind}'))
            markup.add(button1)
        elif i%3 ==0:
            button1=(types.InlineKeyboardButton(week[i], callback_data=f'{week[i]}//{ind}'))
        elif i%3 ==1:
            button2 = (types.InlineKeyboardButton(week[i], callback_data=f'{week[i]}//{ind}'))
        elif i % 3 == 2:
            button3 = (types.InlineKeyboardButton(week[i], callback_data=f'{week[i]}//{ind}'))
    return  markup
def buttons_for_notification(callback):
    markup = types.InlineKeyboardMarkup()
    button1 = (types.InlineKeyboardButton('15 минут', callback_data=f'{callback.data[0]}//{callback.data[1]}//15//not_ad'))
    button2 = (types.InlineKeyboardButton('30 минут', callback_data=f'{callback.data[0]}//{callback.data[1]}//30//not_ad'))
    button3 = (types.InlineKeyboardButton('1 час', callback_data=f'{callback.data[0]}//{callback.data[1]}//60//not_ad'))
    markup.add(button1,button2,button3)
    print(markup)
    return markup
def send_message(chat_id):
    bot.send_message(chat_id ,'скоро начнется запланированное событие!')
def start_notification_system():
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT * FROM users")
    slovar = c.fetchall()
    for x in slovar:
     chat_id=x[0]
     dictionary = json.loads(x[1])  # раcшифровали
     for day in dictionary:
         for time in range(len(dictionary[day])):
             if (as_time_data(json.loads(dictionary[day][time][3]))).notification!=None:
                 current=(as_time_data(json.loads(dictionary[day][time][3]))).notification
                 time_now=[dictionary[day][time][0],dictionary[day][time][1]]
                 set_notofication(day,substract(time_now, current)[0],chat_id)
    db.commit()
    db.close()
def add_to_schedule_jobs(message,pred,day,time):
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={message.chat.id}")
    slovar = c.fetchall()[0][0]
    dictionary = json.loads(slovar)
    for i in range(len(dictionary[day])):
        if dictionary[day][i][0]==time[0]:
            obj=as_time_data(json.loads(dictionary[day][i][3]))
            time = [time[0],time[1]]
            print(time, 'помогите',(substract(time, int(pred))))
            scdl=set_notofication(day, (substract(time, int(pred)))[0], message.chat.id)
            date,time1231312=str(scdl.next_run).split(' ')[0],str(scdl.next_run).split(' ')[1][:5]
            obj.notification= pred#days_of_week[get_day(date).lower()],time1231312
            print(obj.notification)
            dictionary[day][i][3]=obj.to_json()
            dictionary = json.dumps(dictionary)
            c.execute("UPDATE users SET slovar=? WHERE user_id=?", (dictionary, message.chat.id))
            bot.send_message(message.chat.id,f'уведомление успешно установленно на {time1231312}, следующее срабатываение пройзойдет {str(scdl.next_run)[:-3]}')

    db.commit()
    db.close()
    return
def del_notification(callback):
    time,day=eval(callback.data[0]),callback.data[1]
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={callback.message.chat.id}")
    slovar = c.fetchall()[0][0]
    dictionary = json.loads(slovar)
    for i in range(len(dictionary[day])):
        print(dictionary[day][i],day,time)
        if dictionary[day][i][0] == time[0]:
            obj = as_time_data(json.loads(dictionary[day][i][3]))
            print(obj.notification)
            if obj.notification == None:
                bot.send_message(callback.message.chat.id, 'на это время не установленно уведомление.')
                db.commit()
                db.close()
                return
            else:
                time_to_delete=substract(time,obj.notification)[0]+':00'#at_time
                print(time_to_delete)
                obj.notification=None
                dictionary[day][i][3] = obj.to_json()
                dictionary = json.dumps(dictionary)
                c.execute("UPDATE users SET slovar=? WHERE user_id=?", (dictionary, callback.message.chat.id))
                for x in schedule.get_jobs():
                    print(x,str(x.at_time),time_to_delete)
                    if str(x.at_time)==time_to_delete:
                        schedule.cancel_job(x)
                        print('работа удалена из оперативной памяти')
                        print(schedule.get_jobs())
                bot.send_message(callback.message.chat.id,'уведомление успешно удалено')
                db.commit()
                db.close()
def choose_time(callback,ind):
    '''
    :param callback:
    :param ind: параметр который определяет какой callback будет
    :return: время//день//callback
    '''
    chat_id=callback.message.chat.id
    markup = types.InlineKeyboardMarkup()
    what_day=callback.data
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={chat_id}")
    slovar = c.fetchall()[0][0]
    dictionary = json.loads(slovar)  # раcшифровали
    for x in dictionary:
        for i in range(len(dictionary[x])):
            dictionary[x][i]=[dictionary[x][i][0],dictionary[x][i][1]]
    day=dictionary[what_day]
    button1=None
    button2=None
    for i in range(len(day)):
        if i == len(day) - 1 and len(day)%3==1:
            button1 = (types.InlineKeyboardButton(f'{day[i][0]}-{day[i][1]}', callback_data=f'{day[i]}//{what_day}//{ind}'))
            markup.add(button1)
        if i==len(day) -2 and len(day)%3==2:
            button1 = (types.InlineKeyboardButton(f'{day[i][0]}-{day[i][1]}', callback_data=f'{day[i]}//{what_day}//{ind}'))
            button2 = (types.InlineKeyboardButton(f'{day[i+1][0]}-{day[i+1][1]}', callback_data=f'{day[i+1]}//{what_day}//{ind}'))
            markup.add(button1,button2)
        elif i % 3 == 0:
            button1 = (types.InlineKeyboardButton(f'{day[i][0]}-{day[i][1]}', callback_data=f'{day[i]}//{what_day}//{ind}'))
        elif i % 3 == 1:
            button2 = (types.InlineKeyboardButton(f'{day[i][0]}-{day[i][1]}', callback_data=f'{day[i]}//{what_day}//{ind}'))
        elif i % 3 == 2:
            button3 = (types.InlineKeyboardButton(f'{day[i][0]}-{day[i][1]}', callback_data=f'{day[i]}//{what_day}//{ind}'))
            markup.add(button1, button2, button3)
    if day==[]:
        db.commit()
        db.close()
        return 'этот день свободен'
    db.commit()
    db.close()
    return markup
def del_messge(message,id):
    bot.delete_message(message.chat.id, message.message_id - id)
def clear_timetable(message):
    db = sqlite3.connect('databaze.db')
    my_dict = {}
    for x in week:
        my_dict[x]=[]
    json_dict = json.dumps(my_dict)
    c = db.cursor()
    c.execute(f"SELECT slovar FROM users WHERE user_id={message.chat.id}")
    slovar = c.fetchall()[0][0]
    dictionary=json.loads(slovar) # расшифровали
    for x in dictionary:
        dictionary[x]=[]
    json_dict = json.dumps(dictionary)  # шифруем обратно
    c.execute("UPDATE users SET slovar=? WHERE user_id=?", (json_dict,message.chat.id))
    db.commit()  # обновление самой базы данных
    db.close()
    for x in schedule.get_jobs():
        schedule.cancel_job(x)
    start_notification_system()
    bot.send_message(message.chat.id, 'ваше расписание успешно очищенно')
def check_time_range(obj): #added
    if isinstance(obj, list) and len(obj) == 2:
        if all(isinstance(item, str) for item in obj):
            time_pattern = re.compile(r'^\d{2}:\d{2}$')
            if time_pattern.match(obj[0]) and time_pattern.match(obj[1]):
                return True
    return False