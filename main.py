import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram import idle

# --- 1. Log Errors ah Hide Panrathu ---
logging.getLogger("pyrogram").setLevel(logging.ERROR)

def custom_exception_handler(loop, context):
    exception = context.get("exception")
    if exception and "Peer id invalid" in str(exception):
        pass  # Intha error vantha ignore pannidum
    else:
        loop.default_exception_handler(context)

# --- 2. Heroku Config Vars ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

sessions = [
    os.environ.get("STRING_SESSION_1", ""),
    os.environ.get("STRING_SESSION_2", ""),
    os.environ.get("STRING_SESSION_3", ""),
    os.environ.get("STRING_SESSION_4", "")
]

# INGA UNGA GROUP AND BOT USERNAMES AH MATHIKONGA
target_groups = ["@first_group_username", "@second_group_username"] 
bot_ids = ["@bot_1_username", "@bot_2_username"] 

# --- 3. App Initialization ---
bot_app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_apps = [Client(f"account_{i}", api_id=API_ID, api_hash=API_HASH, session_string=s) for i, s in enumerate(sessions) if s]

# --- 4. Debug Message (Unga ID kandupudikka) ---
@bot_app.on_message(filters.private, group=-1)
async def debug_msg(client, message):
    if message.from_user:
        print(f"➔ MESSAGE RECEIVED: From {message.from_user.id} | Text: {message.text}")

# --- 5. Main AllBan Command ---
@bot_app.on_message(filters.command(["AllBan", "allban"], prefixes=["/", ".", "!"]))
async def trigger_ban(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ Neenga intha command-a use panna mudiyathu!")
        
    await message.reply_text("⏳ AllBan command received! Fetching ALL members from both groups (No one will be missed)...")
    
    members = [] 
    
    for group in target_groups:
        try:
            async for member in user_apps[0].get_chat_members(group):
                members.append(member.user.id)
            await message.reply_text(f"✅ Fetched members from {group}")
        except Exception as e:
            await message.reply_text(f"❌ Error fetching from {group}: {e}")

    await message.reply_text(f"🚀 Total members to ban: {len(members)}. Ban Process starts now!")

    chunk_size = len(members) // len(user_apps)
    member_chunks = [members[i:i + chunk_size] for i in range(0, len(members), chunk_size)]
    
    if len(members) % len(user_apps) != 0:
        member_chunks[-1].extend(members[len(user_apps) * chunk_size:])

    async def ban_members(app, chunk, bot_id):
        for user_id in chunk:
            try:
                command_msg = f"/ban {user_id}" 
                await app.send_message(bot_id, command_msg)
                await asyncio.sleep(0.5) 
            except Exception:
                await asyncio.sleep(5)

    tasks = [
        ban_members(user_apps[0], member_chunks[0], bot_ids[0]),
        ban_members(user_apps[1], member_chunks[1], bot_ids[0]),
        ban_members(user_apps[2], member_chunks[2], bot_ids[1]),
        ban_members(user_apps[3], member_chunks[3], bot_ids[1])
    ]

    await asyncio.gather(*tasks)
    await message.reply_text("✅ AllBan Process Completed!")

# --- 6. Start Function ---
async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(custom_exception_handler)

    print("Starting Bot...")
    await bot_app.start()
    
    print("Starting User accounts...")
    for app in user_apps:
        await app.start()
    
    print("Bot & Accounts running! Send /AllBan to the Bot DM.")
    
    await idle()
    
    await bot_app.stop()
    for app in user_apps:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
