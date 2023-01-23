from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import keyboards
from aiogram.contrib.fsm_storage.memory import MemoryStorage

@dp.message_handler(state = Form.add_task_header)
async def new_task_header(message: types.Message):
    new_task_dict['header'] = message.text
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_body)
async def new_task_body(message: types.Message):
    new_task_dict['body'] = message.text
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_deadline)
async def new_task_deadline(message: types.Message):
    new_task_dict['deadline'] = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_assignees)
async def new_task_assignees(message: types.Message):
    new_task_dict['assignees'] = re.split('\s*,*\s+', message.text) 
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.callback_query_handler(Text(startswith='add_task'), state='*')
async def new_task_buttons(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    mes_id = callback.message.message_id
    query = callback.data.replace('add_task_', '')
    if query == 'header':
        await bot.send_message(chat_id, "Напиши название задачи:")
        await Form.add_task_header.set()
    if query == 'body':
        await bot.send_message(chat_id, "Напиши описание задачи:")
        await Form.add_task_body.set()
    if query == 'assignees':
        await Form.add_task_assignees.set()
        await bot.send_message(chat_id, "Укажи никнеймы исполнителей через пробел:")
    if query == 'deadline':
        await bot.send_message(chat_id, "Укажи дедлайн задачи:")
        await Form.add_task_deadline.set()
    if query == 'back':
        key = await get_keyboard(callback.from_user.id)
        await bot.edit_message_text("Задача отменена", chat_id, mes_id, reply_markup=None)
        await Form.admin.set()
    if query == 'save':
        commands.insert_new_task(new_task_dict, callback.from_user.username)
        key = await get_keyboard(callback.from_user.id)
        await Form.admin.set()
        await bot.send_message(chat_id,"Задача сохранена.", reply_markup=key['main'])


@dp.message_handler(Text(equals='Создать задачу', ignore_case=True), state=Form.default)
async def new_task(message: types.Message):
    global new_task_dict
    new_task_dict= {
        'header': '',
        'body': '',
        'assignees': [],
        'deadline': '',
        'creator': '',
        'created_datetime': ''
    }
    await message.answer('Создать задачу:', reply_markup=keyboards.AddTasksKb)
