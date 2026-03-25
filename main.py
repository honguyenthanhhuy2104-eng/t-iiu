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
COIN_GIF = "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
DICE_GIF = "https://media.giphy.com/media/26BRuo6sLetdllPAQ/giphy.gif"

# ================= FLIP =================

@bot.command()
async def flip(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    embed = discord.Embed(title="🪙 Tung xu...", color=0xffff00)
    embed.set_image(url=COIN_GIF)
    msg = await ctx.send(embed=embed)

    await asyncio.sleep(2)

    win = random.choice([True, False])

    if win:
        u["money"] += bet
        result = "🎉 WIN"
    else:
        u["money"] -= bet
        result = "💀 LOSE"

    save()

    embed.title = f"🪙 Kết quả: {result}"
    await msg.edit(embed=embed)

# ================= SLOT =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    embed = discord.Embed(title="🎰 Đang quay...", color=0xff0000)
    embed.set_image(url=SLOT_GIF)
    msg = await ctx.send(embed=embed)

    await asyncio.sleep(3)

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    r = [random.choice(icons) for _ in range(3)]

    if r[0] == r[1] == r[2]:
        win = bet * 8
        u["money"] += win
        text = f"💎 JACKPOT +{win}"
    else:
        u["money"] -= bet
        text = "💀 thua"

    save()

    embed.title = f"🎰 {' | '.join(r)}"
    embed.description = text
    await msg.edit(embed=embed)

# ================= TAIXIU =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    embed = discord.Embed(title="🎲 Lắc xúc xắc...", color=0x00ffff)
    embed.set_image(url=DICE_GIF)
    msg = await ctx.send(embed=embed)

    await asyncio.sleep(3)

    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice.lower() == result:
        u["money"] += bet
        text = "🎉 WIN"
    else:
        u["money"] -= bet
        text = "💀 LOSE"

    save()

    embed.title = f"🎲 {dice} = {total}"
    embed.description = text
    await msg.edit(embed=embed)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} GIF MODE ONLINE")

bot.run(TOKEN)
