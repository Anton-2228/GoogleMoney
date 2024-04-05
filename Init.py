import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import Settings
from CommandManager import CommandManager
from Timer import Timer

credentials = ServiceAccountCredentials.from_json_keyfile_name(Settings.CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())

def createDispatcher():
    dp = Dispatcher(Bot(token=Settings.API_TOKEN, parse_mode="HTML"), storage=MemoryStorage())
    dp.middleware.setup(LoggingMiddleware())
    return dp

def createSheetService():
    sheetService = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)
    return sheetService

def createDriveService():
    driveService = googleapiclient.discovery.build('drive', 'v3', http=httpAuth)
    return driveService

def createCommandManager():
    Settings.setCommands()
    commandManager = CommandManager()
    for i in Settings.commands:
        commandManager.addCommand(i, Settings.commands[i])
    return commandManager

def createTimer():
    return Timer()