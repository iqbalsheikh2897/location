import telebot
import pymongo
import pytz
# Add this at the top with other imports
import time
import requests
from datetime import datetime, timedelta
import threading
import logging
import re
import uuid
from datetime import datetime, timedelta
import random

# MongoDB configuration
uri = "mongodb+srv://itsmatrix4123:Uthaya$0@cluster0.z0o4a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(uri)
db = client['location']
users_collection = db['users']
keys_collection = db['unused_keys']
links_collection = db['links']

# Bot configuration
bot = telebot.TeleBot('8164068971:AAHN-n3nNcDhGBYIrxOpDkU7Jy5VNGlteYc')
admin_id = ["7418099890"]
admin_owner = ["7418099890"]
IST = pytz.timezone('Asia/Kolkata')

def read_users():
    try:
        current_time = datetime.now(IST)
        users = users_collection.find({"expiration": {"$gt": current_time}})
        return {user["user_id"]: user["expiration"] for user in users}
    except Exception as e:
        logging.error(f"Error reading users: {e}")
        return {}

def get_ip_details(ip: str) -> str:
    IPGEOLOCATION_API_KEY = "4e8b380e1e0d44c89f1ef1d46ec5ad20"
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEOLOCATION_API_KEY}&ip={ip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return (
                f"🌍 𝗜𝗣 𝗟𝗢𝗖𝗔𝗧𝗜𝗢𝗡 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n\n"
                f"🔍 IP: {data.get('ip', 'N/A')}\n"
                f"🌐 Continent: {data.get('continent_name', 'N/A')}\n"
                f"🏳️ Country: {data.get('country_name', 'N/A')}\n"
                f"🏢 Region: {data.get('state_prov', 'N/A')}\n"
                f"🌆 City: {data.get('city', 'N/A')}\n"
                f"📍 Latitude: {data.get('latitude', 'N/A')}\n"
                f"📍 Longitude: {data.get('longitude', 'N/A')}\n"
                f"🔌 ISP: {data.get('isp', 'N/A')}\n"
                f"⏰ Timezone: {data.get('time_zone', {}).get('name', 'N/A')}"
            )
        else:
            return f"❌ Error: Unable to fetch details (Status Code: {response.status_code})"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@bot.message_handler(commands=['trace'])
def handle_trace(message):
    user_id = str(message.chat.id)
    users = read_users()
    
    if user_id not in admin_id and user_id not in users:
        bot.reply_to(message, """⛔️ Access Denied
        
💡 Purchase a subscription to use this feature
📢 Contact: @YOUR_CHANNEL""")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, """
📝 𝗨𝗦𝗔𝗚𝗘
• Command: /trace <ip>
• Example: /trace 1.1.1.1""")
        return

    ip = args[1]
    msg = bot.reply_to(message, "🔍 Searching...")
    details = get_ip_details(ip)
    bot.edit_message_text(details, message.chat.id, msg.message_id)

