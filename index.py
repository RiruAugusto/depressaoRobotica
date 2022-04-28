import datetime
import discord
import json
import random
from discord.ext import tasks
from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import locale
from sys import platform
import os
import asyncio

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# importando respostas basicas = fala algo : responde algo
with open('links.json', encoding='utf-8') as data:
    response_object = json.load(data)

# importando configurações pessoais por um json

with open('config.json', 'r') as conf:
    confs = json.load(conf)
    btoken = confs['token']
    prefix = confs['prefix']
    IDCanalProvas = confs['canalDeProvas']
    testeID = confs['testeID']

avisosAutomaticos = True

if btoken == '' or btoken == None:
    print('Sem token do Bot')
    raise RuntimeError('Sem token do Bot')
if prefix == '':
    prefix = '!'
if IDCanalProvas == '':
    avisosAutomaticos = False
    print('Sem ID do canal para avisos automáticos, não haveram mensagens automáticas')

def diaSemana(wDia):
    dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
    return dias[wDia]

def plataformaWindows():
    if platform.startswith("win32"):
        return True
    else:
        return False

def leRoles():
    with open('roles.txt', 'r+', encoding='utf-8') as f:
        roles = f.read()
        return roles.split(',')


def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


# pemitindo o bot ver outras pessoas, e mais algumas coisas da API que eu com certeza entendo
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    
    if avisosAutomaticos:
        canal = bot.get_channel(int(IDCanalProvas))
        if canal in bot.get_all_channels():
            if canal.permissions_for(canal.guild.me).read_messages and canal.permissions_for(canal.guild.me).send_messages:
                if not plataformaWindows:
                    aviso_provas.start(IDCanalProvas)
            else:
                print('Não consigo mandar mesnagens no canal de aviso de provas')
        else:
            print('Não encontrei o canal indicado para os avisos de provas')
    
    print(f'Conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))

    print(f'Usando "{prefix}" como prefixo para comandos.')
  
    print(f'Bot foi iniciado, com {len(bot.users)} usuários, em {len(bot.guilds)} servers.')


@bot.event
async def on_voice_state_update(member, before, after):
    
    if member.id != bot.user.id:
        return

    elif after.channel is not None:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time >= 300:
                await voice.disconnect()
                await canalConectado.send('Cansei de segurar o revólver')
            if not voice.is_connected():
                break
# @bot.event
# async def on_typing(ch, us, wh):
#     await ch.send(f'FALA LOGO {us.mention}')
    
@bot.command()
async def ping(ctx):
    pingm = await ctx.channel.send('Ping?')
    await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - ctx.message.created_at)[8:-3], round(bot.latency*1000)))


@bot.command()
async def role(ctx):
    
    n = random.randint(1, 5)
    if n == 1:
        m = await ctx.channel.send(f'{ctx.message.author.mention}Top!')
    elif n == 2:
        m = await ctx.channel.send(f'{ctx.message.author.mention}Jungle!')
    elif n == 3:
        m = await ctx.channel.send(f'{ctx.message.author.mention}Mid!')
    elif n == 4:
        m = await ctx.channel.send(f'{ctx.message.author.mention}Adc!')
    elif n == 5:
        m = await ctx.channel.send(f'{ctx.message.author.mention}Sup!')

    await ctx.message.delete()
    await m.delete(delay=60)

@slash.slash(name='roleta',
            description='Roleta por texto',
            guild_ids=[317781355113086976, 477183409572282379],
            options=[
                create_option(
                    name='balas',
                    description='Número de balas',
                    required=False,
                    option_type=3
                )
            ])

@bot.command()
async def caralho(ctx):

    await ctx.message.delete()
    roletaVC = ctx.message.guild.voice_client
    roletaVC.play(discord.FFmpegPCMAudio("audio/a.mp3"))

@bot.command()
async def roleta(ctx, *, balas='1'):
    
    heya = bot.get_emoji(895327381437448204)
    gun = bot.get_emoji(895329552518217798)

    if gun not in ctx.guild.emojis:
        gun = ':gun:'
    if heya not in ctx.guild.emojis:
        heya = ':smiley:'
    


    try:
        balas = int(balas)
    except ValueError: 
        mes = await ctx.reply(f'Me fala quando conseguir colocar "{balas}" balas no revólver')
        await mes.delete(delay=10)
        return

    n = random.randint(1, 6)
    if balas < 0:
        await ctx.reply('Muito corajoso você')
    elif balas == 0:
        await ctx.reply(f'{heya} Sobreviveu! Que surpresa né?')
    elif balas > 6:
        await ctx.reply('Você é corajoso até demais')
    elif balas == 6:
        await ctx.reply(f'{gun} Morreu! Achei o suicida')
    elif n <= balas:
        await ctx.reply(f'{gun} Morreu!')
    else:
        await ctx.reply(f'{heya} Sobreviveu!')

