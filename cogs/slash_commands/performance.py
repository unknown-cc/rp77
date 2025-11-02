import os
from discord.ext import commands
from xiancord.core import Cog_Extension
from discord.ext import commands
from discord import app_commands , Interaction , Embed , Colour , ButtonStyle
from discord.ui import View , Button , Modal , TextInput
from discord.app_commands import locale_str as ls
from xiancord.emojis import emojigot
from xiancord.logger import terminal
from xiancord.database import db
from xiancord.time import now_str
from gspread import Worksheet
import discord
GUILD_ID = 1383475660646907966
ROLE_ID = 1425797699810361344
golden_master = 223781411990142976
PRICE_YOULUAN = 10000 # 友露安
PRICE_SPEED = 50000 # 跑速藥水
WORKSHEET : Worksheet= None

def get_nick(member : discord.Member):
    nick = member.nick
    if not nick :
        return member.display_name
    if "｜" in nick:
        return nick.split("｜")[-1]
    else:
        return nick
    
async def get_database():
    global WORKSHEET
    database =  db.get("黑曜國際")
    worksheet = await database.get_sheet("業績紀錄")
    WORKSHEET = worksheet
    
async def update_data(discord_id , nick , product , amount):
    global WORKSHEET
    if not WORKSHEET:
        terminal("資料庫無法連線"); return
    #公司抽成 , 郭郭抽成 , 製造抽成 , 接單抽成
    commission1 , commission2 , commission4 = 0 , 0 , 0 
    if product == "友露安":            
        commission1 = 0.2
        commission2 = 0.0
        commission4 = 0.2
    elif product == "跑速藥水":
        commission1 = 0.9
        commission2 = 0.0
        commission4 = 0.1
    elif product == "槍枝修復":
        commission1 = 0.7
        commission2 = 0.2
        commission4 = 0.1
    elif product == "槍枝出售" :
        commission1 = 0.6
        commission2 = 0.0
        commission4 = 0.1
    elif product == "毒品出售" :
        commission1 = 0.6
        commission2 = 0.0
        commission4 = 0.1
    await WORKSHEET.append_row([now_str("%m/%d %H:%M:%S") , nick , str(discord_id) , product , amount , amount * commission1 , amount * commission2 , amount * commission4])

async def get_data(delete_data = False):
    total_result = {
        'total' : 0,
        'company' : 0,
        'personal' : 0
    }
    data = await WORKSHEET.get_all_records()
    result = {}
    golden_result = {}
    golden_result['amount'] = 0
    golden_result['detail'] = ""
    for d in data:
        # 個人抽成
        discord_id = d["discord_id"]
        r : dict = result.get(discord_id , {})
        detail = r.get("detail" , "")
        amount = r.get("amount" , 0)
        amount += int(d['接單抽成'])
        detail += f"-# {emojigot('ArrowWave_4')}{d['時間']}｜{d['暱稱']}｜{d['產品項目']}｜總金額 {d['總金額']} 元｜分潤 {d['接單抽成']} 元\n"
        r['detail'] = detail
        r['amount'] = amount
        result[discord_id]  = r
        total_result['total'] += int(d['總金額'])
        total_result["company"] += int(d['公司抽成'])
        total_result["personal"] += int(d['接單抽成'])
        # 郭郭抽成
        if d['產品項目'] == "槍枝修復":
            golden_result['amount'] += int(d['郭郭抽成'])
            golden_result['detail'] += f"-# {emojigot('ArrowWave_4')}{d['時間']}｜{d['暱稱']}｜{d['產品項目']}｜總金額 {d['總金額']} 元｜分潤 {d['郭郭抽成']} 元\n"
    if delete_data:
        await WORKSHEET.batch_clear(['A2:Z'])
    return result , golden_result , total_result

