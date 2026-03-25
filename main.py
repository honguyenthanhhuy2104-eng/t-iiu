# FULL FINAL MAX LEVEL DISCORD CASINO BOT
import discord
from discord.ext import commands
import json, random, os, asyncio, time
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
        users[uid] = {
            "money": 1000,
            "bank": 0,
            "last_daily": 0,
            "last_work": 0
        }
    return users[uid]

# ================= UTIL =================

def parse_bet(u, bet):
    if isinstance(bet, str) and bet.lower() == "all":
        return u["money"]
    return int(bet)

# ================= BAL =================
@bot.command()
async def bal(ctx, member: discord.Member = None):
    member = member or ctx.author
    u = get_user(member.id)
    total = u["money"] + u["bank"]

    embed = discord.Embed(title=f"💰 {member.name}", color=0x00ffcc)
    embed.add_field(name="💵 Tiền", value=f"{u['money']:,}")
    embed.add_field(name="🏦 Bank", value=f"{u['bank']:,}")
    embed.add_field(name="💎 Tổng", value=f"{total:,}")

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    await ctx.send(embed=embed)

# ================= PAY CONFIRM =================
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    u = get_user(ctx.author.id)
    if u["money"] < amount:
        return await ctx.send("❌ Không đủ tiền")

    msg = await ctx.send(f"💸 Xác nhận chuyển {amount:,} đến {member.mention}? (yes/no)")

    def check(m): return m.author == ctx.author

    try:
        reply = await bot.wait_for("message", timeout=10, check=check)
    except:
        return await msg.edit(content="⏳ Hết thời gian")

    if reply.content.lower() != "yes":
        return await ctx.send("❌ Đã huỷ")

    r = get_user(member.id)
    u["money"] -= amount
    r["money"] += amount
    save()

    await ctx.send("✅ Thành công")

# ================= BANK =================
@bot.command()
async def deposit(ctx, amount: int):
    u = get_user(ctx.author.id)
    if u["money"] < amount:
        return await ctx.send("❌")

    msg = await ctx.send("🏦 Đang xử lý...")

    for s in ["Kiểm tra", "Xác thực", "Chuyển", "Xong"]:
        await msg.edit(content=f"🏦 {s}...")
        await asyncio.sleep(0.5)

    u["money"] -= amount
    u["bank"] += amount
    save()

    await msg.edit(content=f"✅ Đã gửi {amount:,}")

@bot.command()
async def withdraw(ctx, amount: int):
    u = get_user(ctx.author.id)
    if u["bank"] < amount:
        return await ctx.send("❌")

    u["bank"] -= amount
    u["money"] += amount
    save()

    await ctx.send(f"💸 Rút {amount:,}")

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

    for _ in range(10):
        await msg.edit(content="🎰 " + " | ".join(random.choices(icons,k=3)))
        await asyncio.sleep(0.1)

    r = [random.choice(icons) for _ in range(3)]

    if r[0]==r[1]==r[2]:
        u["money"] += bet*10
        text="WIN"
    else:
        u["money"] -= bet
        text="LOSE"

    save()
    await msg.edit(content=f"🎰 {' | '.join(r)}\n{text}")

