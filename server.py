from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import threading
import time
import uuid
import asyncio
import random
import string
from urllib.parse import parse_qs
import cgi

os.chdir(os.path.dirname(os.path.abspath(__file__)))

UPLOADS_DIR = 'uploads'
APPROVED_DIR = 'approved'
DATA_FILE = 'clips_data.json'
USERS_FILE = 'users_data.json'
PENDING_QUEUE_FILE = 'pending_queue.json'
PRIORITY_SERVER_ID = 1448627910478004388
DNX_CORE_SERVER_ID = 1442471151703167008

for d in [UPLOADS_DIR, APPROVED_DIR]:
    os.makedirs(d, exist_ok=True)

discord_stats = {
    "online": 0,
    "members": 0,
    "last_update": 0,
    "invite_url": ""
}

pending_clips = {}
approved_clips = []
registered_users = {}
video_interactions = {}
page_views = 0
bot_is_online = False
pending_queue = {
    'clips': [],
    'likes': [],
    'dislikes': [],
    'favorites': [],
    'logins': []
}

def generate_password(length=8):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits)
    ]
    password += [random.choice(chars) for _ in range(length - 3)]
    random.shuffle(password)
    return ''.join(password)

def load_clips_data():
    global approved_clips, video_interactions
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                approved_clips = data.get('approved', [])
                video_interactions = data.get('interactions', {})
    except Exception as e:
        print(f"Error loading clips data: {e}")

def save_clips_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'approved': approved_clips,
                'interactions': video_interactions
            }, f)
    except Exception as e:
        print(f"Error saving clips data: {e}")

def load_users_data():
    global registered_users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                registered_users = json.load(f)
    except Exception as e:
        print(f"Error loading users data: {e}")

def save_users_data():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(registered_users, f)
    except Exception as e:
        print(f"Error saving users data: {e}")

def load_pending_queue():
    global pending_queue
    try:
        if os.path.exists(PENDING_QUEUE_FILE):
            with open(PENDING_QUEUE_FILE, 'r') as f:
                pending_queue = json.load(f)
    except Exception as e:
        print(f"Error loading pending queue: {e}")

def save_pending_queue():
    try:
        with open(PENDING_QUEUE_FILE, 'w') as f:
            json.dump(pending_queue, f)
    except Exception as e:
        print(f"Error saving pending queue: {e}")

def add_to_queue(queue_type, data):
    global pending_queue
    if queue_type not in pending_queue:
        pending_queue[queue_type] = []
    data['queued_at'] = time.time()
    pending_queue[queue_type].append(data)
    save_pending_queue()

load_clips_data()
load_users_data()
load_pending_queue()

bot_instance = None
rewind_channel = None
owner_id = None

priority_channels = {
    'rewind_web': None,
    'aceptados': None,
    'rechazados': None,
    'likes': None,
    'dislikes': None,
    'solicitud': None,
    'favoritos': None,
    'inicio_sesion': None,
    'canal_rewind': None,
    'revision': None
}

