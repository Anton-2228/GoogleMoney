import GlobalVariables
from SaveChanges import saveData


class DeleteTable:

    def __init__(self):
        global dp, data, categories, sources, records, Events
        dp = GlobalVariables.dispatcher
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        records = GlobalVariables.records
        Events = GlobalVariables.Events

    async def execute(self, message):
        state = dp.current_state(user=message.from_user.id)

        if await state.get_state() == None:
            await state.set_state(Events.COMFIRM_DELETE[0])
            await message.answer("Напишите 'ПОДТВЕРЖДАЮ УДАЛЕНИЕ' для удаления таблицы.\nСама таблица существовать продолжит, однако привязать её к боту будет уже невозможно")

        elif await state.get_state() == "comfirm_delete":
            text = message.text
            if text != "ПОДТВЕРЖДАЮ УДАЛЕНИЕ":
                await message.answer('Удаление таблицы отменено')
            else:
                del data[str(message.from_user.id)]
                del categories[str(message.from_user.id)]
                del sources[str(message.from_user.id)]
                del records[str(message.from_user.id)]
                state = dp.current_state(user=message.from_user.id)
                await state.reset_state()
                await message.answer('Для создания новой таблицы напишите /start')
                saveData()