@bot.command()
async def comandos(ctx):

    embedComandos = discord.Embed(
    title=f'{bot.user} Comandos', color=0xF0F0F0)

    embedComandos.set_thumbnail(url=bot.user.avatar_url)

    embedComandos.add_field(name=f'{prefix}ping', value='Testa o ping do bot e da API do discord', inline=False)
    embedComandos.add_field(name=f'{prefix}roleta (1-6)', value='Uma roleta russa, opcionalmente escreva o número de balas a ser usado', inline=False)
    embedComandos.add_field(name=f'{prefix}roletav/{prefix}r (1-6)', value=f'Roleta russa por comando de voz, use {prefix}carrega para chamar o bot.\nopcionalmente escreva o número de balas a ser usado', inline=False)
    embedComandos.add_field(name=f'{prefix}comandos', value='Mostra uma lista de comandos', inline=False)
    embedComandos.add_field(name=f'{prefix}provas', value='Mostra as provas para os próximos 7 dias', inline=False)
    
    await ctx.reply(embed=embedComandos)

    # await ctx.reply(f'**{bot.user}**\n{prefix}ping, {prefix}roleta (numero de balas), {prefix}comandos, {prefix}provas, {prefix}roletav')

@bot.command(aliases=['carregar'])
async def carrega(ctx):

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()

    if ctx.author.voice is None:
            await ctx.channel.send("Você não está conectado em nenhum canal de voz")
            return

    global canalConectado
    canalConectado = ctx.channel

    if not is_connected(ctx):
        roletaVC = await ctx.author.voice.channel.connect()
        await ctx.channel.send(f'Conectado em {roletaVC.channel}')

    else:
        roletaVC = ctx.message.guild.voice_client
        await roletaVC.move_to(ctx.author.voice.channel)

    roletaVC.play(discord.FFmpegPCMAudio("audio/reload.mp3"))

@bot.command(aliases=['descarregar'])
async def descarrega(ctx):

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()

    if is_connected(ctx):
        await ctx.message.guild.voice_client.disconnect()
    else:
        await ctx.channel.send('Não estou conectado em nenhum canal')


@bot.command(aliases=['r', 'rpg'])
async def roletav(ctx, *, argumentos='1'):

    if not ctx.message.guild.voice_client:
        await ctx.channel.send(f'Não estou conectado a nenhum canal, use {prefix}carrega')
        return

    if ctx.author.voice is None:
            await ctx.channel.send("Você não está conectado em nenhum canal de voz")
            return

    consegueMover = ctx.author.voice.channel.permissions_for(ctx.guild.me).move_members

    roletaVC = ctx.message.guild.voice_client

    if ctx.author.voice.channel == ctx.message.guild.voice_client.channel:
        if ctx.voice_client.is_playing():
            mes = await ctx.reply('Calma, tem bala pra todo mundo!:)')
            await mes.delete(delay=10)
        else:
            try:
                balas = int(argumentos)
            except ValueError: 
                mes = await ctx.reply(f'Me fala quando conseguir colocar "{argumentos}" balas no revólver')
                await mes.delete(delay=10)
                return

            n = random.randint(1, 6)
            if balas < 0:
                roletaVC.play(discord.FFmpegPCMAudio("audio/uepa.mp3"))
                await asyncio.sleep(1)
                mes = await ctx.reply('Muito corajoso você')
                await mes.delete(delay=10)
            elif balas == 0:
                roletaVC.play(discord.FFmpegPCMAudio("audio/uepa.mp3"))
            elif balas > 6:
                mes = await ctx.reply('Você é corajoso até demais')
                await mes.delete(delay=10)
            elif balas == 6:
                if ctx.invoked_with == 'rpg':
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiroG.mp3"))
                else:
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiro.mp3"))
                await asyncio.sleep(1)
                if consegueMover:
                    await ctx.message.author.move_to(None)
                else:
                    await ctx.reply('Muito forte')
            elif n <= balas:
                if ctx.invoked_with == 'rpg':
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiroG.mp3"))
                else:
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiro.mp3"))
                await asyncio.sleep(1)
                if consegueMover:
                    await ctx.message.author.move_to(None)
                else:
                    await ctx.reply('Muito forte')
            else:
                roletaVC.play(discord.FFmpegPCMAudio("audio/falha.mp3"))
                await asyncio.sleep(1.5)
                roletaVC.play(discord.FFmpegPCMAudio("audio/tambor.mp3"))

    else:
        await roletaVC.move_to(ctx.author.voice.channel)
    
    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()


