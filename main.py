import telebot, transitions
from transitions import Machine
from telebot import types

token = '2072555776:AAGFOVzqr1G7M-L2drj-AizKW56IZXq9bMw'

bot = telebot.TeleBot(token)

PIZZA_SIZE = ["Большую", "Среднюю", "Маленькую"]
PAYMENT_CHOISE = ["Картой", "Наличкой"]
repeat_order = dict()

class OrderPizza():
    pass


order_pizza = OrderPizza()


states = ['waiting_order', 'waiting_size', 'waiting_payment', 'confirm_order', 'processed_order']

transitions = [
    {'trigger': 'order', 'source': 'waiting_order', 'dest': 'waiting_size'},
    {'trigger': 'size', 'source': 'waiting_size', 'dest': 'waiting_payment'},
    {'trigger': 'payment', 'source': 'waiting_payment', 'dest': 'confirm_order'},
    {'trigger': 'processed', 'source': 'confirm_order', 'dest': 'processed_order'},
    {'trigger': 'cancel', 'source': 'confirm_order', 'dest': 'waiting_order'},
    {'trigger': 'reoder', 'source': 'processed_order', 'dest': 'waiting_order'}
]

machine = Machine(order_pizza, states=states, transitions=transitions, initial='waiting_order')


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Заказать пиццу")
    markup.add(item1)
    bot.send_message(message.chat.id, "Привет! Я бот для заказа еды. Выбирай нужные команды на клавиатуре",
                     reply_markup=markup)


@bot.message_handler(content_types='text')
def order_message(message):
    if message.text == "Заказать пиццу":
        if order_pizza.state == 'waiting_order':
            order_pizza.order()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Большую")
        item2 = types.KeyboardButton("Среднюю")
        item3 = types.KeyboardButton("Маленькую")
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, "Какую вы хотите пиццу? Большую или маленькую?", reply_markup=markup)
    elif message.text in PIZZA_SIZE:
        if order_pizza.state == 'waiting_size':
            order_pizza.size()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.InlineKeyboardButton("Наличкой")
        item2 = types.InlineKeyboardButton("Картой")
        markup.add(item1, item2)
        repeat_order['size'] = message.text.lower()
        bot.send_message(message.chat.id, "Как вы будете платить?", reply_markup=markup)
    elif message.text in PAYMENT_CHOISE:
        if order_pizza.state == 'waiting_payment':
            order_pizza.payment()
        repeat_order['payment'] = message.text.lower()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.InlineKeyboardButton("Да")
        item2 = types.InlineKeyboardButton("Нет")
        markup.add(item1, item2)
        bot.send_message(message.chat.id, f"Вы хотите {repeat_order['size']} пиццу, оплата - "
                                          f"{repeat_order['payment']}?", reply_markup=markup)
    elif message.text == "Да":
        if order_pizza.state == 'confirm_order':
            order_pizza.processed()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.InlineKeyboardButton("Заказать пиццу")
            markup.add(item1)
            bot.send_message(message.chat.id, "Спасибо за заказ", reply_markup=markup)
            if order_pizza.state == 'processed_order':
                order_pizza.reoder()
    elif message.text == "Нет":
        if order_pizza.state == 'confirm_order':
            order_pizza.cancel()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.InlineKeyboardButton("Заказать пиццу")
        markup.add(item1)
        bot.send_message(message.chat.id, "Давай попробуем оформить заказ еще раз!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выбери нужный вариант на клавиатуре!")


bot.infinity_polling(non_stop=True)
