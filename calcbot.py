from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = '7827382026:AAE0GZSLrWj1rTWaCEELCGi1RfJ7LC-bw7M'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Create a keyboard for user input
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Start Calculation"))

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Welcome to the Advanced Diet Calculator bot!\n"
        "Please click 'Start Calculation' to begin.",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "Start Calculation")
async def ask_species(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Dog", "Cat")
    await message.reply("Select the animal:", reply_markup=markup)

@dp.message_handler(lambda message: message.text in ["Dog", "Cat"])
async def ask_weight(message: types.Message):
    species = message.text
    await message.answer("Enter the weight of the animal in kg (e.g., 10):")
    dp.storage.data[message.chat.id] = {"species": species}

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit())
async def ask_activity(message: types.Message):
    weight = float(message.text)
    dp.storage.data[message.chat.id]["weight"] = weight

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Low", "Moderate", "High")
    await message.reply("Select the activity level:", reply_markup=markup)

@dp.message_handler(lambda message: message.text in ["Low", "Moderate", "High"])
async def ask_age(message: types.Message):
    activity = message.text
    dp.storage.data[message.chat.id]["activity"] = activity
    await message.reply("Enter the age of the animal in years (e.g., 5):")

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit() and message.text.count('.') <= 1)
async def ask_state(message: types.Message):
    age = float(message.text)
    dp.storage.data[message.chat.id]["age"] = age

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("None", "Pregnant", "Lactating", "Overweight", "Diseased")
    await message.reply("Select the physiological state:", reply_markup=markup)

@dp.message_handler(lambda message: message.text in ["None", "Pregnant", "Lactating", "Overweight", "Diseased"])
async def calculate_diet(message: types.Message):
    state = message.text
    dp.storage.data[message.chat.id]["state"] = state

    data = dp.storage.data[message.chat.id]
    species = data["species"]
    weight = data["weight"]
    activity = data["activity"]
    age = data["age"]

    # Constants and calculations
    is_dog = species == "Dog"
    base_me = 110 * (weight ** 0.75) if is_dog else 100 * (weight ** 0.67)
    activity_multipliers = {"Low": 1.2, "Moderate": 1.4, "High": 1.8}
    me = base_me * activity_multipliers.get(activity, 1.2)

    if state == "Pregnant":
        me *= 1.3
    elif state == "Lactating":
        me *= 2.0
    elif state == "Overweight":
        me *= 0.8
    elif state == "Diseased":
        me *= 1.1

    protein = 2.5 * weight
    fat = 1.2 * weight

    micronutrients = {
        "Calcium (Ca)": 50 * weight,
        "Phosphorus (P)": 40 * weight,
        "Iron (Fe)": 1.5 * weight,
        "Zinc (Zn)": 1.0 * weight,
        "Magnesium (Mg)": 0.5 * weight,
        "Sodium (Na)": 3.0 * weight,
        "Potassium (K)": 2.0 * weight,
        "Vitamin A": 100 * weight,
        "Vitamin D": 10 * weight,
        "Vitamin E": 2.0 * weight,
        "Vitamin C": 5.0 * weight,
        "Taurine": 0 if is_dog else 10 * weight
    }

    # Generate response
    response = (
        f"Diet Calculation Results:\n"
        f"Energy (ME): {me:.2f} kcal/day\n"
        f"Protein: {protein:.2f} g/day\n"
        f"Fat: {fat:.2f} g/day\n"
        f"Micronutrients:\n"
    )
    for nutrient, value in micronutrients.items():
        response += f"  {nutrient}: {value:.2f} mg/day\n"

    await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
