import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
from sqlalchemy import Column, Integer, String,ForeignKey
from models import User, WishLists

engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

with open("token.txt","r") as f:
    token = f.read()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.',intents=intents)
"""
def user_id_in_ids(user_id,ids):
    if len(ids) > 0:
        ids = ids[0]
    for id_ in ids:
        print(id_)
        if user_id == id_:
            return True
    return False
"""

class AddWishView(discord.ui.View):
    def __init__(self,wish_reference,content):
        super().__init__()
        self.wish = wish_reference
        self.content = content
        self.button_reference = None
        self.wish_check_mark_dict = {True: "✔️",False:"❌"}
        self.wish_check_mark_style = {True: discord.ButtonStyle.success,
                                      False: discord.ButtonStyle.danger}
        self.create_check_mark_button()
    def create_check_mark_button(self):
        label = f"ID: {self.wish.id} - {self.wish_check_mark_dict[self.wish.check_mark]}"
        button = discord.ui.Button(label=label, style=self.wish_check_mark_style[self.wish.check_mark])
        self.button_reference = button

        async def callback(interaction: discord.Interaction, b=button, w=self.wish):
            if w.check_mark == True:
                w.check_mark = False
            else:
                w.check_mark = True
            session.commit()
            await self.update(interaction,w,b)

        button.callback = callback
        self.add_item(button)


    async def update(self,interaction,wish,button):
        self.remove_item(button)
        embed = discord.Embed(
            title=f"Adding a new wish for {interaction.user.name}",
            color=discord.Color.brand_green()
        )
        title = wish.title + f" - {self.wish_check_mark_dict[wish.check_mark]}"
        embed.add_field(name=title, value=self.content, inline=False)
        self.create_check_mark_button()
        await interaction.response.edit_message(embed=embed,view=self)
class PageView(discord.ui.View):
    def __init__(self,user_id):
        super().__init__()
        self.page = 5
        begin = 0
        end = 0
        self.wish_buttons = []
        self.user_wishes = session.query(WishLists).filter_by(user_id=user_id).all()
        self.wish_check_mark_dict = {True: ":white_check_mark:", False: ":x:"}
        self.wish_check_mark_style = {True: discord.ButtonStyle.success,
                                      False: discord.ButtonStyle.danger}

        self.right_button_reference = discord.ui.Button(label="▶️",style=discord.ButtonStyle.secondary)
        self.right_button_reference.callback = self.right_button

        self.left_button_reference = discord.ui.Button(label="◀️",style=discord.ButtonStyle.secondary)
        self.left_button_reference.callback = self.left_button

        self.add_item(self.left_button_reference)
        self.add_item(self.right_button_reference)
        # This if statements are used for disabling the buttons
        if self.page == 5:
            self.left_button_reference.disabled = True
        else:
            self.left_button_reference.disabled = False

        if self.page >= len(self.user_wishes):
            self.right_button_reference.disabled = True

        if len(self.user_wishes) > 5:
            end = 5
        else:
            end = len(self.user_wishes)
        self.create_buttons(user_wishes=self.user_wishes[begin:end])
    async def left_button(self,interaction:discord.Interaction):
        embed = discord.Embed(
            title=f"{interaction.user.name}'s wishes",
            color=discord.Color.brand_green()
        )
        user_id = str(interaction.user.id)
        self.user_wishes = session.query(WishLists).filter_by(user_id=user_id).all()
        #print(f'page: {self.page}')

        self.page -= 5
        self.left_button_reference.disabled = False
        if len(self.user_wishes) < 5:
            user_wishes = self.user_wishes[0:len(self.user_wishes)]
        else:
            print(f"user_wishes[{self.page-5}:{self.page}]")
            user_wishes = self.user_wishes[self.page-5:self.page]
        for wish in user_wishes:
            check_mark = self.wish_check_mark_dict[wish.check_mark]
            embed.add_field(name=f"ID: {wish.id} {wish.title} - {check_mark}",value=wish.description,inline=False)
        self.create_buttons(user_wishes=user_wishes)
        await interaction.response.edit_message(embed=embed,view=self)

    async def right_button(self,interaction:discord.Interaction):
        embed = discord.Embed(
            title=f"{interaction.user.name}'s wishes",
            color=discord.Color.brand_green()
        )
        user_id = str(interaction.user.id)
        self.user_wishes = session.query(WishLists).filter_by(user_id=user_id).all()
        #print(f'page: {self.page}')

        self.page += 5
        #print(len(user_wishes),self.page)
        if len(self.user_wishes) < self.page:
            user_wishes = self.user_wishes[self.page-5:len(self.user_wishes)]
        else:
            user_wishes = self.user_wishes[self.page-5:self.page]
        for wish in user_wishes:
            check_mark = self.wish_check_mark_dict[wish.check_mark]
            embed.add_field(name=f"ID: {wish.id} {wish.title} - {check_mark}",value=wish.description,inline=False)
        #print(f"wishes: {user_wishes}")
        self.create_buttons(user_wishes=user_wishes)
        await interaction.response.edit_message(embed=embed,view=self)
    async def update(self,user_wishes,interaction,view):

        embed = discord.Embed(
            title=f"{interaction.user.name}'s wishes",
            color=discord.Color.brand_green()
        )
        for wish in user_wishes:
            check_mark = self.wish_check_mark_dict[wish.check_mark]
            embed.add_field(name=f"ID: {wish.id} {wish.title} - {check_mark}", value=wish.description, inline=False)
        await interaction.response.edit_message(embed=embed,view=view)
    def create_buttons(self,user_wishes):
        # For disabling the buttons (the function is not properly named
        # for this, but I didn't want to change its name now)
        if self.page == 5:
            self.left_button_reference.disabled = True
        else:
            self.left_button_reference.disabled = False
        if self.page >= len(self.user_wishes):
            #print(f"self.page: {self.page} - self.user_wishes: {self.user_wishes}\nDisabling the right button.")
            self.right_button_reference.disabled = True
        else:
            print("Enabling the right button.")
            self.right_button_reference.disabled = False

        if self.wish_buttons != []:
            self.remove_wish_buttons()
        check_mark_dict = {True: "✔️",False:"❌"}
        print(user_wishes)
        for wish in user_wishes:
            emoji = check_mark_dict[wish.check_mark]
            label = f"ID: {wish.id} - {emoji}"

            button = discord.ui.Button(label=label,style=self.wish_check_mark_style[wish.check_mark])
            async def callback(interaction:discord.Interaction, b=button,w=wish):
                if w.check_mark == True:
                    w.check_mark = False
                else:
                    w.check_mark = True
                session.commit()
                self.remove_wish_buttons()
                self.create_buttons(user_wishes)
                await self.update(user_wishes, interaction,self)

                #await interaction.response.send_message(f"You clicked on wish {w.id}")
            button.callback = callback
            self.wish_buttons.append(button)
            self.add_item(button)
    def remove_wish_buttons(self):
        for button in self.wish_buttons:
            self.remove_item(button)
        self.wish_buttons.clear()


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is ready.\nBot id: {bot.user.id}")
@bot.tree.command(name="add-a-wish",description="Adds a wish to the database")
@app_commands.describe(title="title",content="content")
async def add_a_wish(interaction: discord.Interaction,title: str,content: str):
    existing_user = session.query(User).filter_by(user_id=str(interaction.user.id)).first()
    print(existing_user)
    if not existing_user: # Adds the user to the database in case he never interacted with the bot.
        print("adding user")
        new_user = User(user_id=str(interaction.user.id),user_name=interaction.user.name)
        session.add(new_user)
        session.commit()

    new_wish = WishLists(user_id=str(interaction.user.id),title=title,description=content,check_mark=False) # The actual wish class that is added to the database
    session.add(new_wish)
    session.commit()
    embed = discord.Embed(
        title=f"Adding a new wish for {interaction.user.name}",
        color=discord.Color.brand_green()
    )
    embed.add_field(name=title + " - ❌",value=content,inline=False)
    view = AddWishView(wish_reference=new_wish,content=content)
    await interaction.response.send_message(embed=embed,view=view)
