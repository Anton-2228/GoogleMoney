import logging

from commands.AddEmail import AddEmail
from commands.AddRecord import AddRecord
from commands.CreateTable import CreateTable
from commands.DeleteRecord import DeleteRecord
from commands.DeleteTable import DeleteTable
from commands.GetHelp import GetHelp
from commands.GetTable import GetTable
from commands.SetDateReset import SetDateReset
from commands.Synchronize import Synchronize
from commands.Transfer import Transfer

# Способ логирования. При деплое поменять строки
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.INFO, filename="logs.log", format="%(asctime)s %(levelname)s %(message)s")

API_TOKEN = "секрет"
CREDENTIALS_FILE = 'data_files/mmmm-376012-d0a58302e867.json'

def setCommands():
    global commands
    commands = {"start": CreateTable(),
                "table": GetTable(),
                "addEmail": AddEmail(),
                "help": GetHelp(),
                "deleteTable": DeleteTable(),
                "sync": Synchronize(),
                "del": DeleteRecord(),
                "transfer": Transfer(),
                "addRecord": AddRecord()}