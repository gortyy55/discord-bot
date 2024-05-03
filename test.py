import discord
from discord.ext import commands
import mysql.connector
import os
import asyncio

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

@client.event
async def on_ready():
    await client.tree.sync()
    print("started")


 
 




class TicketModel(discord.ui.Modal, title="Big Win Belgium"):
   name = discord.ui.TextInput(label="Nom Prenom", placeholder="eg. Hamid Pettard", required = True, style = discord.TextStyle.short)
   ticket = discord.ui.TextInput(label="les 5 chiffres du ticket", placeholder="eg. 12345", required= True, style=discord.TextStyle.short,max_length=5)



   async def on_submit(self, interaction: discord.Interaction):
     # Check if any of the required fields are empty

        if not self.name.value or not self.ticket.value:
            await interaction.response.send_message("Error: merci de bien remplir les 2 champs", ephemeral=True)
            return 
        

        await interaction.response.send_message("Votre Ticket a Bien etait enregistrer {username}")

        sql = "INSERT INTO participe (Nom, Numero) VALUES (%s, %s)"
        val = (self.name.value, self.ticket.value)
        cursor.execute(sql, val)
        db.commit()
 


@client.tree.command(name="ticket", description="un ticket")
async def ticket(interaction: discord.Interaction):
   await interaction.response.send_modal(TicketModel())


 


@client.command()
async def generate(ctx):
     # Set the required length
     length_of_string = 5
     sample_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
     # k is an argument which will set the length
     generated_string = ''.join(random.choices(sample_str, k = length_of_string))
     query = "INSERT INTO codes VALUES (%s)"
     cursor.execute(query, (generated_string,))
     db.commit()
     await ctx.send(generated_string)



@client.command()
async def check(ctx, code):
    # Check if the code exists in the database
    query = "SELECT * FROM codes WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    if result:
        await ctx.send(f"Code {code} valide.")
    else:
        await ctx.send(f"Code {code} non valide.")
     
    


async def main():
    async with client:
        await client.start("")

asyncio.run(main())