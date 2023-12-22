from nextcord.ext import commands
import nextcord
from nextcord.ui import View, Button
from nextcord import ButtonStyle
import json
import os
import asyncio
from typing import Optional

serverid = server_id

class Configs(commands.Cog):
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
    
    def get_ticket_channel(self, guild: nextcord.Guild) -> Optional[nextcord.TextChannel]:
        channel_id = self.tickets_data.get("ticket_channel_id")
        return guild.get_channel(channel_id)


    async def create_ticket_category(self, interaction: nextcord.Interaction):
        category = await interaction.guild.create_category("NeoTicket")

        await category.set_permissions(interaction.guild.default_role, read_messages=False)
        await category.set_permissions(interaction.guild.me, read_messages=True)

        self.tickets_data["category_id"] = category.id
        self.save_data()

        return category

    @nextcord.slash_command(
        name="ticketconfig",
        description="Configura a categoria onde os tickets serão criados.",
        guild_ids=[serverid]
    )
    async def ticketconfig(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = nextcord.Embed(
                description=f'Você não tem permissão para executar este comando.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        criar_button = Button(style=ButtonStyle.blurple, label="Criar")
        escolher_button = Button(style=ButtonStyle.blurple, label="Escolher")
        deletar_button = Button(style=ButtonStyle.red, label="Deletar")
        mais_button = Button(style=ButtonStyle.green, label="Mais")

        criar_button.callback = self.on_criar_categoria
        escolher_button.callback = self.on_escolher_categoria
        deletar_button.callback = self.on_deletar_categoria
        mais_button.callback = self.on_mais_categoria

        view = View()
        view.add_item(criar_button)
        view.add_item(escolher_button)
        view.add_item(deletar_button)
        view.add_item(mais_button)

        category_id = self.tickets_data.get("category_id")
        category = interaction.guild.get_channel(category_id)
        if category_id:
            try:
                embed = nextcord.Embed(
                    title=f'NeoTicket - Categoria',
                    description=f'Configure aqui a categoria onde os tickets serão criados!\nCategoria atual: {category.mention}',
                    color=nextcord.Color.green()
                )
            except:
                    embed = nextcord.Embed(
                    title=f'NeoTicket - Categoria',
                    description=f'Configure aqui a categoria onde os tickets serão criados!\nCategoria atual: Desconfigurado',
                    color=nextcord.Color.green()
                )
        else:
            embed = nextcord.Embed(
                title=f'NeoTicket - Categoria',
                description=f'Configure aqui a categoria onde os tickets serão criados!\nCategoria atual: Desconfigurado',
                color=nextcord.Color.green()
            )
        self.original_message = await interaction.send(embed=embed, view=view, ephemeral=True)
        view.message = self.original_message
        await asyncio.sleep(30)
        await self.original_message.delete()

    async def on_criar_categoria(self, interaction: nextcord.Interaction):
        category_id = self.tickets_data.get("category_id")
        if category_id:
            category = interaction.guild.get_channel(category_id)
            if category:
                embed = nextcord.Embed(
                    description=f'A categoria já está configurada para os tickets.',
                    color=nextcord.Color.red()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
                return
            
        category = await self.create_ticket_category(interaction)
        embed = nextcord.Embed(
            description=f'Categoria criada com sucesso! Todos os tickets serão criados na categoria NeoTicket.',
            color=nextcord.Color.green()
        )
        mensagem = await interaction.send(embed=embed, ephemeral=True)
        await asyncio.sleep(5)
        await mensagem.delete()
    
    async def on_escolher_categoria(self, interaction: nextcord.Interaction):
        category_id = self.tickets_data.get("category_id")
        if category_id:
            category = interaction.guild.get_channel(category_id)
            if category:
                embed = nextcord.Embed(
                    description=f'A categoria já está configurada para os tickets.',
                    color=nextcord.Color.red()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
                return
        
        embed = nextcord.Embed(
            description=f'Digite o nome da categoria que deseja que os tickets sejam criados:',
            color=nextcord.Color.yellow()
        )
        mensagem = await interaction.send(embed=embed, ephemeral=True)

        try:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                timeout=30.0
            )

            category_name = response.content
            await response.delete()  
            await mensagem.delete()  

            category = nextcord.utils.get(interaction.guild.categories, name=category_name)
            if category:
                self.tickets_data["category_id"] = category.id
                self.save_data()
                await interaction.followup.send(content=f"Categoria configurada para: {category.mention}.", ephemeral=True)
            else:
                new_category = await interaction.guild.create_category(category_name)
                self.tickets_data["category_id"] = new_category.id
                self.save_data()
                mensagem = await interaction.followup.send(content=f"Categoria criada e configurada para: {new_category}.", ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()

        except asyncio.TimeoutError:
            embed = nextcord.Embed(
                description=f'Tempo limite expirado, configuração cancelada.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

    
    async def on_deletar_categoria(self, interaction: nextcord.Interaction):
        category_id = self.tickets_data.get("category_id")
        if not category_id:
            embed = nextcord.Embed(
                description=f'A categoria ainda não está configurada.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        category = interaction.guild.get_channel(category_id)
        if not category:
            embed = nextcord.Embed(
                description=f'A categoria configurada não foi encontrada.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        confirmar_button = Button(style=ButtonStyle.green, label="Sim")
        cancelar_button = Button(style=ButtonStyle.red, label="Não")

        confirmar_button.callback = self.on_confirmar_deletar_categoria
        cancelar_button.callback = self.on_cancelar_deletar_categoria

        view = View()
        view.add_item(confirmar_button)
        view.add_item(cancelar_button)

        embed = nextcord.Embed(
            description=f'Tem certeza que deseja deletar esta categoria?\nIsso também excluirá todos os tickets associados.',
            color=nextcord.Color.yellow()
        )
        message = await interaction.send(embed=embed, view=view, ephemeral=True)

        self.message_to_delete = message

        self.category_to_delete = category

    async def on_confirmar_deletar_categoria(self, interaction: nextcord.Interaction):
        try:
            for channel in self.category_to_delete.channels:
                await channel.delete()

            await self.category_to_delete.delete()

            self.tickets_data.pop("category_id")
            self.save_data()

            await self.message_to_delete.delete()

            embed = nextcord.Embed(
                description=f'Categoria e tickets associados deletados com sucesso.',
                color=nextcord.Color.green()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
        except Exception as e:
            embed = nextcord.Embed(
                description=f'Ocorreu um erro ao deletar a categoria e os tickets: {e}',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()

    async def on_cancelar_deletar_categoria(self, interaction: nextcord.Interaction):
        await self.message_to_delete.delete()
        embed = nextcord.Embed(
            description=f'Ação cancelada. A categoria não será deletada.',
            color=nextcord.Color.red()
        )
        mensagem = await interaction.send(embed=embed, ephemeral=True)
        await asyncio.sleep(5)
        await mensagem.delete()

    async def on_mais_categoria(self, interaction: nextcord.Interaction):
        criar_button = Button(style=ButtonStyle.blurple, label="Criar")
        escolher_button = Button(style=ButtonStyle.blurple, label="Escolher")
        deletar_button = Button(style=ButtonStyle.red, label="Deletar")

        criar_button.callback = self.on_criar_canal
        escolher_button.callback = self.on_escolher_canal
        deletar_button.callback = self.on_deletar_canal

        view = View()
        view.add_item(criar_button)
        view.add_item(escolher_button)
        view.add_item(deletar_button)

        ticket_channel_id = self.tickets_data.get("ticket_channel_id")
        if ticket_channel_id:
            embed = nextcord.Embed(
                title=f'NeoTicket - Canal',
                description=f'Configure aqui o canal onde os usuários poderão criar os tickets!\nCanal atual: <#{ticket_channel_id}>',
                color=nextcord.Color.green()
            )
        else:
            embed = nextcord.Embed(
                title=f'NeoTicket - Canal',
                description=f'Configure aqui o canal onde os usuários poderão criar os tickets!\nCanal atual: Desconfigurado',
                color=nextcord.Color.green()
            )
        message = await interaction.send(embed=embed, view=view, ephemeral=True)
        view.message = message
        await asyncio.sleep(5)
        await message.delete()
        
        await self.original_message.delete()


    async def on_criar_canal(self, interaction: nextcord.Interaction):
        ticket_channel_id = self.tickets_data.get("ticket_channel_id")
        if ticket_channel_id:
            embed = nextcord.Embed(
                description=f'O canal para os usuários criarem tickets já está configurado.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        category_id = self.tickets_data.get("category_id")
        if category_id:
            category = interaction.guild.get_channel(category_id)
            if category:
                ticket_channel = await category.create_text_channel("NeoTicket", overwrites={
                    interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True)
                })

                self.tickets_data["ticket_channel_id"] = ticket_channel.id
                self.save_data()

                embed = nextcord.Embed(
                    description=f'Canal para criar tickets criado com sucesso em: {ticket_channel.mention}.',
                    color=nextcord.Color.green()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
            else:
                embed = nextcord.Embed(
                    description=f'A categoria configurada não foi encontrada.',
                    color=nextcord.Color.red()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
        else:
            embed = nextcord.Embed(
                description=f'A categoria para os tickets ainda não está configurada. Use o comando `/ticketconfig` para configurar a categoria.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()


    async def on_escolher_canal(self, interaction: nextcord.Interaction):
        ticket_channel_id = self.tickets_data.get("ticket_channel_id")
        if ticket_channel_id:
            embed = nextcord.Embed(
                description=f'O canal para os usuários criarem tickets já está configurado.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return
        
        embed = nextcord.Embed(
            description=f'Digite o nome do canal que deseja configurar para os usuários criarem tickets:',
            color=nextcord.Color.yellow()
        )
        message = await interaction.send(embed=embed, ephemeral=True)

        try:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                timeout=30.0
            )

            channel_name = response.content
            await response.delete()  

            category_id = self.tickets_data.get("category_id")
            category = interaction.guild.get_channel(category_id)

            if not category:
                embed = nextcord.Embed(
                    description=f'A categoria ainda não está configurada. Configure a categoria antes de escolher um canal.',
                    color=nextcord.Color.red()
                )
                await message.delete()
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
                return

            selected_channel = next((channel for channel in category.channels if channel.name == channel_name), None)

            if selected_channel:
                self.tickets_data["ticket_channel_id"] = selected_channel.id
                self.save_data()
                embed = nextcord.Embed(
                    description=f'Canal configurado para: {selected_channel.mention}.',
                    color=nextcord.Color.green()
                )
                await message.delete()
                mensagem = await interaction.followup.send(embed=embed, ephemeral=True)
                await asyncio.sleep(5)
                await mensagem.delete()
            else:
                embed = nextcord.Embed(
                    description=f'O canal não existe na categoria.',
                    color=nextcord.Color.red()
                )
                mensagem = await interaction.send(embed=embed, ephemeral=True)
                await message.delete()
                await asyncio.sleep(5)
                await mensagem.delete()

        except asyncio.TimeoutError:
            embed = nextcord.Embed(
                description=f'Tempo limite expirado, configuração cancelada.',
                color=nextcord.Color.red()
            )
            await message.delete()
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()

    async def on_deletar_canal(self, interaction: nextcord.Interaction):
        category_id = self.tickets_data.get("category_id")
        ticket_channel_id = self.tickets_data.get("ticket_channel_id")

        if not category_id or not ticket_channel_id:
            embed = nextcord.Embed(
                description=f'A categoria ou o canal ainda não estão configurados. Configure ambos antes de deletar.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return

        category = interaction.guild.get_channel(category_id)
        ticket_channel = interaction.guild.get_channel(ticket_channel_id)

        ''' if not category or not ticket_channel:
            embed = nextcord.Embed(
                description=f'A categoria ou o canal configurados não foram encontrados.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()
            return'''

        try:
            await ticket_channel.delete()
            self.tickets_data.pop("ticket_channel_id")
            self.save_data()

            embed = nextcord.Embed(
                description=f'Canal deletado com sucesso.',
                color=nextcord.Color.green()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()

        except Exception as e:
            self.tickets_data.pop("ticket_channel_id")
            self.save_data()
            embed = nextcord.Embed(
                description=f'O canal foi deletado ou não tenho permissões para deletá-lo, crie um novo.',
                color=nextcord.Color.red()
            )
            mensagem = await interaction.send(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await mensagem.delete()



def setup(bot):
    bot.add_cog(Configs(bot))
