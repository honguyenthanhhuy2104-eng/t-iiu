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

# ================= SLOT (NO GIF - REALISTIC SPIN) =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰 Đang quay...")

    r = ["❓","❓","❓"]
    speed = 0.05

    # quay nhanh -> chậm dần
    for i in range(15):
        temp = [random.choice(icons) for _ in range(3)]
        await msg.edit(content="🎰 " + " | ".join(temp))
        await asyncio.sleep(speed)
        speed += 0.01

    # dừng từng cột
    for i in range(3):
        for _ in range(5):
            temp = r.copy()
            temp[i] = random.choice(icons)
            await msg.edit(content="🎰 " + " | ".join(temp))
            await asyncio.sleep(0.1)
        r[i] = random.choice(icons)
        await msg.edit(content="🎰 " + " | ".join(r))
        await asyncio.sleep(0.4)

    # kết quả
    if r[0] == r[1] == r[2]:
        win = bet * 8
        u["money"] += win
        text = f"💎 JACKPOT +{win}"
    else:
        u["money"] -= bet
        text = "💀 Thua"

    save()
    await msg.edit(content=f"🎰 {' | '.join(r)}\n{text}")

# ================= TAIXIU (NO GIF - REALISTIC SHAKE) =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🎲 Đang lắc...")

    speed = 0.05

    # lắc nhanh -> chậm dần
    for i in range(12):
        fake = [random.randint(1,6) for _ in range(3)]
        await msg.edit(content=f"🎲 {fake}")
        await asyncio.sleep(speed)
        speed += 0.015

    # kết quả thật
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
    await msg.edit(content=f"🎲 {dice} = {total}\n{text}")

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} REALISTIC MODE ONLINE")

bot.run(TOKEN)
