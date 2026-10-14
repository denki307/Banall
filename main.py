import os
import asyncio
from pyrogram import Client, filters
from pyrogram import idle

# Heroku Config Vars-la kudukka vendiya details
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

target_groups = ["@first_group_username", "@second_group_username"] 
bot_ids = ["@bot_1_username", "@bot_2_username"] 

bot_app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_apps = [Client(f"account_{i}", api_id=API_ID, api_hash=API_HASH, session_string=s) for i, s in enumerate(sessions) if s]

@bot_app.on_message(filters.command(["AllBan", "allban"], prefixes=["/", ".", "!"]))
async def trigger_ban(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ Neenga intha command-a use panna mudiyathu!")
        
    await message.reply_text("⏳ AllBan command received! Fetching ALL members from both groups without filtering...")
    
    # set() ah thookitu direct ah list [] use panrom
    members = [] 
    
    for group in target_groups:
        try:
            async for member in user_apps[0].get_chat_members(group):
                # Duplicate check pannama ellarayum add panrom
                members.append(member.user.id)
            await message.reply_text(f"✅ Fetched members from {group}")
        except Exception as e:
            await message.reply_text(f"❌ Error fetching from {group}: {e}")

    await message.reply_text(f"🚀 Total members to ban (including duplicates): {len(members)}. Ban Process starts now!")

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
            except Exception as e:
                await asyncio.sleep(5)

    tasks = [
        ban_members(user_apps[0], member_chunks[0], bot_ids[0]),
        ban_members(user_apps[1], member_chunks[1], bot_ids[0]),
        ban_members(user_apps[2], member_chunks[2], bot_ids[1]),
        ban_members(user_apps[3], member_chunks[3], bot_ids[1])
    ]

    await asyncio.gather(*tasks)
    await message.reply_text("✅ AllBan Process Completed! Yarum miss aagala.")

async def main():
    print("Starting Bot...")
    await bot_app.start()
    
    print("Starting 4 User accounts...")
    for app in user_apps:
        await app.start()
    
    print("Bot & Accounts running! Send /AllBan to the Bot DM.")
    
    await idle()
    
    await bot_app.stop()
    for app in user_apps:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