# Add the remaining admin commands (, allkeys, allusers, broadcast, remove) 
# from rest2.py here
@bot.message_handler(commands=['addtime'])
def add_time(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, """⛔️ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗
━━━━━━━━━━━━━━━
❌ This command is restricted to admin use only""")
        return

    try:
        args = message.text.split()
        if len(args) != 3:
            bot.reply_to(message, """📝 𝗔𝗗𝗗 𝗧𝗜𝗠𝗘 𝗨𝗦𝗔𝗚𝗘
━━━━━━━━━━━━━━━
Command: /addtime <key> <duration>

⚡️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗙𝗼𝗿𝗺𝗮𝘁:
• Minutes: 30m
• Hours: 12h
• Days: 7d

📝 𝗘𝘅𝗮𝗺𝗽𝗹𝗲𝘀:
• /addtime MATRIX-VIP-ABCD1234 30m
• /addtime MATRIX-VIP-WXYZ5678 24h
• /addtime MATRIX-VIP-EFGH9012 7d""")
            return

        key = args[1]
        duration_str = args[2]
        
        # Find user with this key
        user = users_collection.find_one({"key": key})
        if not user:
            bot.reply_to(message, """❌ 𝗞𝗘𝗬 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗
━━━━━━━━━━━━━━━
The specified key is not associated with any active user.""")
            return

        duration, formatted_duration = parse_time_input(duration_str)
        if not duration:
            bot.reply_to(message, """❌ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━
Please use the following format:
• Minutes: 30m
• Hours: 12h
• Days: 7d""")
            return

        # Update expiration time with IST
        current_expiration = user['expiration'].astimezone(IST)
        new_expiration = current_expiration + duration

        users_collection.update_one(
            {"key": key},
            {"$set": {"expiration": new_expiration}}
        )

        # Notify user
        user_notification = f"""🎉 𝗧𝗜𝗠𝗘 𝗘𝗫𝗧𝗘𝗡𝗗𝗘𝗗
━━━━━━━━━━━━━━━
✨ Your subscription has been extended!

⏱️ 𝗔𝗱𝗱𝗲𝗱 𝗧𝗶𝗺𝗲: {formatted_duration}
📅 𝗡𝗲𝘄 𝗘𝘅𝗽𝗶𝗿𝘆: {new_expiration.strftime('%Y-%m-%d %H:%M:%S')} IST

💫 Enjoy your extended access!
━━━━━━━━━━━━━━━"""
        
        bot.send_message(user['user_id'], user_notification)

        # Current time in IST for admin message
        current_time_ist = datetime.now(IST)

        # Confirm to admin
        admin_message = f"""✅ 𝗧𝗜𝗠𝗘 𝗔𝗗𝗗𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬
━━━━━━━━━━━━━━━
👤 𝗨𝘀𝗲𝗿: @{user['username']}
🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: {user['user_id']}
🔑 𝗞𝗲𝘆: {key}
⏱️ 𝗔𝗱𝗱𝗲𝗱 𝗧𝗶𝗺𝗲: {formatted_duration}
📅 𝗡𝗲𝘄 𝗘𝘅𝗽𝗶𝗿𝘆: {new_expiration.strftime('%Y-%m-%d %H:%M:%S')} IST
⏰ 𝗧𝗶𝗺𝗲 𝗢𝗳 𝗔𝗰𝘁𝗶𝗼𝗻: {current_time_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
━━━━━━━━━━━━━━━"""
        
        bot.reply_to(message, admin_message)

    except Exception as e:
        error_message = f"""❌ 𝗘𝗥𝗥𝗢𝗥
━━━━━━━━━━━━━━━
Failed to add time: {str(e)}
⏰ 𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST"""
        bot.reply_to(message, error_message)

# ... (keep all previous imports and configurations)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)
    is_admin = user_id in admin_id or user_id in admin_owner
    
    # Admin-specific UI
    if is_admin:
        response = f"""
🚀 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗠𝗔𝗧𝗥𝗜𝗫 𝗕𝗢𝗧 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟
━━━━━━━━━━━━━━━━━━━━━━━
🛠 𝗔𝗱𝗺𝗶𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:

⚡️ 𝗨𝘀𝗲𝗿 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁
/allusers - List all active users
/allkeys - Show all generated keys
/remove <key> - Revoke a license key
/addtime <key> <duration> - Extend subscription

📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁𝗶𝗻𝗴
/broadcast <message> - Broadcast to all users

🔑 𝗞𝗲𝘆 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗼𝗻
/key <duration> - Generate new license key

🌍 𝗧𝗼𝗼𝗹𝘀
/trace <ip> - Geolocate an IP address

━━━━━━━━━━━━━━━━━━━━━━━
👤 𝗨𝘀𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
/redeem <key> - Activate your license
/check - View subscription status

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @MATRIX_CHEATS
⏰ 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST"""
    else:
        # Regular user UI
        response = f"""
✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗠𝗔𝗧𝗥𝗜𝗫 𝗕𝗢𝗧
━━━━━━━━━━━━━━━━━━━━━━━
🛡 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗜𝗣 𝗧𝗿𝗮𝗰𝗸𝗶𝗻𝗴 𝗧𝗼𝗼𝗹𝘀

⚡️ 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
/redeem <key> - Activate your license
/check - View subscription status
/trace <ip> - Geolocate an IP address

━━━━━━━━━━━━━━━━━━━━━━━
💎 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:
• IP Geolocation Tracking
• Detailed ISP Information
• Real-time Location Data

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @MATRIX_CHEATS
⏰ 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST"""

    bot.reply_to(message, response)

