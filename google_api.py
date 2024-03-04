import pprint #telegram-bot@telegrambot-414710.iam.gserviceaccount.com
from google.oauth2 import service_account #
from googleapiclient.discovery import build
import telebot
import sqlite3
import json
import re
import time
from telebot import types
from datetime import datetime, timedelta
from info_structure import *
bot=telebot.TeleBot('6600443788:AAE4dA8vLdHeW306IpkuCGVeNIFvA8pJpWY')
class gologolome:
    SCOPES=["https://www.googleapis.com/auth/calendar"]
    FILE_PATH = 'telegrambot-414710-3279ff80d61e.json'
    def __init__(self):
        credentials= service_account.Credentials.from_service_account_file(filename=self.FILE_PATH, scopes=self.SCOPES)
        self.service = build('calendar','v3',credentials=credentials)
    def get_calendar_list(self):
        return self.service.calendarList().list().execute()
    def insert_new_id(self,calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }
        return  self.service.calendarList().insert(body=calendar_list_entry).execute()
    def add_event(self,calendar_id,event):
        return self.service.events().insert(calendarId=calendar_id, body=event).execute()

 # "RRULE:FREQ=WEEKLY;BYDAY=MO"
# event = {
#   'summary': 'Google I/O 2015',
#   'location': '800 Howard St., San Francisco, CA 94103',
#   'description': 'A chance to hear more about Google\'s developer products.',
#   'start': {
#     'dateTime': '2015-05-28T09:00:00-07:00',
#   },
#   'end': {
#     'dateTime': '2015-05-28T17:00:00-07:00',
#   },
#   'recurrence': [
#     'RRULE:FREQ=WEEKLY;COUNT=2'
#   ],
# }
# obj=gologolome()
# obj.add_event('s09t05@gmail.com',event)
# gologolome.insert_new_id(obj,'s09t05@gmail.com')
def finaly_add_to_google_calendar(callback):
   " время // день // callback"
   obj = gologolome()
   time,day=eval(callback.data[0]),callback.data[1]
   db = sqlite3.connect('databaze.db')
   c = db.cursor()
   c.execute(f"SELECT google_id FROM users_google WHERE user_id={callback.message.chat.id}")
   id = c.fetchall()[0][0]
   c.execute(f"SELECT slovar FROM users WHERE user_id={callback.message.chat.id}")
   slovar = c.fetchall()[0][0]
   dictionary = json.loads(slovar)

   date=find_nearest_weekday(week_dict[day])
   print(date,time[0]) #f'{date}T{time[0]}
   event = {
    'summary': 'название',
    'description': '',
    'start': {'dateTime': f'{date}T{time[0]}:00',
              'timeZone': 'Europe/Moscow'},
    'end': {'dateTime': f'{date}T{time[1]}:00',
              'timeZone': 'Europe/Moscow'},
    'recurrence': ['RRULE:FREQ=WEEKLY']
}

   print(event,id)
   obj.add_event(id,event)
   pprint.pprint(obj.add_event(id,event))
   bot.send_message(callback.message.chat.id,'запись успешно добавленна в ваш гугл календарь')
   db.commit()
   db.close()


def check_if_google_connected(message):
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT google_id FROM users_google WHERE user_id={message.chat.id}")
    id = c.fetchall()[0][0]
    db.commit()
    db.close()
    print(id,123123123123123)
    if id != None: return True
    else: return False


def add_id(message):
    indificator=message.text[0]
    print(indificator)
    obj = gologolome()
    gologolome.insert_new_id(obj,indificator)
    db = sqlite3.connect('databaze.db')
    c = db.cursor()
    c.execute(f"SELECT google_id FROM users_google WHERE user_id={message.chat.id}")
    id=c.fetchall()
    print(id)
    if id!=None:
        c.execute("UPDATE users_google SET google_id=? WHERE user_id=?", (indificator, message.chat.id))
        bot.send_message(message.chat.id,'вы уже привязали календарь к боту')
        db.commit()
        db.close()
        return
    else:
        c.execute("UPDATE users_google SET google_id=? WHERE user_id=?", (indificator, message.chat.id))
        db.commit()
        db.close()
        bot.send_message(message.chat.id,'ваш календарь успешно привязан')








calendar='s09t05@gmail.com'
obj=gologolome()
# event=obj.add_event(calendar_id=calendar,body=event)
pprint.pprint(obj.get_calendar_list())
# obj.insert_new_id(calendar_id='s09t05@gmail.com')
# pprint.pprint(obj.get_calendar_list())
