import asyncio
import json
import random
from dataclasses import dataclass
from typing import List

import disnake
from typing_extensions import Self

from quizbot import config
from quizbot.bot import QuizBot


def load_questions():
    with open("quizbot/data/questions.json") as f:
        return json.load(f)


@dataclass
class QuizItem:
    """
    Class that represents a quiz item as loaded from
    questions.json
    """

    question: str
    correct: str
    incorrect: List[str]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Allows us to create  QuizItem class instance from a
        quiz item dict item loaded from questions.json
        """

        return cls(
            question=data["question"],
            correct=data["correct"],
            incorrect=data["incorrect"],
        )


class Quiz:
    """
    This class handles the main logic for the Quiz presented
    to members after button click.  It shuffles, then interates
    through the available QuizItems and stores the number of
    correct/incorrectly answers questions, then displays a
    "Success" embed (3+ were answered correctly) or a "Failed" embed
    otherwise.   It also handles button timeout on the questions which
    forces a Failed state

    Attributes
    ----------
    bot: :type:`QuizBot`
        The bot object associated with this quiz for facilitating the interaction wait_for method

    message: :type:`disnake.Message`
        The original message that was sent when the button was first clicked

    member: :type:`disnake.Member`
        The member that clicked the button to start the quiz

    items: :type:`List[QuizItem]`
        A list of QuiZItem that is created on init from questions.json data

    correct: :type:`int`
        The amount of questions answered correctly

    incorrect: :type:`int`
        The amount of questions answered incorrectly
    """

    bot: QuizBot

    def __init__(self, message: disnake.Message, member: disnake.Member):

        self.message = message
        self.member = member
        # loads the list of QuizItems into self.items, then shuffles
        # the list on init so that the order of questions is different
        # each time a quiz is started
        self.items = self.load_quiz_items()
        random.shuffle(self.items)

        self.correct = 0
        self.incorrect = 0

    async def start_quiz(self):
        """
        Starts the quiz and handles all of the necessary logic for iterating
        the questions, building the embeds and buttons, then waiting for and handling
        the button click interactions.
        """

        await asyncio.sleep(2)

        # iterate the QuizItems and present the questions/answers
        # to the user
        for i, item in enumerate(self.items):

            # creates a list of all available answers and shuffles them
            answers = [item.correct] + item.incorrect
            random.shuffle(answers)

            # construct the embed and view instances
            embed = self.build_embed(item)
            view = self.create_view(answers)

            # no interaction has happened yet, so we just edit the message
            if i == 0:
                await self.message.edit(None, embed=embed, view=view)

            # button interaction has taken place at this point, so
            # we need to edit the message and also respond to the inter
            else:
                await inter.response.edit_message(None, embed=embed, view=view)

            # Waiting for the interaction from the user selecting an answer
            # if it times out, the user auto fails the quiz and will incur the cooldown
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for(
                    "button_click", check=lambda i: i.author == self.member, timeout=60
                )
            except asyncio.TimeoutError:
                try:
                    await self.message.edit(
                        "Whoops. Looks like you ran out of time which caused you to fail this time. Try again in 10 minutes.",
                        embed=None,
                        view=view.clear_items(),
                    )
                except disnake.NotFound:
                    # In case the user closes the ephemeral message.  We will just
                    # stop the view and end the quiz with no changes being made
                    pass

                except:
                    raise  # raise any other exceptions so that can be caught and fixed

                finally:
                    # always stop the view and the quiz on any exception that takes place
                    return view.stop()

            # get the answer from the button and compare to verify
            # if the selected answer is correct or not
            label = inter.component.label

            if label == item.correct:
                self.correct += 1
            else:
                self.incorrect += 1

            # stops the view (buttons) to get it out of memory and not cause
            # a memory leak with multiple views being constructed and sitting idle
            view.stop()

        # quiz has finished (ie, all questions have been asked)

        if self.correct >= 3:
            embed = config.get_correct_embed(self.member.guild.id)
            message = (
                f"Great job! You got {self.correct} out of {len(self.items)} correct!"
            )
            await self.member.add_roles(disnake.Object(id=config.quiz_role))

        else:
            message = f"So close, but you only got {self.correct} out of {len(self.items)} correct."
            embed = config.get_incorrect_embed(self.member.guild.id)

        await inter.response.edit_message(message, embed=embed, view=view.clear_items())

    def create_view(self, answers: list[str]) -> disnake.ui.View:
        """
        Create the view and add answer buttons and then returns the view

        Parameters
        ----------
        answers: :type:`List[str]`
             A list of the randomized correct/incorrect answer strings
        """
        view = disnake.ui.View()
        [
            view.add_item(disnake.ui.Button(label=a, style=disnake.ButtonStyle.primary))
            for a in answers
        ]

        return view

    def build_embed(self, item: QuizItem) -> disnake.Embed:
        """Builds the embed for the question and returns it

        Parameters
        ----------
        item: :type:`QuizItem`
            The QuizItem that represents the current question
        """

        embed = disnake.Embed(
            title="Quiz in Process", description=f"\u200b\n{item.question}\n\u200b"
        )

        return embed

    def load_quiz_items(self) -> List[QuizItem]:
        """Load the questions and answers from JSON and returns
        a lit of QuizItem objects"""
        items = []
        data = load_questions()
        for item in data:
            items.append(QuizItem.from_dict(item))

        return items
