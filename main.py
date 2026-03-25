import discord
from discord.ext import commands
import json, random, os, asyncio, time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ TOKEN not found")

# ================= CONFIG =================
WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/3o7TKr3nzbh5WgCFxe/giphy.gif"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================
def load():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
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
        users[uid] = {"money": 1000, "bank": 0, "last_daily": 0, "last_work": 0}
    return users[uid]

def parse_bet(u, bet):
    if isinstance(bet, str) and bet.lower() == "all":
        return max(1, u["money"])
    return max(1, int(bet))

# ================= BASIC =================
@bot.command()
async def bal(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 {u['money']:,} | 🏦 {u['bank']:,}")

# ================= PAY =================
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["money"] < amount:
        return await ctx.send("❌")

    msg = await ctx.send(f"💸 Chuyển {amount:,}? (yes/no)")
    def check(m): return m.author == ctx.author

    try:
        reply = await bot.wait_for("message", timeout=10, check=check)
    except:
        return await ctx.send("⏳ Timeout")

    if reply.content.lower() != "yes":
        return await ctx.send("❌ Hủy")

    r = get_user(member.id)
    u["money"] -= amount
    r["money"] += amount
    save()

    await ctx.send("✅ Done")

# ================= BANK =================
@bot.command()
async def deposit(ctx, amount:int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["money"] < amount:
        return await ctx.send("❌")

    u["money"] -= amount
    u["bank"] += amount
    save()
    await ctx.send("🏦 Đã gửi")

@bot.command()
async def withdraw(ctx, amount:int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["bank"] < amount:
        return await ctx.send("❌")

    u["bank"] -= amount
    u["money"] += amount
    save()
    await ctx.send("💸 Đã rút")

# ================= DAILY =================
@bot.command()
async def daily(ctx):
    u = get_user(ctx.author.id)
    if time.time() - u["last_daily"] < 86400:
        return await ctx.send("⏳")

    reward = random.randint(500,1500)
    u["money"] += reward
    u["last_daily"] = time.time()
    save()
    await ctx.send(f"🎁 +{reward}")

# ================= WORK =================
@bot.command()
async def work(ctx):
    u = get_user(ctx.author.id)
    if time.time() - u["last_work"] < 20:
        return await ctx.send("⏳")

    jobs = ["Dev","Driver","Streamer","Hacker","Singer","Banker"]
    earn = random.randint(200,1000)

    u["money"] += earn
    u["last_work"] = time.time()
    save()

    await ctx.send(f"💼 {random.choice(jobs)} +{earn}")

# ================= SLOT =================
@bot.command()
async def slot(ctx, bet):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    if u["money"] < bet:
        return await ctx.send("❌")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰...")

    for i in range(10):
        await msg.edit(content="🎰 " + " | ".join(random.choices(icons,k=3)))
        await asyncio.sleep(0.07)

    r = [random.choice(icons) for _ in range(3)]

    if r[0]==r[1]==r[2]:
        u["money"] += bet*10
        text="🎉 WIN"
        gif=WIN_GIF
    else:
        u["money"] -= bet
        text="💀 LOSE"
        gif=LOSE_GIF

    save()

    embed = discord.Embed(title="🎰 SLOT",description=f"{' | '.join(r)}\n{text}")
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= TAIXIU =================
@bot.command()
async def taixiu(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    msg = await ctx.send("🎲 Lắc...")
    emoji = ["⚀","⚁","⚂","⚃","⚄","⚅"]

    for i in range(15):
        await msg.edit(content="🎲 " + " ".join(random.choices(emoji,k=3)))
        await asyncio.sleep(0.07 + i*0.01)

    dice = [random.randint(1,6) for _ in range(3)]
    visual = " ".join([emoji[d-1] for d in dice])

    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice == result:
        u["money"] += bet
        text="🎉 WIN"
        gif=WIN_GIF
    else:
        u["money"] -= bet
        text="💀 LOSE"
        gif=LOSE_GIF

    save()

    embed = discord.Embed(title="🎲 TÀI XỈU",description=f"{visual}\nTổng: {total} → {result}\n{text}")
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= BAU CUA =================
@bot.command()
async def baucu(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    animals = ["nai","bầu","gà","cá","cua","tôm"]
    icons = {"nai":"🦌","bầu":"🍐","gà":"🐓","cá":"🐟","cua":"🦀","tôm":"🦐"}

    if choice not in animals:
        return await ctx.send("❌")

    msg = await ctx.send("🎲 Lắc...")

    for i in range(15):
        fake = [icons[random.choice(animals)] for _ in range(3)]
        await msg.edit(content="🎲 " + " | ".join(fake))
        await asyncio.sleep(0.07 + i*0.01)

    dice = [random.choice(animals) for _ in range(3)]
    visual = " | ".join([icons[d] for d in dice])

    count = dice.count(choice)

    if count>0:
        win = bet*count
        u["money"] += win
        text=f"🎉 Trúng {count} +{win}"
        gif=WIN_GIF
    else:
        u["money"] -= bet
        text="💀 Thua"
        gif=LOSE_GIF

    save()

    embed = discord.Embed(title="🎲 BẦU CUA",description=f"{visual}\n{text}")
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= BLACKJACK =================
games = {}

def draw(): return random.randint(1,11)

@bot.command()
async def bj(ctx, bet):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    games[ctx.author.id] = {
        "bet": bet,
        "player":[draw(),draw()],
        "dealer":[draw(),draw()]
    }

    g = games[ctx.author.id]
    await ctx.send(f"🃏 {g['player']} ({sum(g['player'])}) | Dealer: {g['dealer'][0]}, ?")

@bot.command()
async def hit(ctx):
    if ctx.author.id not in games:
        return await ctx.send("❌")

    g = games[ctx.author.id]
    g["player"].append(draw())

    if sum(g["player"])>21:
        get_user(ctx.author.id)["money"] -= g["bet"]
        save()
        games.pop(ctx.author.id)
        return await ctx.send("💀 Bù")

    await ctx.send(str(g["player"]))

@bot.command()
async def stand(ctx):
    if ctx.author.id not in games:
        return

    g = games[ctx.author.id]

    while sum(g["dealer"])<17:
        g["dealer"].append(draw())

    p = sum(g["player"])
    d = sum(g["dealer"])

    u = get_user(ctx.author.id)

    if d>21 or p>d:
        u["money"] += g["bet"]
        gif=WIN_GIF
        text="🎉 WIN"
    else:
        u["money"] -= g["bet"]
        gif=LOSE_GIF
        text="💀 LOSE"

    save()
    games.pop(ctx.author.id)

    embed = discord.Embed(title="🃏 BLACKJACK",description=f"{p} vs {d}\n{text}")
    embed.set_image(url=gif)

    await ctx.send(embed=embed)

# ================= BACCARAT =================
@bot.command()
async def baccarat(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    player = random.randint(0,9)
    banker = random.randint(0,9)

    result = "player" if player>banker else "banker" if banker>player else "tie"

    if choice==result:
        u["money"] += bet*2
        gif=WIN_GIF
        text="🎉 WIN"
    else:
        u["money"] -= bet
        gif=LOSE_GIF
        text="💀 LOSE"

    save()

    embed = discord.Embed(title="🃏 BACCARAT",description=f"P:{player} B:{banker}\n{result}\n{text}")
    embed.set_image(url=gif)

    await ctx.send(embed=embed)

# ================= ERROR =================
@bot.event
async def on_command_error(ctx, error):
    print("ERROR:", error)
    await ctx.send("⚠️ Lỗi")

# ================= READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} ONLINE")

bot.run(TOKEN)
