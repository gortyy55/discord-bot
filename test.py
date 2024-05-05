import discord
from discord.ext import commands
import mysql.connector
import os
import asyncio
import datetime

import random

db = mysql.connector.connect(
    host="",
    user="Gortyy",
    password="",
    database="Lotto"
)
cursor = db.cursor()
cursor2 = db.cursor()


client = commands.Bot(command_prefix="/", intents=discord.Intents.all())


#creates to a user a new channel with his name that only him can see and interact with
async def create_private_channel(interaction: discord.Interaction):
    author_name = interaction.user.name  # Get the ID of the user who pressed the button
    
    # Define the category ID
    category_id = 1236583155750797374  # ID of the category to create the channels in

    # Get the category object
    category = interaction.guild.get_channel(category_id)

    if not category:
        await interaction.response.send_message("Category not found.")
        return

    # Create a new channel with the user's ID
    user_channel_name = f"table-de-{author_name}"
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    new_channel = await interaction.guild.create_text_channel(name=user_channel_name, overwrites=overwrites, category=category)

    # Send a message confirming the creation of the channel
    await interaction.response.send_message(f"Channel '{user_channel_name}' created successfully. You can now write in it.",delete_after=10)

    return new_channel

async def create_private_channel_with_view(interaction: discord.Interaction):
    try:
        # Create the private channel
        new_channel = await create_private_channel(interaction)

        # Ensure the new channel is created before sending the view
        if new_channel:
            # Create the view
            view = SimpleView()
            button = discord.ui.Button(label="Demander une table", style=discord.ButtonStyle.success)
            view.add_item(button)
            
            # Send the view to the new channel
            await new_channel.send("Demander une table", view=view)
    except Exception as e:
        print(f"Error creating private channel with view: {e}")



async def ensure_button_view(channel):
    view = SimpleView2()
    await channel.send("Demander une Table", view=view)

async def ensure_menu_view(channel):
    view = SimpleView()
    await channel.send("Remplir un ticket", view=view)

@client.event
async def on_ready():
    await client.tree.sync()
    channel_id = 1236590341470158959  # ID of the channel where you want to display the button view
    channel = client.get_channel(channel_id)
    if channel:
        await ensure_button_view(channel)
    print("started")

#check if its the right channel for a command
async def is_channel(ctx):
  return ctx.channel.id == 1165232857023774811
 




class TicketModel(discord.ui.Modal, title="Big Win Belgium"):
   Codeactivation = discord.ui.TextInput(label="Votre Code du Ticket", placeholder="eg. LMQ7E", required = True, style = discord.TextStyle.short,max_length=5)
   name = discord.ui.TextInput(label="Nom Prenom", placeholder="eg. Hamid Pettard", required = True, style = discord.TextStyle.short)
   ticket = discord.ui.TextInput(label="les 5 chiffres du ticket", placeholder="eg. 12345", required= True, style=discord.TextStyle.short,max_length=5)



   async def on_submit(self, interaction: discord.Interaction):

    # Get the current date and time
    now = datetime.datetime.now()
    current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")

    # Check if any of the required fields are empty
    if not self.name.value or not self.Codeactivation.value or not self.ticket.value:
        await interaction.response.send_message("Error: Merci de bien remplir les 3 champs.", ephemeral=True)
        return 

    # Execute SQL query to check if the activation code is valid
    query = "SELECT * FROM codes WHERE code = %s"
    cursor.execute(query, (self.Codeactivation.value,))
    result = cursor.fetchone()

    if result:
        # If the code is valid, insert the participant's data into the database
        sql = "INSERT INTO participe (Nom, Numero) VALUES (%s, %s)"
        val = (self.name.value, self.ticket.value)
        cursor.execute(sql, val)
        db.commit()

        # Update or delete the code based on the number of available tickets
        if result[1] == 1:
            delete_query = "DELETE FROM codes WHERE code = %s"
            cursor.execute(delete_query, (self.Codeactivation.value,))
            db.commit()
            await interaction.response.send_message("Votre ticket a été enregistré avec succès.")

            # Send the filled digits with the date and time to the user in a private message
            
            user = interaction.user
            await user.send(f"Vous avez rempli les chiffres suivants: {self.ticket.value} le {current_datetime}")
        else:
            update_query = "UPDATE codes SET nbrTickets = nbrTickets - 1 WHERE code = %s"
            cursor.execute(update_query, (self.Codeactivation.value,))
            db.commit()

            # Send the filled digits with the date and time to the user in a private message
            user = interaction.user
            await user.send(f"Vous avez rempli les chiffres suivants: {self.ticket.value} le {current_datetime}")

    else:
        # If the code is invalid, send an error message
        await interaction.response.send_message("Code d'activation invalide. Ticket non enregistré.")


@client.tree.command(name="ticket", description="un ticket")
async def ticket(interaction: discord.Interaction):
   await interaction.response.send_modal(TicketModel())


 

#generer un code d'actiovation d'un ticket pour celui qui paye
@client.command()
@commands.check(is_channel)
async def generate(ctx , number: int=None):
     if number == None or number < 1 or number > 10 :
      await ctx.send("merci de rajouter le nombre de tickets apres la commande, (min 1 - max 10)")
      return
    
    
    # Set the required length
     length_of_string = 5
     sample_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
     # k is an argument which will set the length
     generated_string = ''.join(random.choices(sample_str, k = length_of_string))
     query = "INSERT INTO codes VALUES (%s,%s)"
     cursor.execute(query, (generated_string,number))
     db.commit()
     await ctx.send(generated_string)



#verifier si un code d'actiovation est valide ou non
@client.command()
async def check(ctx, code):
    # Check if the code exists in the database
    query = "SELECT * FROM codes WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    if result:
        await ctx.send(f"**{ctx.author.display_name} le Code {code} est valide. et il reste {result[1]} utilisations a ce code**")
    else:
        await ctx.send(f"{ctx.author.display_name} ce code n'es pas valide Code {code} non valide.")

class SimpleView(discord.ui.View):
    
    @discord.ui.button(label="remplir un ticket",style=discord.ButtonStyle.success)
    async def remplir(self, interaction : discord.Interaction, button : discord.Button):
       await interaction.response.send_modal(TicketModel())

class SimpleView2(discord.ui.View):
    
    @discord.ui.button(label="Demander une table", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction,button: discord.Button,):
       await create_private_channel_with_view(interaction)
       

@client.command()
async def button2(ctx):
   view = SimpleView2()
   await ctx.send("Choose an action:", view=view)


@client.command()
async def delete_all_channels(ctx):
    try:
        # Define the category ID
        category_id = 1236583155750797374  # ID of the category containing the channels to be deleted

        # Get the category object
        category = ctx.guild.get_channel(category_id)

        if not category:
            await ctx.send("Category not found.")
            return

        # Iterate over the channels in the category and delete them
        for channel in category.channels:
            await channel.delete()

        await ctx.send("All channels in the category have been deleted.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
async def clear_acceuil(ctx):
    try:
        # Get the channel object
        channel_id = 1236590341470158959  # ID of the channel to clear
        channel = client.get_channel(channel_id)

        if not channel:
            await ctx.send("Channel not found.")
            return

        # Delete all messages in the channel
        await channel.purge()

        await ctx.send("All messages in the channel have been cleared.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


async def main():
    async with client:
        await client.start("")

asyncio.run(main())