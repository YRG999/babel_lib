# random_tarot.py

import random

# Define a list of tarot cards with their meanings
tarot_cards = {
    "The Fool": "New beginnings, spontaneity, adventure, taking risks.",
    "The Magician": "Manifestation, resourcefulness, power, inspired action.",
    "The High Priestess": "Intuition, unconscious knowledge, mystery, inner voice.",
    "The Empress": "Nurturing, abundance, motherhood, nature, fertility.",
    "The Emperor": "Authority, structure, control, father figure.",
    "The Hierophant": "Tradition, conformity, spiritual guidance, education.",
    "The Lovers": "Love, union, choices, harmony, relationships.",
    "The Chariot": "Willpower, determination, control, victory through action.",
    "Strength": "Courage, compassion, inner strength, patience.",
    "The Hermit": "Soul-searching, introspection, inner guidance, solitude.",
    "Wheel of Fortune": "Cycles, change, fate, fortune, karma.",
    "Justice": "Fairness, truth, law, cause and effect.",
    "The Hanged Man": "Letting go, sacrifice, new perspectives, pause.",
    "Death": "Transformation, endings, new beginnings, transition.",
    "Temperance": "Balance, moderation, harmony, patience.",
    "The Devil": "Addiction, materialism, playfulness, negative influences.",
    "The Tower": "Sudden change, upheaval, chaos, revelation.",
    "The Star": "Hope, inspiration, serenity, healing.",
    "The Moon": "Illusion, fear, anxiety, subconscious, intuition.",
    "The Sun": "Joy, success, positivity, vitality.",
    "Judgment": "Reflection, reckoning, inner calling, awakening.",
    "The World": "Completion, fulfillment, achievement, travel."
}

# Define a function to draw a random tarot card and print its meaning
def draw_tarot_card():
    # Randomly select a tarot card
    card = random.choice(list(tarot_cards.keys()))
    meaning = tarot_cards[card]
    return f"Tarot Card: {card}\nMeaning: {meaning}"

# Draw a tarot card and print the result
if __name__ == "__main__":
    tarot_output = draw_tarot_card()
    print(tarot_output)