import discord
from discord import ui, SelectOption
from discord.ui import View, Button, Modal, TextInput, button, Select
from discord.ext import commands, tasks
import datetime
from discord import app_commands, Interaction, Member, User, utils as Utils
import asyncio
from typing import Optional
import sqlite3
import os
from discord import ButtonStyle, Embed
import qrcode
from discord.ui import Button, View
import tempfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re
import aiosqlite
import crcmod.predefined
import paypalrestsdk
import pytz
import aiohttp
from humanfriendly import parse_timespan, InvalidTimespan
from discord import FFmpegPCMAudio
import random
import time
import requests
from io import BytesIO

DATABASE_PATH = 'economy.db'


@bot.event
async def on_ready():
    print("Estou conectado!!!")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s)")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


@bot.command()
@commands.has_permissions(kick_members=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def serverinfo(ctx):
    server = ctx.guild

    embed = discord.Embed(title="Server Info", color=0x00ff00)
    embed.add_field(name="Server Name", value=server.name, inline=False)
    embed.add_field(name="Server ID", value=server.id, inline=False)
    embed.add_field(name="Owner", value=f"{server.owner.name}#{server.owner.discriminator}", inline=False)
    embed.add_field(name="Members", value=server.member_count, inline=False)
    embed.add_field(name="Bots", value=sum(1 for member in server.members if member.bot), inline=False)
    embed.add_field(name="Channels", value=len(server.channels), inline=False)
    embed.add_field(name="Roles", value=len(server.roles), inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send('Channel locked.')

@bot.command()
@commands.has_permissions(kick_members=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send('Channel unlocked.')


@bot.tree.command(name="oi")
async def oi(interaction: discord.Interaction):
    await interaction.response.send_message(f"oi {interaction.user.mention}")

@bot.tree.command(name="mute", description="Da Castigo/mute")
@commands.has_permissions(kick_members=True)
@app_commands.describe(
    user="O usuário que você deseja mutar.",
    timelimit="O tempo em que o usuário será mutado (ex: 5m para 5 minutos)."
)
async def mute(
	interaction:discord.Interaction,
	user: Member,
	timelimit: Optional[str],
):
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

    # Verificando se a unidade de tempo fornecida é válida
    unit = timelimit[-1].lower()
    if unit not in time_units:
        return

    try:
        # Convertendo o tempo para segundos
        gettime = int(timelimit[:-1]) * time_units[unit]
    except ValueError:
        return

    newtime = datetime.timedelta(seconds=gettime)

    # Usando a nova função de mute
    await user.edit(timed_out_until=discord.utils.utcnow() + newtime)
    await interaction.response.send_message(f"**{user}** Punido com Sucesso!!!")



@bot.command()
@commands.is_owner() 
async def sync(ctx,guild=None):
    await ctx.send("**Anti Raid Básico Sincronizado!!!**",view=SubButton())

@bot.command()
@commands.is_owner() 
async def desync(ctx,guild=None):
    await ctx.send("**Anti Raid Básico foi desativado!!!**",view=SubButton())


@bot.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, timelimit):
    # Mapeando as unidades de tempo para seus respectivos segundos
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

    # Verificando se a unidade de tempo fornecida é válida
    unit = timelimit[-1].lower()
    if unit not in time_units:
        await ctx.send("Unidade de tempo inválida. Use 's' para segundos, 'm' para minutos, 'h' para horas, 'd' para dias.")
        return

    try:
        # Convertendo o tempo para segundos
        gettime = int(timelimit[:-1]) * time_units[unit]
    except ValueError:
        await ctx.send("Formato de tempo inválido.")
        return

    newtime = datetime.timedelta(seconds=gettime)

    # Usando a nova função de mute
    await member.edit(timed_out_until=discord.utils.utcnow() + newtime)

    # Criando um embed sem descrição
    embed = discord.Embed(title=f'{member.display_name} Mutado com Sucesso', color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command()
async def unmute(ctx, member: discord.Member):
    # Usando a nova função de unmute
    await member.edit(timed_out_until=None)

    # Criando um embed sem descrição e sem rodapé
    embed = discord.Embed(
        title=f'{member.display_name} Desmutado com Sucesso',
        color=discord.Color.green()
    )

    # Enviando o embed
    await ctx.send(embed=embed)

class EmbedCustomizerView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.interaction = interaction
        self.embed = discord.Embed(title="Título inicial", description="Descrição inicial", color=0x00ff00)

    async def on_timeout(self):
        await self.interaction.response.edit_message(embed=self.embed, view=None)


    @discord.ui.button(label="Adicionar Título", style=discord.ButtonStyle.grey, emoji="✏️")
    async def add_title_button(self, interaction: discord.Interaction, button: ui.Button):
        title_modal = TitleModal(self)
        await interaction.response.send_modal(title_modal)

    @discord.ui.button(label="Adicionar Descrição", style=discord.ButtonStyle.grey, emoji="📝")
    async def add_description_button(self, interaction: discord.Interaction, button: ui.Button):
        description_modal = DescriptionModal(self)
        await interaction.response.send_modal(description_modal)

    @discord.ui.button(label="Escolher Cor", style=discord.ButtonStyle.grey, emoji="<a:red_brilho:806565883346550905>")
    async def choose_color_button(self, interaction: discord.Interaction, button: ui.Button):
        color_modal = ColorModal(self)
        await interaction.response.send_modal(color_modal)

    @discord.ui.button(label="Adicionar Imagem", style=discord.ButtonStyle.grey)
    async def add_image_button(self, interaction: discord.Interaction, button: ui.Button):
        image_modal = ImageModal(self)
        await interaction.response.send_modal(image_modal)

    @discord.ui.button(label="Enviar Embed", style=discord.ButtonStyle.green)
    async def send_embed_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Sucesso!!!", ephemeral=True)
        await interaction.channel.send(embed=self.embed)

    @discord.ui.button(label="Exportar Python", style=discord.ButtonStyle.primary)
    async def export_python_button(self, interaction: discord.Interaction, button: ui.Button):
        python_code = f"""```python
embed = discord.Embed(title="{self.embed.title}", description="{self.embed.description}", color={self.embed.color.value}"""
        
        if self.embed.image:
            python_code += f""", url="{self.embed.image.url}" """
        
        python_code += """)
interaction.channel.send(embed=embed)
```"""
        await interaction.response.send_message(python_code, ephemeral=True)

    @discord.ui.button(label="Importar Python", style=discord.ButtonStyle.primary)
    async def import_python_button(self, interaction: discord.Interaction, button: ui.Button):
        import_modal = PythonImportModal(self)
        await interaction.response.send_modal(import_modal)
      
    @discord.ui.button(label="Remover Título", style=discord.ButtonStyle.danger, emoji="❌")
    async def remove_title_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.title = None  # Remove o título
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label="Remover Descrição", style=discord.ButtonStyle.danger, emoji="❌")
    async def remove_description_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.description = None  # Remove a descrição
        await interaction.response.edit_message(embed=self.embed)      



@bot.tree.command(name="embed", description="Personalize um embed")
async def custom_embed(interaction: discord.Interaction):
    embed = discord.Embed(title="Título inicial", description="Descrição inicial", color=0x00ff00)
    view = EmbedCustomizerView(interaction)
    embed_message = await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    view.embed_message = embed_message



class TitleModal(ui.Modal, title="Adicionar Título"):
    def __init__(self, view):
        super().__init__(timeout=60)
        self.view = view

    title_input = ui.TextInput(label="Digite o título", placeholder="Título...", style=discord.TextStyle.short)
	
    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = f"{self.title_input.value}"
        await interaction.response.edit_message(embed=self.view.embed)

class DescriptionModal(ui.Modal, title="Adicionar Descrição"):
    def __init__(self, view):
        super().__init__(timeout=60)
        self.view = view

    description_input = ui.TextInput(label="Digite a descrição", placeholder="Descrição...", style=discord.TextStyle.long)
	
    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.description = f"{self.description_input.value}"
        await interaction.response.edit_message(embed=self.view.embed)

class ColorModal(ui.Modal, title="Escolher Cor"):
    def __init__(self, view):
        super().__init__(timeout=60)
        self.view = view

    color_input = ui.TextInput(label="Digite a cor em formato hexadecimal", placeholder="#RRGGBB", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Converta a cor hexadecimal de string para inteiro
            color_value = int(self.color_input.value, 16)
            self.view.embed.color = discord.Colour(color_value)
            await interaction.response.edit_message(embed=self.view.embed)
        except ValueError:
            await interaction.response.send_message("Formato de cor inválido. Use o formato #RRGGBB.", ephemeral=True)
		

class ImageModal(ui.Modal, title="Adicionar Imagem"):
    def __init__(self, view):
        super().__init__(timeout=60)
        self.view = view

    image_url_input = ui.TextInput(label="Digite a URL da imagem", placeholder="URL da imagem...", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.set_image(url=self.image_url_input.value)
        await interaction.response.edit_message(embed=self.view.embed)

class PythonImportModal(ui.Modal, title="Importar Python"):
    def __init__(self, view):
        super().__init__(timeout=60)
        self.view = view

    python_code_input = ui.TextInput(label="Cole aqui o código Python para o Embed", placeholder="Código Python...", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Obtém o código Python fornecido
            embed = self.python_code_input.value


            # Define o Embed criado como resposta
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao avaliar o código Python: {e}", ephemeral=True)

@bot.command(name="servers")
async def get_server_count(ctx):
    await ctx.send(f"Estou atualmente em {len(bot.guilds)} servidores.")


@bot.tree.command(name="servers")
async def servers(interaction: discord.Interaction):
    await interaction.response.send_message(f"Estou atualmente em {len(bot.guilds)} servidores.", ephemeral=True)


class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="atendimento",label="Atendimento", emoji="📨"),
            discord.SelectOption(value="denuncia",label="Denúncia", emoji="🚨"),
        ]
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "atendimento":
            await interaction.response.send_message("Então, gostaria de abrir um ticket?",ephemeral=True,view=CreateTicket())
        if self.values[0] == "denuncia":
            await interaction.response.send_message("Então, gostaria de abrir um ticket de denúncia?",ephemeral=True,view=CreateTicket2())


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value = None

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, emoji="➕")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True, content=f"Você já tem um atendimento em andamento!")
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!", view=None)
                    return

        if ticket is not None:
            await ticket.edit(archived=False, locked=False)
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080, invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(ephemeral=True, content=f"Criei um ticket para você! {ticket.mention}")
        await ticket.send(f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e aguarde até que um atendente responda.\n\n<@&1240283766551744535>\nApós a sua questão ser sanada, você pode usar `/fecharticket` para encerrar o atendimento!")

        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Ticket Criado", color=discord.Color.green())
            embed.add_field(name="Usuário", value=interaction.user.mention, inline=True)
            embed.add_field(name="Canal", value=ticket.name, inline=True)
            embed.add_field(name="ID do Canal", value=ticket.id, inline=True)
            embed.timestamp = interaction.created_at
            await log_channel.send(embed=embed)


class CreateTicket2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value = None

    @discord.ui.button(label="Abrir Ticket de denúncia", style=discord.ButtonStyle.green, emoji="➕")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True, content=f"Você já tem um atendimento em andamento!")
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!", view=None)
                    return

        if ticket is not None:
            await ticket.edit(archived=False, locked=False)
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080, invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(ephemeral=True, content=f"Criei um ticket para você! {ticket.mention}")
        await ticket.send(f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e aguarde até que um atendente responda.\n\n<@&1240283766551744535><@&1240283766551744534>\nApós a sua questão ser sanada, você pode usar `/fecharticket` para encerrar o atendimento!")

        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Ticket de Denúncia Criado", color=discord.Color.green())
            embed.add_field(name="Usuário", value=interaction.user.mention, inline=True)
            embed.add_field(name="Canal", value=ticket.name, inline=True)
            embed.add_field(name="ID do Canal", value=ticket.id, inline=True)
            embed.timestamp = interaction.created_at
            await log_channel.send(embed=embed)

id_cargo_atendente = 1257326799076196392
mod = 1257326799076196392
log_channel_id = 1240283767344599080

@bot.tree.command(name = 'setup', description='Setup')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="Central de ajuda", description="Escolha uma opção abaixo:", color=00000)
    embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0446.gif")
    await interaction.response.send_message(embed=embed, view=DropdownView()) 
	

@bot.tree.command(name="fecharticket", description='Feche um atendimento atual.')
async def _fecharticket1(interaction: discord.Interaction):
    mod = interaction.guild.get_role(id_cargo_atendente)
    extra_role = interaction.guild.get_role(1257326799076196392)
    
    if (str(interaction.user.id) in interaction.channel.name or 
        mod in interaction.user.roles or 
        extra_role in interaction.user.roles):
        
        await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
        await interaction.channel.edit(archived=True, locked=True)

        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Ticket Fechado", color=discord.Color.red())
            embed.add_field(name="Usuário", value=interaction.user.mention, inline=True)
            embed.add_field(name="Canal", value=interaction.channel.name, inline=True)
            embed.add_field(name="ID do Canal", value=interaction.channel.id, inline=True)
            embed.timestamp = interaction.created_at
            await log_channel.send(embed=embed)
    else:
        await interaction.response.send_message("Isso não pode ser feito aqui...")

target_user_id = 1199338020088840272

invite_regex = re.compile(r"(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)[a-zA-Z0-9]+")

target_channel_id = 1258081237902561401  # ID do canal específico

ping_role_id = 1261528441417760848

# Listas de respostas aleatórias
responses_create = [
    "Arquivo criado com sucesso! Espero que esteja tudo certinho!",
    "Prontinho, o arquivo foi criado.",
    "Aqui está! O arquivo foi criado sem problemas.",
    "Feito! O arquivo foi criado como você pediu."
]

responses_edit = [
    "Adição feita com sucesso! Está pronto para uso.",
    "Prontinho, conteúdo adicionado ao arquivo.",
    "Tudo certo! O arquivo foi atualizado.",
    "Concluído! O conteúdo foi inserido no arquivo."
]

responses_reset = [
    "Estou pronto para um novo começo! (Simulação de reset)",
    "Resetando... pronto! Tudo limpinho!",
    "O bot foi resetado! Pronto para novas instruções.",
    "Tudo resetado! Vamos começar do zero."
]

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('invites.db')
cursor = conn.cursor()

# Criação da tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS invites (
    user_id INTEGER,
    invite_count INTEGER DEFAULT 0
)
''')
conn.commit()

# Listas de respostas aleatórias
responses_create = [
    "Arquivo criado com sucesso! Espero que esteja tudo certinho!",
    "Prontinho, o arquivo foi criado.",
    "Aqui está! O arquivo foi criado sem problemas.",
    "Feito! O arquivo foi criado como você pediu."
]

responses_edit = [
    "Adição feita com sucesso! Está pronto para uso.",
    "Prontinho, conteúdo adicionado ao arquivo.",
    "Tudo certo! O arquivo foi atualizado.",
    "Concluído! O conteúdo foi inserido no arquivo."
]

responses_reset = [
    "Estou pronto para um novo começo! (Simulação de reset)",
    "Resetando... pronto! Tudo limpinho!",
    "O bot foi resetado! Pronto para novas instruções.",
    "Tudo resetado! Vamos começar do zero."
]

ignore_trovao = False

# Função para conectar ao banco de dados e criar a tabela se não existir
def setup_database():
    with sqlite3.connect('invites.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invites (
            user_id INTEGER PRIMARY KEY,
            invite_count INTEGER DEFAULT 0
        )
        ''')
        conn.commit()