# ================= TAIXIU (PHYSICS DICE + GIF) =================
@bot.command()
async def taixiu(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    if u["money"] < bet:
        return await ctx.send("❌")

    msg = await ctx.send("🎲 Lắc xúc xắc...")

    emoji = ["⚀","⚁","⚂","⚃","⚄","⚅"]

    # hiệu ứng vật lý (nhảy + đổi góc)
    velocity = 0.05
    for i in range(20):
        dice_anim = [random.choice(emoji) for _ in range(3)]
        await msg.edit(content=f"🎲 {' '.join(dice_anim)}")
        await asyncio.sleep(velocity)
        velocity += 0.01  # chậm dần giống vật lý

    await msg.edit(content="🎲 Đang dừng...")
    await asyncio.sleep(0.7)

    dice = [random.randint(1,6) for _ in range(3)]
    visual = " ".join([emoji[d-1] for d in dice])

    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice == result:
        u["money"] += bet
        text = "🎉 WIN"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        text = "💀 LOSE"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(
        title="🎲 TÀI XỈU PHYSICS",
        description=f"{visual}
Tổng: {total} → {result}
{text}",
        color=random.choice([0x00ffcc,0xffcc00,0xff0066])
    )
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= FLIP =================
@bot.command()
async def flip(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    result = random.choice(["heads","tails"])

    if choice == result:
        u["money"] += bet
    else:
        u["money"] -= bet

    save()
    await ctx.send(f"🪙 {result}")

# ================= BLACKJACK =================
games = {}

def draw(): return random.randint(1,11)

@bot.command()
async def bj(ctx, bet:int):
    u = get_user(ctx.author.id)
    if u["money"] < bet:
        return

    games[ctx.author.id] = {
        "bet": bet,
        "player": [draw(),draw()],
        "dealer": [draw(),draw()]
    }

    g = games[ctx.author.id]
    await ctx.send(f"{g['player']} | Dealer {g['dealer'][0]}, ?")

@bot.command()
async def hit(ctx):
    g = games.get(ctx.author.id)
    if not g: return

    g["player"].append(draw())

    if sum(g["player"])>21:
        get_user(ctx.author.id)["money"] -= g["bet"]
        games.pop(ctx.author.id)
        save()
        await ctx.send("💀 Bù")
    else:
        await ctx.send(str(g["player"]))

@bot.command()
async def stand(ctx):
    g = games.get(ctx.author.id)
    if not g: return

    while sum(g["dealer"])<17:
        g["dealer"].append(draw())

    p = sum(g["player"])
    d = sum(g["dealer"])

    u = get_user(ctx.author.id)

    if d>21 or p>d:
        u["money"] += g["bet"]
    else:
        u["money"] -= g["bet"]

    save()
    games.pop(ctx.author.id)

    await ctx.send(f"{p} vs {d}")

# ================= BACCARAT =================
@bot.command()
async def baccarat(ctx, bet:int, choice:str):
    u = get_user(ctx.author.id)
    if u["money"] < bet:
        return

    p = random.randint(0,9)
    b = random.randint(0,9)

    result = "player" if p>b else "banker" if b>p else "tie"

    if choice == result:
        u["money"] += bet*2
    else:
        u["money"] -= bet

    save()
    await ctx.send(f"P:{p} B:{b} => {result}")

# ================= BOMB =================
@bot.command()
async def bomb(ctx, bet:int, choice:str):
    u = get_user(ctx.author.id)
    result = random.choice(["sống","nổ"])

    if choice == result:
        u["money"] += bet*3
    else:
        u["money"] -= bet

    save()
    await ctx.send(result)

# ================= BAU CUA (PHYSICS + GIF) =================
@bot.command()
async def baucu(ctx, bet, choice:str):
    u = get_user(ctx.author.id)
    bet = parse_bet(u, bet)

    animals = ["nai","bầu","gà","cá","cua","tôm"]

    if choice not in animals:
        return await ctx.send("❌ Chọn: nai/bầu/gà/cá/cua/tôm")

    icons = {
        "nai":"🦌","bầu":"🍐","gà":"🐓",
        "cá":"🐟","cua":"🦀","tôm":"🦐"
    }

    msg = await ctx.send("🎲 Lắc bầu cua...")

    velocity = 0.05
    for i in range(20):
        fake = [icons[random.choice(animals)] for _ in range(3)]
        await msg.edit(content="🎲 " + " | ".join(fake))
        await asyncio.sleep(velocity)
        velocity += 0.01

    await msg.edit(content="🎲 Mở bát...")
    await asyncio.sleep(0.8)

    dice = [random.choice(animals) for _ in range(3)]
    visual = " | ".join([icons[d] for d in dice])

    count = dice.count(choice)

    if count > 0:
        win = bet * count
        u["money"] += win
        result_text = f"🎉 Trúng {count} lần +{win:,}"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        result_text = "💀 Không trúng"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(
        title="🎲 BẦU CUA PHYSICS",
        description=result_text,
        color=random.choice([0x00ffcc,0xffcc00,0xff0066])
    )

    embed.add_field(name="Kết quả", value=visual)
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= TOP =================
@bot.command()
async def top(ctx):
    s = sorted(users.items(), key=lambda x: x[1]["money"]+x[1]["bank"], reverse=True)
    msg="TOP\n"
    for i,(uid,data) in enumerate(s[:5]):
        user=await bot.fetch_user(int(uid))
        msg+=f"{i+1}. {user.name} - {data['money']+data['bank']}\n"
    await ctx.send(msg)

# ================= HELP =================
@bot.command()
async def guide(ctx):
    await ctx.send("slot, taixiu, flip, bj, baccarat, bomb | bal, pay, bank...")

# ================= READY =================
@bot.event
async def on_ready():
    print("BOT MAX ONLINE")

bot.run(TOKEN)
