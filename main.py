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

# ================= WIN/LOSE GIF =================

WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/ISOckXUybVfQ4/giphy.gif"

# ================= SLOT ULTRA REAL =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰 Đang quay...")

    reels = [[random.choice(icons) for _ in range(20)] for _ in range(3)]
    pos = [0,0,0]
    speed = [0.05, 0.07, 0.09]

    # quay lệch nhau
    for i in range(20):
        display = []
        for j in range(3):
            pos[j] = (pos[j] + 1) % len(reels[j])
            display.append(reels[j][pos[j]])
        await msg.edit(content="🎰 " + " | ".join(display))
        await asyncio.sleep(min(speed))
        speed = [s+0.01 for s in speed]

    # dừng từng cột
    final = []
    for i in range(3):
        for _ in range(6):
            temp = final + [random.choice(icons)] + ["❓"]*(2-i)
            await msg.edit(content="🎰 " + " | ".join(temp))
            await asyncio.sleep(0.1)
        final.append(random.choice(icons))
        await msg.edit(content="🎰 " + " | ".join(final + ["❓"]*(2-i)))
        await asyncio.sleep(0.5)

    r = final

    # near win (tạo cảm giác suýt trúng)
    if r[0] == r[1] and r[2] != r[1] and random.random() < 0.3:
        r[2] = random.choice([x for x in icons if x != r[1]])

    if r[0] == r[1] == r[2]:
        win = bet * 10
        u["money"] += win
        result = f"💎 JACKPOT +{win}"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        result = "💀 Thua"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(title="🎰 KẾT QUẢ", description=result)
    embed.add_field(name="Reels", value=" | ".join(r))
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= TAIXIU ULTRA =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🎲 Đang lắc...")

    speed = 0.05

    # lắc mạnh
    for i in range(15):
        fake = [random.randint(1,6) for _ in range(3)]
        await msg.edit(content=f"🎲 {fake}")
        await asyncio.sleep(speed)
        speed += 0.01

    await msg.edit(content="🎲 Đang mở bát...")
    await asyncio.sleep(1)

    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice.lower() == result:
        u["money"] += bet
        text = "🎉 WIN"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        text = "💀 LOSE"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(title=f"🎲 {dice} = {total}", description=text)
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} ULTRA REAL CASINO ONLINE")

bot.run(TOKEN)
