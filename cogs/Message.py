import disnake
from disnake.ext import commands
from .module import REQ_database as Rdb
import random
import time
import json
import sqlite3

db = Rdb.DataBase

    
class Message(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_message(self, message):
        
        # Установка главных переменных
        user = message.author.id
        timeMessage = time.strftime('%H:%M', time.gmtime(round(time.time() + 36000)))
        # Проверка на ботовость того, кто отправил сообщение
        if message.author.bot:
            return
        else:
            db.Check(user_id=message.author.id, user_name=message.author.name).user()


        try:
            con = sqlite3.connect('../bots/database.db')
            cur = con.cursor()
            cur.execute(f"UPDATE channel_data SET count = count + 1 WHERE ID = {message.channel.id}")
            con.commit()
        except:
            pass

        # Проверка на упоминание пользователя и инкремент при правде
        mentioned = message.raw_mentions
        if (mentioned is not None):
            try:
                ment= message.raw_mentions[0]
                user_data = db.Info(user_id=user).user()
                if (user_data[5] < round(time.time())) and ment != user:
                    db.User(user_id=ment, value=1, column='mentions').upParam()
                    db.User(user_id=user, value=30).lockMent()
            except:
                pass
            

        # Проверка актуальности уровня
        userExpNow= db.Info(user_id=user).user()[3]
        userLvlNow= db.Info(user_id=user).user()[2]
        userLvl = db.Info().whatIsLvl(exp=userExpNow)
        # Загрузки конфигурацции
        with open(f'../bots/config/levels/{message.guild.id}.json') as f:
            level_config = json.load(f)
            rank = []
            for item in level_config:
                rank.append(item)
            f.close()

        if userLvl != userLvlNow:
            end = True
            s = []
            # Разбиваем ключи на массив связанных чисел, для проверки диапазона
            for item in level_config:
                s.append(item.split('-'))
            iser = []
            # Проверка диапазона по связанным ключам
            for item in s:
                try:
                    iser.append(int(item[0]) <= userLvl <= int(item[1]))
                except:
                    end = False
            # Выдача ролей
            if end:
                ti = 0
                for index, item in enumerate(iser):
                    if item:
                        ti = index
                        await message.author.add_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][0]))
                for index, item in enumerate(iser):
                    if index != ti:
                        await message.author.remove_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][0]))
            # if end:
            #     for index, tufa in enumerate(iser):
            #         if tufa and index == 0:
            #             await message.author.add_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][0]))
            #         elif tufa and index != 0:
            #             await message.author.add_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][1]))
            #         elif not tufa and index not in [0, len(rank)-1]:
            #             await message.author.remove_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][1]))
            #         else:
            #             await message.author.remove_roles(self.bot.get_guild(message.guild.id).get_role(level_config[rank[index]][0]))

            if message.author.id != 374061361606688788:
                embed = disnake.Embed(
                title=f'Изменение силы души у: \n``{message.author.name}`` | ``{message.author.nick}``',
                description=f'Сила души изменилась\n```с {userLvlNow} до {userLvl}```',
                colour=disnake.Color.dark_gold()
                )
                embed.set_thumbnail(url=message.author.avatar)
                db.User(column='lvl', user_id=user, value=userLvl).setParam()
                await self.bot.get_channel(992673176448417792).send(embed=embed)


        # Проверка таймера реакций
        if db.Bot(self).checkLock():
            return

        # Загрузка конфигов
        with open('../bots/config/message.json') as file:
            config = json.load(file)
        # Проверка на создателя
        if message.author.id != 374061361606688788:
            # Выпадения опыта ~30% и денег с шансом ~10%
            # Шанс выпадения шарда с шансом 0,005%
            valueRandom = random.randint(1, 1000)
            valuePupet = random.randint(1,5)
            if valueRandom <= config['exp']:  # Выпадение опыта ')
                db.Exp(user=user, value=valuePupet).add()
                db.Bot(value=10).lock()
                return
            if valueRandom <= config['money']:  # Выпадение денег
                val = random.randint(0, 1000)
                if val <= config['super_money']:
                    print(f'{timeMessage} | Выпали супер-деньги ({val}) | {message.author.global_name}')
                    db.Money(user=user, currency='shard', value=valuePupet).add()
                    return
                print(f'{timeMessage} | Выпали деньги ({valueRandom}) | {message.author.global_name}')
                db.Money(user=user, value=valuePupet).add()
                db.Bot(value=10).lock()
                return

        # Исключение частых символов
        simbol = '/.,&?!()'
        content = message.content
        for item in simbol:
            content = content.replace(item, '')

        # Проверка на разрешенный канал
        if message.guild is None:
            return
        file = open(f"../bots/acesses/{message.guild.id}.txt", mode='a+')
        file.seek(0)
        susc = []
        for item in file:
            susc.append(item.rstrip())
        file.close()

        # Проверка на канал в котором произошел ивент
        if str(message.channel.id) not in susc:
            return
        # простые слова-реакции
        file = open('../bots/React_text/Base_react_pony.txt', mode='r', encoding='utf-8')
        num = random.randint(1, 1000)
        mass_react = []
        for ent in file:
            mass_react.append(ent.rstrip())
        file.close()
        # Гифки
        file = open('../bots/content/Gif/base.txt', mode='r')
        gifs = []
        for item in file:
            gifs.append(item.rstrip())
        file.close()
        
        # Случайные реакции поняшки
        if num <= config['text_react_chance']:
            print(f"{timeMessage} | Случайный_ответ | {message.channel}")
            await message.channel.send(f"_{random.choice(mass_react)}_")
            db.Bot(value=config['text_react_timer']).lock()
            return
        if num <= config['emoji_react_chance']:
            print(f"{timeMessage} | Случайный_ответ_2 | {message.channel}")
            emoji = message.guild.emojis
            await message.channel.send(random.choice(emoji))
            db.Bot(value=config['emoji_react_timer']).lock()
            return
        if num <= config['reaction_react_chance']:
            print(f"{timeMessage} | Случайный_ответ_3 | {message.channel}")
            emoji = message.guild.emojis
            await message.add_reaction(random.choice(emoji))
            db.Bot(value=config['reaction_react_timer']).lock()
            return
        '''if num >= 198:
            print(f"{timeMessage} | Случайный_ответ_4 | {message.channel}")
            await message.channel.send(random.choice(gifs))
            db.Bot(value=20).lock()
            return
        '''
        # Слова на которые откликается бот
        react_role = config['reaction_word']

        if message.author.id == 374061361606688788:
            return
        # Отклик поняшки на слова, что указаны в config.json["reaction_word"]
        for content in content.split(' '):
            for react in react_role:
                if content.lower() == react:
                    choice = random.randint(1, 4)
                    emoji = message.guild.emojis
                    if choice == 1:
                        print(f"{timeMessage} | Ответ | {message.channel}")
                        await message.channel.send(f"_{random.choice(mass_react)}_")
                        db.Bot(value=30).lock()
                        return
                    elif choice == 2:
                        print(f"{timeMessage} | Ответ_2 | {message.channel}")
                        await message.channel.send(random.choice(emoji))
                        db.Bot(value=20).lock()
                        return
                    elif choice == 3:
                        print(f"{timeMessage} | Ответ_3 | {message.channel}")
                        await message.add_reaction(random.choice(emoji))
                        db.Bot(value=20).lock()
                        return
                    '''elif choice == 4:
                        print(f"{timeMessage} | Ответ_4 | {message.channel}")
                        await message.channel.send(random.choice(gifs))
                        db.Bot(value=20).lock()
                        return
                    '''


# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Message(bot))
    print(f'Запуск модуля MESSAGE.system')