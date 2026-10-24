"""User-facing copy shared by every interface."""

from __future__ import annotations

APP_NAME = "Maths Frenzy"
TAGLINE = "A fast-paced mental-maths game and calculator."
CREDITS = "Follow ABC Apps on Instagram @abc_apps_official or on Facebook: ABC apps"

PLEDGE = "I promise to be consistent in learning maths."
PLEDGE_REQUIRED = "You have to agree to be consistent in learning maths before you can play."

HOW_TO_PLAY: tuple[str, ...] = (
    "There are three levels: Beginner, Advanced and Master. "
    "Each level has its own difficulty, so pick the one that matches your skill.",
    "After choosing a level, choose the operation you want to practise: "
    "addition, subtraction, multiplication or division.",
    "Each round has 20 questions and you get 20 seconds for each one. "
    "Answer before the timer runs out to score a point.",
    "Division answers are rounded to two decimal places.",
)

TUTORIAL_INTRO = "Let's have a little tutorial, champ..."
TUTORIAL_QUESTION = "4 + 4"
TUTORIAL_ANSWER = 8
TUTORIAL_HINT = "The right answer is 8. Enter 8 and press Check to continue."
TUTORIAL_DONE = "Well done! Why don't we try it in the real game?"
