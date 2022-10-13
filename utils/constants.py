class Constants:
    MAX_CLAIM_TIME = 1800  # Max time to claim a code, in seconds
    INVITE_LINK = "https://dsc.gg/memetopia"
    FAST_MATH_MINIMUM_ACE = 10  # Minimum amount of questions to get an ace. This is to prevent playing Fast Math
                                # with only one question, getting it right, and getting the bonus.
    FAST_MATH_MAX_ANSWER_TIME = 5  # Number of seconds to answer a Fast Math question

    class XPSettings:
        FRIEND_CODE_XP = 5500  # XP the code creator gets
        FRIEND_CODE_CLAIMER_XP = 3500  # XP the code claimer gets

        MESSAGE_XP = 20  # Amount of XP author gets for a message
        DAILY_XP = 500 # Amount of XP each day

        TRIVIA_CORRECT_EASY = 25  # Amount of XP for getting a true-or-false trivia question correct (easy)
        TRIVIA_CORRECT_MED = 50
        TRIVIA_CORRECT_HARD = 69

        RUS_ROULETTE_XP = 100  # Amount of XP to give for winning Russian Roulette

        FAST_MATH_QUESTION_XP = 10  # Amount of XP for answering a Fast Math question successfully.
        FAST_MATH_ACE_XP = 0.25  # Bonus XP to award to someone for getting all questions correct.


    class Ranks:
        RANK_1 = 10000
        RANK_2 = 40000
        RANK_3 = 110000
        RANK_4 = 230000
        RANK_5 = 310000

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