@bot.tree.command(name="my-wishes",description="Shows all of your wishes.")
async def my_wishes(interaction:discord.Interaction):
    user_id = str(interaction.user.id)
    user_wishes = session.query(WishLists).filter_by(user_id=user_id).all()
    page = 5
    if len(user_wishes) < page:
        page = len(user_wishes)
    user_wishes = user_wishes[0:page]
    embed = discord.Embed(
        title=f"{interaction.user.name}'s wishes",
        color=discord.Color.brand_green()

    )
    for wish in user_wishes:
        wish_check_mark_dict = {True:":white_check_mark:",False:":x:"}
        check_mark = wish_check_mark_dict[wish.check_mark]
        embed.add_field(name=f"ID: {wish.id} {wish.title} - {check_mark}",value=wish.description,inline=False)
    view = PageView(user_id)
    await interaction.response.send_message(embed=embed,view=view)
@bot.tree.command(name="delete-wish",description="Deletes a wish specified by its ID.")
@app_commands.describe(id="ID")
async def delete_wish(interaction:discord.Interaction,id: str):
    user_id = str(interaction.user.id)
    wish_to_delete = session.query(WishLists).filter(WishLists.id == id).first()
    if wish_to_delete == None:
        await interaction.response.send_message("You can't delete a wish that doesn't exist.")
        return
    if wish_to_delete.user_id != user_id:
        await interaction.response.send_message("You can't delete a wish that isn't yours.")
        return
    session.delete(wish_to_delete)
    session.commit()
    await interaction.response.send_message(f"You successfully deleted a wish with the ID: {id}")
@bot.tree.command(name="edit-a-wish",description="edits an already made wish.")
@app_commands.describe(id="ID",title="title",content="content",checkmark="check mark")
async def edit_a_wish(interaction:discord.Interaction,id: str, title: str = "optional", content: str = "optional", checkmark: bool = False):
    user_id = str(interaction.user.id)
    wish = session.query(WishLists).filter(WishLists.id == id).first()
    if wish.user_id != user_id:
        await interaction.response.send_message("You can't edit a wish that isn't yours.")
        return
    if title == 'optional':
        title = wish.title
    if content == 'optional':
        content = wish.description
    wish.title = title
    wish.description = content
    wish.check_mark = checkmark
    session.commit()

    check_mark_dict = {True: "✔️", False: "❌"}

    embed = discord.Embed(
        title=f"Editing a wish with the ID {wish.id} for {interaction.user.name}",
        color=discord.Color.brand_green()
    )
    embed.add_field(name=title + f" - {check_mark_dict[wish.check_mark]}",value=content,inline=False)
    view = AddWishView(wish_reference=wish,content=content)
    await interaction.response.send_message(embed=embed,view=view)

bot.run(token)