@bot.message_handler(commands=['check'])
def check_subscription(message):
    user_id = str(message.chat.id)
    current_time = datetime.now(IST)
    
    try:
        user = users_collection.find_one({
            "user_id": user_id,
            "expiration": {"$gt": current_time}
        })
        
        if user:
            expiration = user['expiration'].astimezone(IST)
            remaining = expiration - current_time
            response = f"""
✅ 𝗔𝗖𝗧𝗜𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━
🔑 License Key: {user['key']}
⏰ Time Remaining: {remaining.days} days {remaining.seconds//3600} hours
📅 Expiration Date: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST

💎 𝗔𝗰𝗰𝗲𝘀𝘀 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:
• IP Geolocation Tracking
• Detailed ISP Reports
• 24/7 Premium Support"""
        else:
            response = """
❌ 𝗡𝗢 𝗔𝗖𝗧𝗜𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━
💡 Purchase a subscription to unlock premium features:
/redeem <key> - Activate your license

📢 Contact @MATRIX_CHEATS for license keys"""

        bot.reply_to(message, response)
        
    except Exception as e:
        error_msg = f"""
⚠️ 𝗘𝗥𝗥𝗢𝗥 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗦𝗧𝗔𝗧𝗨𝗦
━━━━━━━━━━━━━━━
{str(e)}"""
        bot.reply_to(message, error_msg)

# ... (keep all other existing handlers and functions)

