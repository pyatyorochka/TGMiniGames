import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

TOKEN = "СЮДА ТОКЕН"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранение состояния игр по chat_id
game_states = {}

# ============================
# Вспомогательные клавиатуры
# ============================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Угадай число 🎲", callback_data="menu:guess_number")],
        [InlineKeyboardButton(text="Blackjack 🃏", callback_data="menu:blackjack")],
        [InlineKeyboardButton(text="Камень-Ножницы-Бумага ✂️🪨📄", callback_data="menu:rps")],
        [InlineKeyboardButton(text="Кубик 🎲", callback_data="menu:dice")],
        [InlineKeyboardButton(text="Викторина ❓", callback_data="menu:trivia")],
        [InlineKeyboardButton(text="Виселица 🪢", callback_data="menu:hangman")],
        [InlineKeyboardButton(text="Слот-машина 🎰", callback_data="menu:slots")],
        [InlineKeyboardButton(text="Математик 🧮", callback_data="menu:math")],
        [InlineKeyboardButton(text="Монетка 🪙", callback_data="menu:coin")],
        [InlineKeyboardButton(text="High-Low Карта 🃏", callback_data="menu:highlow")],
    ])

def exit_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])

# ============================
# Обработчик /start
# ============================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    if chat_id in game_states:
        del game_states[chat_id]
    await message.answer("Добро пожаловать! Выберите игру:", reply_markup=main_menu())

