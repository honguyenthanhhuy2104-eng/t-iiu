import discord
from discord.ext import commands
import json, random, os, asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================

def load():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load()


def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"money": 1000}
    return users[uid]

# ================= GIF LINKS =================

SLOT_GIF = "https://media.giphy.com/media/3o7aCTfyhYawdOXcFW/giphy.gif"
SLOT_STOP_GIF = "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"
DICE_GIF = "https://media.giphy.com/media/l0MYGb3y1Wk8Y2G0k/giphy.gif"
WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/ISOckXUybVfQ4/giphy.gif"

# ================= SLOT =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    embed = discord.Embed(title="🎰 Máy đang quay...", color=0xff0000)
    embed.set_image(url=SLOT_GIF)
    msg = await ctx.send(embed=embed)

    await asyncio.sleep(2)

    # dừng từng cột
    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    r = ["❓","❓","❓"]

    for i in range(3):
        await asyncio.sleep(1)
        r[i] = random.choice(icons)
        embed.title = f"🎰 {' | '.join(r)}"
        embed.set_image(url=SLOT_STOP_GIF)
        await msg.edit(embed=embed)

    # kết quả
    if r[0] == r[1] == r[2]:
        win = bet * 8
        u["money"] += win
        result = f"💎 JACKPOT +{win}"
        embed.set_image(url=WIN_GIF)
    else:
        u["money"] -= bet
        result = "💀 Thua"
        embed.set_image(url=LOSE_GIF)

    save()

    embed.description = result
    await msg.edit(embed=embed)

# ================= TAIXIU =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    embed = discord.Embed(title="🎲 Đang lắc xúc xắc...", color=0x00ffff)
    embed.set_image(url=DICE_GIF)
    msg = await ctx.send(embed=embed)

    await asyncio.sleep(3)

    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice.lower() == result:
        u["money"] += bet
        text = "🎉 WIN"
        embed.set_image(url=WIN_GIF)
    else:
        u["money"] -= bet
        text = "💀 LOSE"
        embed.set_image(url=LOSE_GIF)

    save()

    embed.title = f"🎲 {dice} = {total}"
    embed.description = text
    await msg.edit(embed=embed)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} ULTRA GIF ONLINE")

bot.run(TOKEN)
