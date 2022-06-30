import time

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from change_name import search_data, get_card_info, prepare_card_info, info_to_upload

# state options
ENTER_API_KEY = 1
ENTER_NM_ID = 2
ENTER_NEW_NAME = 3


# function to handle the /start command
def start(update, context):
    context.user_data['state'] = ENTER_API_KEY
    update.message.reply_text("Для начала работы с ботом предоставьте API ключ")


def received_api_key(update, context):
    api_key = update.message.text
    try:
        for i in range(5):
            info = requests.get('https://suppliers-api.wildberries.ru/api/v1/directory/wbsizes',
                            headers={"Authorization": api_key})
            if info.status_code == 200 or info.status_code == 401:
                break
            else:
                time.sleep(1)

        if info.status_code != 200:
            update.message.reply_text("Что-то пошло не так..." + str(info.status_code))
            update.message.reply_text("Статус " + str(info.status_code))
            if info.status_code == 401:
                update.message.reply_text("Введён неверный API ключ")
            update.message.reply_text("Попробуйте ещё раз")
            raise ValueError("invalid value")
        else:
            context.user_data['api_key'] = api_key
            context.user_data['state'] = ENTER_NM_ID
            update.message.reply_text("Верный API ключ")
            update.message.reply_text("Введите номенклатуру товара, у которого хотите изменить наименование")
    except:
        update.message.reply_text("Что-то пошло не так 1...")


def change_name(update, info, context):
    info = prepare_card_info(info=info, headers={"Authorization": context.user_data['api_key']})
    context.user_data['card_info'] = info
    context.user_data['state'] = ENTER_NEW_NAME
    update.message.reply_text("Текущее наименование товара: {}".format(info['card']['addin'][1]['params'][0]['value']))
    update.message.reply_text(
        "Введите новое наименование товара. После отправки сообщения наименование будет изменено.")


def received_nm_id(update, context):
    try:
        nm_id = int(update.message.text)
    except:
        update.message.reply_text("Номенклатура должна состоять только из цифр. Попробуйте ещё раз.")
        raise ValueError("invalid value")
    data = search_data(nm_id)
    try:
        for i in range(5):
            info = get_card_info(data=data, headers={"Authorization": context.user_data['api_key']})
            # update.message.reply_text("Информация о товаре загружена. Статус " + str(info.status_code))
            if info.status_code == 200:
                break
            else:
                time.sleep(1)

        if info.status_code == 200:
            change_name(update, info, context)
        elif info.status_code == 401:
            update.message.reply_text("Номенклатура не найдена. Попробуйте ещё раз.")
        else:
            update.message.reply_text(
                "Что-то пошло не так при загрузке карточки товара. Попробуйте ввести номенклатуру ещё раз.")
    except:
        update.message.reply_text("Что-то пошло не так. Код ошибки {}. Попробуйте ещё раз.".format(info.status_code))


def received_new_name(update, context):
    new_name = str(update.message.text)
    try:
        info = info_to_upload(context.user_data['card_info'], new_name)
        updated_info = requests.post('https://suppliers-api.wildberries.ru/card/update',
                                     json=info,
                                     headers={"Authorization": context.user_data['api_key']})
        if updated_info.status_code != 200:
            update.message.reply_text("Что-то пошло не так...")
            update.message.reply_text("Попробуйте ещё раз")
            raise ValueError("invalid value")
        else:
            context.user_data['state'] = ENTER_NM_ID
            update.message.reply_text("Наименование успешно изменено")
            update.message.reply_text("Введите номенклатуру товара, у которого хотите изменить наименование")
    except:
        update.message.reply_text(
            "Что-то пошло не так. Попробуйте ещё раз.")


# function to handle the /help command
def help(update, context):
    update.message.reply_text('help command received')


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('an error occured')


# function to handle normal text
def text(update, context):
    if context.user_data['state'] == ENTER_API_KEY:
        return received_api_key(update, context)

    if context.user_data['state'] == ENTER_NM_ID:
        return received_nm_id(update, context)

    if context.user_data['state'] == ENTER_NEW_NAME:
        return received_new_name(update, context)


def main():
    TOKEN = "5299391428:AAHs4zLVrFwvw4GfW6zNMIdnfVNG6884jn0"

    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialogue
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()