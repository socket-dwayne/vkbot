import time

import cache
import vkapi
from log import datetime_format

def main(a, args):
    dialogs = a.messages.getDialogs(unread=1)['items']
    messages = {}
    users = []
    chats = []
    for msg in dialogs:
        def cb(req, resp):
            messages[req['peer_id']] = resp['items'][::-1]

        a.messages.getHistory.delayed(peer_id=vkapi.utils.getSender(msg['message']), count=min(msg['unread'], 10)).callback(cb)
        if 'chat_id' in msg['message']:
            chats.append(msg['message']['chat_id'])
        else:
            users.append(msg['message']['user_id'])
    uc = cache.UserCache(a, 'online')
    cc = cache.ConfCache(a)
    uc.load(users)
    cc.load(chats)
    a.sync()
    if dialogs:
        print('-------------------------\n')
    else:
        print('Nothing here')
    for msg in dialogs:
        m = msg['message']
        if 'chat_id' in m:
            print('Chat "{}" ({}): {}'.format(cc[m['chat_id']]['title'], m['chat_id'], msg['unread']))
        else:
            print('{} {} ({}){}: {}'.format(uc[m['user_id']]['first_name'], uc[m['user_id']]['last_name'], m['user_id'],
                  ', online' if uc[m['user_id']]['online'] else '', msg['unread']))
        print()
        for i in messages[vkapi.utils.getSender(msg['message'])]:
            print('[{}] {}'.format(time.strftime(datetime_format, time.localtime(i['date'])), i['body']))
            print()
        print('-------------------------\n')