class performance(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業績"
        self.record = {}
        self.worksheet = None
   
    async def cog_load(self):
        await get_database()
    
    @app_commands.command(name=ls("performance" , zh_TW="銷售回報") , description=ls("result performance" , zh_TW="銷售回報"))
    @app_commands.guild_only()
    @app_commands.guilds(GUILD_ID)
    @app_commands.rename(product = ls("product" , zh_TW="產品") , amount = ls("amount" , zh_TW="總金額") , image = ls("image" , zh_TW="公庫附圖"))
    @app_commands.choices(
        product = [
            app_commands.Choice(name="槍枝修復" , value= "槍枝修復"),
            app_commands.Choice(name="跑速藥水" , value= "跑速藥水"),
            app_commands.Choice(name="友露安" , value= "友露安"),
            app_commands.Choice(name="槍枝出售" , value= "槍枝出售"),
            app_commands.Choice(name="毒品出售" , value= "毒品販售"),])
    async def performance_result(self , interaction:Interaction , product:str , amount : int , image:discord.Attachment):
        user = interaction.user
        embed = Embed(title = "銷售回報" , description=f"__<@&{ROLE_ID}> 簽核過才會進資料庫__")
        embed.add_field(name="回報人員" , value=user.mention , inline=False)
        embed.add_field(name="產品類型" , value=product)
        embed.add_field(name="回報金額" , value=amount)
        embed.set_image(url=image.url)
        embed.set_thumbnail(url=user.avatar.url)
        await interaction.response.send_message(embed=embed , view=TicketView() , silent=True)

    def get_output(self , guild :discord.Guild , result :dict , golden_result :dict , total_result :dict , delete :bool):
        output = ""
        if not result == {}:
            for discord_id , r in result.items():
                member = guild.get_member(int(discord_id))
                if not member:continue
                output += f"### {emojigot('029')} {member.nick} ({member.id})｜總分潤：{r['amount']} 元\n{r['detail']}\n"
            output += f"### {emojigot('040')} 郭郭 ({golden_master}) ｜總分潤：{golden_result['amount']} 元\n{golden_result['detail']}"
            if delete:
                title = f"### {emojigot('StarryMoon_azalea')} 總營收："
            else:
                title = f"### {emojigot('StarryMoon_azalea')} 當前營收："
            output = title + f"{total_result['total']} 元\n{emojigot('ArrowWave_red')}公司｜總抽成：{total_result['company']} 元\n{emojigot('ArrowWave_white')}成員｜總抽成：{total_result['personal']} 元\n{emojigot('ArrowWave_cyan')}郭郭｜總抽成：{golden_result['amount']} 元\n" + output
        else:
            output = f"{emojigot('butterfly1')} 目前沒有任何紀錄"
        return output
    async def interaction_output(self, interaction : Interaction , output:str):
        if len(output) >= 2000:
            part = ""
            lines = output.split("\n")
            for line in lines:
                if not line : continue
                new_line = line + "\n"
                if len(part + new_line) >= 2000:
                    await interaction.channel.send(content=part)
                    part = ""
                else:
                    part+= new_line
            else:
                await interaction.channel.send(content=part)
        else:
            await interaction.followup.edit_message('@original' , content=output)

    performance_group = app_commands.Group(name=ls("performance_group" , zh_TW="業績") , description=ls("performance_group" , zh_TW="業績相關指令"),
                                           guild_ids=[GUILD_ID,] , guild_only=True)

    @performance_group.command(name=ls("performance_settlement" , zh_TW="結算") , description=ls("performance_settlement" , zh_TW="業績結算，清除業績紀錄，統計每個人應得分潤"))
    async def performance_settlement(self, interaction:Interaction):
        await interaction.response.send_message("正在統計數據....." , ephemeral=True , delete_after=3)
        result  , golden_result  , total_result = await get_data(delete_data=True)
        output = self.get_output(interaction.guild , result , golden_result , total_result , True)
        await self.interaction_output(interaction , output)

    @performance_group.command(name=ls("performance_show" , zh_TW="顯示") , description=ls("performance_show" , zh_TW="只列出目前的統計數據，不做結算，不清除資料"))
    async def performance_show(self, interaction:Interaction):
        await interaction.response.send_message("正在統計數據....." , ephemeral=True , delete_after=3)
        result  , golden_result  , total= await get_data()
        output = self.get_output(interaction.guild , result , golden_result , total , False)        
        await self.interaction_output(interaction , output)


async def setup(bot:commands.Bot):
    await bot.add_cog(performance(bot))
    bot.add_view(TicketView())

class TicketView(View):
    def __init__(self, *, timeout = None):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="上級簽核", custom_id="signButton" ,
                       style=ButtonStyle.grey , emoji=emojigot('check3'))
    async def signButtonCallback(self , interaction : Interaction , button :Button):
        for role in interaction.user.roles:
            if role.id == ROLE_ID:
                break
        else:
            return await interaction.response.send_message(f"{emojigot('no3')} 你不是 <@&{ROLE_ID}>" , ephemeral=True)
        self.clear_items()
        superior = get_nick(interaction.user)
        button.label = f"{superior}｜已簽核"
        button.disabled = True
        self.add_item(button)
        await interaction.response.edit_message(view=self)
        # 新增置資料庫
        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name == "回報人員":
                discord_id = field.value.strip("<@!>")
                member = interaction.guild.get_member(int(discord_id))
                nick = get_nick(member)
            elif field.name == "產品類型":
                product = field.value
            elif field.name == "回報金額":
                amount = int(field.value)
        await update_data(discord_id , nick , product , amount)

    @discord.ui.button(label="抽單", custom_id="deleteButton" ,
                       style=ButtonStyle.grey , emoji=emojigot('Sakura_red'))
    async def deleteButtonCallback(self , interaction : Interaction , button :Button):
        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name == "回報人員":
                discord_id = field.value.strip("<@!>")
                member = interaction.guild.get_member(int(discord_id))
        user = interaction.user
        if user.id == member.id:
            return await interaction.message.delete()
        else:
            for role in user.roles:
                if role.id == ROLE_ID:
                    break
            else:
                return await interaction.response.send_message(f"{emojigot('no3')} 必須是本人或 <@&{ROLE_ID}> 才能撤銷" , ephemeral=True)
            modal = Modal(title="抽單" , timeout=None)
            reason_input_text = TextInput(label="原因" , placeholder="請輸入原因" ,default="錯" , required=True , max_length=10)
            async def on_submit(interaction:Interaction):
                await interaction.response.defer()
            modal.add_item(reason_input_text)
            modal.on_submit = on_submit
            await interaction.response.send_modal(modal)
            await modal.wait()
            superior = get_nick(interaction.user)
            if reason_input_text.value:
                self.clear_items()
                button.label = f"{superior}｜抽單-{reason_input_text.value}"
                button.disabled=True
                self.add_item(button)
                return await interaction.message.edit(view=self)