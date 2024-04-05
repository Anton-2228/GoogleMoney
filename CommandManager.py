class CommandManager:
    def __init__(self):
        self.commands = {}
    
    def getCommands(self):
        return self.commands

    def addCommand(self, title, command):
        self.commands[title] = command

    async def launchCommand(self, title, message):
        response = await self.commands[title].execute(message)