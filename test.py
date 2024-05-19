import discord
from discord.ext import commands
import mysql.connector
import os
import asyncio
import datetime
import random

db = mysql.connector.connect(
    host="46.105.28.192",
    user="Gortyy",
    password="Testtest",
    database="Lotto"
)
cursor = db.cursor()
cursor2 = db.cursor()

client = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# Création d'un nouveau canal privé pour un utilisateur
async def create_private_channel(interaction: discord.Interaction):
    author_name = interaction.user.name
    category_id = 1236583155750797374
    category = interaction.guild.get_channel(category_id)

    if not category:
        await interaction.response.send_message("Category not found.")
        return

    user_channel_name = f"🔖table-de-{author_name}"
    
    # Check if the channel already exists
    existing_channel = discord.utils.get(category.channels, name=user_channel_name)
    if existing_channel:
        await interaction.response.send_message(f"Channel '{user_channel_name}' already exists.", delete_after=10 , ephemeral=True)
        return existing_channel

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    new_channel = await interaction.guild.create_text_channel(name=user_channel_name, overwrites=overwrites, category=category)
    await interaction.response.send_message(f"Channel '{user_channel_name}' crée avec succès.", delete_after=10, ephemeral=True)
    return new_channel

async def create_private_channel_with_view(interaction: discord.Interaction):
    try:
        new_channel = await create_private_channel(interaction)
        if new_channel:
            view = SimpleView()
            await new_channel.send("Demander une table", view=view)
    except Exception as e:
        print(f"Error creating private channel with view: {e}")

async def ensure_button_view(channel):
    view = SimpleView2()
    await channel.send("Demander une Table", view=view)

async def ensure_menu_view(channel):
    view = SimpleView()
    await channel.send("Remplir un ticket", view=view)

async def ensure_admin_view(channel):
    view = AdminView()
    await channel.send("Vider Les Channels", view=view)

@client.event
async def on_ready():
    await client.tree.sync()
    channel_id = 1236590341470158959
    channel = client.get_channel(channel_id)
    if channel:
        await channel.purge()
        await ensure_button_view(channel)
    
    channel_id2 = 1236607661840138260
    channel2 = client.get_channel(channel_id2)
    if channel2:
        await channel2.purge()
        await ensure_admin_view(channel2)

    print("started")

# Vérifie si le message provient du bon canal
async def is_channel(ctx):
    return ctx.channel.id == 1236607661840138260

