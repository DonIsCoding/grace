from emoji import emojize
from sqlalchemy import String, Column, Integer, column
from sqlalchemy.orm import relationship
from bot import app
from bot.models.extensions.fun.language.trigger_word import TriggerWord
from db.model import Model


class Trigger(app.base, Model):
    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    positive_emoji_code = Column(String, nullable=False)
    negative_emoji_code = Column(String, nullable=False)
    trigger_words = relationship("TriggerWord")

    @property
    def words(self):
        for trigger_word in self.trigger_words:
            yield trigger_word.word

    @property
    def positive_emoji(self):
        return emojize(self.positive_emoji_code)

    @property
    def negative_emoji(self):
        return emojize(self.negative_emoji)

    def add_trigger_word(self, trigger_word):
        TriggerWord(trigger_id=self.id, word=trigger_word).save()