# Chama a função para configurar o banco de dados
setup_database()

# Função para salvar o envio de convite no banco de dados
def save_invite(user_id):
    with sqlite3.connect('invites.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_count FROM invites WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            invite_count = result[0] + 1
            cursor.execute('UPDATE invites SET invite_count = ? WHERE user_id = ?', (invite_count, user_id))     
        else:
            cursor.execute('INSERT INTO invites (user_id, invite_count) VALUES (?, ?)', (user_id, 1))
        conn.commit()

# Comando 'cont' para mostrar a contagem de convites enviados por um usuário
@bot.command()
async def cont(ctx, member: discord.Member = None):
    # Se o usuário não mencionar ninguém, será usado o autor da mensagem
    member = member or ctx.author
    
    # Executa a consulta SQL para buscar a contagem de convites
    with sqlite3.connect('invites.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_count FROM invites WHERE user_id = ?', (member.id,))
        result = cursor.fetchone()

    # Verifica se encontrou um resultado e envia a mensagem correspondente
    if result:
        await ctx.send(f'{member.mention} **fez {result[0]} parceria(s).**')
    else:
        await ctx.send(f'{member.mention} **ainda não fez nenhuma parceria.**')



@bot.event
async def on_message(message):
    global ignore_trovao

    if message.author == bot.user:
        return

    # Verifica se a mensagem foi enviada no canal específico e contém um convite
    if message.channel.id == target_channel_id:
        # Verifica se há um link de convite no conteúdo
        if invite_regex.search(message.content):
            # Marca o cargo específico
            role = discord.utils.get(message.guild.roles, id=ping_role_id)
            await message.channel.send(f'{role.mention}, {message.author.mention} **New Parceria**!')

            # Salva o convite no banco de dados
            save_invite(message.author.id)
            await message.channel.send(f'{message.author.mention} **fez mais uma parceria.**')

    else:
        # Verifica se a mensagem contém um link de convite do Discord fora do canal permitido
        if invite_regex.search(message.content):
            # Apenas administradores podem enviar links de convite fora do canal específico
            if not message.author.guild_permissions.administrator:
                try:
                    await message.delete()
                    await message.channel.send(f'{message.author.mention}**, links de convite do Discord não são permitidos.**')
                except discord.errors.Forbidden:
                    await message.channel.send('Não tenho permissão para apagar mensagens.')
                  
    # Adiciona XP por mensagem
    add_xp(message.author.id, 2)

    # Função de ignorar e voltar a responder o "Senhor Trovão"
    if message.mentions and message.author.id == target_user_id:
        if "ignorar" in message.content.lower() and bot.user in message.mentions:
            ignore_trovao = True
            await message.channel.send("Estou ignorando suas mensagens, senhor trovão.")
            return
        elif "falar" in message.content.lower() and bot.user in message.mentions:
            ignore_trovao = False
            await message.channel.send("Voltei a te escutar, senhor trovão!")
            return

    # Ignora o "Senhor Trovão" se ele estiver sob a condição de ignorar
    if ignore_trovao and message.author.id == target_user_id:
        return

    # Checa se o autor da mensagem é o 'senhor trovão' e o bot foi mencionado
    if message.mentions and message.author.id == target_user_id:
        if bot.user in message.mentions:
            await message.channel.send("Quem você deseja banir hoje senhor trovão?")

            def check(m):
                return m.author.id == target_user_id and m.channel == message.channel

            try:
                response = await bot.wait_for('message', check=check, timeout=60.0)

                if response.content.lower() == "cancelar":
                    await message.channel.send('O processo foi cancelado.')
                    return
                elif response.content.lower().startswith("ordem:"):
                    await message.channel.send('Ok Senhor trovão, às suas ordens.')
                    return
                elif response.content.lower().startswith("permissão de banir"):
                    mentioned_users = response.mentions
                    if mentioned_users:
                        user_to_ban = mentioned_users[0]
                        await message.channel.send(f'Ok, quando você falar "Sinal Verde" irei banir {user_to_ban.mention}. Diga "Cancelar" para não banir ele.')

                        try:
                            confirmation = await bot.wait_for('message', check=check, timeout=60.0)

                            if confirmation.content.lower() == "sinal verde":
                                await user_to_ban.ban(reason="Banned by senhor trovão")
                                await message.channel.send(f'Usuário {user_to_ban.name} ({user_to_ban.id}) foi banido.')
                            elif confirmation.content.lower() == "cancelar":
                                await message.channel.send('O processo foi cancelado.')
                            else:
                                await message.channel.send('Comando não reconhecido. O processo foi cancelado.')

                        except asyncio.TimeoutError:
                            await message.channel.send('Tempo esgotado para resposta. O processo foi cancelado.')

                    else:
                        await message.channel.send('Nenhum usuário mencionado. O processo foi cancelado.')
                    return

                words = response.content.split()
                for word in words:
                    if word.isdigit():
                        user_id = int(word)
                        user = message.guild.get_member(user_id)
                        if user:
                            await user.ban(reason="Banned by senhor trovão")
                            await message.channel.send(f'Usuário {user.name} ({user_id}) foi banido.')
                        else:
                            await message.channel.send(f'Não consegui encontrar o usuário com ID {user_id}.')
                        break
                else:
                    await message.channel.send('Nenhum ID válido encontrado na mensagem.')

            except discord.errors.Forbidden:
                await message.channel.send('Eu não tenho permissão para banir este usuário.')
            except discord.ext.commands.errors.CommandInvokeError as e:
                await message.channel.send(f'Ocorreu um erro: {e}')
            except asyncio.TimeoutError:
                await message.channel.send('Tempo esgotado para resposta.')

    # Novas funcionalidades: detecção de palavras-chave como "criar", "editar" e "reset"
    if bot.user.mentioned_in(message):
        content = message.content.lower()  # Converte a mensagem para minúsculas

        # Verifica se a palavra "criar" está na mensagem
        if "criar" in content:
            if "arquivo" in content:
                filename = content.split("arquivo")[-1].strip()  # Extrai o nome do arquivo
                if filename:
                    try:
                        with open(filename, 'w') as f:
                            f.write("# Arquivo criado pelo bot\n")
                        response = random.choice(responses_create)  # Escolhe uma resposta aleatória
                        await message.channel.send(response)
                    except Exception as e:
                        await message.channel.send(f'Erro ao criar arquivo: {e}')

        # Verifica se a palavra "editar" está na mensagem
        elif "editar" in content:
            if "arquivo" in content:
                filename = content.split("arquivo")[-1].strip()  # Extrai o nome do arquivo
                if filename:
                    try:
                        with open(filename, 'a') as f:
                            f.write("\n# Conteúdo adicionado pelo bot\n")
                        response = random.choice(responses_edit)  # Escolhe uma resposta aleatória
                        await message.channel.send(response)
                    except Exception as e:
                        await message.channel.send(f'Erro ao editar arquivo: {e}')

        # Verifica se a palavra "reset" está na mensagem
        elif "reset" in content:
            response = random.choice(responses_reset)  # Escolhe uma resposta aleatória
            await message.channel.send(response)

    # Verifica se a mensagem foi enviada no canal específico e menciona alguém
    if message.channel.id == target_channel_id:
        if message.mentions:
            for mentioned_user in message.mentions:
                embed = discord.Embed(
                    title="PARCERIA CONCLUÍDA! :hibiscus:\nNova parceria Realizada!",
                    description="> **Você poderá voltar sempre que quiser para fazer mais parcerias com nosso servidor!\n"
                                "> Caso tenha alguma dúvida, converse com a staff que te atendeu.\n"
                                "> -# Mensagem enviada pelo servidor:** [InfinityVoid](https://discord.gg/infinityvoid)",
                    color=discord.Color(0x973187)
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1232075807250321408/1283519030908555274/f6846c6a6d128ac0106eea3a85a0125a.gif?ex=66e6957f&is=66e543ff&hm=33bbfc3d9fae83bca3b129be32c61612ef9a4f95299f101024ddcd217b06b58c&")

                try:
                    await mentioned_user.send(embed=embed)
                except discord.Forbidden:
                    await message.channel.send(f'Não consegui enviar uma mensagem privada para {mentioned_user.mention}.')

    await bot.process_commands(message)


@bot.tree.command(name="pv", description="Enviar uma mensagem privada para um usuário.")
@app_commands.describe(
    usuario="O usuário que você deseja manda a mensagem",
    mensagem="A mensagem que você deseja enviar para o usuário."
)
async def privado(interaction: discord.Interaction, usuario: discord.User, mensagem: str):
    # Enviar mensagem privada
    try:
        await usuario.send(mensagem)
        await interaction.response.send_message("Mensagem enviada com sucesso.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Não foi possível enviar a mensagem. O usuário pode ter desativado as mensagens diretas.", ephemeral=True)


DATABASE_PATH = 'economy.db'

# Conectar ao banco de dados e criar a tabela se não existir
def initialize_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS economy (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            last_daily INTEGER DEFAULT 0
        )
        ''')
        conn.commit()

initialize_db()

# Função para obter o saldo de um usuário
def get_balance(user_id):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT balance FROM economy WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO economy (user_id, balance) VALUES (?, ?)', (user_id, 0))
            conn.commit()
            return 0
        return result[0]

# Função para atualizar o saldo de um usuário
def update_balance(user_id, amount):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('UPDATE economy SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

# Função para obter o último uso do comando daily
def get_last_daily(user_id):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT last_daily FROM economy WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO economy (user_id, last_daily) VALUES (?, ?)', (user_id, 0))
            conn.commit()
            return 0
        return result[0]

# Função para atualizar o último uso do comando daily
def update_last_daily(user_id, timestamp):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('UPDATE economy SET last_daily = ? WHERE user_id = ?', (timestamp, user_id))
        conn.commit()

# Função para converter valores abreviados
def parse_amount(amount_str):
    match = re.match(r"(\d+)([kKmM]?)", amount_str)
    if match:
        number = int(match.group(1))
        suffix = match.group(2).lower()
        if suffix == 'k':
            return number * 1000
        elif suffix == 'm':
            return number * 1000000
        else:
            return number
    else:
        raise ValueError("Invalid amount format")

@bot.command(name='bal')
async def bal(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = member.id
    balance = get_balance(user_id)
    
    if member == ctx.author:
        await ctx.send(f'{member.mention}, você tem **<:InfinityCoin:1258546072222040084>{balance} Infinity Coins.**')
    else:
        await ctx.send(f'{ctx.author.mention}, {member.mention} tem **<:InfinityCoin:1258546072222040084>{balance} Infinity Coins.**')

@bot.command(name='daily')
async def daily(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())
    last_daily = get_last_daily(user_id)
    
    if current_time - last_daily < 86400:  # 86400 segundos = 24 horas
        time_left = 86400 - (current_time - last_daily)
        next_claim_time = current_time + time_left
        await ctx.send(f'{ctx.author.mention},\n<a:CEU_money:1259663579511128115> **|** Você já recebeu sua Recompensa Diariamente!\n\n'
                       f'<a:inf_exc:1259608593947164773> **|** Atenção: Lembrando que você pode pegar a recompensa diária todos os dias e, você pode pegar novamente em <t:{next_claim_time}:t>!')
        return
    
    amount = random.randint(2000, 5000)
    update_balance(user_id, amount)
    update_last_daily(user_id, current_time)
    balance = get_balance(user_id)
    next_claim_time = current_time + 86400
    await ctx.send(f'{ctx.author.mention},\n<a:CEU_money:1259663579511128115> **|** Receba a sua Recompensa Diariamente!\n\n'
                   f'<a:presente:1257114822563336262> **|** Quantia: {amount} InfinityCoins\n\n'
                   f'<a:inf_exc:1259608593947164773> **|** Atenção: Lembrando que você pode pegar a recompensa diária todos os dias e, se você pegar agora, você poderá pegar a recompensa diária novamente em <t:{next_claim_time}:t>!')

@bot.command(name='pay')
async def pay(ctx, member: discord.Member, amount: str):
    sender_id = ctx.author.id
    receiver_id = member.id
    amount = parse_amount(amount)
    
    if amount <= 0:
        await ctx.send(f'{ctx.author.mention}, o valor deve ser positivo.')
        return
    
    sender_balance = get_balance(sender_id)
    if sender_balance < amount:
        await ctx.send(f'{ctx.author.mention}, você não tem Infinity Coins suficientes para transferir.')
        return
    
    update_balance(sender_id, str(-amount))
    update_balance(receiver_id, str(amount))
    await ctx.send(f'{ctx.author.mention} transferiu **<:InfinityCoin:1258546072222040084>{amount} Infinity Coins** para {member.mention}.')

products = [
    {"name": "VIP Dragon", "price": 20000, "description": "Acesso VIP Dragon", "role_id": 1258479012028747828},
    {"name": "VIP Eclipse", "price": 30000, "description": "Acesso VIP Eclipse", "role_id": 1258479013047963760},
    {"name": "VIP Soul", "price": 45000, "description": "Acesso VIP Soul", "role_id": 1258479013941215365},
    {"name": "VIP UwU", "price": 65000, "description": "Acesso VIP UwU", "role_id": 1258201893910351994},
    {"name": "VIP Phoenix", "price": 100000, "description": "Acesso VIP Phoenix", "role_id": 1258479027631423570},
    {"name": "VIP Essence", "price": 150000, "description": "Acesso VIP Essence", "role_id": 1258479028197789736},
    {"name": "VIP Void", "price": 235000, "description": "Acesso VIP Void", "role_id": 1258479046564778124},
    {"name": "VIP Killer", "price": 340000, "description": "Acesso VIP Killer", "role_id": 1258479047214895234},
    {"name": "VIP Gold", "price": 500000, "description": "Acesso VIP Gold", "role_id": 1258479047873269860},
    {"name": "VIP Thunder", "price": 700000, "description": "Acesso VIP Thunder", "role_id": 1258479061953417216},
    {"name": "VIP Infinity", "price": 1000000, "description": "Acesso VIP Infinity", "role_id": 1258479062142156901},
    {"name": "VIP Soul Reaper", "price": 1400000, "description": "Acesso VIP Soul Reaper", "role_id": 1258596475101773824},
    {"name": "VIP Nightmer", "price": 2000000, "description": "Acesso VIP Nightmer", "role_id": 1258596475286323295},
    {"name": "VIP Shenanigans", "price": 2750000, "description": "Acesso VIP Shenanigans", "role_id": 1258604775591907390},
    {"name": "VIP Cookie", "price": 3500000, "description": "Acesso VIP Cookie", "role_id": 1258596476762853418},
    {"name": "VIP Blizzard", "price": 5000000, "description": "Acesso VIP Blizzard", "role_id": 1258596477144535040},
    {"name": "VIP Blood", "price": 7000000, "description": "Acesso VIP Blood", "role_id": 1258604776539820075},
    {"name": "VIP Z҉̡̏͝a̶͢͡l̵҇͜g҉̢͗͠o̴̡͡", "price": 1000000, "description": "Acesso VIP Z҉̡̏͝a̶͢͡l̵҇͜g҉̢͗͠o̴̡͡", "role_id": 1258814259882885282},
    {"name": "VIP ¿Mystery?", "price": 15000000, "description": "Acesso VIP ¿Mystery?", "role_id": 1258615948173119548},
    {"name": "VIP Minøs Øne", "price": 20000000, "description": "Acesso VIP Minøs Øne", "role_id": 1258820781056593990},
]

# Verifica se o usuário possui o cargo para desconto
DISCOUNT_ROLE_ID = 1257071596313776198

class StoreView(View):
    def __init__(self, user_id, page=0):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.page = page
        self.max_page = (len(products) - 1) // 1  # Cada página mostra 1 produto

        # Botões de navegação
        self.previous_button = Button(label='Anterior', style=discord.ButtonStyle.secondary, custom_id=f'previous_{user_id}')
        self.previous_button.callback = self.previous_page
        self.add_item(self.previous_button)

        self.page_label = Button(label=f'Página {self.page + 1}/{self.max_page + 1}', style=discord.ButtonStyle.secondary, disabled=True)
        self.add_item(self.page_label)

        self.next_button = Button(label='Próximo', style=discord.ButtonStyle.secondary, custom_id=f'next_{user_id}')
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)

        # Botão de compra
        for product in products[self.page:self.page + 1]:
            buy_button = Button(label=f'Comprar {product["name"]} - {product["price"]} Infinity Coins', style=discord.ButtonStyle.primary, custom_id=f'buy_{product["name"]}_{user_id}')
            buy_button.callback = self.buy_product
            self.add_item(buy_button)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Você não pode interagir com esta loja.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    async def previous_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await self.update_store(interaction)
        else:
            await interaction.response.send_message("Você já está na primeira página.", ephemeral=True)

    async def next_page(self, interaction: discord.Interaction):
        if self.page < self.max_page:
            self.page += 1
            await self.update_store(interaction)
        else:
            await interaction.response.send_message("Você já está na última página.", ephemeral=True)

    async def buy_product(self, interaction: discord.Interaction):
        button = interaction.data['custom_id']
        product_name = button.split('_')[1]
        product = next(p for p in products if p["name"] == product_name)
        balance = get_balance(self.user_id)
        
        # Verifica se o usuário tem o cargo de desconto
        has_discount_role = interaction.user.get_role(DISCOUNT_ROLE_ID) is not None
        discount_price = product["price"] * 0.6 if has_discount_role else product["price"]

        if balance < discount_price:
            await interaction.response.send_message(f"Você não tem Infinity Coins suficientes para comprar {product_name}.", ephemeral=True)
        else:
            update_balance(self.user_id, f'-{discount_price}')
            role = interaction.guild.get_role(product["role_id"])
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Você comprou {product_name} por <:InfinityCoin:1258546072222040084>{discount_price} Infinity Coins e recebeu o cargo correspondente.")

    async def update_store(self, interaction: discord.Interaction):
        for item in self.children[:]:
            self.remove_item(item)
        
        # Botões de navegação
        self.add_item(self.previous_button)
        self.page_label.label = f'Página {self.page + 1}/{self.max_page + 1}'
        self.add_item(self.page_label)
        self.add_item(self.next_button)

        # Botão de compra
        for product in products[self.page:self.page + 1]:
            buy_button = Button(label=f'Comprar {product["name"]} - {product["price"]} Infinity Coins', style=discord.ButtonStyle.primary, custom_id=f'buy_{product["name"]}_{self.user_id}')
            buy_button.callback = self.buy_product
            self.add_item(buy_button)

        # Atualizar o embed
        product = products[self.page]
        embed = discord.Embed(
            title="__Loja VIP__",
            description=f"**{product['name']}\n\n{product['description']}\n\nPreço: {product['price']} moedas**",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        embed.set_thumbnail(url="https://www.tibiawiki.com.br/images/c/c3/Tibiapedia.gif")
        embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0446.gif")
        embed.set_author(name='Sr.Trovão', icon_url='https://www.tibiawiki.com.br/images/3/31/Scroll_of_the_Stolen_Moment.gif')

        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name='store')
async def store(interaction: discord.Interaction):
    embed = discord.Embed(
        title="__Loja VIP__",
        description=f"**{products[0]['name']}\n\n{products[0]['description']}\n\nPreço: {products[0]['price']} moedas**",
        color=discord.Color.from_rgb(0, 0, 0)
    )
    embed.set_thumbnail(url="https://www.tibiawiki.com.br/images/c/c3/Tibiapedia.gif")
    embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0446.gif")
    embed.set_author(name='Sr.Trovão', icon_url='https://www.tibiawiki.com.br/images/3/31/Scroll_of_the_Stolen_Moment.gif')

    view = StoreView(interaction.user.id)
    message = await interaction.response.send_message(embed=embed, view=view)
    view.message = message


# Comando para adicionar dinheiro a um usuário
@bot.tree.command(name='add_money', description="Adiciona dinheiro a um usuário. Apenas administradores podem usar este comando.")
@app_commands.describe(member="O membro para quem você quer adicionar dinheiro.", amount="A quantidade de dinheiro para adicionar.")
@app_commands.checks.has_permissions(administrator=True)
async def add_money(interaction: discord.Interaction, member: discord.Member, amount: str):
    try:
        parsed_amount = parse_amount(str(amount))
        if parsed_amount <= 0:
            await interaction.response.send_message("A quantidade deve ser maior que zero.", ephemeral=True)
            return

        update_balance(member.id, parsed_amount)
        await interaction.response.send_message(f"Adicionados {amount} moedas para {member.mention}.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Formato de quantidade inválido. Use números com k para mil ou m para milhão, por exemplo, 2k ou 1m.", ephemeral=True)




@bot.command()
async def anticonvite(ctx):
    await ctx.send("Deseja ativar o anti convite?", view=Sc())
    view = Sc()

class Sc(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.value = None
        self.timeout = 600

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="✖️")
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="# **<a:loanding:1236781815159849021>**", delete_after=1) # aqui ele deleta a mensagem

    @discord.ui.button(label="Sim!", style=discord.ButtonStyle.green, emoji="✅")
    async def f(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("AntiConvite ativado!, Meu chefinho WuW")

# ID do canal de logs
log_channel_id = 1240283767344599080



@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(log_channel_id)

    if before.channel is None and after.channel is not None:
        # Membro entrou na call
        voice_start_times[member.id] = datetime.datetime.utcnow()

        embed = discord.Embed(
            title="🔊 Membro Entrou no Canal de Voz",
            description=f'**{member}** entrou no canal de voz **{after.channel.name}**',
            color=discord.Color.green()
        )
        embed.set_footer(text=f'ID do usuário: {member.id}')
        embed.timestamp = discord.utils.utcnow()
        await log_channel.send(embed=embed)

    elif before.channel is not None and after.channel is None:
        # Membro saiu da call
        start_time = voice_start_times.pop(member.id, None)
        if start_time:
            duration = datetime.datetime.utcnow() - start_time
            seconds = duration.total_seconds()
            xp_earned = calculate_xp(seconds)
            
            # Atualizar o XP do membro aqui
            # update_member_xp(member.id, xp_earned)  # Função de atualização de XP

            embed = discord.Embed(
                title="🔊 Membro Saiu do Canal de Voz",
                description=f'**{member}** saiu do canal de voz **{before.channel.name}**\n'
                            f'Tempo na call: {duration}\n'
                            f'XP ganho: {xp_earned}',
                color=discord.Color.red()
            )
            embed.set_footer(text=f'ID do usuário: {member.id}')
            embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    
    log_channel = bot.get_channel(log_channel_id)

    embed = discord.Embed(title="📝 Mensagem Editada",
                          description=f'**{before.author}** editou uma mensagem no canal {before.channel.mention}',
                          color=discord.Color.yellow())
    embed.add_field(name="Antiga mensagem", value=before.content, inline=False)
    embed.add_field(name="Nova mensagem", value=after.content, inline=False)
    await log_channel.send(embed=embed)

deleted_messages_cache = {}

@tasks.loop(seconds=3)
async def check_deleted_messages():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=100):
                    if message.id not in deleted_messages_cache:
                        deleted_messages_cache[message.id] = message.content
            except Exception as e:
                print(f'Erro ao acessar o histórico do canal {channel.name}: {e}')
    
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                history_ids = [message.id for message in await channel.history(limit=100).flatten()]
                deleted_ids = [msg_id for msg_id in deleted_messages_cache if msg_id not in history_ids]
                
                for msg_id in deleted_ids:
                    message_content = deleted_messages_cache.pop(msg_id, None)
                    if message_content:
                        log_channel = bot.get_channel(log_channel_id)
                        embed = discord.Embed(
                            title="📝 Mensagens Deletadas",
                            description=f'**Mensagem:** {message_content}\n**Canal:** {channel.mention}',
                            color=discord.Color.red()
                        )
                        embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=embed)
            except Exception as e:
                print(f'Erro ao acessar o histórico do canal {channel.name}: {e}')

log_channel_id = 1240283767344599080

@bot.event
async def on_message_delete(message):
    log_channel = bot.get_channel(log_channel_id)
    embed = discord.Embed(
        title="📝 Mensagem Deletada",
        description=f'**Mensagem:** {message.content}\n**Canal:** {message.channel.mention}',
        color=discord.Color.red()
    )
    embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)
    embed.set_footer(text=f'ID do usuário: {message.author.id}')
    embed.timestamp = discord.utils.utcnow()
    await log_channel.send(embed=embed)

@bot.event
async def on_raw_message_delete(payload):
    log_channel = bot.get_channel(log_channel_id)
    channel = bot.get_channel(payload.channel_id)

    embed = discord.Embed(
        title="📝 Mensagem Deletada",
        description=f'**ID da Mensagem:** {payload.message_id}\n**Canal:** {channel.mention}',
        color=discord.Color.red()
    )
    embed.timestamp = discord.utils.utcnow()
    await log_channel.send(embed=embed)

@bot.event
async def on_raw_bulk_message_delete(payload):
    log_channel = bot.get_channel(log_channel_id)
    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)

    embed = discord.Embed(
        title="📝 Mensagens Deletadas em Massa",
        description=f'{len(payload.message_ids)} mensagens deletadas no canal {channel.mention}',
        color=discord.Color.red()
    )
    embed.timestamp = discord.utils.utcnow()
    await log_channel.send(embed=embed)

    # Iterar pelas mensagens deletadas
    for message_id in payload.message_ids:
        try:
            message = await channel.fetch_message(message_id)
            single_embed = discord.Embed(
                title="📝 Mensagem Deletada",
                description=f'**Mensagem:** {message.content}\n**Canal:** {channel.mention}',
                color=discord.Color.red()
            )
            single_embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)
            single_embed.set_footer(text=f'ID do usuário: {message.author.id}')
            single_embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=single_embed)
        except discord.NotFound:
            # A mensagem já não está mais acessível, mas ainda podemos registrar algo
            single_embed = discord.Embed(
                title="📝 Mensagem Deletada",
                description=f'**ID da Mensagem:** {message_id}\n**Canal:** {channel.mention}',
                color=discord.Color.red()
            )
            single_embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=single_embed)



# Função para configurar o banco de dados
def setup_database():
    conn = sqlite3.connect('xp_system.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS user_xp (
        user_id INTEGER PRIMARY KEY,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS voice_time (
        user_id INTEGER PRIMARY KEY,
        time_spent INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )''')

    conn.commit()
    conn.close()

setup_database()

# Função para buscar dados de acordo com o período
def fetch_data(period, page, is_voice=False):
    conn = sqlite3.connect('xp_system.db')
    c = conn.cursor()
    table = 'voice_time' if is_voice else 'user_xp'

    query = f'SELECT user_id, xp, level FROM {table} ORDER BY xp DESC LIMIT 10 OFFSET ?'
    c.execute(query, ((page - 1) * 10,))
    results = c.fetchall()
    conn.close()
    return results

# Classe para gerenciar a interface de paginação
class RankingView(View):
    def __init__(self, ctx, is_voice):
        super().__init__(timeout=60)  # Adiciona timeout para evitar que a view falhe após inatividade
        self.ctx = ctx
        self.page = 1
        self.is_voice = is_voice
        self.results_per_page = 10  # Número de resultados por página
        self.period = "atual"  # Valor padrão para o período
        self.total_pages = self.calculate_total_pages()  # Calcula o número total de páginas
        self.embed = discord.Embed(title="Top Usuários por XP", color=discord.Color.blue())
        self.update_buttons()

    def calculate_total_pages(self):
        conn = sqlite3.connect('xp_system.db')
        c = conn.cursor()
        table = 'voice_time' if self.is_voice else 'user_xp'
        c.execute(f'SELECT COUNT(*) FROM {table}')
        total_entries = c.fetchone()[0]
        conn.close()
        return max(1, (total_entries // self.results_per_page) + (1 if total_entries % self.results_per_page else 0))

    def update_buttons(self):
        # Atualiza os botões de navegação
        self.clear_items()
        self.prev_button = Button(label='Anterior', style=discord.ButtonStyle.secondary, disabled=(self.page == 1))
        self.next_button = Button(label='Próximo', style=discord.ButtonStyle.secondary, disabled=(self.page == self.total_pages))
        self.page_label = Button(label=f'Página {self.page}/{self.total_pages}', style=discord.ButtonStyle.secondary, disabled=True)
        self.period_select = PeriodSelectView(custom_id=f"period_select_{id(self)}")
        self.prev_button.callback = self.previous_page
        self.next_button.callback = self.next_page
        self.add_item(self.prev_button)
        self.add_item(self.page_label)
        self.add_item(self.next_button)
        self.add_item(self.period_select)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author

    async def update_page(self):
        # Atualiza o conteúdo do embed com base na página atual
        results = fetch_data(self.period, self.page, is_voice=self.is_voice)
        self.embed.clear_fields()

        for idx, row in enumerate(results):
            user_id, xp, level = row
            try:
                user = await self.ctx.bot.fetch_user(user_id)
                user_name = user.name
            except discord.errors.NotFound:
                user_name = "Usuário desconhecido"

            self.embed.add_field(name=f"{(self.page - 1) * 10 + idx + 1}. {user_name}", value=f"XP: {xp}, Nível: {level}", inline=False)

        self.update_buttons()

    # Função para avançar para a página anterior
    async def previous_page(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.update_page()
        await interaction.response.edit_message(embed=self.embed, view=self)  # Edita a mensagem e responde à interação

    # Função para avançar para a próxima página
    async def next_page(self, interaction: discord.Interaction):
        if self.page < self.total_pages:
            self.page += 1
            await self.update_page()
        await interaction.response.edit_message(embed=self.embed, view=self)  # Edita a mensagem e responde à interação

# Classe Select personalizada para selecionar o período
class PeriodSelectView(Select):
    def __init__(self, custom_id):
        options = [
            discord.SelectOption(label="Atual", value="atual"),
            discord.SelectOption(label="Semanal", value="semanal"),
            discord.SelectOption(label="Mensal", value="mensal"),
            discord.SelectOption(label="Anual", value="anual")
        ]
        super().__init__(placeholder="Selecione o período...", options=options, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        parent_view = self.view
        parent_view.period = self.values[0]  # Atualiza o período selecionado
        await parent_view.update_page()
        await interaction.response.edit_message(embed=parent_view.embed, view=parent_view)  # Responde editando a mensagem

# Comando para exibir o ranking de XP de mensagens
@bot.command()
async def top(ctx):
    view = RankingView(ctx, is_voice=False)
    await view.update_page()  # Atualiza a página inicial
    await ctx.send(embed=view.embed, view=view)  # Envia a mensagem com o embed e a view

# Sistema de tempo para voice calls
voice_start_times = {}

# Função para iniciar a contagem de tempo quando o usuário entra na call
def start_voice_session(user_id):
    voice_start_times[user_id] = time.time()

# Função para finalizar a contagem de tempo e calcular o XP
def end_voice_session(user_id):
    if user_id in voice_start_times:
        start_time = voice_start_times.pop(user_id)
        elapsed_time = time.time() - start_time  # Calcula o tempo decorrido em segundos
        xp_gained = calculate_xp(elapsed_time)
        add_xp(user_id, xp_gained, is_voice=True)

# Função para calcular XP baseado no tempo em segundos
def calculate_xp(seconds):
    return seconds // 60  # 1 XP por minuto

# Função para adicionar XP ao usuário
def add_xp(user_id, amount, is_voice=False):
    conn = sqlite3.connect('xp_system.db')
    c = conn.cursor()

    if is_voice:
        c.execute('SELECT xp, level FROM voice_time WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            xp, level = result
            new_xp = xp + amount
            new_level = calculate_level(new_xp)
            c.execute('UPDATE voice_time SET xp = ?, level = ? WHERE user_id = ?', (new_xp, new_level, user_id))
        else:
            c.execute('INSERT INTO voice_time (user_id, xp, level) VALUES (?, ?, ?)', (user_id, amount, calculate_level(amount)))
    else:
        c.execute('SELECT xp, level FROM user_xp WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            xp, level = result
            new_xp = xp + amount
            new_level = calculate_level(new_xp)
            c.execute('UPDATE user_xp SET xp = ?, level = ? WHERE user_id = ?', (new_xp, new_level, user_id))
        else:
            c.execute('INSERT INTO user_xp (user_id, xp, level) VALUES (?, ?, ?)', (user_id, amount, calculate_level(amount)))

    conn.commit()
    conn.close()

# Função para calcular o nível baseado no XP
def calculate_level(xp):
    level = 0
    total_xp_for_next_level = 0

    while xp >= total_xp_for_next_level:
        level += 1
        xp -= total_xp_for_next_level
        total_xp_for_next_level = level * 100  # Exemplo: cada nível requer 100 * nível de XP

    return level

# Comando para exibir o ranking de tempo de call
@bot.command()
async def voice(ctx):
    view = RankingView(ctx, is_voice=True)
    await view.update_page()
    await ctx.send(embed=view.embed, view=view)

reaction_roles = {}

@bot.tree.command(name="adicionar_reacao_cargo", description="Adiciona uma reação a uma mensagem e atribui um cargo quando alguém reage.")
@app_commands.describe(
    message_id="O ID da mensagem para adicionar a reação.",
    emoji="O emoji para usar na reação.",
    role_id="O ID do cargo para atribuir quando alguém reagir."
)
async def adicionar_reacao_cargo(interaction: discord.Interaction, message_id: str, emoji: str, role_id: str):
    channel = interaction.channel
    try:
        message = await channel.fetch_message(message_id)
        role = interaction.guild.get_role(int(role_id))
        
        if not role:
            await interaction.response.send_message("ID do cargo fornecido é inválido.", ephemeral=True)
            return

        # Obter o emoji
        custom_emoji = None
        if emoji.startswith('<') and emoji.endswith('>'):
            custom_emoji = discord.PartialEmoji.from_str(emoji)

        if custom_emoji:
            await message.add_reaction(custom_emoji)
        else:
            await message.add_reaction(emoji)
        
        if message_id not in reaction_roles:
            reaction_roles[message_id] = {}
        reaction_roles[message_id][emoji] = role_id
        
        await interaction.response.send_message(f"Reação {emoji} adicionada à mensagem e o cargo {role.name} será atribuído.", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message("Mensagem não encontrada.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Falha ao adicionar a reação.", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) in reaction_roles:
        if str(payload.emoji) in reaction_roles[str(payload.message_id)]:
            guild = bot.get_guild(payload.guild_id)
            role_id = reaction_roles[str(payload.message_id)][str(payload.emoji)]
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.message_id) in reaction_roles:
        if str(payload.emoji) in reaction_roles[str(payload.message_id)]:
            guild = bot.get_guild(payload.guild_id)
            role_id = reaction_roles[str(payload.message_id)][str(payload.emoji)]
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.remove_roles(role)



@bot.command()
@commands.has_permissions(administrator=True)
async def remove_roles(ctx, member: discord.Member):
    try:
        await ctx.send(f"Removendo todos os cargos de {member.mention}...")
        for role in member.roles[1:]:  # Ignora o cargo @everyone
            try:
                await member.remove_roles(role)
                await asyncio.sleep(1)  # Adiciona um atraso de 1 segundo entre cada remoção de cargo
            except discord.HTTPException as e:
                await ctx.send(f"Falha ao remover o cargo {role.name}: {e}")
        await ctx.send(f"Todos os cargos foram removidos de {member.mention}.")
    except Exception as e:
        await ctx.send(f"Ocorreu um erro: {e}")



# Dicionário para armazenar as expansões, seus níveis e bônus
expansions = {
    "Sukuna": {"level": 3, "bonus": 1000, "description": "Cortes precisos com bônus garantido.", "barrier": False},
    "Campo de caça, Infinito.": {"level": 9, "bonus": 9000, "description": "A pessoa pode fazer o que ela quiser na expansão.", "barrier": True},
    # Adicione mais expansões conforme necessário
}

# ID do usuário que pode usar "Campo de caça, Infinito." e suas permissões especiais
special_user_id = 1199338020088840272

# URL da imagem para enviar como anexo
image_url = "https://cdn.discordapp.com/attachments/1257828848251441276/1266448695918858361/Artificial_Intelligence.gif?ex=66f98fc2&is=66f83e42&hm=b6a2b6ec14d5e51a06eec68da75ffec0b2f78e2dbc3f7e46de7877e85c80315f&"

# Dicionário para gerenciar as expansões ativas
active_expansions = {}

# Dicionário para gerenciar os cooldowns dos usuários
cooldowns = {}

# Função para criar um canal privado entre o atacante e o alvo
async def create_private_channel(ctx, attacker, target):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        attacker: discord.PermissionOverwrite(read_messages=True),
        target: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await guild.create_text_channel(f"dominio-{attacker.name}-vs-{target.name}", overwrites=overwrites)
    return channel

# Função para lidar com a disputa de domínios
async def domain_dispute(channel, attacker, target, attacker_expansion, target_expansion=None):
    await channel.send(f"{attacker.mention} lançou a expansão de domínio {attacker_expansion}!")

    if target_expansion:
        await channel.send(f"{target.mention} lançou a expansão {target_expansion}!")

        # Comparar os níveis das expansões
        attacker_level = expansions[attacker_expansion]["level"]
        target_level = expansions[target_expansion]["level"]

        if attacker_level > target_level:
            await channel.send(f"{attacker.mention} prevaleceu com a expansão de nível {attacker_level} contra {target_level}!")
            await apply_bonus(channel, attacker, attacker_expansion)
        elif target_level > attacker_level:
            await channel.send(f"{target.mention} prevaleceu com a expansão de nível {target_level} contra {attacker_level}!")
            await apply_bonus(channel, target, target_expansion)
        else:
            # Se os níveis são iguais, determinar o vencedor aleatoriamente
            if random.random() < 0.5:
                await channel.send(f"{attacker.mention} prevaleceu na disputa!")
                await apply_bonus(channel, attacker, attacker_expansion)
            else:
                await channel.send(f"{target.mention} prevaleceu na disputa!")
                await apply_bonus(channel, target, target_expansion)
    else:
        # Se não houve contra-ataque
        await channel.send(f"{target.mention} não conseguiu contra-atacar a tempo.")
        await apply_bonus(channel, attacker, attacker_expansion)

    # Esperar 30 segundos antes de deletar o canal
    await asyncio.sleep(30)
    await channel.send("A expansão de domínio terminou.")
    await channel.delete()

    return True

# Função para aplicar bônus ao vencedor
async def apply_bonus(channel, winner, expansion):
    bonus = expansions[expansion]["bonus"]
    await channel.send(f"{winner.mention} ganhou um bônus de {bonus} InfinityCoins por vencer com a expansão {expansion}!")
    # Adicione lógica para adicionar moedas aqui

# Função para baixar e enviar a imagem
async def send_image_as_attachment(channel):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open('temp_image.gif', 'wb') as f:
                    f.write(await response.read())
                await channel.send(
                    content="Você está na expansão 'Campo de caça, Infinito.', e <@1199338020088840272> pode fazer o que quiser com você, inclusive banir e mutar.",
                    files=[discord.File('temp_image.gif')]
                )
                os.remove('temp_image.gif')  # Limpar o arquivo temporário após o envio
            else:
                await channel.send("Não foi possível baixar a imagem.")

# Função para lidar com ações especiais do usuário com ID especial
async def handle_special_user_actions(channel, target):
    # Enviar a imagem como anexo
    await send_image_as_attachment(channel)

    active_expansions[channel.id] = {"target": target, "end_time": None}

    def check(m):
        return m.author.id == special_user_id and m.channel == channel and m.content.startswith("!action ")

    while channel.id in active_expansions:
        try:
            action_message = await bot.wait_for('message', check=check, timeout=999999999.0)
            action_content = action_message.content.split(" ", 1)[1].strip()

            if action_content.startswith("mute "):
                timelimit = action_content.split(" ", 1)[1]
                time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

                # Verificando se a unidade de tempo fornecida é válida
                unit = timelimit[-1].lower()
                if unit not in time_units:
                    await channel.send(f"Unidade de tempo {unit} não reconhecida.")
                    continue

                try:
                    # Convertendo o tempo para segundos
                    gettime = int(timelimit[:-1]) * time_units[unit]
                except ValueError:
                    await channel.send(f"Formato de tempo inválido.")
                    continue

                newtime = datetime.timedelta(seconds=gettime)

                # Usando a nova função de mute
                await target.edit(timed_out_until=discord.utils.utcnow() + newtime)
                await channel.send(f"{target.mention} foi mutado por {newtime}.")

            elif action_content == "unmute":
                await target.edit(timed_out_until=None)
                await channel.send(f"{target.mention} foi desmutado.")
            elif action_content == "ban":
                await target.ban(reason="Banido por estar na expansão 'Campo de caça, Infinito.'")
                await channel.send(f"{target.mention} foi banido.")
            elif action_content == "end":
                await channel.send(f"A expansão 'Campo de caça, Infinito.' foi encerrada por {special_user_id}.")
                await channel.delete()
                break
            else:
                await channel.send(f"Ação {action_content} não reconhecida.")
        except asyncio.TimeoutError:
            await channel.send(f"O poder de <@1199338020088840272> acabou. A expansão 'Campo de caça, Infinito.' foi encerrada.")
            await channel.delete()
            break

# Função para verificar e atualizar o cooldown de um usuário
def check_cooldown(user_id, cooldown_period):
    if user_id in cooldowns:
        last_used, cooldown_time = cooldowns[user_id]
        time_diff = datetime.datetime.now() - last_used
        if time_diff < cooldown_period:
            return False, cooldown_period - time_diff
    return True, None

# Função para definir o cooldown de um usuário
def set_cooldown(user_id, cooldown_time):
    cooldowns[user_id] = (datetime.datetime.now(), cooldown_time)

# Comando para iniciar a expansão de domínio
@bot.command()
async def expand(ctx, target: discord.Member, *, expansion: str):
    attacker = ctx.author
    expansion = expansion.strip('"')

    cooldown_period = datetime.timedelta(hours=1)
    can_use, remaining_cooldown = check_cooldown(attacker.id, cooldown_period)
    if not can_use:
        await ctx.send(f"{attacker.mention}, você precisa esperar {remaining_cooldown} antes de usar outra expansão.")
        return

    if expansion == "Campo de caça, Infinito." and attacker.id == special_user_id:
        channel = await create_private_channel(ctx, attacker, target)
        await ctx.send(f"{attacker.mention} iniciou a expansão de domínio 'Campo de caça, Infinito.' contra {target.mention}!")
        await handle_special_user_actions(channel, target)
        set_cooldown(attacker.id, cooldown_period)  # Definindo cooldown de 1 hora
    elif expansion in expansions:
        channel = await create_private_channel(ctx, attacker, target)
        await ctx.send(f"{attacker.mention} iniciou a expansão de domínio {expansion} contra {target.mention}!")

        active_expansions[channel.id] = {"attacker": attacker, "target": target, "expansion": expansion, "end_time": datetime.datetime.now() + datetime.timedelta(seconds=10)}
        
        try:
            await channel.send(f"{target.mention}, você tem 5 segundos para contra-atacar usando sua própria expansão de domínio. Use o comando `!counter <nome_da_expansão>`!")
            await asyncio.sleep(5)  # Tempo para contra-atacar

            # Verificar se o alvo lançou uma expansão de contra-ataque
            if "counter_expansion" in active_expansions[channel.id]:
                target_expansion = active_expansions[channel.id]["counter_expansion"]
                await domain_dispute(channel, attacker, target, expansion, target_expansion)
            else:
                await domain_dispute(channel, attacker, target, expansion)

        except asyncio.TimeoutError:
            await ctx.send(f"O tempo da expansão de domínio {expansion} acabou.")
            del active_expansions[channel.id]
        set_cooldown(attacker.id, cooldown_period)  # Definindo cooldown de 1 hora
    else:
        await ctx.send(f"Expansão {expansion} não reconhecida.")

# Comando para contra-atacar a expansão de domínio
@bot.command()
async def counter(ctx, *, expansion: str):
    expansion = expansion.strip('"')
    if ctx.channel.id in active_expansions:
        active_expansions[ctx.channel.id]["counter_expansion"] = expansion
        await ctx.send(f"{ctx.author.mention} contra-atacou com a expansão {expansion}!")
    else:
        await ctx.send(f"Não há nenhuma expansão ativa neste canal para contra-atacar.")

# Comando para se defender com Domínio Simples
@bot.command()
async def defend(ctx):
    defender = ctx.author
    cooldown_period = datetime.timedelta(hours=5)
    can_use, remaining_cooldown = check_cooldown(defender.id, cooldown_period)
    if not can_use:
        await ctx.send(f"{defender.mention}, você precisa esperar {remaining_cooldown} antes de usar o Domínio Simples novamente.")
        return

    if ctx.channel.id in active_expansions:
        expansion_details = active_expansions[ctx.channel.id]
        target = expansion_details["target"]
        if defender == target:
            success = random.random() < 0.5  # 50% de chance de sucesso
            if success:
                await ctx.send(f"{defender.mention} usou Domínio Simples e se defendeu com sucesso!")
                await asyncio.sleep(30)
                await ctx.channel.delete()
            else:
                await ctx.send(f"{defender.mention} usou Domínio Simples, mas falhou na defesa.")
            set_cooldown(defender.id, cooldown_period)  # Definindo cooldown de 5 horas
        else:
            await ctx.send(f"{defender.mention}, você não está sendo atacado no momento.")
    else:
        await ctx.send(f"Não há nenhuma expansão ativa neste canal para se defender.")


@bot.command()
async def jumpscare(ctx):
    image_url = "https://cdn.discordapp.com/attachments/1241088737782272092/1268353690771787858/Screenshot_20240726-122357_Discord.jpg?ex=66ac1dec&is=66aacc6c&hm=86dc360fda90d5077ecbac27198824959dd7a85dc0244e39e925cbb2f01b5fae&"
    embed = discord.Embed(color=discord.Color.red())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


# Configuração do banco de dados SQLite
conn = sqlite3.connect('batalha_turnos.db')
c = conn.cursor()

# Criação das tabelas no banco de dados
c.execute('''CREATE TABLE IF NOT EXISTS personagens (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER UNIQUE,
                 hp INTEGER,
                 max_hp INTEGER,
                 level INTEGER
             )''')
c.execute('''CREATE TABLE IF NOT EXISTS habilidades (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 skill_name TEXT,
                 damage INTEGER,
                 FOREIGN KEY(user_id) REFERENCES personagens(user_id)
             )''')
conn.commit()

# Lista de mensagens de ataque aleatórias
attack_messages = [
    "{attacker} chutou a cabeça de {target} e ela bateu com tudo no chão!",
    "{attacker} desferiu um soco poderoso em {target}, fazendo-o cambalear!",
    "{attacker} aplicou uma rasteira em {target}, derrubando-o!",
    "{attacker} lançou uma pedra que atingiu {target} no ombro!",
    "{attacker} deu um empurrão forte em {target}, que quase caiu!",
    "{attacker} pulou e acertou uma voadora em {target}!",
    "{attacker} deu uma cabeçada em {target}, atordoando-o!",
    "{attacker} socou o estômago de {target}, tirando seu ar!",
    "{attacker} deu um chute giratório em {target}!",
    "{attacker} mordeu o braço de {target}, causando dor!",
    "{attacker} puxou o cabelo de {target} e o jogou no chão!",
    "{attacker} arremessou {target} contra uma parede!",
    "{attacker} acertou uma cotovelada no rosto de {target}!",
    "{attacker} usou uma tática suja e deu um tapa em {target}!",
    "{attacker} lançou uma série de socos em {target}, sem dar chance de defesa!",
]


class Character:
    def __init__(self, user_id, hp, level, max_hp=None):
        self.user_id = user_id
        self.hp = hp
        self.max_hp = max_hp or hp
        self.level = level
        self.attacks_given = 0
        self.attacks_received = 0
        self.black_flash_active = False
        self.skills = self.load_skills()  # Carrega habilidades do banco de dados

    def take_damage(self, damage):
        self.hp -= damage
        self.attacks_received += 1
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def load_skills(self):
        c.execute('SELECT skill_name, damage FROM habilidades WHERE user_id = ?', (self.user_id,))
        return dict(c.fetchall())

def get_or_create_character(user_id):
    c.execute('SELECT * FROM personagens WHERE user_id = ?', (user_id,))
    row = c.fetchone()

    if row:
        return Character(row[1], row[2], row[4], row[3])
    else:
        character = Character(user_id, hp=100, level=1)
        c.execute('INSERT INTO personagens (user_id, hp, max_hp, level) VALUES (?, ?, ?, ?)',
                  (user_id, character.hp, character.max_hp, character.level))
        conn.commit()
        return character

def update_character(character):
    c.execute('UPDATE personagens SET hp = ?, max_hp = ?, level = ? WHERE user_id = ?',
              (character.hp, character.max_hp, character.level, character.user_id))
    conn.commit()

def add_skill(user_id, skill_name, damage):
    c.execute('INSERT INTO habilidades (user_id, skill_name, damage) VALUES (?, ?, ?)',
              (user_id, skill_name, damage))
    conn.commit()

# Função para atualizar o saldo ao final da batalha
def update_balance_on_battle_end(winner_id, loser_id):
    # O vencedor ganha 2000 infinity coins
    update_balance(winner_id, 2000)
    
    # O perdedor perde 5000 infinity coins, mas o saldo nunca pode ser negativo
    current_balance = get_balance(loser_id)
    amount_to_deduct = min(5000, current_balance)  # Garante que o saldo não ficará negativo
    update_balance(loser_id, -amount_to_deduct)
  

@bot.command(name="addskill")
@commands.has_permissions(administrator=True)
async def add_skill_command(ctx, member: discord.Member, skill_name: str, damage: int):
    add_skill(member.id, skill_name, damage)
    await ctx.send(f"Habilidade **{skill_name}** com dano **{damage}** adicionada a {member.mention}!")

class BattleView(View):
    def __init__(self, player: Character, opponent: Character, message, player_name, opponent_name):
        super().__init__(timeout=None)
        self.player = player
        self.opponent = opponent
        self.turn = 0
        self.message = message
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.current_turn = player if random.choice([True, False]) else opponent
        self.current_turn_name = player_name if self.current_turn == player else opponent_name

        self.update_buttons()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.current_turn.user_id

    async def update_status(self):
        self.update_buttons()

        embed = Embed(
            title="⚔️ Batalha Iniciada!",
            color=0x5A0004
        )
        embed.add_field(name=f"{self.player_name}", value=f"**HP**: {self.player.hp}/{self.player.max_hp}", inline=True)
        embed.add_field(name=f"{self.opponent_name}", value=f"**HP**: {self.opponent.hp}/{self.opponent.max_hp}", inline=True)
        embed.set_footer(text=f"Turno de {self.current_turn_name}")
        embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0172.gif")      
        await self.message.edit(embed=embed, view=self)

    def switch_turn(self):
        self.current_turn = self.opponent if self.current_turn == self.player else self.player
        self.current_turn_name = self.opponent_name if self.current_turn == self.opponent else self.player_name
        self.turn += 1
        self.update_buttons()

    async def end_battle(self, interaction):
        winner = self.player if self.player.is_alive() else self.opponent
        loser = self.opponent if winner == self.player else self.player
        winner_name = self.player_name if winner == self.player else self.opponent_name
        loser_name = self.opponent_name if loser == self.opponent else self.player_name

        # Atualizar saldo dos jogadores
        reward_winner = 2000  # 2k para o vencedor
        penalty_loser = 5000  # 5k para o perdedor

        # Funções fictícias para atualizar o saldo - substitua pelas reais se houver
        update_balance(winner.user_id, reward_winner)
        update_balance(loser.user_id, -penalty_loser)

        # Enviar mensagem explicando as mudanças de saldo
        embed = discord.Embed(
            title="🏆 Batalha Concluída!",
            description=f"{winner_name} é o vencedor!\n\n"
                        f"💰 **{winner_name}** ganhou 2000 infinity coins!\n"
                        f"💸 **{loser_name}** perdeu 5000 infinity coins!",
            color=0xFFD700
        )
        embed.add_field(name=f"{self.player_name}", value=f"**HP**: {self.player.hp}/{self.player.max_hp}", inline=True)
        embed.add_field(name=f"{self.opponent_name}", value=f"**HP**: {self.opponent.hp}/{self.opponent.max_hp}", inline=True)

        await self.message.edit(embed=embed)
        self.stop()

    @discord.ui.button(label="Atacar", style=ButtonStyle.primary)
    async def attack(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.current_turn.user_id:
            await interaction.response.send_message("⛔ Não é o seu turno!", ephemeral=True)
            return

        damage = random.randint(15, 25)
        
        if self.current_turn.black_flash_active and random.randint(1, 100) <= 30:
            damage = random.randint(50, 75)
            black_flash_message = f"🔥 **BLACK FLASH!** {self.current_turn_name} acertou um ataque devastador!"

        target = self.opponent if self.current_turn == self.player else self.player
        target_name = self.opponent_name if target == self.opponent else self.player_name
        target.take_damage(damage)
        self.current_turn.attacks_given += 1

        attack_message = random.choice(attack_messages).format(attacker=self.current_turn_name, target=target_name)
        if self.current_turn.black_flash_active and damage > 25:
            attack_message += f"\n\n{black_flash_message}"

        attack_embed = Embed(title="💥 Ataque Realizado!", description=attack_message, color=0x8B0000)
        attack_embed.add_field(name=f"{target_name}", value=f"**HP Restante**: {target.hp}/{target.max_hp}", inline=False)

        if not target.is_alive():
            await self.end_battle(interaction)
        else:
            await interaction.response.send_message(embed=attack_embed)
            self.switch_turn()
            await self.update_status()

    @discord.ui.button(label="Curar", style=ButtonStyle.grey, emoji="<a:red_brilho:806565883346550905>")
    async def heal(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.current_turn.user_id:
            await interaction.response.send_message("⛔ Não é o seu turno!", ephemeral=True)
            return

        heal_amount = random.randint(10, 20)
        self.current_turn.heal(heal_amount)

        heal_embed = Embed(title="<a:R_HeartRed:1277261128690438248> Cura Realizada!", color=0x3A0002)
        heal_embed.add_field(name=f"{self.current_turn_name} se curou!", value=f"Recuperou **{heal_amount}** HP!", inline=False)
        heal_embed.add_field(name=f"{self.current_turn_name}", value=f"**HP Atual**: {self.current_turn.hp}/{self.current_turn.max_hp}", inline=False)
        heal_embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0172.gif") 

        await interaction.response.send_message(embed=heal_embed)
        self.switch_turn()
        await self.update_status()

    @discord.ui.button(label="Fugir", style=ButtonStyle.danger)
    async def run(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.current_turn.user_id:
            await interaction.response.send_message("⛔ Não é o seu turno!", ephemeral=True)
            return

        embed = Embed(title="🏃‍♂️ Fuga!", description=f"{self.current_turn_name} fugiu da batalha!", color=0xFF0000)
        await self.message.edit(embed=embed)
        self.stop()

    @discord.ui.button(label="Black Flash", style=ButtonStyle.grey, disabled=True)
    async def black_flash(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.current_turn.user_id:
            await interaction.response.send_message("⛔ Não é o seu turno!", ephemeral=True)
            return

        if not self.special_ready(self.current_turn):
            await interaction.response.send_message("⛔ Você ainda não pode usar esta habilidade!", ephemeral=True)
            return

        self.current_turn.black_flash_active = True

        black_flash_embed = Embed(
            title="⚡ Black Flash Ativado!",
            description=f"{self.current_turn_name} ativou o Black Flash! Seus ataques agora têm uma chance de causar dano completo!",
            color=0x790001
        )
        black_flash_embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0221.gif")    
        black_flash_embed.set_thumbnail(url="https://www.tibiawiki.com.br/images/8/80/Crunor%27s_Heart.gif")      

        await interaction.response.send_message(embed=black_flash_embed)
        self.switch_turn()
        await self.update_status()

    def special_ready(self, character):
        return character.attacks_given >= 3 and character.attacks_received >= 3

    def update_buttons(self):
        self.black_flash.disabled = not self.special_ready(self.current_turn)

    @discord.ui.button(label="Skills", style=ButtonStyle.secondary)
    async def show_skills(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.current_turn.user_id:
            await interaction.response.send_message("⛔ Não é o seu turno!", ephemeral=True)
            return

        options = [
            discord.SelectOption(label=skill, description=f"Causa {damage} de dano.")
            for skill, damage in self.current_turn.skills.items()
        ]

        if not options:
            await interaction.response.send_message("Você só pode usar ataques normais!", ephemeral=True)
            return

        select_menu = Select(placeholder="Escolha uma habilidade", options=options)

        async def select_callback(interaction: Interaction):
            skill_name = select_menu.values[0]
            damage = self.current_turn.skills[skill_name]
            target = self.opponent if self.current_turn == self.player else self.player
            target_name = self.opponent_name if target == self.opponent else self.player_name
            target.take_damage(damage)
            self.current_turn.attacks_given += 1

            skill_message = f"{self.current_turn_name} usou a habilidade **{skill_name}** causando **{damage}** de dano!"

            skill_embed = Embed(title="<:blue_b:1285649704692089064>Habilidade Usada!", description=skill_message, color=0x98E1FF)
            skill_embed.add_field(name=f"{target_name}", value=f"**HP Restante**: {target.hp}/{target.max_hp}", inline=False)

            if not target.is_alive():
                await self.end_battle(interaction)
            else:
                await interaction.response.send_message(embed=skill_embed)
                self.switch_turn()
                await self.update_status()

        select_menu.callback = select_callback
        view = View(timeout=60)
        view.add_item(select_menu)
        await interaction.response.send_message("Selecione sua habilidade:", view=view, ephemeral=True)

@bot.command(name="battle")
async def battle(ctx, opponent: discord.Member):
    player = get_or_create_character(ctx.author.id)
    opponent_char = get_or_create_character(opponent.id)

    view = BattleView(player, opponent_char, None, ctx.author.display_name, opponent.display_name)
    battle_message = await ctx.send("A batalha começou!", view=view)
    view.message = battle_message
    await view.update_status()
      
          


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1269943871346053172)
    if channel:
        # Mensagem de boas-vindas
        welcome_message = f"## {member.mention} __Seja bem-vindo(a)__"
        
        # Embed personalizado
        embed = discord.Embed(
            description="> **Esperamos que você goste da nossa comunidade e que se divirta bastante aqui dentro. "
                        "Leia as Regras em ⁠<#1240283767986323461>﻿ para que não acabe quebrando nenhuma regra ou leve uma punição inesperada.**\n"
                        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                        "* **Você poderá saber mais sobre os cargos de leveis em ⁠<#1265824094801105016>﻿ ou caso queira saber os Preços ou benefícios dos VIPs, "
                        "basta olhar em ⁠<#1258106299887910963>﻿**\n\n"
                        "* **Você poderá escolher uma cor para personalizar o seu nick em ⁠<#1257878327511748700>﻿﻿**\n\n"
                        "* **Caso você queira conhecer mais sobre o servidor, temos um canal explicando onde temos todos os chats, "
                        "basta dar uma olhadinha em <#1271567924506923040>﻿**",
            color=discord.Color.from_rgb(204, 102, 255)  # Cor roxa meio rosa
        )
        
        # Anexar a imagem ao embed
        embed.set_image(url="https://cdn.discordapp.com/attachments/1240283767017439335/1271566087997100117/6_Sem_Titulo_20240809164024.jpg?ex=66b7cdb3&is=66b67c33&hm=2f5a71679eb71d76e316acd1800ddfb82b3ac46024dac123f314ad2007688ef4&")
        
        await channel.send(welcome_message, embed=embed)




 # IDs dos cargos
ROLE_IDS = {
    "grand-canyon": 1285249486012284978,
    "campos-florestais": 1285249718561144903,
    "floresta-sombria": 1285249896257163448,
    "praias-grandes": 1285250824934654003
}

class RoleSelect(discord.ui.Select):
    def __init__(self, user):
        options = [
            discord.SelectOption(label="Grand Canyon", value="grand-canyon"),
            discord.SelectOption(label="Campos Florestais", value="campos-florestais"),
            discord.SelectOption(label="Floresta Sombria", value="floresta-sombria"),
            discord.SelectOption(label="Praias Grandes", value="praias-grandes")
        ]
        self.user = user
        super().__init__(placeholder="Escolha o local", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        # Verifique se o usuário que está interagindo é o mesmo que usou o comando
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode usar este menu!", ephemeral=True)
            return
        
        guild = interaction.guild
        member = interaction.user
        selected_role_name = self.values[0]
        selected_role_id = ROLE_IDS[selected_role_name]
        selected_role = guild.get_role(selected_role_id)

        # Remove cargos anteriores
        for role_id in ROLE_IDS.values():
            role = guild.get_role(role_id)
            if role in member.roles:
                await member.remove_roles(role)
        
        # Adiciona o novo cargo
        await member.add_roles(selected_role)
        await interaction.response.send_message(f"Você está viajando para: {selected_role.name}", ephemeral=True)

class RoleSelectView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(user))

@bot.tree.command(name="world", description="Viaje pelo mundo")
async def world(interaction: discord.Interaction):
    await interaction.response.send_message("Escolha o local jovem guerreiro:", view=RoleSelectView(interaction.user), ephemeral=True)



# View da loja com o botão de compra
class ShopView(View):
    def __init__(self, user_id, user_balance):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.user_balance = user_balance

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="??? 100k Infinity coins", style=ButtonStyle.gray)
    async def buy_six_eyes(self, interaction: Interaction, button: Button):
        if self.user_balance >= 100000:
            # Deduzir o valor e adicionar a habilidade
            update_balance(self.user_id, -100000)
            add_skill(self.user_id, "Seis Olhos", 50)

            embed = Embed(title="Compra Concluída!", description="Você adquiriu a habilidade **Seis Olhos**!", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Apagar a mensagem da loja no canal
            await interaction.message.delete()
        else:
            embed = Embed(title="Saldo Insuficiente", description="Você não tem 100 mil Infinity coins.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Comando Shops para enviar o menu da loja
@bot.tree.command(name="shops")
async def shops(interaction: discord.Interaction):
    # Criando o menu de seleção
    options = [
        discord.SelectOption(label="Seis Olhos", description="Loja para comprar a habilidade Seis Olhos")
    ]
    
    select = Select(placeholder="Selecione uma loja", options=options)

    async def select_callback(interaction: Interaction):
        if select.values[0] == "Seis Olhos":
            # Embed da loja clandestina
            embed = Embed(title="Loja Clandestina",
                          description="**Estou apenas passando por aqui... Deseja comprar a habilidade **???** por 100k Infinity coins?**",
                          color=0xBEA151)
            embed.set_author(
                name="Vendedor", 
                icon_url="https://pbs.twimg.com/profile_images/1059927973808295938/EMUSMMAu_400x400.jpg"
            ) 
            embed.set_thumbnail(url="https://www.tibiawiki.com.br/images/c/c3/Tibiapedia.gif")
            embed.set_image(url="https://www.imagensanimadas.com/data/media/562/linha-imagem-animada-0455.gif")          
            # Enviar embed na loja específica (campo florestal)
            shop_channel = interaction.guild.get_channel(1284502310474481796)
            if shop_channel:
                await shop_channel.send(embed=embed, view=ShopView(interaction.user.id, get_balance(interaction.user.id)))

            # Responder ao usuário com uma mensagem customizada
            response_embed = Embed(title="Bem-vindo, guerreiro!",
                                   description="Olá jovem guerreiro, deseja uma loja para comprar a habilidade **Seis Olhos**? Bem, tem uma loja clandestina lá em **Campos Florestais**!",
                                   color=0xC2A100)
            response_embed.set_thumbnail(url="https://www.tibiawiki.com.br/images/3/31/Scroll_of_the_Stolen_Moment.gif")
            response_embed.set_image(url="https://cdn.discordapp.com/attachments/1260414838853734497/1285676697579946056/Mapa.png?ex=66eb233b&is=66e9d1bb&hm=b73cdbc5aacb7a628021848c2ecdb5b31f7accc977a77f2279a66e6e686907a0&")
          
            response_embed.set_author(
                         name="Vendedor", 
                         icon_url="https://pbs.twimg.com/profile_images/1059927973808295938/EMUSMMAu_400x400.jpg"
            )   
            await interaction.response.send_message(embed=response_embed, ephemeral=True)

    select.callback = select_callback

    # View para o menu de seleção
    view = View(timeout=60)
    view.add_item(select)
    await interaction.response.send_message("Selecione uma loja:", view=view, ephemeral=True)


# IDs dos canais
CANAL_APROVACAO_ID = 1240283767017439337  # Canal onde as parcerias serão enviadas para aprovação
CANAL_PARCERIAS_ID = 1258081237902561401  # Canal onde as parcerias aprovadas serão postadas

class ParceriaModal(ui.Modal, title="Parceria"):
    convite = ui.TextInput(label="Convite do Servidor", placeholder="Insira o link de convite do servidor", required=True)
    requisitos = ui.TextInput(label="Requisitos da Parceria", style=discord.TextStyle.paragraph, placeholder="Escreva os requisitos da parceria", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        canal_aprovacao = bot.get_channel(CANAL_APROVACAO_ID)
        
        # Cria a mensagem de parceria para aprovação
        embed = discord.Embed(title="Nova Solicitação de Parceria", color=0x9BF5FF)
        embed.add_field(name="Convite", value=self.convite.value, inline=False)
        embed.add_field(name="Requisitos", value=self.requisitos.value, inline=False)
        embed.set_image(url="https://media.discordapp.net/attachments/1232075807250321408/1283519030908555274/f6846c6a6d128ac0106eea3a85a0125a.gif?ex=66fb04bf&is=66f9b33f&hm=701a8063bfdfaea046184c3caf5c20c60f76179f096ed21f1606eabb0fdb5e20")
        
        # Envia mensagem para o canal de aprovação com botão
        view = AprovarParceriaView(self.convite.value, self.requisitos.value, interaction.user)
        await canal_aprovacao.send(embed=embed, view=view)
        await interaction.response.send_message("Sua solicitação de parceria foi enviada para aprovação!", ephemeral=True)

class AprovarParceriaView(ui.View):
    def __init__(self, convite, requisitos, solicitante):
        super().__init__()
        self.convite = convite
        self.requisitos = requisitos
        self.solicitante = solicitante  # Quem solicitou a parceria

    @ui.button(label="Aprovar Parceria", style=ButtonStyle.grey)
    async def aprovar_callback(self, interaction: discord.Interaction, button: ui.Button):
        canal_parcerias = bot.get_channel(CANAL_PARCERIAS_ID)
        
        # Mensagem final da parceria aprovada no canal de parcerias
        embed = discord.Embed(title="✧ ･ ﾟ: * PARCERIA REALIZADA * : ･ ﾟ ✧", color=0xC6C6C6)
        embed.add_field(name="**⊱❥╺╸Convite:**", value=self.convite, inline=False)
        embed.set_image(url="https://media.discordapp.net/attachments/1232075807250321408/1283519030908555274/f6846c6a6d128ac0106eea3a85a0125a.gif?ex=66fb04bf&is=66f9b33f&hm=701a8063bfdfaea046184c3caf5c20c60f76179f096ed21f1606eabb0fdb5e20")      
        await canal_parcerias.send(embed=embed)
        
        # Envia mensagem privada para o solicitante
        embed_dm = discord.Embed(
            title="PARCERIA CONCLUÍDA! :hibiscus:\nNova parceria Realizada!",
            description=(
                "> **Você poderá voltar sempre que quiser para fazer mais parcerias com nosso servidor!\n"
                "> Caso tenha alguma dúvida, converse com a staff que te atendeu.\n"
                "> Mensagem enviada pelo servidor:** [InfinityVoid](https://discord.gg/infinityvoid)"
            ),
            color=discord.Color(0x973187)
        )
        embed_dm.set_image(url="https://media.discordapp.net/attachments/1232075807250321408/1283519030908555274/f6846c6a6d128ac0106eea3a85a0125a.gif?ex=66fb04bf&is=66f9b33f&hm=701a8063bfdfaea046184c3caf5c20c60f76179f096ed21f1606eabb0fdb5e20")

        try:
            # Envia a mensagem privada para quem fez a solicitação
            await self.solicitante.send(embed=embed_dm)
            await interaction.response.send_message("Parceria aprovada e enviada para o canal de parcerias e mensagem privada enviada ao solicitante!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Parceria aprovada, mas não consegui enviar a mensagem privada ao solicitante.", ephemeral=True)

        await interaction.message.delete()
      
        self.stop()

# View com botão que ativa o modal de parceria
class ParceriaView(ui.View):
    @ui.button(label="Enviar Solicitação", style=ButtonStyle.grey, emoji="<a:red_brilho:806565883346550905>")
    async def enviar_solicitacao(self, interaction: discord.Interaction, button: ui.Button):
        modal = ParceriaModal()
        await interaction.response.send_modal(modal)

# Comando Slash para Parceria que envia o Embed com o botão
@bot.tree.command(name="parceria", description="Solicitar uma nova parceria.")
async def slash_parceria(interaction: discord.Interaction):
    # Verifica se o usuário tem permissão de administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="✧ ･ ﾟ: * PARCERIA AUTOMÁTICA * : ･ ﾟ ✧",
        description="**⊱❥╺╸Envie uma solicitação e nossos staffs irão avaliar!**\n**__Atenção__!:** Esse sistema apenas enviara um embed com link de convite no canal de parcerias, sem nenhum outro tipo de mensagem, os staffs ficaram encarregados de cumprir os requisitos.\nCaso queira mandar uma parceria que mandamos uma descrição do servidor ou algo mais vá no PV de um staff.",
        color=14582527
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1232075807250321408/1283519030908555274/f6846c6a6d128ac0106eea3a85a0125a.gif?ex=66fb04bf&is=66f9b33f&hm=701a8063bfdfaea046184c3caf5c20c60f76179f096ed21f1606eabb0fdb5e20")

    view = ParceriaView()  # Cria a view com o botão
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_member_update(before, after):
    # Verifica se o usuário começou a dar boost no servidor
    if before.premium_since is None and after.premium_since is not None:
        # Canal onde o embed será enviado
        channel = after.guild.get_channel(1258070114566410361)  # Substitua pelo ID do canal

        # Cria o embed com a mensagem personalizada
        embed = discord.Embed(
            title="## NOVO IMPULSO REALIZADO! <:inf_heartboost:1261026850717700288>",  # Título com emoji
            description=f"{after.mention} **REALIZOU NOVO BOOST!** <a:Evoluodenitro:1257096477319106662>\n\n"
                        f"<a:inf_seta:1259608572275195996> **Agradecemos ao seu impulso em nosso servidor, esperamos que aproveite os benefícios do seu novo cargo:** <@&1257071596313776198>\n\n"
                        f"<a:inf_seta:1259608572275195996> **O <@&1257071596313776198> tem vários benefícios, você poderá ver todos eles em** <#1258070030474543204>.\n"
                        f"**__Esperamos que aproveite__!**",
            color=0xFFC0CB  # Cor do embed
        )

        # Opcional: Adiciona uma imagem do avatar do usuário ao embed
        embed.set_thumbnail(url=after.avatar.url)

        # Envia o embed no canal
        await channel.send(embed=embed)



@bot.command(name="if")
@commands.has_permissions(administrator=True)
async def remove_coins(ctx, member: discord.Member, amount):
    user_id = member.id

    # Se o valor for 'all', remove tudo
    if amount.lower() == 'all':
        balance = get_balance(user_id)
        update_balance(user_id, -balance)
        await ctx.send(f"Todo o saldo de {member.mention} foi removido ({balance} Infinity Coins).")
    else:
        try:
            amount = int(amount)
            current_balance = get_balance(user_id)
            if amount > current_balance:
                await ctx.send(f"{member.mention} não tem saldo suficiente. Saldo atual: {current_balance} Infinity Coins.")
            else:
                update_balance(user_id, -amount)
                await ctx.send(f"{amount} Infinity Coins foram removidos de {member.mention}.")
        except ValueError:
            await ctx.send("Por favor, insira um valor numérico válido ou 'all'.")      



@bot.command()
async def card(ctx):
    # Abrir a imagem base (mesmo diretório do bot)
    base_image = Image.open("image.png")  # Nome da imagem fornecida
    
    # Baixar o avatar do usuário
    avatar_url = str(ctx.author.avatar.url)
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")

    # Redimensionar o avatar
    avatar = avatar.resize((315, 315))  # Ajuste para o tamanho desejado

    # Inserir o avatar na imagem base (posição baseada no layout da imagem)
    base_image.paste(avatar, (58, 150))  # Ajuste as coordenadas conforme necessário

    # Editar o nome na imagem
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.truetype(font_path, 48)
    draw.text((663, 161), ctx.author.display_name, font=font, fill="black")  # Nome do usuário

    # Salvar a imagem temporária
    base_image.save("output_card.png")

    # Enviar a imagem gerada no canal
    await ctx.send(file=discord.File("output_card.png"))

# Caminho relativo para a fonte
font_path = "Stalysta_personal use.ttf"

ROLE_ID_1 = 1288434543212232734
ROLE_ID_2 = 1288434546022285394


@bot.command()
@commands.has_permissions(administrator=True)  # Somente administradores podem usar este comando
async def xp_set_cargo(ctx):
    guild = ctx.guild
    role1 = guild.get_role(ROLE_ID_1)
    role2 = guild.get_role(ROLE_ID_2)

    if role1 and role2:
        for member in guild.members:
            if not member.bot:  # Não adicionar cargos em bots
                try:
                    await member.add_roles(role1, role2)
                    await ctx.send(f"Cargos adicionados ao {member.mention}.")
                    await asyncio.sleep(0.1)  # Delay de 0,3 segundos por membro
                except discord.DiscordException as e:
                    await ctx.send(f"Erro ao adicionar cargos para {member.mention}: {e}")
    else:
        await ctx.send("Um ou ambos os cargos não foram encontrados.")


bot.run('01001111 01110001 01110101 01100101 00100000 01110110 01101111 01100011 11101010 00100000 01100101 01110011 01110100 11100001 00100000 01100110 01100001 01111010 01100101 01101110 01100100 01101111 00111111 00100000 01010000 01110010 01101111 01100011 01110101 01110010 01100001 01101110 01100100 01101111 00100000 01110100 01101111 01101011 01100101 01101110 00100000 01100100 01101111 00100000 01101101 01100101 01110101 00100000 01100010 01101111 01110100 00111111 ')