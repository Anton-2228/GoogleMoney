import datetime

import GlobalVariables
from SaveChanges import saveData


class SetDateReset:

    def __init__(self):
        global dp, data, categories, sources, records, Events, daysUntilNextMonth
        dp = GlobalVariables.dispatcher
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        records = GlobalVariables.records
        Events = GlobalVariables.Events
        daysUntilNextMonth = GlobalVariables.daysUntilNextMonth

    async def execute(self, message):
        state = dp.current_state(user=message.from_user.id)
        if await state.get_state() == None:
            await state.set_state(Events.COMFIRM_CHANGE_DATE_RESET[0])
            await message.answer("Напишите день, в который будет происходить переход таблицы на новый месяц(этот день должен быть в каждом месяце, т.е. меньший 29)")
        elif await state.get_state() == "comfirm_change_date_reset":
            #try:
            userData = data[str(message.from_user.id)]
            today = datetime.date.today()
            curDay = userData["currentMonth"].split('-')
            if int(message.text.split()[0]) >= int(curDay[2]):
                nex = today + datetime.timedelta(days=int(message.text.split()[0])) - datetime.timedelta(days=int(curDay[2]))
            else:
                nex = today + datetime.timedelta(days=daysUntilNextMonth[int(curDay[1])]) + datetime.timedelta(days=int(message.text.split()[0])) - datetime.timedelta(days=int(curDay[2]))
            userData["nextMonth"] = str(nex)
            saveData()
            await state.reset_state()
            await message.answer("Дата заменена")
            #except:
            #    await message.answer("Странное число")