# ============================
# Возврат в главное меню
# ============================
@dp.callback_query(lambda c: c.data == "exit:menu")
async def exit_to_menu(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in game_states:
        del game_states[chat_id]
    await callback.message.edit_text("Добро пожаловать! Выберите игру:", reply_markup=main_menu())
    await callback.answer()

# ============================
# Обработка выбора игры
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("menu:"))
async def start_game(callback: types.CallbackQuery):
    data = callback.data.split(":")[1]
    chat_id = callback.message.chat.id

    # Сбрасываем старое состояние (если было)
    if chat_id in game_states:
        del game_states[chat_id]

    # ===== Угадай число =====
    if data == "guess_number":
        target = random.randint(1, 100)
        game_states[chat_id] = {"game": "guess_number", "target": target, "tries": 0}
        text = (
            "Я загадал число от 1 до 100. 🤔\n"
            "Попробуй угадать! Введи своё число:"
        )
        await callback.message.edit_text(text, reply_markup=exit_button())

    # ===== Blackjack =====
    elif data == "blackjack":
        deck = [r + s for r in "23456789TJQKA" for s in "CDHS"]
        random.shuffle(deck)
        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]
        game_states[chat_id] = {"game": "blackjack", "deck": deck, "player": player, "dealer": dealer}
        player_text = " ".join(player)
        text = (
            f"Blackjack 🃏\n"
            f"Ваши карты: {player_text}\n"
            f"Дилер показывает: {dealer[0]}\n"
            "Выберите действие:"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🃏 Взять карту (Hit)", callback_data="bj:hit"),
                InlineKeyboardButton(text="🛑 Остановиться (Stand)", callback_data="bj:stand")
            ],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)

    # ===== Камень-Ножницы-Бумага =====
    elif data == "rps":
        game_states[chat_id] = {"game": "rps"}
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✊ Камень", callback_data="rps:rock"),
                InlineKeyboardButton(text="✋ Бумага", callback_data="rps:paper"),
                InlineKeyboardButton(text="✌️ Ножницы", callback_data="rps:scissors")
            ],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text("Камень-Ножницы-Бумага! Выберите:", reply_markup=keyboard)

    # ===== Кубик =====
    elif data == "dice":
        game_states[chat_id] = {"game": "dice"}
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔼 Большое (4-6)", callback_data="dice:high"),
                InlineKeyboardButton(text="🔽 Маленькое (1-3)", callback_data="dice:low")
            ],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text("Кубик 🎲! Угадай: большое (4-6) или маленькое (1-3)?", reply_markup=keyboard)

    # ===== Викторина =====
    elif data == "trivia":
        question = "Столица Франции?"
        options = [("Париж", True), ("Лондон", False), ("Берлин", False), ("Рим", False)]
        random.shuffle(options)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=opt[0], callback_data=f"trivia:{opt[1]}")] for opt in options] + 
            [[InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]]
        )
        game_states[chat_id] = {"game": "trivia"}
        await callback.message.edit_text(question, reply_markup=keyboard)

    # ===== Виселица =====
    elif data == "hangman":
        words = ["азбука", "виселица","питон","бот","тест"]
        word = random.choice(words)
        state = {
            "game": "hangman",
            "word": word,
            "guessed": [],
            "tries": 6
        }
        display = " ".join(["_" for _ in word])
        game_states[chat_id] = state
        row1 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(13)]
        row2 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(13, 26)]
        row3 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(26, 33)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            row1,
            row2,
            row3,
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(f"Виселица 🪢\n{display}\nОсталось попыток: 6", reply_markup=keyboard)

    # ===== Слот-машина =====
    elif data == "slots":
        game_states[chat_id] = {"game": "slots"}
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎰 Крутить", callback_data="slots:spin")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text("Слот-машина 🎰! Нажми «Крутить»:", reply_markup=keyboard)

    # ===== Математик =====
    elif data == "math":
        a, b = random.randint(1, 10), random.randint(1, 10)
        op = random.choice(["+", "-"])
        answer = eval(f"{a}{op}{b}")
        options = [answer] + [answer + random.choice([-2, -1, 1, 2]) for _ in range(3)]
        random.shuffle(options)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=str(opt), callback_data=f"math:{opt==answer}")] for opt in options] +
            [[InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]]
        )
        game_states[chat_id] = {"game": "math"}
        await callback.message.edit_text(f"Математик 🧮\nРешите: {a} {op} {b}", reply_markup=keyboard)

    # ===== Монетка =====
    elif data == "coin":
        game_states[chat_id] = {"game": "coin"}
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Орёл", callback_data="coin:heads")],
            [InlineKeyboardButton(text="🔴 Решка", callback_data="coin:tails")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text("Монетка 🪙! Выберите Орёл или Решка:", reply_markup=keyboard)

    # ===== High-Low Карта =====
    elif data == "highlow":
        deck = list(range(1, 14))
        first = random.choice(deck)
        game_states[chat_id] = {"game": "highlow", "first": first}
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬆️ Выше", callback_data="highlow:higher")],
            [InlineKeyboardButton(text="⬇️ Ниже", callback_data="highlow:lower")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(f"High-Low Карта 🃏\nПервая карта: {first}\nСледующая будет выше или ниже?", reply_markup=keyboard)

    await callback.answer()

# ============================
# Угадай число: обработка текстовых сообщений
# ============================
@dp.message(lambda m: m.text and game_states.get(m.chat.id, {}).get("game") == "guess_number")
async def handle_guess_number(message: types.Message):
    chat_id = message.chat.id
    state = game_states[chat_id]
    text = message.text.strip()

    if not text.isdigit():
        await message.answer("❗ Введите, пожалуйста, число от 1 до 100.")
        return

    guess = int(text)
    target = state["target"]
    state["tries"] += 1

    if guess < 1 or guess > 100:
        await message.answer("❗ Число должно быть от 1 до 100. Попробуйте снова.")
        return

    if guess < target:
        await message.answer("Моё число больше! 🔼 Попробуйте ещё раз.")
    elif guess > target:
        await message.answer("Моё число меньше! 🔽 Попробуйте ещё раз.")
    else:
        tries = state["tries"]
        text = (
            f"🎉 Поздравляю! Вы угадали число {target} за {tries} попыток.\n"
            "Хотите сыграть ещё раз?"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:guess_number")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await message.answer(text, reply_markup=keyboard)
        del game_states[chat_id]

# ============================
# Blackjack
# ============================
def calculate_hand_value(cards):
    value = 0
    aces = 0
    for card in cards:
        rank = card[:-1]
        if rank.isdigit():
            value += int(rank)
        elif rank in ["T", "J", "Q", "K"]:
            value += 10
        else:  # "A"
            aces += 1
            value += 11
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

@dp.callback_query(lambda c: c.data and c.data.startswith("bj:"))
async def handle_blackjack(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "blackjack":
        await callback.answer("Нет активной игры Blackjack.", show_alert=True)
        return

    action = callback.data.split(":")[1]
    deck = state["deck"]
    player = state["player"]
    dealer = state["dealer"]

    if action == "hit":
        card = deck.pop()
        player.append(card)
        player_val = calculate_hand_value(player)
        if player_val > 21:
            text = (
                f"Вы взяли {card}. Ваши карты: {player} ({player_val}).\n"
                "Перебор! Вы проиграли. 😢"
            )
            await callback.message.edit_text(text, reply_markup=main_menu())
            del game_states[chat_id]
            await callback.answer()
            return
        hand_text = (
            f"Вы взяли {card}. Ваши карты: {player} ({player_val}).\n"
            f"Дилер показывает: {dealer[0]}\n"
            "Ваш ход:"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🃏 Взять (Hit)", callback_data="bj:hit"),
                InlineKeyboardButton(text="🛑 Стоп (Stand)", callback_data="bj:stand")
            ],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(hand_text, reply_markup=keyboard)
    else:  # Stand
        dealer_val = calculate_hand_value(dealer)
        while dealer_val < 17:
            card = state["deck"].pop()
            dealer.append(card)
            dealer_val = calculate_hand_value(dealer)
        player_val = calculate_hand_value(player)
        if dealer_val > 21:
            result = "Дилер перебрал! Вы победили! 🎉"
        elif dealer_val > player_val:
            result = "Дилер выигрывает. 😢"
        elif dealer_val < player_val:
            result = "Вы побеждаете! 🎉"
        else:
            result = "Ничья! 🤝"

        text = (
            f"Дилер: {dealer} ({dealer_val})\n"
            f"Вы: {player} ({player_val})\n"
            f"{result}"
        )
        await callback.message.edit_text(text, reply_markup=main_menu())
        del game_states[chat_id]

    await callback.answer()

# ============================
# Камень-Ножницы-Бумага
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("rps:"))
async def handle_rps(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "rps":
        await callback.answer("Нет активной игры Камень-Ножницы-Бумага.", show_alert=True)
        return

    user_choice = callback.data.split(":")[1]
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    if user_choice == bot_choice:
        result = "Ничья!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "Вы выиграли! 🎉"
    else:
        result = "Вы проиграли! 😢"

    mapping = {"rock": "Камень", "paper": "Бумага", "scissors": "Ножницы"}
    text = f"Вы: {mapping[user_choice]}\nБот: {mapping[bot_choice]}\n{result}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:rps")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# Кубик
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("dice:"))
async def handle_dice(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "dice":
        await callback.answer("Нет активной игры Кубик.", show_alert=True)
        return

    guess = callback.data.split(":")[1]  # "high" или "low"
    roll = random.randint(1, 6)
    if (roll >= 4 and guess == "high") or (roll <= 3 and guess == "low"):
        result = "Вы выиграли! 🎉"
    else:
        result = "Вы проиграли! 😢"
    text = f"Выпало: {roll}\n{result}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:dice")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# Викторина
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("trivia:"))
async def handle_trivia(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "trivia":
        await callback.answer("Нет активной Викторины.", show_alert=True)
        return

    correct = callback.data.split(":")[1] == "True"
    if correct:
        text = "Верно! 🎉"
    else:
        text = "Неверно! 😢 Правильный ответ: Париж."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:trivia")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# Виселица
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("hangman_letter:"))
async def handle_hangman(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "hangman":
        await callback.answer("Нет активной игры Виселица.", show_alert=True)
        return

    letter = callback.data.split(":")[1].lower()
    word = state["word"]
    guessed = state["guessed"]
    tries = state["tries"]

    if letter in guessed:
        await callback.answer("Эта буква уже была!", show_alert=True)
        return

    guessed.append(letter)
    if letter not in word:
        tries -= 1
        state["tries"] = tries

    display = " ".join([ch.upper() if ch in guessed else "_" for ch in word])

    if all(ch in guessed for ch in word):
        text = f"Виселица 🪢\nСлово: {word.upper()}\nВы выиграли! 🎉"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:hangman")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)
        del game_states[chat_id]
        await callback.answer()
        return
    elif tries <= 0:
        text = f"Виселица 🪢\nСлово: {word.upper()}\nВы проиграли! 😢"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:hangman")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)
        del game_states[chat_id]
        await callback.answer()
        return

    state["guessed"] = guessed
    state["tries"] = tries
    row1 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(13)]
    row2 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(13, 26)]
    row3 = [InlineKeyboardButton(text=chr(ord('А') + i), callback_data=f"hangman_letter:{chr(ord('А') + i)}") for i in range(26, 33)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        row1,
        row2,
        row3,
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(f"Виселица 🪢\n{display}\nОсталось попыток: {tries}", reply_markup=keyboard)
    await callback.answer()

# ============================
# Слот-машина
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("slots:"))
async def handle_slots(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "slots":
        await callback.answer("Нет активной Слот-машины.", show_alert=True)
        return

    action = callback.data.split(":")[1]
    if action == "spin":
        symbols = ["🍒", "🍋", "🍊", "⭐", "7️⃣"]
        reels = [random.choice(symbols) for _ in range(3)]
        if len(set(reels)) == 1:
            result = "Джекпот! 🎉"
        else:
            result = "Попробуйте ещё раз! 😢"
        text = f"Крутится: {' '.join(reels)}\n{result}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Снова", callback_data="slots:spin")],
            [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()

# ============================
# Математик
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("math:"))
async def handle_math(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "math":
        await callback.answer("Нет активной игры Математик.", show_alert=True)
        return

    correct = callback.data.split(":")[1] == "True"
    if correct:
        text = "Верно! 🎉"
    else:
        text = "Неверно! 😢"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:math")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# Монетка
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("coin:"))
async def handle_coin(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "coin":
        await callback.answer("Нет активной игры Монетка.", show_alert=True)
        return

    guess = callback.data.split(":")[1]  # "heads" или "tails"
    flip = random.choice(["heads", "tails"])
    if guess == flip:
        text = f"Монета показала { 'Орёл' if flip=='heads' else 'Решка' }. Вы выиграли! 🎉"
    else:
        text = f"Монета показала { 'Орёл' if flip=='heads' else 'Решка' }. Вы проиграли! 😢"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:coin")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# High-Low Карта
# ============================
@dp.callback_query(lambda c: c.data and c.data.startswith("highlow:"))
async def handle_highlow(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    state = game_states.get(chat_id)
    if not state or state.get("game") != "highlow":
        await callback.answer("Нет активной игры High-Low.", show_alert=True)
        return

    guess = callback.data.split(":")[1]  # "higher" или "lower"
    first = state["first"]
    next_card = random.randint(1, 13)
    if (next_card > first and guess == "higher") or (next_card < first and guess == "lower"):
        text = f"Первая карта: {first}\nСледующая: {next_card}\nВы выиграли! 🎉"
    elif next_card == first:
        text = f"Первая карта: {first}\nСледующая: {next_card}\nНичья! 🤝"
    else:
        text = f"Первая карта: {first}\nСледующая: {next_card}\nВы проиграли! 😢"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Снова", callback_data="menu:highlow")],
        [InlineKeyboardButton(text="🔙 Выход в меню", callback_data="exit:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    del game_states[chat_id]
    await callback.answer()

# ============================
# Запуск бота
# ============================
if __name__ == "__main__":
    dp.run_polling(bot)
