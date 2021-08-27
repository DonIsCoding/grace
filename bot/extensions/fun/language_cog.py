from logging import critical

from discord.ext.commands import Cog, command
from discord import Message
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from bot.models.extensions.fun.language.trigger import Trigger


class LanguageCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        # I know not everyone working here is familiar with NLTK so I'll explain some of the terminology.
        # Not to be confused with Auth Tokens, tokenization just means splitting the natural language
        # into discrete meaningful chunks, usually it's words, but words like "it's" or "ain't" will be
        # split into "it is" and "are not".
        # We're using the casual tokenizer for now, but it can be changed down the line so long as you're
        # aware of any new behaviors. https://www.nltk.org/api/nltk.tokenize.html

        self.tokenizer = TweetTokenizer()
        self.sid = SentimentIntensityAnalyzer()

        # Linus trigger model
        self.linus_trigger = Trigger.where(name="Linus").first()

    async def penguin_react(self, message: Message):
        """
        Checks to see if a message contains a reference to Linus (torvalds only), will be made more complicated
        as needed. If a linus reference is positively identified, Grace will react with a penguin emoji.
        I know using NLTK is kinda like bringing a tomahawk missile to a knife fight, but it may come in handy for
        future tasks, so the tokenizer object will be shared across all methods.

        :param message: A discord message to check for references to our lord and savior.
        :return: None
        """
        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = list(map(lambda s: s.lower(), message_tokens))
        linustarget = [i for i, x in enumerate(tokenlist) if x in self.linus_trigger.words]
        # Get the indices of all linuses in the message

        if linustarget:
            fail = False
            for linusindex in linustarget:
                try:
                    if tokenlist[linusindex + 1] == 'tech' and tokenlist[linusindex + 2] == 'tips':
                        fail = True
                    elif tokenlist[linusindex + 1] == 'and' and tokenlist[linusindex + 2] == 'lucy':
                        fail = True
                except IndexError:
                    pass

                # Here we're using the VADER algorithm to prevent Grace from reacting to messages that
                # speak negatively about linus. We run whole message through vader and if the aggregated
                # score is less than 0, then we throw it out.

                sv = self.sid.polarity_scores(message.content)
                if sv['neu'] + sv['pos'] < sv['neg'] or sv['pos'] == 0.0:
                    fail = True
                    if sv['neg'] > sv['pos']:
                        await message.add_reaction(self.linus_trigger.negative_emoji)
                        return
                overrideset = self.linus_trigger.words
                if set(overrideset) & set(tokenlist):
                    fail = False

            if not fail:
                await message.add_reaction(self.linus_trigger.positive_emoji)

    @Cog.listener()
    async def on_message(self, message):
        await self.penguin_react(message)


def setup(bot):
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon')

    bot.add_cog(LanguageCog(bot))