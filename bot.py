
import requests
import json

TOKEN = '7800947883:AAEqWXq-apF0pQCTlRPP5AWJtQL-L8zCvhI'
BOT_USERNAME = 'EterafChatBot'
API = f'https://api.telegram.org/bot{TOKEN}/'
ADMIN_ID = 8183296620
CHANNEL_USERNAME = '@KOCSHER_IR'

users = {}
blocked = set()
reply_map = {}
mode = {}

def send(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    requests.post(API + 'sendMessage', data=data)

def check_member(user_id):
    r = requests.get(API + f'getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}').json()
    try:
        return r['result']['status'] in ['member', 'administrator', 'creator']
    except:
        return False

def keyboard(btns):
    return {'keyboard': [[{'text': b}] for b in btns], 'resize_keyboard': True}

def inline_button(text, url_or_data, url=True):
    key = 'url' if url else 'callback_data'
    return {'inline_keyboard': [[{key: url_or_data, 'text': text}]]}

def get_updates(offset=None):
    r = requests.get(API + 'getUpdates', params={'timeout': 100, 'offset': offset}).json()
    return r['result']

offset = None

while True:
    updates = get_updates(offset)
    for u in updates:
        offset = u['update_id'] + 1

        if 'message' in u:
            m = u['message']
            cid = m['chat']['id']
            text = m.get('text', '')
            uname = m['from'].get('username', 'ندارد')
            users[cid] = uname

            if cid in blocked:
                continue

            if not check_member(cid):
                btn = inline_button('عضویت در کانال', f'https://t.me/{CHANNEL_USERNAME[1:]}')
                send(cid, '⚠️ لطفاً ابتدا در کانال زیر عضو شوید:', reply_markup=btn)
                continue

            if cid in mode:
                step = mode[cid]
                if step == 'support':
                    send(ADMIN_ID, f'📩 پیام پشتیبانی از @{uname}:

{text}')
                    send(cid, '✅ پیام شما برای پشتیبانی ارسال شد.', reply_markup=keyboard(['بازگشت']))
                    del mode[cid]
                elif step == 'awaiting_id':
                    if text.startswith('@'):
                        target = None
                        for uid, un in users.items():
                            if un == text[1:]:
                                target = uid
                                break
                        if target:
                            reply_map[cid] = target
                            mode[cid] = target
                            send(cid, '✍️ پیام خود را بنویسید، ناشناس ارسال می‌شود:', reply_markup=keyboard(['بازگشت']))
                        else:
                            send(cid, '❌ این کاربر هنوز ربات را استارت نکرده.', reply_markup=keyboard(['بازگشت']))
                    else:
                        send(cid, '❗ آیدی را با @ وارد کن.', reply_markup=keyboard(['بازگشت']))
                elif isinstance(step, int):
                    target = step
                    btn = {'inline_keyboard': [[{
                        'text': '🚫 بلاک کاربر',
                        'callback_data': f'block_{cid}'
                    }]]}
                    send(target, f'✉️ پیام ناشناس:

{text}', reply_markup=btn)
                    send(cid, '✅ پیام شما ناشناس ارسال شد.', reply_markup=keyboard(['بازگشت']))
                    del mode[cid]
                continue

            if text.startswith('/start'):
                if ' ' in text:
                    sender = text.split()[1]
                    if str(cid) == sender:
                        send(cid, '❗ این لینک مخصوص خودت هست!')
                    else:
                        mode[cid] = int(sender)
                        send(cid, '✍️ پیام خود را بنویس، ناشناس برای طرف مقابل ارسال می‌شود:', reply_markup=keyboard(['بازگشت']))
                else:
                    btns = ['🔗 لینک ناشناس من', '✉️ پیام ناشناس با آیدی', '📨 پشتیبانی', 'ℹ️ راهنما']
                    if cid == ADMIN_ID:
                        btns.append('🛠 مدیریت')
                    send(cid, 'به ربات <b>اعتراف‌چت</b> خوش آمدی!', reply_markup=keyboard(btns))

            elif text == '🔗 لینک ناشناس من':
                link = f'https://t.me/{BOT_USERNAME}?start={cid}'
                send(cid, f'✨ لینک ناشناس شما:
{link}', reply_markup=keyboard(['بازگشت']))

            elif text == '✉️ پیام ناشناس با آیدی':
                send(cid, '🔍 آیدی فرد مورد نظر را وارد کن (با @):', reply_markup=keyboard(['بازگشت']))
                mode[cid] = 'awaiting_id'

            elif text == '📨 پشتیبانی':
                send(cid, '📝 پیام خود را برای پشتیبانی بنویس:', reply_markup=keyboard(['بازگشت']))
                mode[cid] = 'support'

            elif text == 'ℹ️ راهنما':
                help_msg = (
                    '❔ <b>راهنما</b>

'
                    'با این ربات می‌تونی پیام ناشناس بگیری یا بفرستی!
'
                    '1. لینک اختصاصی‌تو بگیر و بفرست
'
                    '2. با آیدی هم می‌تونی ناشناس پیام بدی
'
                    '3. پشتیبانی در دسترسه

'
                    '🌀 کانال: <a href="https://t.me/KOCSHER_IR">@KOCSHER_IR</a>'
                )
                send(cid, help_msg, reply_markup=keyboard(['بازگشت']))

            elif text == '🛠 مدیریت' and cid == ADMIN_ID:
                admin_btns = ['👥 کاربران', '✅ جوین‌شده‌ها', '🚫 بلاک‌شده‌ها', 'بازگشت']
                send(cid, '🔐 پنل مدیریت:', reply_markup=keyboard(admin_btns))

            elif text == '👥 کاربران' and cid == ADMIN_ID:
                out = '\n'.join([f'@{u}' for u in users.values()])
                send(cid, f'👥 لیست کاربران:\n{out or "خالی"}')

            elif text == '✅ جوین‌شده‌ها' and cid == ADMIN_ID:
                out = [f'@{users[i]}' for i in users if check_member(i)]
                send(cid, f'✅ اعضای عضو شده:\n' + '\n'.join(out or ['هیچ‌کس']))

            elif text == '🚫 بلاک‌شده‌ها' and cid == ADMIN_ID:
                out = [f'@{users.get(i, i)}' for i in blocked]
                send(cid, f'🚫 کاربران بلاک‌شده:\n' + '\n'.join(out or ['هیچ‌کس']))

            elif text == 'بازگشت':
                btns = ['🔗 لینک ناشناس من', '✉️ پیام ناشناس با آیدی', '📨 پشتیبانی', 'ℹ️ راهنما']
                if cid == ADMIN_ID:
                    btns.append('🛠 مدیریت')
                send(cid, 'منو اصلی:', reply_markup=keyboard(btns))

        elif 'callback_query' in u:
            q = u['callback_query']
            data = q['data']
            uid = q['from']['id']
            if data.startswith('block_'):
                target = int(data.split('_')[1])
                blocked.add(target)
                send(uid, '✅ کاربر مورد نظر بلاک شد.', reply_markup=keyboard(['بازگشت']))
