import GlobalVariables
from SaveChanges import saveData
from commands.Synchronize import Synchronize


class Transfer():
    def __init__(self):
        global data, sources, categories
        data = GlobalVariables.data
        sources = GlobalVariables.sources
        categories = GlobalVariables.categories

    async def execute(self, message):
        userData = data[str(message.from_user.id)]
        userSources = sources[str(message.from_user.id)]
        userCategories = categories[str(message.from_user.id)]

        args = str(message.get_args()).split()
        if len(args) != 4:
            await message.answer("Странные счета")
        elif args[2].lower() == args[3].lower():
            await message.answer("Счета должны быть разными")
        else:
            fr = None
            to = None
            for i in userSources:
                if userSources[i]['name'].lower() == args[2].lower():
                    fr = i
                if userSources[i]['name'].lower() == args[3].lower():
                    to = i
            if fr == None:
                await message.answer("Первого счета не существует")
            if to == None:
                await message.answer("Второго счета не существует")
            else:
                try:
                    userData["sources"][fr] -= (int(args[0]) + int(args[1]))
                    userData["sources"][to] += int(args[0])

                    await message.answer("Перевод успешен")
                    sy = Synchronize()
                    await sy.syncTotal(userData, userCategories, userSources)
                    saveData()
                except:
                    await message.answer("Странная сумма")