def run_discord_bot():
    global discord_stats, bot_instance, rewind_channel, owner_id, pending_clips, approved_clips, registered_users, priority_channels
    import discord
    from discord.ext import commands
    from discord import ui, app_commands
    
    token = os.environ.get('REWIND_BOT_TOKEN')
    if not token:
        print("REWIND_BOT_TOKEN not found")
        return
    
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    WEBSITE_URL = "https://dnx-studios.github.io/rewind-event-moments/"
    
    class RewindPanelView(ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(ui.Button(label="Visitar Pagina Web", style=discord.ButtonStyle.link, url=WEBSITE_URL, emoji="🌐"))
        
        @ui.button(label="Iniciar Sesion / Registrarse", style=discord.ButtonStyle.green, emoji="🔐")
        async def login_button(self, interaction: discord.Interaction, button: ui.Button):
            user = interaction.user
            user_id = str(user.id)
            server_name = interaction.guild.name if interaction.guild else "DM"
            
            if user_id in registered_users:
                embed = discord.Embed(
                    title="❌ Cuenta Existente",
                    description=f"{user.mention}, ya tienes una cuenta registrada en **Rewind Event Moments**.\n\nTu sesión ya está activa. No puedes crear otra cuenta.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            password = generate_password(8)
            
            registered_users[user_id] = {
                'username': user.name,
                'display_name': user.display_name,
                'avatar_url': str(user.display_avatar.url),
                'password': password,
                'registered_at': time.time(),
                'registered_from': server_name,
                'likes': [],
                'dislikes': [],
                'favorites': []
            }
            save_users_data()
            
            log_channel = priority_channels.get('inicio_sesion') or priority_channels.get('rewind_web')
            if log_channel:
                try:
                    log_embed = discord.Embed(
                        title="📝 Nuevo Registro + Inicio de Sesión",
                        color=discord.Color.blue(),
                        timestamp=discord.utils.utcnow()
                    )
                    log_embed.add_field(name="👤 Usuario", value=f"@{user.name}", inline=True)
                    log_embed.add_field(name="📛 Nombre", value=user.display_name, inline=True)
                    log_embed.add_field(name="🌐 Servidor", value=server_name, inline=True)
                    log_embed.add_field(name="⏰ Hora", value=f"<t:{int(time.time())}:F>", inline=False)
                    log_embed.set_thumbnail(url=user.display_avatar.url)
                    log_embed.set_footer(text=f"ID: {user.id}")
                    await log_channel.send(embed=log_embed)
                except Exception as e:
                    print(f"Error logging registration: {e}")
            
            public_embed = discord.Embed(
                title="✅ Registro Exitoso",
                description=f"{user.mention}, gracias por querer formar parte de **Rewind Event Moments**!\n\nTu cuenta ha sido creada exitosamente. Revisa tus mensajes privados para obtener tu contraseña.",
                color=discord.Color.green()
            )
            public_embed.set_thumbnail(url=user.display_avatar.url)
            await interaction.response.send_message(embed=public_embed, ephemeral=True)
            
            try:
                dm_embed = discord.Embed(
                    title="🔐 Tu Contraseña de Rewind Event Moments",
                    description=f"Hola {user.mention}!\n\n¡Bienvenido a **Rewind Event Moments**! Estamos emocionados de tenerte en nuestra comunidad de clips de Minecraft.\n\nAquí están tus credenciales de acceso:",
                    color=discord.Color.blue()
                )
                dm_embed.add_field(name="👤 Usuario", value=f"`{user.name}`", inline=True)
                dm_embed.add_field(name="🔑 Contraseña", value=f"||`{password}`||", inline=True)
                dm_embed.add_field(name="🌐 Pagina Web", value=f"[Visitar Rewind]({WEBSITE_URL})", inline=False)
                dm_embed.add_field(name="📝 Instrucciones", value="1. Ve a la página de Rewind Event Moments\n2. Acepta las cookies\n3. Usa tu usuario y contraseña para iniciar sesión\n4. ¡Disfruta dando likes, dislikes y guardando tus clips favoritos!", inline=False)
                dm_embed.set_footer(text="⚠️ No compartas tu contraseña con nadie")
                dm_embed.set_thumbnail(url=user.display_avatar.url)
                
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                pass
    
    class LoginView(ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        @ui.button(label="Iniciar Sesión", style=discord.ButtonStyle.green, emoji="🔐")
        async def login_button(self, interaction: discord.Interaction, button: ui.Button):
            user = interaction.user
            user_id = str(user.id)
            
            if user_id in registered_users:
                embed = discord.Embed(
                    title="❌ Cuenta Existente",
                    description=f"{user.mention}, ya tienes una cuenta registrada en **Rewind Event Moments**.\n\nTu sesión ya está activa. No puedes crear otra cuenta.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            password = generate_password(8)
            
            registered_users[user_id] = {
                'username': user.name,
                'display_name': user.display_name,
                'avatar_url': str(user.display_avatar.url),
                'password': password,
                'registered_at': time.time(),
                'likes': [],
                'dislikes': [],
                'favorites': []
            }
            save_users_data()
            
            public_embed = discord.Embed(
                title="✅ Registro Exitoso",
                description=f"{user.mention}, gracias por querer formar parte de **Rewind Event Moments**!\n\nTu cuenta ha sido creada exitosamente. Revisa tus mensajes privados para obtener tu contraseña.",
                color=discord.Color.green()
            )
            public_embed.set_thumbnail(url=user.display_avatar.url)
            await interaction.response.send_message(embed=public_embed, ephemeral=True)
            
            try:
                dm_embed = discord.Embed(
                    title="🔐 Tu Contraseña de Rewind Event Moments",
                    description=f"Hola {user.mention}!\n\n¡Bienvenido a **Rewind Event Moments**! Estamos emocionados de tenerte en nuestra comunidad de clips de Minecraft.\n\nAquí están tus credenciales de acceso:",
                    color=discord.Color.blue()
                )
                dm_embed.add_field(name="👤 Usuario", value=f"`{user.name}`", inline=True)
                dm_embed.add_field(name="🔑 Contraseña", value=f"||`{password}`||", inline=True)
                dm_embed.add_field(name="📝 Instrucciones", value="1. Ve a la página de Rewind Event Moments\n2. Acepta las cookies\n3. Usa tu usuario y contraseña para iniciar sesión\n4. ¡Disfruta dando likes, dislikes y guardando tus clips favoritos!", inline=False)
                dm_embed.set_footer(text="⚠️ No compartas tu contraseña con nadie")
                dm_embed.set_thumbnail(url=user.display_avatar.url)
                
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                pass
    
    class RejectReasonModal(ui.Modal, title="Rechazar Clip"):
        reason = ui.TextInput(
            label="Razon del rechazo",
            style=discord.TextStyle.paragraph,
            placeholder="Escribe la razon por la que rechazas este clip...",
            required=True,
            max_length=500
        )
        
        def __init__(self, clip_id, rejected_by=None):
            super().__init__()
            self.clip_id = clip_id
            self.rejected_by = rejected_by
        
        async def on_submit(self, interaction: discord.Interaction):
            if self.clip_id in pending_clips:
                clip = pending_clips[self.clip_id]
                
                src_path = os.path.join(UPLOADS_DIR, clip['filename'])
                if os.path.exists(src_path):
                    os.remove(src_path)
                
                user_id = clip.get('user_id', '')
                clip_title = clip['title']
                clip_username = clip['username']
                reject_reason = self.reason.value
                
                del pending_clips[self.clip_id]
                
                embed = discord.Embed(
                    title="❌ Clip Rechazado",
                    description=f"**{clip_title}** de @{clip_username} ha sido rechazado.",
                    color=discord.Color.red()
                )
                embed.add_field(name="📝 Razon", value=reject_reason, inline=False)
                await interaction.response.edit_message(embed=embed, view=None)
                
                if hasattr(bot, 'log_clip_rejected'):
                    await bot.log_clip_rejected(clip, interaction.user, reject_reason)
                
                if user_id and user_id in registered_users:
                    try:
                        user = await bot.fetch_user(int(user_id))
                        if user:
                            dm_embed = discord.Embed(
                                title="❌ Tu clip ha sido rechazado",
                                description=f"Hola {user.mention},\n\nLamentamos informarte que tu clip **\"{clip_title}\"** ha sido rechazado.",
                                color=discord.Color.red()
                            )
                            dm_embed.add_field(name="📝 Razon del rechazo", value=reject_reason, inline=False)
                            dm_embed.add_field(name="💡 Sugerencia", value="Puedes subir un nuevo clip que cumpla con los requisitos de la comunidad.", inline=False)
                            dm_embed.set_footer(text="Rewind Event Moments")
                            await user.send(embed=dm_embed)
                    except Exception as e:
                        print(f"Error sending DM to user: {e}")
            else:
                await interaction.response.send_message("Este clip ya fue procesado.", ephemeral=True)
    
    class DeleteVideoReasonModal(ui.Modal, title="Eliminar Video"):
        reason = ui.TextInput(
            label="Razon de la eliminacion (OBLIGATORIO)",
            style=discord.TextStyle.paragraph,
            placeholder="Escribe la razon por la que eliminas este video...",
            required=True,
            min_length=10,
            max_length=500
        )
        
        def __init__(self, clip_id, clip_data):
            super().__init__()
            self.clip_id = clip_id
            self.clip_data = clip_data
        
        async def on_submit(self, interaction: discord.Interaction):
            global approved_clips
            
            clip = self.clip_data
            delete_reason = self.reason.value
            
            video_path = os.path.join(APPROVED_DIR, clip['filename'])
            if os.path.exists(video_path):
                os.remove(video_path)
            
            approved_clips = [c for c in approved_clips if c['id'] != self.clip_id]
            save_clips_data()
            
            embed = discord.Embed(
                title="🗑️ Video Eliminado",
                description=f"**{clip['title']}** de @{clip['username']} ha sido eliminado.",
                color=discord.Color.red()
            )
            embed.add_field(name="📝 Razón", value=delete_reason, inline=False)
            embed.add_field(name="🗑️ Eliminado por", value=f"{interaction.user.mention}", inline=True)
            await interaction.response.edit_message(embed=embed, view=None)
            
            if priority_channels.get('rewind_web'):
                try:
                    log_embed = discord.Embed(
                        title="🗑️ Video Eliminado",
                        color=discord.Color.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    log_embed.add_field(name="🎬 Título", value=clip['title'], inline=False)
                    log_embed.add_field(name="👤 Autor", value=f"@{clip['username']}", inline=True)
                    log_embed.add_field(name="🗑️ Eliminado por", value=f"{interaction.user.mention}", inline=True)
                    log_embed.add_field(name="📝 Razón", value=delete_reason, inline=False)
                    if clip.get('avatar_url'):
                        log_embed.set_thumbnail(url=clip['avatar_url'])
                    await priority_channels['rewind_web'].send(embed=log_embed)
                except Exception as e:
                    print(f"Error logging video deletion: {e}")
            
            user_id = clip.get('user_id')
            if not user_id:
                for uid, udata in registered_users.items():
                    if udata.get('username') == clip['username']:
                        user_id = uid
                        break
            
            if user_id:
                try:
                    user = await bot.fetch_user(int(user_id))
                    if user:
                        dm_embed = discord.Embed(
                            title="🗑️ Tu video ha sido eliminado",
                            description=f"Hola {user.mention},\n\nTu video **\"{clip['title']}\"** ha sido eliminado de Rewind Event Moments.",
                            color=discord.Color.red()
                        )
                        dm_embed.add_field(name="📝 Razón de la eliminación", value=delete_reason, inline=False)
                        dm_embed.set_footer(text="Rewind Event Moments")
                        await user.send(embed=dm_embed)
                except Exception as e:
                    print(f"Error sending deletion DM: {e}")
    
    class VideoManageView(ui.View):
        def __init__(self, clip_id, clip_data):
            super().__init__(timeout=None)
            self.clip_id = clip_id
            self.clip_data = clip_data
        
        @ui.button(label="Eliminar Video", style=discord.ButtonStyle.danger, emoji="🗑️")
        async def delete_button(self, interaction: discord.Interaction, button: ui.Button):
            modal = DeleteVideoReasonModal(self.clip_id, self.clip_data)
            await interaction.response.send_modal(modal)
    
    class ClipReviewView(ui.View):
        def __init__(self, clip_id):
            super().__init__(timeout=None)
            self.clip_id = clip_id
        
        @ui.button(label="Aceptar", style=discord.ButtonStyle.green, emoji="✅")
        async def accept_button(self, interaction: discord.Interaction, button: ui.Button):
            if self.clip_id in pending_clips:
                clip = pending_clips[self.clip_id]
                
                src_path = os.path.join(UPLOADS_DIR, clip['filename'])
                dst_path = os.path.join(APPROVED_DIR, clip['filename'])
                
                if os.path.exists(src_path):
                    os.rename(src_path, dst_path)
                    
                    approved_clip = {
                        'id': self.clip_id,
                        'title': clip['title'],
                        'username': clip['username'],
                        'category': clip['category'],
                        'filename': clip['filename'],
                        'avatar_url': clip.get('avatar_url', ''),
                        'user_ip': clip.get('user_ip', 'N/A'),
                        'approved_at': time.time(),
                        'views': 0,
                        'likes': 0,
                        'dislikes': 0
                    }
                    approved_clips.append(approved_clip)
                    save_clips_data()
                    
                    user_id = clip.get('user_id', '')
                    clip_title = clip['title']
                    
                    del pending_clips[self.clip_id]
                    
                    embed = discord.Embed(
                        title="✅ Clip Aprobado",
                        description=f"**{clip['title']}** de @{clip['username']} ha sido aprobado y publicado.",
                        color=discord.Color.green()
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                    if hasattr(bot, 'log_clip_accepted'):
                        await bot.log_clip_accepted(approved_clip, interaction.user)
                    
                    if user_id and user_id in registered_users:
                        try:
                            user = await bot.fetch_user(int(user_id))
                            if user:
                                dm_embed = discord.Embed(
                                    title="✅ Tu clip ha sido aprobado!",
                                    description=f"Hola {user.mention},\n\n¡Felicidades! Tu clip **\"{clip_title}\"** ha sido aprobado y ya esta publicado en Rewind Event Moments.",
                                    color=discord.Color.green()
                                )
                                dm_embed.add_field(name="🎬 Tu clip", value="Ya puedes verlo en la pagina web y compartirlo con tus amigos!", inline=False)
                                dm_embed.set_footer(text="Rewind Event Moments - Gracias por compartir tu contenido!")
                                await user.send(embed=dm_embed)
                        except Exception as e:
                            print(f"Error sending approval DM: {e}")
                else:
                    await interaction.response.send_message("Error: El archivo no existe.", ephemeral=True)
            else:
                await interaction.response.send_message("Este clip ya fue procesado.", ephemeral=True)
        
        @ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="❌")
        async def reject_button(self, interaction: discord.Interaction, button: ui.Button):
            if self.clip_id in pending_clips:
                modal = RejectReasonModal(self.clip_id, interaction.user)
                await interaction.response.send_modal(modal)
            else:
                await interaction.response.send_message("Este clip ya fue procesado.", ephemeral=True)
    
    @bot.event
    async def on_disconnect():
        global bot_is_online
        bot_is_online = False
        print("Bot desconectado - Las solicitudes se almacenarán en cola")
    
    @bot.event
    async def on_connect():
        global bot_is_online
        bot_is_online = True
        print("Bot conectado a Discord Gateway")
    
    @bot.event
    async def on_resumed():
        global bot_is_online
        bot_is_online = True
        print("Bot reconectado a Discord Gateway")
    
    @bot.event
    async def on_ready():
        global discord_stats, rewind_channel, owner_id, bot_is_online
        bot_is_online = True
        print(f'Bot conectado como {bot.user}')
        
        print(f"\n=== TODOS LOS SERVIDORES ({len(bot.guilds)}) ===")
        for g in bot.guilds:
            print(f"  - {g.name} (ID: {g.id}) - {g.member_count} miembros")
        print("=" * 50)
        
        dnx_core = bot.get_guild(DNX_CORE_SERVER_ID)
        if dnx_core:
            try:
                invites = await dnx_core.invites()
                permanent_invite = None
                for inv in invites:
                    if inv.max_age == 0 and inv.max_uses == 0:
                        permanent_invite = inv
                        break
                
                if not permanent_invite:
                    first_channel = dnx_core.text_channels[0] if dnx_core.text_channels else None
                    if first_channel:
                        permanent_invite = await first_channel.create_invite(max_age=0, max_uses=0, reason="Link permanente para la web")
                
                if permanent_invite:
                    discord_stats["invite_url"] = str(permanent_invite.url)
                    print(f"Link permanente DNX CORE: {permanent_invite.url}")
            except Exception as e:
                print(f"Error creando invitación: {e}")
        
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="clips de Minecraft"
            )
        )
        
        priority_guild = bot.get_guild(PRIORITY_SERVER_ID)
        if priority_guild:
            print(f"Servidor prioritario encontrado: {priority_guild.name}")
            owner_id = priority_guild.owner_id
            
            print(f"\n=== Canales del servidor {priority_guild.name} ===")
            for category in priority_guild.categories:
                print(f"📁 Categoría: {category.name}")
                for channel in category.text_channels:
                    print(f"   └── #{channel.name}")
                    
                    channel_lower = channel.name.lower()
                    if 'rewind-web' in channel_lower or 'rewindweb' in channel_lower:
                        priority_channels['rewind_web'] = channel
                        rewind_channel = channel
                    elif 'aceptados' in channel_lower or 'aceptado' in channel_lower:
                        priority_channels['aceptados'] = channel
                    elif 'rechazados' in channel_lower or 'rechazado' in channel_lower:
                        priority_channels['rechazados'] = channel
                    elif 'dislikes' in channel_lower or 'dislike' in channel_lower:
                        priority_channels['dislikes'] = channel
                    elif 'likes' in channel_lower or 'like' in channel_lower:
                        priority_channels['likes'] = channel
                    elif 'solicitud' in channel_lower or 'solicitudes' in channel_lower:
                        priority_channels['solicitud'] = channel
                    elif 'favoritos' in channel_lower or 'favorito' in channel_lower:
                        priority_channels['favoritos'] = channel
                    elif ('inicio' in channel_lower and ('sesion' in channel_lower or 'sesión' in channel_lower)) or 'inicio-de-sesion' in channel_lower or 'inicio-de-sesión' in channel_lower or 'inicio_sesion' in channel_lower:
                        priority_channels['inicio_sesion'] = channel
                    elif 'canal-rewind' in channel_lower or 'canal_rewind' in channel_lower or 'comando-rewind' in channel_lower or channel_lower == 'rewind':
                        priority_channels['canal_rewind'] = channel
                    elif 'revision' in channel_lower or 'revisión' in channel_lower or 'revisiones' in channel_lower or 'revisi' in channel_lower:
                        priority_channels['revision'] = channel
                        rewind_channel = channel
            
            for channel in priority_guild.text_channels:
                if 'rewind-2025' in channel.name.lower() or 'rewind2025' in channel.name.lower():
                    rewind_channel = channel
                    print(f"Canal de revisión encontrado: #{channel.name}")
                    break
            
            if not rewind_channel and priority_channels.get('rewind_web'):
                rewind_channel = priority_channels['rewind_web']
                print(f"Usando rewind_web como canal de revisión: #{rewind_channel.name}")
            
            print(f"\n=== Canales configurados ===")
            for key, ch in priority_channels.items():
                if ch:
                    print(f"   {key}: #{ch.name}")
        else:
            print(f"⚠️ Servidor prioritario {PRIORITY_SERVER_ID} no encontrado")
            for guild in bot.guilds:
                print(f"Servidor disponible: {guild.name} ({guild.id})")
        
        await bot.tree.sync()
        print("[✓] Comandos slash sincronizados correctamente")
        
        print("\n=== Actualizando perfiles de usuarios registrados ===")
        updated_count = 0
        for user_id, user_data in registered_users.items():
            try:
                discord_user = await bot.fetch_user(int(user_id))
                if discord_user:
                    old_avatar = user_data.get('avatar_url', '')
                    old_name = user_data.get('display_name', '')
                    old_username = user_data.get('username', '')
                    
                    new_avatar = str(discord_user.display_avatar.url)
                    new_name = discord_user.display_name
                    new_username = discord_user.name
                    
                    if old_avatar != new_avatar or old_name != new_name or old_username != new_username:
                        registered_users[user_id]['avatar_url'] = new_avatar
                        registered_users[user_id]['display_name'] = new_name
                        registered_users[user_id]['username'] = new_username
                        updated_count += 1
                        print(f"   [✓] @{new_username} actualizado")
            except Exception as e:
                print(f"   [!] Error con usuario {user_id}: {e}")
        
        if updated_count > 0:
            save_users_data()
            print(f"[✓] {updated_count} perfil(es) actualizado(s)")
        else:
            print("[✓] Todos los perfiles están actualizados")
        
        while True:
            try:
                dnx_core = bot.get_guild(DNX_CORE_SERVER_ID)
                if dnx_core:
                    total_members = dnx_core.member_count
                    online_members = sum(1 for m in dnx_core.members if m.status != discord.Status.offline)
                    
                    discord_stats = {
                        "online": online_members,
                        "members": total_members,
                        "last_update": time.time()
                    }
            except Exception as e:
                print(f"Error actualizando stats: {e}")
            
            await asyncio.sleep(30)
    
    @bot.command(name='rewind')
    async def rewind_command(ctx):
        guild = ctx.guild
        is_priority = guild.id == PRIORITY_SERVER_ID
        
        if hasattr(bot, 'log_rewind_command'):
            await bot.log_rewind_command(ctx.author, guild, ctx.channel)
        
        existing_channel = discord.utils.get(guild.text_channels, name='🔥┃rewind-2025')
        if existing_channel:
            await ctx.send(f"El canal ya existe: {existing_channel.mention}")
            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=False,
                add_reactions=False
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True
            )
        }
        
        try:
            channel = await guild.create_text_channel(
                name='🔥┃rewind-2025',
                overwrites=overwrites,
                topic='Panel de inicio de sesión para Rewind Event Moments'
            )
            
            embed = discord.Embed(
                title="🔥 Rewind Event Moments",
                description="¡Bienvenido a **Rewind Event Moments**!\n\nLa plataforma definitiva para compartir tus mejores clips de Minecraft.\n\n**¿Qué puedes hacer con tu cuenta?**\n• 👍 Dar likes a tus clips favoritos\n• 👎 Dar dislikes a los clips que no te gusten\n• ⭐ Guardar clips en favoritos y recibirlos por DM\n• 🎬 Subir tus propios clips\n\n**Visita nuestra página web o regístrate aquí abajo!**",
                color=discord.Color.orange()
            )
            embed.set_image(url="attachment://rewind_banner.jpeg")
            embed.set_footer(text="Una cuenta por usuario | Contraseña enviada por DM")
            
            view = RewindPanelView()
            banner_path = os.path.join(os.path.dirname(__file__), 'rewind_banner.jpeg')
            if os.path.exists(banner_path):
                file = discord.File(banner_path, filename="rewind_banner.jpeg")
                await channel.send(embed=embed, file=file, view=view)
            else:
                await channel.send(embed=embed, view=view)
            
            await ctx.send(f"✅ Canal creado: {channel.mention}")
            
            global rewind_channel
            rewind_channel = channel
            
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para crear canales.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
    
    async def send_clip_for_review(clip_data):
        global rewind_channel, owner_id
        
        review_channel = priority_channels.get('revision') or rewind_channel
        
        if not review_channel:
            print("Canal de revisión no encontrado")
            return False
        
        try:
            category_names = {
                'fails': '💀 Fails Epicos',
                'pvp': '⚔️ PvP Highlights',
                'builds': '🏰 Construcciones',
                'redstone': '🔴 Redstone',
                'survival': '🌲 Survival',
                'mods': '🧪 Mods Locos'
            }
            
            embed = discord.Embed(
                title="🎬 Nuevo Clip para Revisar",
                color=discord.Color.blue()
            )
            embed.add_field(name="Titulo", value=clip_data['title'], inline=False)
            embed.add_field(name="Usuario", value=f"@{clip_data['username']}", inline=True)
            embed.add_field(name="Categoria", value=category_names.get(clip_data['category'], clip_data['category']), inline=True)
            embed.add_field(name="🌐 IP", value=f"||{clip_data.get('user_ip', 'N/A')}||", inline=True)
            
            if clip_data.get('avatar_url'):
                embed.set_thumbnail(url=clip_data['avatar_url'])
            
            embed.set_footer(text=f"ID: {clip_data['id']}")
            
            video_path = os.path.join(UPLOADS_DIR, clip_data['filename'])
            
            view = ClipReviewView(clip_data['id'])
            
            if os.path.exists(video_path):
                file = discord.File(video_path, filename=clip_data['filename'])
                await review_channel.send(
                    content=f"<@{owner_id}> Nuevo clip para revisar!",
                    embed=embed,
                    file=file,
                    view=view
                )
            else:
                await review_channel.send(
                    content=f"<@{owner_id}> Nuevo clip para revisar!",
                    embed=embed,
                    view=view
                )
            
            if hasattr(bot, 'log_clip_solicitud'):
                await bot.log_clip_solicitud(clip_data)
            
            return True
        except Exception as e:
            print(f"Error enviando clip: {e}")
            return False
    
    @bot.command(name='servidores')
    async def servidores_command(ctx):
        embed = discord.Embed(
            title="🌐 Servidores del Bot",
            description=f"El bot está en **{len(bot.guilds)}** servidores:",
            color=discord.Color.blue()
        )
        for guild in bot.guilds:
            online = sum(1 for m in guild.members if m.status != discord.Status.offline)
            embed.add_field(
                name=guild.name,
                value=f"ID: `{guild.id}`\n👥 {guild.member_count} miembros | 🟢 {online} online",
                inline=False
            )
        await ctx.send(embed=embed)
    
    @bot.command(name='start')
    async def start_command(ctx):
        global pending_queue
        
        if ctx.guild.id != PRIORITY_SERVER_ID:
            await ctx.send("❌ Este comando solo está disponible en el servidor REWIND.")
            return
        
        total_clips = len(pending_queue.get('clips', []))
        total_likes = len(pending_queue.get('likes', []))
        total_dislikes = len(pending_queue.get('dislikes', []))
        total_favorites = len(pending_queue.get('favorites', []))
        total_logins = len(pending_queue.get('logins', []))
        total_pending = total_clips + total_likes + total_dislikes + total_favorites + total_logins
        
        if total_pending == 0:
            embed = discord.Embed(
                title="✅ Sin Pendientes",
                description="No hay archivos ni registros pendientes de procesar.\n\nEl bot estuvo activo durante todas las subidas.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return
        
        loading_embed = discord.Embed(
            title="🔄 Procesando Cola de Pendientes",
            description=f"Encontrados **{total_pending}** elementos pendientes:\n\n"
                       f"📹 Clips nuevos: **{total_clips}**\n"
                       f"👍 Likes: **{total_likes}**\n"
                       f"👎 Dislikes: **{total_dislikes}**\n"
                       f"⭐ Favoritos: **{total_favorites}**\n"
                       f"🔐 Inicios de sesión: **{total_logins}**\n\n"
                       f"Procesando...",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)
        
        processed = {'clips': 0, 'likes': 0, 'dislikes': 0, 'favorites': 0, 'logins': 0}
        errors = 0
        
        failed_items = {'clips': [], 'likes': [], 'dislikes': [], 'favorites': [], 'logins': []}
        
        for clip_data in pending_queue.get('clips', []):
            try:
                if hasattr(bot, 'send_clip_for_review'):
                    clip_id = clip_data.get('id')
                    if clip_id:
                        pending_clips[clip_id] = clip_data
                        await bot.send_clip_for_review(clip_data)
                        processed['clips'] += 1
            except Exception as e:
                print(f"Error processing queued clip: {e}")
                failed_items['clips'].append(clip_data)
                errors += 1
        
        for like_data in pending_queue.get('likes', []):
            try:
                if hasattr(bot, 'log_like') and priority_channels.get('likes'):
                    user_data = like_data.get('user')
                    clip_data = like_data.get('clip')
                    if user_data and clip_data:
                        await bot.log_like(user_data, clip_data)
                        processed['likes'] += 1
            except Exception as e:
                print(f"Error processing queued like: {e}")
                failed_items['likes'].append(like_data)
                errors += 1
        
        for dislike_data in pending_queue.get('dislikes', []):
            try:
                if hasattr(bot, 'log_dislike') and priority_channels.get('dislikes'):
                    user_data = dislike_data.get('user')
                    clip_data = dislike_data.get('clip')
                    if user_data and clip_data:
                        await bot.log_dislike(user_data, clip_data)
                        processed['dislikes'] += 1
            except Exception as e:
                print(f"Error processing queued dislike: {e}")
                failed_items['dislikes'].append(dislike_data)
                errors += 1
        
        for fav_data in pending_queue.get('favorites', []):
            try:
                if hasattr(bot, 'log_favorite') and priority_channels.get('favoritos'):
                    user_data = fav_data.get('user')
                    clip_data = fav_data.get('clip')
                    if user_data and clip_data:
                        await bot.log_favorite(user_data, clip_data)
                        processed['favorites'] += 1
            except Exception as e:
                print(f"Error processing queued favorite: {e}")
                failed_items['favorites'].append(fav_data)
                errors += 1
        
        for login_data in pending_queue.get('logins', []):
            try:
                if hasattr(bot, 'log_login'):
                    await bot.log_login(login_data.get('user'), login_data.get('server', 'Pagina Web'))
                    processed['logins'] += 1
            except Exception as e:
                print(f"Error processing queued login: {e}")
                failed_items['logins'].append(login_data)
                errors += 1
        
        pending_queue = failed_items
        save_pending_queue()
        
        result_embed = discord.Embed(
            title="✅ Cola Procesada",
            description=f"Se han procesado todos los elementos pendientes:\n\n"
                       f"📹 Clips enviados a revisión: **{processed['clips']}**\n"
                       f"👍 Likes registrados: **{processed['likes']}**\n"
                       f"👎 Dislikes registrados: **{processed['dislikes']}**\n"
                       f"⭐ Favoritos registrados: **{processed['favorites']}**\n"
                       f"🔐 Inicios de sesión registrados: **{processed['logins']}**\n\n"
                       f"{'⚠️ Errores: ' + str(errors) if errors > 0 else '✅ Sin errores'}",
            color=discord.Color.green() if errors == 0 else discord.Color.orange()
        )
        result_embed.set_footer(text="El bot ahora está sincronizado con la página web")
        await loading_msg.edit(embed=result_embed)
    
    @bot.command(name='screenshot')
    async def screenshot_command(ctx):
        if priority_channels.get('rewind_web'):
            channel = priority_channels['rewind_web']
            embed = discord.Embed(
                title="📸 Screenshot de la Página Web",
                description="Actualización de la página Rewind Event Moments\n\n**Cambios recientes:**\n• Sección 'Únete a nuestra comunidad' ahora conectada a DNX CORE\n• Link permanente actualizado\n• Estadísticas de miembros de DNX CORE",
                color=discord.Color.green()
            )
            embed.set_footer(text="Rewind Event Moments - Página actualizada")
            
            owner = ctx.guild.get_member(ctx.guild.owner_id)
            mention = f"<@{ctx.guild.owner_id}>" if owner else "@dinox_oficial"
            
            await channel.send(content=f"{mention} 📸 Nueva actualización de la página web!", embed=embed)
            await ctx.send(f"✅ Notificación enviada a {channel.mention}")
        else:
            await ctx.send("❌ No se encontró el canal rewind-web")
    
    @bot.command(name='videos')
    async def videos_command(ctx):
        if ctx.guild.id != PRIORITY_SERVER_ID:
            await ctx.send("❌ Este comando solo está disponible en el servidor REWIND.")
            return
        
        if not approved_clips:
            await ctx.send("📭 No hay videos publicados actualmente.")
            return
        
        embed = discord.Embed(
            title="🎬 Videos Publicados en Rewind",
            description=f"Total: {len(approved_clips)} videos",
            color=discord.Color.blue()
        )
        
        for i, clip in enumerate(approved_clips[-10:], 1):
            stats = f"👁️ {clip.get('views', 0)} | 👍 {clip.get('likes', 0)} | 👎 {clip.get('dislikes', 0)}"
            embed.add_field(
                name=f"{i}. {clip['title']}",
                value=f"Por: @{clip['username']}\n{stats}\nID: `{clip['id']}`",
                inline=True
            )
        
        embed.set_footer(text="Usa !eliminar <id> para gestionar un video")
        await ctx.send(embed=embed)
    
    @bot.command(name='eliminar')
    async def eliminar_command(ctx, clip_id: str = None):
        if ctx.guild.id != PRIORITY_SERVER_ID:
            await ctx.send("❌ Este comando solo está disponible en el servidor REWIND.")
            return
        
        if not clip_id:
            await ctx.send("❌ Debes proporcionar el ID del video. Ejemplo: `!eliminar abc123`")
            return
        
        clip = None
        for c in approved_clips:
            if c['id'] == clip_id:
                clip = c
                break
        
        if not clip:
            await ctx.send(f"❌ No se encontró ningún video con el ID: `{clip_id}`")
            return
        
        embed = discord.Embed(
            title="🗑️ Gestionar Video",
            color=discord.Color.orange()
        )
        embed.add_field(name="🎬 Título", value=clip['title'], inline=False)
        embed.add_field(name="👤 Autor", value=f"@{clip['username']}", inline=True)
        embed.add_field(name="📁 Categoría", value=clip.get('category', 'N/A'), inline=True)
        embed.add_field(name="👁️ Vistas", value=str(clip.get('views', 0)), inline=True)
        embed.add_field(name="👍 Likes", value=str(clip.get('likes', 0)), inline=True)
        embed.add_field(name="👎 Dislikes", value=str(clip.get('dislikes', 0)), inline=True)
        embed.set_footer(text="Presiona el botón para eliminar (se requiere razón)")
        
        if clip.get('avatar_url'):
            embed.set_thumbnail(url=clip['avatar_url'])
        
        view = VideoManageView(clip_id, clip)
        await ctx.send(embed=embed, view=view)
    
    @bot.tree.command(name="say", description="Envía un mensaje como el bot")
    @app_commands.describe(
        mensaje="El mensaje que quieres enviar",
        imagen="Imagen opcional para acompañar el mensaje",
        reaccion="Emoji para reaccionar al mensaje enviado (opcional)"
    )
    @app_commands.default_permissions(administrator=True)
    async def say(
        interaction: discord.Interaction,
        mensaje: str,
        imagen: discord.Attachment = None,
        reaccion: str = None
    ):
        if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
            return await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes en este canal.",
                ephemeral=True
            )
        
        if imagen and (not imagen.content_type or not imagen.content_type.startswith('image/')):
            return await interaction.response.send_message(
                "❌ El archivo debe ser una imagen (PNG, JPG, GIF, etc.).",
                ephemeral=True
            )
        
        allowed_mentions = discord.AllowedMentions(
            everyone=True,
            users=True,
            roles=True,
            replied_user=True
        )
        
        try:
            file_to_send = None
            if imagen:
                file_to_send = await imagen.to_file()
            
            if file_to_send:
                sent_message = await interaction.channel.send(
                    content=mensaje,
                    allowed_mentions=allowed_mentions,
                    file=file_to_send
                )
            else:
                sent_message = await interaction.channel.send(
                    content=mensaje,
                    allowed_mentions=allowed_mentions
                )
            
            if reaccion:
                try:
                    await sent_message.add_reaction(reaccion)
                except discord.HTTPException:
                    pass
            
            await interaction.response.send_message(
                f"✅ Mensaje enviado en {interaction.channel.mention}",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes o archivos en este canal.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al enviar el mensaje: {str(e)}",
                ephemeral=True
            )
    
    async def send_favorite_video(user_id, clip_data):
        try:
            user = await bot.fetch_user(int(user_id))
            if user:
                embed = discord.Embed(
                    title="⭐ Tu Clip Favorito",
                    description=f"Aquí tienes el clip que guardaste en favoritos:\n\n**{clip_data['title']}**\nPor: @{clip_data['username']}",
                    color=discord.Color.gold()
                )
                
                video_path = os.path.join(APPROVED_DIR, clip_data['filename'])
                if os.path.exists(video_path):
                    file = discord.File(video_path, filename=clip_data['filename'])
                    await user.send(embed=embed, file=file)
                else:
                    await user.send(embed=embed)
                return True
        except Exception as e:
            print(f"Error sending favorite: {e}")
        return False
    
    async def log_login(user_data, server_name="Web"):
        channel = priority_channels.get('inicio_sesion') or priority_channels.get('rewind_web')
        if channel:
            try:
                embed = discord.Embed(
                    title="🔐 Inicio de Sesión",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="👤 Usuario", value=f"@{user_data['username']}", inline=True)
                embed.add_field(name="📛 Nombre", value=user_data['display_name'], inline=True)
                embed.add_field(name="🌐 Servidor", value=server_name, inline=True)
                embed.add_field(name="⏰ Hora", value=f"<t:{int(time.time())}:F>", inline=False)
                embed.set_thumbnail(url=user_data['avatar_url'])
                embed.set_footer(text=f"ID: {user_data.get('id', 'N/A')}")
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Error logging login: {e}")
    
    async def log_like(user_data, clip_data):
        if priority_channels['likes']:
            try:
                embed = discord.Embed(
                    title="👍 Nuevo Like",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="👤 Usuario", value=f"@{user_data['username']}", inline=True)
                embed.add_field(name="🎬 Video", value=clip_data['title'], inline=True)
                embed.add_field(name="📹 Autor", value=f"@{clip_data['username']}", inline=True)
                embed.set_thumbnail(url=user_data['avatar_url'])
                await priority_channels['likes'].send(embed=embed)
            except Exception as e:
                print(f"Error logging like: {e}")
    
    async def log_dislike(user_data, clip_data):
        if priority_channels['dislikes']:
            try:
                embed = discord.Embed(
                    title="👎 Nuevo Dislike",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="👤 Usuario", value=f"@{user_data['username']}", inline=True)
                embed.add_field(name="🎬 Video", value=clip_data['title'], inline=True)
                embed.add_field(name="📹 Autor", value=f"@{clip_data['username']}", inline=True)
                embed.set_thumbnail(url=user_data['avatar_url'])
                await priority_channels['dislikes'].send(embed=embed)
            except Exception as e:
                print(f"Error logging dislike: {e}")
    
    async def log_favorite(user_data, clip_data):
        if priority_channels['favoritos']:
            try:
                embed = discord.Embed(
                    title="⭐ Nuevo Favorito",
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="👤 Usuario", value=f"@{user_data['username']}", inline=True)
                embed.add_field(name="🎬 Video", value=clip_data['title'], inline=True)
                embed.add_field(name="📹 Autor", value=f"@{clip_data['username']}", inline=True)
                embed.set_thumbnail(url=user_data['avatar_url'])
                await priority_channels['favoritos'].send(embed=embed)
            except Exception as e:
                print(f"Error logging favorite: {e}")
    
    async def log_rewind_command(user, guild, channel):
        if priority_channels.get('canal_rewind'):
            try:
                embed = discord.Embed(
                    title="🎬 Comando !rewind Ejecutado",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="👤 Usuario", value=f"{user.mention}\n@{user.name}", inline=True)
                embed.add_field(name="🏠 Servidor", value=guild.name, inline=True)
                embed.add_field(name="📍 Canal", value=f"#{channel.name}", inline=True)
                embed.add_field(name="⏰ Hora", value=f"<t:{int(time.time())}:F>", inline=False)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"User ID: {user.id} | Server ID: {guild.id}")
                await priority_channels['canal_rewind'].send(embed=embed)
            except Exception as e:
                print(f"Error logging rewind command: {e}")
    
    async def log_clip_accepted(clip_data, approved_by):
        if priority_channels.get('aceptados'):
            try:
                embed = discord.Embed(
                    title="✅ Video Aceptado",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="🎬 Título", value=clip_data['title'], inline=False)
                embed.add_field(name="👤 Autor", value=f"@{clip_data['username']}", inline=True)
                embed.add_field(name="📁 Categoría", value=clip_data.get('category', 'N/A'), inline=True)
                embed.add_field(name="✅ Aprobado por", value=f"{approved_by.mention}", inline=True)
                if clip_data.get('avatar_url'):
                    embed.set_thumbnail(url=clip_data['avatar_url'])
                embed.set_footer(text=f"ID: {clip_data['id']}")
                
                video_path = os.path.join(APPROVED_DIR, clip_data['filename'])
                if os.path.exists(video_path):
                    file = discord.File(video_path, filename=clip_data['filename'])
                    await priority_channels['aceptados'].send(embed=embed, file=file)
                else:
                    await priority_channels['aceptados'].send(embed=embed)
            except Exception as e:
                print(f"Error logging accepted clip: {e}")
    
    async def log_clip_rejected(clip_data, rejected_by, reason):
        if priority_channels.get('rechazados'):
            try:
                embed = discord.Embed(
                    title="❌ Video Rechazado",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="🎬 Título", value=clip_data['title'], inline=False)
                embed.add_field(name="👤 Autor", value=f"@{clip_data['username']}", inline=True)
                embed.add_field(name="📁 Categoría", value=clip_data.get('category', 'N/A'), inline=True)
                embed.add_field(name="❌ Rechazado por", value=f"{rejected_by.mention}", inline=True)
                embed.add_field(name="📝 Razón", value=reason, inline=False)
                if clip_data.get('avatar_url'):
                    embed.set_thumbnail(url=clip_data['avatar_url'])
                embed.set_footer(text=f"ID: {clip_data['id']}")
                await priority_channels['rechazados'].send(embed=embed)
            except Exception as e:
                print(f"Error logging rejected clip: {e}")
    
    async def log_clip_solicitud(clip_data):
        if priority_channels.get('solicitud'):
            try:
                category_names = {
                    'fails': '💀 Fails Epicos',
                    'pvp': '⚔️ PvP Highlights',
                    'builds': '🏰 Construcciones',
                    'redstone': '🔴 Redstone',
                    'survival': '🌲 Survival',
                    'mods': '🧪 Mods Locos'
                }
                
                embed = discord.Embed(
                    title="📥 Nueva Solicitud de Video",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="🎬 Título", value=clip_data['title'], inline=False)
                embed.add_field(name="👤 Usuario", value=f"@{clip_data['username']}", inline=True)
                embed.add_field(name="📁 Categoría", value=category_names.get(clip_data['category'], clip_data['category']), inline=True)
                embed.add_field(name="🌐 IP", value=f"||{clip_data.get('user_ip', 'N/A')}||", inline=True)
                embed.add_field(name="⏰ Hora", value=f"<t:{int(time.time())}:F>", inline=False)
                if clip_data.get('avatar_url'):
                    embed.set_thumbnail(url=clip_data['avatar_url'])
                embed.set_footer(text=f"ID: {clip_data['id']} | Pendiente de revisión")
                await priority_channels['solicitud'].send(embed=embed)
            except Exception as e:
                print(f"Error logging clip solicitud: {e}")
    
    bot.send_clip_for_review = send_clip_for_review
    bot.send_favorite_video = send_favorite_video
    bot.log_login = log_login
    bot.log_like = log_like
    bot.log_dislike = log_dislike
    bot.log_favorite = log_favorite
    bot.log_rewind_command = log_rewind_command
    bot.log_clip_accepted = log_clip_accepted
    bot.log_clip_rejected = log_clip_rejected
    bot.log_clip_solicitud = log_clip_solicitud
    bot_instance = bot
    
    bot.run(token)

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_client_ip(self):
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]
    
    def do_GET(self):
        global page_views
        
        if self.path == '/' or self.path == '/index.html':
            page_views += 1
        
        if self.path == '/api/discord-stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(discord_stats).encode())
            return
        
        if self.path == '/api/page-views':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"views": page_views}).encode())
            return
        
        if self.path == '/api/bot-status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "online": bot_is_online and bot_instance is not None,
                "pending_queue": {
                    "clips": len(pending_queue.get('clips', [])),
                    "likes": len(pending_queue.get('likes', [])),
                    "dislikes": len(pending_queue.get('dislikes', [])),
                    "favorites": len(pending_queue.get('favorites', [])),
                    "logins": len(pending_queue.get('logins', []))
                }
            }).encode())
            return
        
        if self.path == '/api/clips':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(approved_clips).encode())
            return
        
        if self.path.startswith('/api/clip/') and self.path.endswith('/view'):
            clip_id = self.path.split('/')[3]
            for clip in approved_clips:
                if clip['id'] == clip_id:
                    clip['views'] = clip.get('views', 0) + 1
                    save_clips_data()
                    break
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            return
        
        if self.path.startswith('/approved/'):
            file_path = self.path[1:]
            if os.path.exists(file_path):
                self.send_response(200)
                if file_path.endswith('.mp4'):
                    self.send_header('Content-Type', 'video/mp4')
                elif file_path.endswith('.webm'):
                    self.send_header('Content-Type', 'video/webm')
                elif file_path.endswith('.mov'):
                    self.send_header('Content-Type', 'video/quicktime')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        return super().do_GET()
    
    def do_POST(self):
        global pending_clips, bot_instance, registered_users, video_interactions
        
        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')
        
        if self.path == '/api/login':
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                password = data.get('password', '')
                
                for user_id, user_data in registered_users.items():
                    if user_data['password'] == password:
                        login_data = {
                            'id': user_id,
                            'username': user_data['username'],
                            'display_name': user_data['display_name'],
                            'avatar_url': user_data['avatar_url']
                        }
                        if bot_is_online and bot_instance and hasattr(bot_instance, 'log_login'):
                            try:
                                future = asyncio.run_coroutine_threadsafe(
                                    bot_instance.log_login(login_data, "Pagina Web"),
                                    bot_instance.loop
                                )
                                future.result(timeout=5)
                            except Exception as e:
                                print(f"Error logging login: {e}")
                                add_to_queue('logins', {'user': login_data, 'server': 'Pagina Web'})
                        else:
                            add_to_queue('logins', {'user': login_data, 'server': 'Pagina Web'})
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'user': {
                                'id': user_id,
                                'username': user_data['username'],
                                'display_name': user_data['display_name'],
                                'avatar_url': user_data['avatar_url'],
                                'likes': user_data.get('likes', []),
                                'dislikes': user_data.get('dislikes', []),
                                'favorites': user_data.get('favorites', [])
                            }
                        }).encode())
                        return
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Contraseña incorrecta'
                }).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
                return
        
        if self.path == '/api/like':
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                user_id = data.get('user_id')
                clip_id = data.get('clip_id')
                
                if user_id in registered_users:
                    user = registered_users[user_id]
                    
                    if clip_id in user.get('dislikes', []):
                        user['dislikes'].remove(clip_id)
                        for clip in approved_clips:
                            if clip['id'] == clip_id:
                                clip['dislikes'] = max(0, clip.get('dislikes', 0) - 1)
                    
                    if clip_id not in user.get('likes', []):
                        if 'likes' not in user:
                            user['likes'] = []
                        user['likes'].append(clip_id)
                        for clip in approved_clips:
                            if clip['id'] == clip_id:
                                clip['likes'] = clip.get('likes', 0) + 1
                                if bot_is_online and bot_instance and hasattr(bot_instance, 'log_like'):
                                    try:
                                        future = asyncio.run_coroutine_threadsafe(
                                            bot_instance.log_like(user, clip),
                                            bot_instance.loop
                                        )
                                        future.result(timeout=5)
                                    except Exception as e:
                                        print(f"Error logging like: {e}")
                                        add_to_queue('likes', {'user': user, 'clip': clip})
                                else:
                                    add_to_queue('likes', {'user': user, 'clip': clip})
                    
                    save_users_data()
                    save_clips_data()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    return
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Usuario no encontrado'}).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
                return
        
        if self.path == '/api/dislike':
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                user_id = data.get('user_id')
                clip_id = data.get('clip_id')
                
                if user_id in registered_users:
                    user = registered_users[user_id]
                    
                    if clip_id in user.get('likes', []):
                        user['likes'].remove(clip_id)
                        for clip in approved_clips:
                            if clip['id'] == clip_id:
                                clip['likes'] = max(0, clip.get('likes', 0) - 1)
                    
                    if clip_id not in user.get('dislikes', []):
                        if 'dislikes' not in user:
                            user['dislikes'] = []
                        user['dislikes'].append(clip_id)
                        for clip in approved_clips:
                            if clip['id'] == clip_id:
                                clip['dislikes'] = clip.get('dislikes', 0) + 1
                                if bot_is_online and bot_instance and hasattr(bot_instance, 'log_dislike'):
                                    try:
                                        future = asyncio.run_coroutine_threadsafe(
                                            bot_instance.log_dislike(user, clip),
                                            bot_instance.loop
                                        )
                                        future.result(timeout=5)
                                    except Exception as e:
                                        print(f"Error logging dislike: {e}")
                                        add_to_queue('dislikes', {'user': user, 'clip': clip})
                                else:
                                    add_to_queue('dislikes', {'user': user, 'clip': clip})
                    
                    save_users_data()
                    save_clips_data()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    return
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Usuario no encontrado'}).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
                return
        
        if self.path == '/api/favorite':
            try:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                user_id = data.get('user_id')
                clip_id = data.get('clip_id')
                
                if user_id in registered_users:
                    user = registered_users[user_id]
                    
                    if clip_id not in user.get('favorites', []):
                        if 'favorites' not in user:
                            user['favorites'] = []
                        user['favorites'].append(clip_id)
                        save_users_data()
                        
                        for clip in approved_clips:
                            if clip['id'] == clip_id:
                                if bot_is_online and bot_instance:
                                    try:
                                        if hasattr(bot_instance, 'log_favorite'):
                                            future = asyncio.run_coroutine_threadsafe(
                                                bot_instance.log_favorite(user, clip),
                                                bot_instance.loop
                                            )
                                            future.result(timeout=5)
                                        if hasattr(bot_instance, 'send_favorite_video'):
                                            future = asyncio.run_coroutine_threadsafe(
                                                bot_instance.send_favorite_video(user_id, clip),
                                                bot_instance.loop
                                            )
                                            future.result(timeout=10)
                                    except Exception as e:
                                        print(f"Error with favorite: {e}")
                                        add_to_queue('favorites', {'user': user, 'clip': clip})
                                else:
                                    add_to_queue('favorites', {'user': user, 'clip': clip})
                                break
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                    return
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Usuario no encontrado'}).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
                return
        
        if self.path == '/api/upload':
            try:
                if 'multipart/form-data' in content_type:
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST',
                                 'CONTENT_TYPE': content_type}
                    )
                    
                    username = form.getvalue('username', '')
                    title = form.getvalue('title', '')
                    category = form.getvalue('category', '')
                    user_id = form.getvalue('user_id', '')
                    
                    avatar_url = ''
                    if user_id and user_id in registered_users:
                        avatar_url = registered_users[user_id].get('avatar_url', '')
                    
                    user_ip = self.get_client_ip()
                    
                    video_item = form['video']
                    if video_item.file:
                        clip_id = str(uuid.uuid4())[:8]
                        
                        original_filename = video_item.filename
                        ext = os.path.splitext(original_filename)[1].lower()
                        if ext not in ['.mp4', '.webm', '.mov']:
                            ext = '.mp4'
                        
                        filename = f"{clip_id}{ext}"
                        filepath = os.path.join(UPLOADS_DIR, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(video_item.file.read())
                        
                        clip_data = {
                            'id': clip_id,
                            'username': username,
                            'title': title,
                            'category': category,
                            'filename': filename,
                            'avatar_url': avatar_url,
                            'user_id': user_id,
                            'user_ip': user_ip,
                            'uploaded_at': time.time()
                        }
                        
                        pending_clips[clip_id] = clip_data
                        
                        sent_to_discord = False
                        queued = False
                        
                        if bot_is_online and bot_instance and hasattr(bot_instance, 'send_clip_for_review'):
                            try:
                                future = asyncio.run_coroutine_threadsafe(
                                    bot_instance.send_clip_for_review(clip_data),
                                    bot_instance.loop
                                )
                                future.result(timeout=10)
                                sent_to_discord = True
                            except Exception as e:
                                print(f"Error sending to Discord: {e}")
                                add_to_queue('clips', clip_data)
                                queued = True
                        else:
                            add_to_queue('clips', clip_data)
                            queued = True
                            print(f"Bot offline - Clip {clip_id} added to queue")
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'message': 'Clip enviado para revision' if sent_to_discord else 'Clip guardado en cola (bot offline)',
                            'clip_id': clip_id,
                            'queued': queued
                        }).encode())
                        return
                
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Invalid request'}).encode())
                
            except Exception as e:
                print(f"Upload error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
            return
        
        self.send_response(404)
        self.end_headers()

def start_bot():
    token = os.environ.get('REWIND_BOT_TOKEN')
    if token:
        print("Iniciando bot de Discord...")
        run_discord_bot()
    else:
        print("Bot de Discord no iniciado - REWIND_BOT_TOKEN no configurado")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    server = HTTPServer(('0.0.0.0', 5000), Handler)
    print('Servidor corriendo en puerto 5000')
    server.serve_forever()