@bot.message_handler(commands=['allkeys'])
def show_all_keys(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
    
    try:
        # Aggregate unused keys with duration grouping
        keys = keys_collection.aggregate([
            {
                "$lookup": {
                    "from": "reseller_transactions",
                    "localField": "key",
                    "foreignField": "key_generated",
                    "as": "transaction"
                }
            },
            {
                "$match": {"is_used": False}
            },
            {
                "$sort": {"duration": 1, "created_at": -1}
            }
        ])
        
        if not keys:
            bot.reply_to(message, "📝 No unused keys available")
            return

        # Group keys by duration and reseller
        duration_keys = {}
        reseller_keys = {}
        total_keys = 0
        
        for key in keys:
            total_keys += 1
            duration = key['duration']
            reseller_id = key['transaction'][0]['reseller_id'] if key.get('transaction') else 'admin'
            
            if duration not in duration_keys:
                duration_keys[duration] = 0
            duration_keys[duration] += 1
            
            if reseller_id not in reseller_keys:
                reseller_keys[reseller_id] = []
                
            created_at_ist = key['created_at'].astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')
            key_info = f"""🔑 Key: `{key['key']}`
⏱ Duration: {duration}
📅 Created: {created_at_ist} IST"""
            reseller_keys[reseller_id].append(key_info)

        # Build summary section
        response = f"""📊 𝗞𝗲𝘆𝘀 𝗦𝘂𝗺𝗺𝗮𝗿𝘆
━━━━━━━━━━━━━━━
📦 Total Keys: {total_keys}

⏳ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗕𝗿𝗲𝗮𝗸𝗱𝗼𝘄𝗻:"""

        for duration, count in sorted(duration_keys.items()):
            response += f"\n• {duration}: {count} keys"

        response += "\n\n🔑 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗞𝗲𝘆𝘀 𝗯𝘆 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿:\n"

        # Add reseller sections
        for reseller_id, keys_list in reseller_keys.items():
            try:
                if reseller_id == 'admin':
                    reseller_name = "Admin Generated"
                else:
                    user_info = bot.get_chat(reseller_id)
                    reseller_name = f"@{user_info.username}" if user_info.username else user_info.first_name
                
                response += f"\n👤 {reseller_name} ({len(keys_list)} keys):\n"
                response += "━━━━━━━━━━━━━━━\n"
                response += "\n\n".join(keys_list)
                response += "\n\n"
            except Exception:
                continue

        # Split response if too long
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                bot.reply_to(message, response[x:x+4096])
        else:
            bot.reply_to(message, response)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching keys: {str(e)}")


@bot.message_handler(commands=['allusers'])
def show_users(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
        
    try:
        current_time = datetime.now(IST)
        
        # Aggregate users with reseller info and sort by expiration
        users = users_collection.aggregate([
            {
                "$match": {
                    "expiration": {"$gt": current_time}
                }
            },
            {
                "$lookup": {
                    "from": "reseller_transactions",
                    "localField": "key",
                    "foreignField": "key_generated",
                    "as": "transaction"
                }
            },
            {
                "$sort": {
                    "expiration": 1
                }
            }
        ])
        
        if not users:
            bot.reply_to(message, "📝 No active users found")
            return

        # Group users by reseller
        reseller_users = {}
        total_users = 0
        
        for user in users:
            reseller_id = user['transaction'][0]['reseller_id'] if user.get('transaction') else 'admin'
            if reseller_id not in reseller_users:
                reseller_users[reseller_id] = []
                
            remaining = user['expiration'].astimezone(IST) - current_time
            expiration_ist = user['expiration'].astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')
            
            user_info = f"""👤 User: @{user.get('username', 'N/A')}
🆔 ID: `{user['user_id']}`
🔑 Key: `{user['key']}`
⏳ Remaining: {remaining.days}d {remaining.seconds // 3600}h
📅 Expires: {expiration_ist} IST"""
            reseller_users[reseller_id].append(user_info)
            total_users += 1

        # Build response message
        response = f"👥 Active Users: {total_users}\n\n"
        
        for reseller_id, users_list in reseller_users.items():
            try:
                if reseller_id == 'admin':
                    reseller_name = "Admin Generated"
                else:
                    user_info = bot.get_chat(reseller_id)
                    reseller_name = f"@{user_info.username}" if user_info.username else user_info.first_name
                    
                response += f"👤 {reseller_name} ({len(users_list)} users):\n"
                response += "━━━━━━━━━━━━━━━\n"
                response += "\n\n".join(users_list)
                response += "\n\n"
            except Exception:
                continue

        # Split response if too long
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                bot.reply_to(message, response[x:x+4096])
        else:
            bot.reply_to(message, response)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching users: {str(e)}")


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
        
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, "📝 Usage: /broadcast <message>")
        return
        
    broadcast_text = args[1]
    
    try:
        current_time = datetime.now(IST)
        users = list(users_collection.find({"expiration": {"$gt": current_time}}))
        
        if not users:
            bot.reply_to(message, "❌ No active users found to broadcast to.")
            return
            
        success_count = 0
        failed_users = []
        
        for user in users:
            try:
                formatted_message = f"""
📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘
{broadcast_text}
━━━━━━━━━━━━━━━
𝗦𝗲𝗻𝘁 𝗯𝘆: @{message.from_user.username}
𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST"""

                bot.send_message(user['user_id'], formatted_message)
                success_count += 1
                time.sleep(0.1)  # Prevent flooding
                
            except Exception as e:
                failed_users.append(f"@{user['username']}")
        
        summary = f"""
✅ 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗦𝘂𝗺𝗺𝗮𝗿𝘆:
📨 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {len(users)}
✅ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹: {success_count}
❌ 𝗙𝗮𝗶𝗹𝗲𝗱: {len(failed_users)}"""

        if failed_users:
            summary += "\n❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘂𝘀𝗲𝗿𝘀:\n" + "\n".join(failed_users)
            
        bot.reply_to(message, summary)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error during broadcast: {str(e)}")

@bot.message_handler(commands=['remove'])
def remove_key(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "📝 Usage: /remove <key>")
            return

        key = args[1]
        removed_from = []

        # Remove from unused keys collection
        result = keys_collection.delete_one({"key": key})
        if result.deleted_count > 0:
            removed_from.append("unused keys database")

        # Find and remove from users collection
        user = users_collection.find_one_and_delete({"key": key})
        if user:
            removed_from.append("active users database")
            # Send notification to the user
            user_notification = f"""
🚫 𝗞𝗲𝘆 𝗥𝗲𝘃𝗼𝗸𝗲𝗱
Your license key has been revoked by an administrator.
🔑 Key: {key}
⏰ Revoked at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST
📢 For support or to purchase a new key:
• Contact any admin or reseller
• Visit @MATRIX_CHEATS
"""
            try:
                bot.send_message(user['user_id'], user_notification)
            except Exception as e:
                logging.error(f"Failed to notify user {user['user_id']}: {e}")

        if not removed_from:
            bot.reply_to(message, f"""
❌ 𝗞𝗲𝘆 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱
The key {key} was not found in any database.
""")
            return

        # Send success message to admin
        admin_message = f"""
✅ 𝗞𝗲𝘆 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆
🔑 Key: {key}
📊 Removed from: {', '.join(removed_from)}
⏰ Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST
"""
        if user:
            admin_message += f"""
👤 User Details:
• Username: @{user.get('username', 'N/A')}
• User ID: {user['user_id']}
"""
        bot.reply_to(message, admin_message)

    except Exception as e:
        error_message = f"""
❌ 𝗘𝗿𝗿𝗼𝗿 𝗥𝗲𝗺𝗼𝘃𝗶𝗻𝗴 𝗞𝗲𝘆
⚠️ Error: {str(e)}
"""
        logging.error(f"Error removing key: {e}")
        bot.reply_to(message, error_message)

def create_indexes():
    try:
        users_collection.create_index("user_id", unique=True)
        users_collection.create_index("expiration")
        keys_collection.create_index("key", unique=True)
        links_collection.create_index("link_id", unique=True)
        links_collection.create_index("expiration")
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

def parse_time_input(time_input):
    match = re.match(r"(\d+)([mhd])", time_input)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        
        if unit == "m":
            return timedelta(minutes=number), f"{number}m"
        elif unit == "h":
            return timedelta(hours=number), f"{number}h"
        elif unit == "d":
            return timedelta(days=number), f"{number}d"
    return None, None


@bot.message_handler(commands=['key'])
def generate_key(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "📝 Usage: /key <duration>\nExample: /key 1d, /key 7d")
            return

        duration_str = args[1]
        duration, formatted_duration = parse_time_input(duration_str)
        if not duration:
            bot.reply_to(message, "❌ Invalid duration format. Use: 1d, 7d, 30d")
            return

        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
        numbers = ''.join(str(random.randint(0, 9)) for _ in range(4))
        key = f"MATRIX-VIP-{letters}{numbers}"

        # Insert into MongoDB
        keys_collection.insert_one({
            "key": key,
            "duration": formatted_duration,
            "created_at": datetime.now(IST),
            "is_used": False
        })

        bot.reply_to(message, f"""✅ Key Generated Successfully
🔑 Key: `{key}`
⏱ Duration: {formatted_duration}
📅 Generated: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST""")
    except Exception as e:
        bot.reply_to(message, f"❌ Error generating key: {str(e)}")


@bot.message_handler(commands=['redeem'])
def redeem_key(message):
    try:
        user_id = str(message.chat.id)
        if user_id.startswith('-'):
            bot.reply_to(message, """
⚠️ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗
━━━━━━━━━━━━━━━
❌ This command cannot be used in groups
🔐 Please use this command in private chat with the bot

📱 How to use:
1. Open MATRIX BOT in private
2. Start the bot
3. Use /redeem command there

💡 This ensures your license key remains private and secure
━━━━━━━━━━━━━━━""")
            return

        args = message.text.split()
        if len(args) != 2:
            usage_text = """
💎 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗠𝗣𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━
📝 𝗨𝘀𝗮𝗴𝗲: /redeem 𝗠𝗔𝗧𝗥𝗜𝗫-𝗩𝗜𝗣-𝗫𝗫𝗫𝗫

⚠️ 𝗜𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁 𝗡𝗼𝘁𝗲𝘀:
• 𝗞𝗲𝘆𝘀 𝗮𝗿𝗲 𝗰𝗮𝘀𝗲-𝘀𝗲𝗻𝘀𝗶𝘁𝗶𝘃𝗲
• 𝗢𝗻𝗲-𝘁𝗶𝗺𝗲 𝘂𝘀𝗲 𝗼𝗻𝗹𝘆
• 𝗡𝗼𝗻-𝘁𝗿𝗮𝗻𝘀𝗳𝗲𝗿𝗮𝗯𝗹𝗲

🔑 𝗘𝘅𝗮𝗺𝗽𝗹𝗲: /redeem 𝗠𝗔𝗧𝗥𝗜𝗫-𝗩𝗜𝗣-𝗔𝗕𝗖𝗗𝟭𝟮𝟯𝟰

💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆? 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀
━━━━━━━━━━━━━━━"""
            bot.reply_to(message, usage_text)
            return

        key = args[1].strip()
        username = message.from_user.username or "Unknown"
        current_time = datetime.now(IST)

        existing_user = users_collection.find_one({
            "user_id": user_id,
            "expiration": {"$gt": current_time}
        })

        if existing_user:
            expiration = existing_user['expiration'].astimezone(IST)
            bot.reply_to(message, f"""
⚠️ 𝗔𝗖𝗧𝗜𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗
━━━━━━━━━━━━━━━
👤 User: @{message.from_user.username}
🔑 Key: {existing_user['key']}

⏰ 𝗧𝗶𝗺𝗲𝗹𝗶𝗻𝗲:
• Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} IST
• Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST

⚠️ 𝗡𝗼𝘁𝗶𝗰𝗲:
You cannot redeem a new key while having an active subscription.
Please wait for your current subscription to expire.

💡 𝗧𝗶𝗽: Use /check to view your subscription status
━━━━━━━━━━━━━━━""")
            return

        key_doc = keys_collection.find_one({"key": key, "is_used": False})
        if not key_doc:
            bot.reply_to(message, "❌ Invalid or already used key!")
            return

        duration_str = key_doc['duration']
        duration, _ = parse_time_input(duration_str)
        
        if not duration:
            bot.reply_to(message, "❌ Invalid key duration!")
            return

        redeemed_at = datetime.now(IST)
        expiration = redeemed_at + duration

        users_collection.insert_one({
            "user_id": user_id,
            "username": username,
            "key": key,
            "redeemed_at": redeemed_at,
            "expiration": expiration
        })

        keys_collection.update_one({"key": key}, {"$set": {"is_used": True}})

        user_message = f"""
✨ 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✨
━━━━━━━━━━━━━━━
👤 User: @{username}
🆔 ID: {user_id}
🔑 Key: {key}

⏰ 𝗧𝗶𝗺𝗲𝗹𝗶𝗻𝗲:
• Activated: {redeemed_at.strftime('%Y-%m-%d %H:%M:%S')} IST
• Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST
• Duration: {duration_str}

💎 𝗦𝘁𝗮𝘁𝘂𝘀: Active ✅
📢 Channel: @MATRIX_CHEATS
━━━━━━━━━━━━━━━

💡 Use /matrix command to launch attacks
⚡️ Use /check to view system status"""

        bot.reply_to(message, user_message)

        admin_message = f"""
🚨 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗡𝗢𝗧𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━
👤 User: @{username}
🆔 User ID: {user_id}
🔑 Key: {key}
⏱️ Duration: {duration_str}
📅 Activated: {redeemed_at.strftime('%Y-%m-%d %H:%M:%S')} IST
📅 Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST
━━━━━━━━━━━━━━━"""

        for admin in admin_id:
            bot.send_message(admin, admin_message)

    except Exception as e:
        error_message = f"""
❌ 𝗘𝗥𝗥𝗢𝗥 𝗥𝗘𝗗𝗘𝗘𝗠𝗜𝗡𝗚 𝗞𝗘𝗬
━━━━━━━━━━━━━━━
⚠️ Error: {str(e)}
⏰ Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST
━━━━━━━━━━━━━━━"""
        bot.reply_to(message, error_message)

def main():
    while True:
        try:
            print("Bot is running...")
            bot.polling(timeout=60)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