# @bot.command()
# async def adiciona(ctx, roleNova):

#     roles = leRoles()
#     if roles == ['']:
#         roles.clear()
#     roles.append(roleNova)

#     roles = ','.join(roles)

#     with open('roles.txt', 'r+', encoding='utf-8') as f:
#         f.seek(0)
#         f.write(roles)
#     await ctx.channel.send(leRoles())

# @bot.command()
# async def remove(ctx, roleRemove):

#     roles = leRoles()
#     if roleRemove in roles:
#         roles.remove(roleRemove)

#     roles = ','.join(roles)
#     print(roles)

#     with open('roles.txt', 'r+', encoding='utf-8') as f:
#         f.seek(0)
#         f.write(roles)
#     await ctx.channel.send(leRoles())    


@bot.command()
async def provas(ctx):

    with open('provas.json', encoding='utf-8') as prov:
        provas = json.load(prov)

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()
    
    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()

    embedProvas = discord.Embed(
    title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para a semana', color=0x336EFF)

    embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

    for attribute in provas:
            value = provas[attribute]
            diaDaProva = datetime.date.fromisoformat(value)

            if(diaDaProva-hoje).days == 1:
                embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
                embedProvas.color = 0xFFFF00

            if(diaDaProva-hoje).days == 0:
                embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
                embedProvas.color = 0xFF0000
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'__->**É HOJE FIOTE** PROVA DE {attribute}, {diaDaSemana}, {dia}__', inline=False)
            
            elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'->Prova de {attribute}, {diaDaSemana}, {dia} em **{(diaDaProva-hoje).days} dias**', inline=False)


    mensagemJunto = await ctx.channel.send(f'{ctx.author.mention}')
    mensagemEmbed = await ctx.channel.send(embed=embedProvas)
    await mensagemJunto.delete(delay=60)
    await mensagemEmbed.delete(delay=60)

# @bot.command
# async def reseta(ctx):

#     # depois revisitar esse codigo, ele nao eh amigavel com varios servers
#     # especificar o server e canal
#     if ctx.author.id == testeID:
#         aviso_provas.cancel()
#         aviso_provas.start(IDCanalProvas)
#     else:
#         ctx.reply('você não possui permissão para usar esse comando!')

@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    if ctx.content.lower().__contains__('bitches'):
        await ctx.channel.send("  ⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝\n⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇\n  ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀\n   ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁\n  ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉\n  ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂\n  ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂\n  ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁\n  ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏\n  ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝\n  ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟\n  ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟\n  ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀")
    
    if ctx.content in response_object:
        await ctx.channel.send(response_object[ctx.content])

    if bot.user.mentioned_in(ctx):
        await comandos(ctx)
    
    await bot.process_commands(ctx)


@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas(IDcanalProvas):

    with open('provas.json', encoding='utf-8') as prov:
        provas = json.load(prov)

    canalProvas = bot.get_channel(int(IDcanalProvas))

    # verificar se as mensagens sao do bot antes de deletar
    await canalProvas.purge(limit=2, bulk=False)

    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()
    
    embedProvas = discord.Embed(
            title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description='Provas para a semana', color=0x336EFF)
    
    embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

    for attribute in provas:
            value = provas[attribute]

            diaDaProva = datetime.date.fromisoformat(value)

            if(diaDaProva-hoje).days == 1:
                embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
                embedProvas.color = 0xFFFF00

            if(diaDaProva-hoje).days == 0:
                embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
                embedProvas.color = 0xFF0000
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'__->**É HOJE RAPAZIADA** PROVA DE {attribute}, {diaDaSemana}, {dia}__', inline=False)

            elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'->Prova de {attribute}, {diaDaSemana}, {dia} em **{(diaDaProva-hoje).days} dias**', inline=False)

    await canalProvas.send('@everyone')
    await canalProvas.send(embed=embedProvas)

bot.run(btoken)

