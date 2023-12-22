from nextcord.ext import commands
import nextcord
from nextcord import ButtonStyle
import asyncio
import json

serverid = server_id

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "tickets_config.json"
        self.tickets_data = {}

        self.load_data()

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.tickets_data = json.load(f)
        except FileNotFoundError:
            pass

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.tickets_data, f)

    @nextcord.slash_command(
        name="ticket",
        description="Abre um novo ticket.",
        guild_ids=[serverid]
    )
    async def ticket(self, interaction: nextcord.Interaction):
        self.load_data()
        category_id = self.tickets_data.get("category_id")
        ticket_channel_id = self.tickets_data.get("ticket_channel_id")

        if not category_id or not ticket_channel_id:
            embed = nextcord.Embed(
                description=f'A categoria ou o canal para os tickets não está configurada. Use o comando `/ticketconfig` para configurar.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        existing_ticket = next((channel for channel in interaction.guild.text_channels if channel.category_id == category_id and f'ticket-{interaction.user.name}' == channel.name), None)

        if existing_ticket:
            embed = nextcord.Embed(
                description=f'Você já possui um ticket aberto em: <#{existing_ticket.id}>.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        if interaction.channel.id != ticket_channel_id:
            embed = nextcord.Embed(
                description=f'Você só pode criar um ticket no canal correto: <#{ticket_channel_id}>.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        category = interaction.guild.get_channel(category_id)
        ticket_channel = await category.create_text_channel(f'ticket-{interaction.user.name}', overwrites={
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)
        })

        self.tickets_data[ticket_channel.id] = interaction.user.id
        self.save_data()

        embed = nextcord.Embed(
            title=f'Ticket - {interaction.user.name}',
            description=f'Olá {interaction.user.mention}, sua solicitação foi aberta, aguarde o atendimento.',
            color=nextcord.Color.green()
        )

        async def on_fechar_ticket(interaction: nextcord.Interaction):
            ticket_owner_id = self.tickets_data.get(ticket_channel.id)
            if ticket_owner_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                await ticket_channel.delete()
            else:
                embed = nextcord.Embed(
                    description=f'Você não tem permissão para fechar este ticket.',
                    color=nextcord.Color.red()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()

        fechar_ticket = nextcord.ui.Button(style=ButtonStyle.danger, label="Fechar Ticket")
        fechar_ticket.callback = on_fechar_ticket

        view = nextcord.ui.View()
        view.add_item(fechar_ticket)

        message = await ticket_channel.send(embed=embed, view=view)
        view.message = message
        embed = nextcord.Embed(
            description=f'Um novo ticket foi aberto em: <#{ticket_channel.id}>.',
            color=nextcord.Color.green()
        )
        mensagem = await interaction.send(embed=embed, ephemeral=True)
        await asyncio.sleep(5)
        await mensagem.delete()

def setup(bot):
    bot.add_cog(Tickets(bot))