class CodesModel(discord.ui.Modal, title="Big Win Belgium Code Generateur"):
    nombrecodes = discord.ui.TextInput(label="Nombre d'utilisations du code", placeholder="eg. 1 - 10", required=True, style=discord.TextStyle.short, max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.nombrecodes.value:
            await interaction.response.send_message("Error: Merci de bien remplir le champ.", ephemeral=True, delete_after=10)
            return 
        
        try:
            number = int(self.nombrecodes.value)
            if number < 1 or number > 10:
                await interaction.response.send_message("Merci de saisir un nombre entre 1 et 10.", ephemeral=True, delete_after=10)
                return
            await generate2(interaction, number)
        except ValueError:
            await interaction.response.send_message("Merci de saisir un nombre valide.", ephemeral=True, delete_after=10)

class TicketModel(discord.ui.Modal, title="Big Win Belgium"):
    Codeactivation = discord.ui.TextInput(label="Votre Code du Ticket", placeholder="eg. LMQ7E", required=True, style=discord.TextStyle.short, max_length=5)
    name = discord.ui.TextInput(label="Nom Prenom", placeholder="eg. Hamid Pettard", required=True, style=discord.TextStyle.short)
    ticket = discord.ui.TextInput(label="les 5 chiffres du ticket", placeholder="eg. 12345", required=True, style=discord.TextStyle.short, max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        now = datetime.datetime.now()
        current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")

        if not self.name.value or not self.Codeactivation.value or not self.ticket.value:
            await interaction.response.send_message("Error: Merci de bien remplir les 3 champs.", ephemeral=True)
            return

        query = "SELECT * FROM codes WHERE code = %s"
        cursor.execute(query, (self.Codeactivation.value,))
        result = cursor.fetchone()

        if result:
            sql = "INSERT INTO participe (Nom, Numero) VALUES (%s, %s)"
            val = (self.name.value, self.ticket.value)
            cursor.execute(sql, val)
            db.commit()

            if result[1] == 1:
                delete_query = "DELETE FROM codes WHERE code = %s"
                cursor.execute(delete_query, (self.Codeactivation.value,))
                db.commit()
                await interaction.response.send_message("Votre ticket a été enregistré avec succès.", delete_after=10)
                user = interaction.user
                await user.send(f"Vous avez rempli les chiffres suivants: {self.ticket.value} le {current_datetime}")
            else:
                update_query = "UPDATE codes SET nbrTickets = nbrTickets - 1 WHERE code = %s"
                cursor.execute(update_query, (self.Codeactivation.value,))
                db.commit()
                await interaction.response.send_message("Votre ticket a été enregistré avec succès.", delete_after=10)
                user = interaction.user
                await user.send(f"Vous avez rempli les chiffres suivants: {self.ticket.value} le {current_datetime}")
        else:
            await interaction.response.send_message("Code d'activation invalide. Ticket non enregistré.", delete_after=10)

@client.tree.command(name="ticket", description="un ticket")
async def ticket(interaction: discord.Interaction):
    await interaction.response.send_modal(TicketModel())

@client.command()
@commands.check(is_channel)
async def generate(ctx, number: int = None):
    if number is None or number < 1 or number > 10:
        await ctx.send("Merci de rajouter le nombre de tickets après la commande, (min 1 - max 10)")
        return
    
    length_of_string = 5
    sample_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    generated_string = ''.join(random.choices(sample_str, k=length_of_string))
    query = "INSERT INTO codes (code, nbrTickets) VALUES (%s, %s)"
    cursor.execute(query, (generated_string, number))
    db.commit()
    await ctx.send(generated_string)

async def generate2(interaction, number: int):
    if number < 1 or number > 10:
        await interaction.response.send_message("Merci de rajouter le nombre de tickets après la commande, (min 1 - max 10)", ephemeral=True)
        return
    
    length_of_string = 5
    sample_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    generated_string = ''.join(random.choices(sample_str, k=length_of_string))
    query = "INSERT INTO codes (code, nbrTickets) VALUES (%s, %s)"
    cursor.execute(query, (generated_string, number))
    db.commit()
    await interaction.response.send_message(f"Code généré : {generated_string}", ephemeral=True)

@client.command()
async def check(ctx, code):
    query = "SELECT * FROM codes WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    if result:
        await ctx.send(f"**{ctx.author.display_name} le Code {code} est valide. Il reste {result[1]} utilisations à ce code**",)
    else:
        await ctx.send(f"{ctx.author.display_name} ce code n'est pas valide. Code {code} non valide.")

class SimpleView(discord.ui.View):
    @discord.ui.button(label="remplir un ticket", style=discord.ButtonStyle.success)
    async def remplir(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_modal(TicketModel())

class AdminView(discord.ui.View):
    @discord.ui.button(label="Vider les channels", style=discord.ButtonStyle.red)
    async def channelsdel(self, interaction: discord.Interaction, button: discord.Button):
        await delete_all_channels(interaction)
    
    @discord.ui.button(label="Generer un code", style=discord.ButtonStyle.blurple)
    async def generertickets(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_modal(CodesModel())
    
    @discord.ui.button(label="Générer Un Chiffre Gagnant", style=discord.ButtonStyle.green)
    async def generate_random_number_button(self, interaction: discord.Interaction, button: discord.Button):
        await generate_random_number(interaction)

class SimpleView2(discord.ui.View):
    @discord.ui.button(label="Demander une table", style=discord.ButtonStyle.success)
    async def create(self, interaction, button: discord.Button):
        await create_private_channel_with_view(interaction)

@client.command()
async def button2(ctx):
    view = SimpleView2()
    await ctx.send("Choose an action:", view=view)

@client.command()
@commands.check(is_channel)
async def delete_all_channels(ctx):
    try:
        category_id = 1236583155750797374
        category = ctx.guild.get_channel(category_id)

        if not category:
            await ctx.send("Category not found.")
            return

        for channel in category.channels:
            await channel.delete()

        await ctx.send("All channels in the category have been deleted.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
@commands.check(is_channel)  # Vérifie que la commande est exécutée dans le bon canal
async def generate_random_number(ctx):
    # Générer un nombre aléatoire entre 00001 et 99999
    random_number = random.randint(1, 99999)
    formatted_number = f"{random_number:05d}"  # Pour formater le nombre avec 5 chiffres

    # Récupérer le canal où afficher le nombre généré
    target_channel_id = 1241597088622448753
    target_channel = client.get_channel(target_channel_id)
    

    if target_channel:
        await target_channel.purge()
        await target_channel.send(f"Le Chiffre Gagnant est le : {formatted_number}")
    else:
        await ctx.send("Le canal cible n'a pas été trouvé.")

@client.command()
@commands.check(is_channel)
async def clear_acceuil(ctx):
    try:
        channel_id = 1236590341470158959
        channel = client.get_channel(channel_id)

        if not channel:
            await ctx.send("Channel not found.")
            return

        await channel.purge()
        await ctx.send("All messages in the channel have been cleared.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

async def main():
    async with client:
        await client.start("MTIzNTg1MjAyMzczMjM3NTU1Mw.GwWhPe.El0pyhm8SXNeT_PaECZ4lndy6q0RYxwKwpfSVM")

asyncio.run(main())
