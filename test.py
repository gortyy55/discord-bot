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
   Codeactivation = discord.ui.TextInput(label="Vote Code du Ticket", placeholder="eg. LMQ7E", required = True, style = discord.TextStyle.short,max_length=5)
   name = discord.ui.TextInput(label="Nom Prenom", placeholder="eg. Hamid Pettard", required = True, style = discord.TextStyle.short)
   ticket = discord.ui.TextInput(label="les 5 chiffres du ticket", placeholder="eg. 12345", required= True, style=discord.TextStyle.short,max_length=5)



   async def on_submit(self, interaction: discord.Interaction):
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
        else:
            update_query = "UPDATE codes SET nbrTickets = nbrTickets - 1 WHERE code = %s"
            cursor.execute(update_query, (self.Codeactivation.value,))
            db.commit()
            await interaction.response.send_message("Votre ticket a été enregistré avec succès.")

    else:
        # If the code is invalid, send an error message
        await interaction.response.send_message("Code d'activation invalide. Ticket non enregistré.")


@client.tree.command(name="ticket", description="un ticket")
async def ticket(interaction: discord.Interaction):
   await interaction.response.send_modal(TicketModel())


 

#generer un code d'actiovation d'un ticket pour celui qui paye
@client.command()
async def generate(ctx , number: int=None):
     if number == None :
      await ctx.send("merci de rajouter le nombre de tickets apres la commande")
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
        await ctx.send(f"Code {code} valide.")
    else:
        await ctx.send(f"Code {code} non valide.")
     
    


async def main():
    async with client:
        await client.start("")

asyncio.run(main())