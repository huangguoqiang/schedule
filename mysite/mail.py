#!usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
import datetime
from email.header import Header
from email.mime.text import MIMEText
from mysite.models import Schedule

__author__ = 'huang'

WEEKDAY_LIST = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

# notify the duty in those days
PRE_NOTIFY_COUNT = 31
POST_NOTIFY_COUNT = 2

# Default email domain
DOMAIN = '@21vianet.com'

# the 1st pair of duty pair in the DUTY_LIST on duty at this date
BASE_DATE = datetime.date(2018, 3, 11)

NORMAL_DUTY_LIST = [
    '---',
    'zhang.yepeng-bl',
    'zhang.yepeng-bl',
    'zhang.yepeng-bl',
    'zhang.yepeng-bl',
    'zhang.yepeng-bl',
    '---',
]

MAIL_TEST = [
    'huang.guoqiang-bl@21vianet.com',
]

MAIL_CC = [
    'zhang.yepeng-bl@21vianet.com',
    'bluemix-paas@21vianet.com',
    'bluemix-cdl-landing@wwpdl.vnet.ibm.com',
    #    'bjwangjq@cn.ibm.com',
    #    'bjzongzw@cn.ibm.com',
    #    'chensl@cn.ibm.com',
    #    'dongnadn@cn.ibm.com',
    #    'harris.hui@hk1.ibm.com',
    #    'huanhy@cn.ibm.com',
    #    'hyanbj@cn.ibm.com',
    #    'jiangjz@cn.ibm.com',
    #    'jiangmk@cn.ibm.com',
    #    'jytjiang@cn.ibm.com',
    #    'lijiajia@cn.ibm.com',
    #    'liudaw@cn.ibm.com',
    #    'liuxubin@cn.ibm.com',
    #    'ljianbj@cn.ibm.com',
    #    'ljibj@cn.ibm.com',
    #    'myuebj@cn.ibm.com',
    #    'pyxie@cn.ibm.com',
    #    'shihuib@cn.ibm.com',
    #    'wyyangbj@cn.ibm.com',
    #    'xuezhiy@cn.ibm.com',
    #    'yahuij@cn.ibm.com',
    #    'yaohaif@cn.ibm.com',
    #    'zhangsj@cn.ibm.com',
    #    '18611869923@wo.cn',
    #    '276808285@qq.com',
    #    'bluemix-paas@21vianet.com',
]


def send_notification(test=False):
    if test:
        print
        'In testing...'
    mail_host = '127.0.0.1'
    mail_port = 25
    mail_user = 'duty_notify'
    mail_postfix = '21vianet.com'
    sender = mail_user + '<' + mail_user + '@' + mail_postfix + '>'

    details_array = []
    date_from = datetime.datetime.today() + datetime.timedelta(days=-1 * POST_NOTIFY_COUNT)
    date_to = datetime.datetime.today() + datetime.timedelta(days=PRE_NOTIFY_COUNT - 1)
    queryset_base = Schedule.objects.filter(date__range=(date_from, date_to)).filter(team_id=1, is_base=False).all()
    old_date = datetime.datetime(1999, 10, 1, 0, 0)
    member_dict = {}
    for obj in queryset_base:
        if old_date < obj.date:
            old_date = obj.date
            member_dict[old_date.strftime('%Y-%m-%d')] =
    for i in range(-1 * POST_NOTIFY_COUNT, PRE_NOTIFY_COUNT, 1):
        loop_date = (datetime.date.today() + datetime.timedelta(days=i))
        # loop_date = 4
        normal_duty_member = get_normal_duty_info(loop_date)
        duty_member = get_duty_info(loop_date)
        details_array.append([loop_date.strftime('%Y-%m-%d'),
                              WEEKDAY_LIST[loop_date.weekday()],
                              normal_duty_member,
                              duty_member])
    # the '[:]' will create a list object to avoid to modify the orig list
    # duty_normal_today =  details_array[POST_NOTIFY_COUNT][1][:]
    duty_today = details_array[POST_NOTIFY_COUNT][3][:]
    duty_tonight = details_array[POST_NOTIFY_COUNT][3][:]
    duty_tomorrow = details_array[POST_NOTIFY_COUNT + 1][3][:]
    duty_tomorrow_night = details_array[POST_NOTIFY_COUNT + 1][3][:]
    mail_to = [item + DOMAIN for item in (duty_today[0] + duty_tonight[1])]

    msg = MIMEText(format_msg_detail(details_array), 'html', 'utf-8')
    msg['Subject'] = Header(
        '21V PaaS Duty Today:[{today_p[0]}({today_p[1]})], [{tonight_p[0]}({tonight_p[1]})]; Duty Tomorrow:[{tomorrow_p[0]}({tomorrow_p[1]})], [{tomorrow_night_p[0]}({tomorrow_night_p[1]})]'.format(
            today_p=NAME_DICT[duty_today[0][0]],
            today_s=NAME_DICT[duty_today[0][1]],
            tonight_p=NAME_DICT[duty_tonight[1][0]],
            tonight_s=NAME_DICT[duty_tonight[1][1]],
            tomorrow_p=NAME_DICT[duty_tomorrow[0][0]],
            tomorrow_s=NAME_DICT[duty_tomorrow[0][1]],
            tomorrow_night_p=NAME_DICT[duty_tomorrow_night[1][0]],
            tomorrow_night_s=NAME_DICT[duty_tomorrow_night[1][1]]),

        'utf-8')
    msg['From'] = sender
    msg['To'] = ','.join(mail_to)
    msg['Cc'] = ','.join(MAIL_CC)

    try:
        s = smtplib.SMTP(mail_host, mail_port)
        s.sendmail(sender, MAIL_TEST if test else (mail_to + MAIL_CC), msg.as_string())
        s.quit()
        print
        'Sent'
    except smtplib.SMTPException as e:
        print
        e


def get_normal_duty_info(date_to_check):
    date_delta = (date_to_check - BASE_DATE).days
    loop_count = date_delta / 1
    loop_index = date_delta % 1
    duty_index_l1 = loop_count % len(NORMAL_DUTY_LIST)
    duty_normal = NORMAL_DUTY_LIST[duty_index_l1][:]
    return duty_normal
