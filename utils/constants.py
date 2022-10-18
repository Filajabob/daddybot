import json

class Constants:
    MAX_CLAIM_TIME = 1800  # Max time to claim a code, in seconds
    INVITE_LINK = "https://dsc.gg/memetopia"
    FAST_MATH_MINIMUM_ACE = 15  # Minimum amount of questions to get an ace. This is to prevent playing Fast Math
                                # with only one question, getting it right, and getting the bonus.
    FAST_MATH_MAX_ANSWER_TIME = 5  # Number of seconds to answer a Fast Math question

    GAMES = ["Minecraft", "Fortnite", "Valorant", "Roblox", "Just Chill"]  # Games recognized in the LFG system
    MEMETOPIA_ID = 1021919859203903488

    REQUIRED_VOTES_TO_SKIP = 3  # Required amount of votes to skip a song

    class XPSettings:
        FRIEND_CODE_XP = 5500  # XP the code creator gets
        FRIEND_CODE_CLAIMER_XP = 3500  # XP the code claimer gets

        MESSAGE_XP = 20  # Amount of XP author gets for a message
        DAILY_XP = 500 # Amount of XP each day

        TRIVIA_CORRECT_EASY = 20  # Amount of XP for getting a true-or-false trivia question correct (easy)
        TRIVIA_CORRECT_MED = 30
        TRIVIA_CORRECT_HARD = 40

        RUS_ROULETTE_XP = 100  # Amount of XP to give for winning Russian Roulette

        FAST_MATH_QUESTION_XP = 15  # Amount of XP for answering a Fast Math question successfully.
        FAST_MATH_ACE_XP = 0.3  # Bonus XP to award to someone for getting all questions correct.


    class Ranks:
        RANK_1 = 10000
        RANK_2 = 40000
        RANK_3 = 150000
        RANK_4 = 270000
        RANK_5 = 450000

        RANK_1_ID = 1022605556948668506
        RANK_2_ID = 1022606250376175630
        RANK_3_ID = 1022607191569600573
        RANK_4_ID = 1022607587595796490
        RANK_5_ID = 1021922977845104661

    class MemeCoin:
        TAX_PERCENTAGE = 0.042  # Percentage taken from a transfer
        TAX_MINIMUM = 50  # Minimum transfer amount for tax to be applied

        DAILY_MEMECOIN = 50  # Amount of MemeCoin every day

        TRIVIA_CORRECT_EASY = 5  # Amount of MemeCoin for getting a true-or-false trivia question correct (easy)
        TRIVIA_CORRECT_MED = 10
        TRIVIA_CORRECT_HARD = 20

        FAST_MATH_QUESTION_MEMECOIN = 2  # See Constants.XPSettings.FAST_MATH_QUESTION_XP
        FAST_MATH_ACE_MEMECOIN = 0.25  # See Constants.XPSettings.FAST_MATH_ACE_XP

    class Market:
        XP_BUNDLE_SIZE = 200  # Amount of XP to sell at once. Must also change assets/bot/items.generic.json to change this.

        with open("assets/bot/market/items/generic.json", 'r') as f:
            XP_BUNDLE_COST = json.load(f)["xp"]["cost"]
