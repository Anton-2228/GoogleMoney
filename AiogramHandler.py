import GlobalVariables

import logging
import json
import re
import datetime

import asyncio

import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem, Item
from aiogram.types import BotCommand

dp = GlobalVariables.dispatcher
Events = GlobalVariables.Events
commandManager = GlobalVariables.commandManager

data = GlobalVariables.data
globTimer = GlobalVariables.globTimer
counter = GlobalVariables.counter

@dp.message_handler(state=Events.COMFIRM_CHANGE_DATE_RESET[0])
@dp.message_handler(state=Events.CHOICE_TABLE_NAME[0])
@dp.message_handler(state=Events.SET_EMAIL[0])
@dp.message_handler(commands=['start'])
async def startFunc(message: types.Message):
    response = await commandManager.launchCommand('start', message)

@dp.message_handler(commands=['addemail'])
async def addEmail(message: types.Message):
    response = await commandManager.launchCommand('addEmail', message)

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    response = await commandManager.launchCommand('help', message)

@dp.message_handler(commands=["sync"])
@dp.message_handler(state=Events.CORRECT_TABLE[0], commands=["sync"])
async def synchronize(message: types.Message):
    response = await commandManager.launchCommand('sync', message)

@dp.message_handler(commands=["transfer"])
async def transfer(message: types.Message):
    response = await commandManager.launchCommand('transfer', message)

@dp.message_handler(state=Events.CORRECT_TABLE[0])
async def errorRecord(message: types.Message):
    await message.answer("Исправьте таблицу и синхронизируйте её")

@dp.message_handler(commands=["table"])
async def getTable(message: types.Message):
    response = await commandManager.launchCommand('table', message)

@dp.message_handler(commands=["del"])
async def deleteLastRecord(message: types.Message):
    response = await commandManager.launchCommand('del', message)

@dp.message_handler(state=Events.COMFIRM_DELETE[0])
@dp.message_handler(commands=["deletetable"])
async def deleteTable(message: types.Message):
    response = await commandManager.launchCommand('deleteTable', message)

@dp.message_handler()
async def newRecord(message: types.Message):
    response = await commandManager.launchCommand('addRecord', message)

async def startup(dispatcher: Dispatcher):
    for i in data:
        counter.create_task(globTimer.execute(i))

async def shutdown(dispatcher: Dispatcher):
    for i in GlobalVariables.data:
        state = dp.current_state(user=i)
        await state.reset_state()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

def start():
    executor.start_polling(dp, on_startup=startup, on_shutdown=shutdown)