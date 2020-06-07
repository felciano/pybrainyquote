# -*- coding: utf-8 -*-

import pybrainyquote

topics = ["Love", "Rabbi", "Abyss", "Inspiration"]

quote = pybrainyquote.Quote.random(topics)
print(quote)
