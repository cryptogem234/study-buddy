"""
Seed script for Study Buddy.
Run from the backend/ directory:
    python seed_data.py
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import Question, Achievement, LessonCard

Base.metadata.create_all(bind=engine)

QUESTIONS = [
    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Parts of Speech (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Parts of Speech","difficulty":"easy",
     "question_text":"In the sentence 'The happy dog barked loudly,' what part of speech is 'happy'?",
     "option_a":"Noun","option_b":"Verb","option_c":"Adjective","option_d":"Adverb",
     "correct_answer":"C",
     "explanation":"'Happy' describes the noun 'dog,' so it is an adjective. Adjectives modify nouns and pronouns."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"easy",
     "question_text":"Which word in 'She runs quickly every morning' is an adverb?",
     "option_a":"She","option_b":"Runs","option_c":"Quickly","option_d":"Morning",
     "correct_answer":"C",
     "explanation":"'Quickly' modifies the verb 'runs' by telling us how she runs. Words that modify verbs are adverbs."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"medium",
     "question_text":"Identify the preposition in: 'The book is on the shelf beside the window.'",
     "option_a":"book","option_b":"is","option_c":"on","option_d":"window",
     "correct_answer":"C",
     "explanation":"'On' is a preposition showing the relationship between 'book' and 'shelf.'"},

    {"subject":"English","topic":"Parts of Speech","difficulty":"easy",
     "question_text":"What part of speech is 'happiness' in: 'Happiness fills the room'?",
     "option_a":"Verb","option_b":"Adjective","option_c":"Noun","option_d":"Adverb",
     "correct_answer":"C",
     "explanation":"'Happiness' names a concept — an abstract noun. Nouns name people, places, things, or ideas."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"easy",
     "question_text":"In 'The bird sings beautifully,' what part of speech is 'sings'?",
     "option_a":"Noun","option_b":"Adjective","option_c":"Adverb","option_d":"Verb",
     "correct_answer":"D",
     "explanation":"'Sings' is an action verb — it tells what the bird does."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"medium",
     "question_text":"Which word is a pronoun in: 'The teacher gave them extra time'?",
     "option_a":"teacher","option_b":"gave","option_c":"them","option_d":"time",
     "correct_answer":"C",
     "explanation":"'Them' is a pronoun that replaces a noun referring to a group of people. Pronouns stand in for nouns."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"medium",
     "question_text":"What type of conjunction is 'although' in: 'Although it was cold, we went outside'?",
     "option_a":"Coordinating conjunction","option_b":"Subordinating conjunction","option_c":"Correlative conjunction","option_d":"Conjunctive adverb",
     "correct_answer":"B",
     "explanation":"'Although' is a subordinating conjunction connecting a dependent clause to an independent clause."},

    {"subject":"English","topic":"Parts of Speech","difficulty":"hard",
     "question_text":"In 'Wow, that was an incredible performance!' the word 'Wow' is an example of:",
     "option_a":"Adjective","option_b":"Adverb","option_c":"Interjection","option_d":"Noun",
     "correct_answer":"C",
     "explanation":"'Wow' is an interjection — a word expressing strong emotion, grammatically separate from the rest of the sentence."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Grammar (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Grammar","difficulty":"easy",
     "question_text":"Which of the following is a complete sentence?",
     "option_a":"Running through the park.","option_b":"The tall tree in the yard.",
     "option_c":"Because it was raining hard.","option_d":"The dog chased the ball.",
     "correct_answer":"D",
     "explanation":"A complete sentence needs a subject and a predicate. 'The dog' is the subject and 'chased the ball' is the predicate. Options A–C are fragments."},

    {"subject":"English","topic":"Grammar","difficulty":"medium",
     "question_text":"Which sentence uses the correct form of the verb?",
     "option_a":"Neither the students nor the teacher were ready.",
     "option_b":"Neither the students nor the teacher was ready.",
     "option_c":"Neither the students nor the teacher are ready.",
     "option_d":"Neither the students nor the teacher be ready.",
     "correct_answer":"B",
     "explanation":"With 'neither…nor,' the verb agrees with the subject closest to it. 'Teacher' is singular, so use 'was.'"},

    {"subject":"English","topic":"Grammar","difficulty":"hard",
     "question_text":"Which sentence contains a dangling modifier?",
     "option_a":"Running to the bus, Maria dropped her backpack.",
     "option_b":"Running to the bus, the backpack was dropped.",
     "option_c":"Maria, running to the bus, dropped her backpack.",
     "option_d":"Maria dropped her backpack while running to the bus.",
     "correct_answer":"B",
     "explanation":"In option B, 'Running to the bus' appears to modify 'the backpack,' which cannot run. The modifier dangles because its subject (Maria) is missing."},

    {"subject":"English","topic":"Grammar","difficulty":"medium",
     "question_text":"Which sentence has inconsistent verb tense?",
     "option_a":"She walked to school and carried her bag.","option_b":"She walks to school and carries her bag.",
     "option_c":"She walked to school and drops her lunch.","option_d":"She will walk to school and will carry her bag.",
     "correct_answer":"C",
     "explanation":"'Walked' is past tense, but 'drops' is present tense. Verb tense must be consistent within a sentence unless the time truly changes."},

    {"subject":"English","topic":"Grammar","difficulty":"medium",
     "question_text":"Which of the following is a run-on sentence?",
     "option_a":"I like pizza, and she likes tacos.",
     "option_b":"Although it was late, they kept studying.",
     "option_c":"I was tired I went to bed.",
     "option_d":"The cat sat on the mat.",
     "correct_answer":"C",
     "explanation":"'I was tired I went to bed' fuses two independent clauses without a conjunction or punctuation — a run-on sentence. Add a period, semicolon, or comma + conjunction."},

    {"subject":"English","topic":"Grammar","difficulty":"medium",
     "question_text":"Which sentence is written in active voice?",
     "option_a":"The ball was kicked by Maria.","option_b":"The trophy was won by the team.",
     "option_c":"Maria kicked the ball.","option_d":"The song was sung by the choir.",
     "correct_answer":"C",
     "explanation":"In active voice, the subject performs the action: 'Maria (subject) kicked (verb) the ball.' In passive voice, the subject receives the action."},

    {"subject":"English","topic":"Grammar","difficulty":"hard",
     "question_text":"Which sentence uses correct parallel structure?",
     "option_a":"She enjoys swimming, to hike, and running.","option_b":"She enjoys swimming, hiking, and running.",
     "option_c":"She enjoys to swim, hiking, and to run.","option_d":"She enjoys swimming, hikes, and to run.",
     "correct_answer":"B",
     "explanation":"Parallel structure requires items in a list to have the same grammatical form. 'Swimming, hiking, and running' are all gerunds (-ing form), which is consistent."},

    {"subject":"English","topic":"Grammar","difficulty":"hard",
     "question_text":"Which sentence uses 'whom' correctly?",
     "option_a":"Whom is calling?","option_b":"To who should I address the letter?",
     "option_c":"Whom should I call?","option_d":"Who did you give it to?",
     "correct_answer":"C",
     "explanation":"Use 'whom' when it is the object of a verb or preposition (him/her test: 'Should I call him?' → him = whom). 'Who' is a subject (he/she test)."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Punctuation (7 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Punctuation","difficulty":"medium",
     "question_text":"Which sentence uses a comma correctly?",
     "option_a":"I went to the store, and I bought milk.","option_b":"I went to the store and, I bought milk.",
     "option_c":"I went, to the store and I bought milk.","option_d":"I went to the store and I, bought milk.",
     "correct_answer":"A",
     "explanation":"When two independent clauses are joined by a coordinating conjunction (like 'and'), a comma is placed before the conjunction."},

    {"subject":"English","topic":"Punctuation","difficulty":"medium",
     "question_text":"Where should an apostrophe be in: 'The cats toy was missing.'?",
     "option_a":"cats' toy","option_b":"cat's toy","option_c":"cats toy'","option_d":"No apostrophe needed",
     "correct_answer":"B",
     "explanation":"One cat owns the toy, so use 'cat's' (singular possessive) with the apostrophe before the 's.'"},

    {"subject":"English","topic":"Punctuation","difficulty":"easy",
     "question_text":"Which sentence correctly uses an apostrophe in a contraction?",
     "option_a":"Its raining outside.","option_b":"It's raining outside.","option_c":"Its' raining outside.","option_d":"I'ts raining outside.",
     "correct_answer":"B",
     "explanation":"'It's' is the contraction of 'it is.' The apostrophe replaces the missing letter 'i'. 'Its' (no apostrophe) is the possessive pronoun."},

    {"subject":"English","topic":"Punctuation","difficulty":"hard",
     "question_text":"Which sentence uses a semicolon correctly?",
     "option_a":"I wanted to go; but it was raining.","option_b":"She studied hard; therefore, she passed the test.",
     "option_c":"He likes; apples, oranges, and grapes.","option_d":"We went to the; park after school.",
     "correct_answer":"B",
     "explanation":"A semicolon joins two closely related independent clauses. With a conjunctive adverb like 'therefore,' use a semicolon before it and a comma after."},

    {"subject":"English","topic":"Punctuation","difficulty":"medium",
     "question_text":"Which sentence correctly uses a colon?",
     "option_a":"I need: milk and eggs.","option_b":"She said: that she was tired.",
     "option_c":"I need three things: milk, eggs, and bread.","option_d":"He was: tall, strong, and fast.",
     "correct_answer":"C",
     "explanation":"A colon introduces a list, explanation, or elaboration. It should follow a complete independent clause — 'I need three things' is complete before the colon."},

    {"subject":"English","topic":"Punctuation","difficulty":"medium",
     "question_text":"Which sentence correctly punctuates a direct quotation?",
     "option_a":'She said, "I will be there at noon."',"option_b":'She said "I will be there at noon".',
     "option_c":'She said, I will be there at noon.',"option_d":'She, said "I will be there at noon."',
     "correct_answer":"A",
     "explanation":"Direct quotations use quotation marks around the speaker's exact words. A comma separates the dialogue tag from the quotation, and the period goes inside the closing quotation mark."},

    {"subject":"English","topic":"Punctuation","difficulty":"medium",
     "question_text":"Which sentence correctly uses a comma after an introductory clause?",
     "option_a":"When the rain stopped we went outside.","option_b":"When the rain stopped, we went outside.",
     "option_c":"When, the rain stopped we went outside.","option_d":"When the rain, stopped we went outside.",
     "correct_answer":"B",
     "explanation":"When a sentence begins with a dependent (introductory) clause, place a comma after it before the main clause begins."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Vocabulary (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Vocabulary","difficulty":"medium",
     "question_text":"What does the word 'benevolent' most nearly mean?",
     "option_a":"Cruel and harsh","option_b":"Kind and generous","option_c":"Lazy and careless","option_d":"Brave and bold",
     "correct_answer":"B",
     "explanation":"'Benevolent' comes from Latin 'bene' (well) + 'volens' (wishing). It describes someone kind and generous who wishes others well."},

    {"subject":"English","topic":"Vocabulary","difficulty":"hard",
     "question_text":"Which word is a synonym for 'eloquent'?",
     "option_a":"Clumsy","option_b":"Silent","option_c":"Articulate","option_d":"Confused",
     "correct_answer":"C",
     "explanation":"'Eloquent' means able to express ideas fluently and persuasively. 'Articulate' shares this meaning."},

    {"subject":"English","topic":"Vocabulary","difficulty":"medium",
     "question_text":"What does 'ambiguous' mean?",
     "option_a":"Clearly understood","option_b":"Very dangerous","option_c":"Open to more than one interpretation; unclear","option_d":"Extremely large",
     "correct_answer":"C",
     "explanation":"'Ambiguous' describes something that can be understood in more than one way, making it unclear or confusing. Root: Latin 'ambigere' (to wander about)."},

    {"subject":"English","topic":"Vocabulary","difficulty":"medium",
     "question_text":"A 'meticulous' person is best described as:",
     "option_a":"Careless and rushed","option_b":"Showing extreme care and attention to detail","option_c":"Very loud and enthusiastic","option_d":"Shy and introverted",
     "correct_answer":"B",
     "explanation":"'Meticulous' comes from Latin 'metus' (fear). A meticulous person is extremely careful and precise, paying attention to every small detail."},

    {"subject":"English","topic":"Vocabulary","difficulty":"medium",
     "question_text":"Read: 'The parched hiker drank three bottles of water.' What does 'parched' mean?",
     "option_a":"Energetic","option_b":"Extremely thirsty or dry","option_c":"Lost and confused","option_d":"Tired and sleepy",
     "correct_answer":"B",
     "explanation":"Context clue: the hiker drank three bottles of water, suggesting extreme thirst. 'Parched' means very dry or extremely thirsty."},

    {"subject":"English","topic":"Vocabulary","difficulty":"easy",
     "question_text":"The prefix 'mis-' (as in 'misunderstand' or 'misbehave') means:",
     "option_a":"Again","option_b":"Before","option_c":"Not or wrongly","option_d":"After",
     "correct_answer":"C",
     "explanation":"The prefix 'mis-' means wrongly or badly. Misunderstand = understand wrongly. Misbehave = behave badly. Misplace = place wrongly."},

    {"subject":"English","topic":"Vocabulary","difficulty":"easy",
     "question_text":"The suffix '-ology' (as in 'biology' or 'geology') means:",
     "option_a":"Fear of","option_b":"The study of","option_c":"Full of","option_d":"Without",
     "correct_answer":"B",
     "explanation":"'-ology' comes from Greek 'logos' (word, reason). Biology = study of life. Geology = study of Earth. Psychology = study of the mind."},

    {"subject":"English","topic":"Vocabulary","difficulty":"medium",
     "question_text":"The Latin root 'aud' (as in 'auditorium,' 'audible,' 'audience') means:",
     "option_a":"See","option_b":"Write","option_c":"Carry","option_d":"Hear",
     "correct_answer":"D",
     "explanation":"The root 'aud' means hear. An auditorium is a place where you hear performances. Audible means able to be heard. The audience listens."},

    {"subject":"English","topic":"Vocabulary","difficulty":"easy",
     "question_text":"Which word is a synonym for 'abundant'?",
     "option_a":"Scarce","option_b":"Plentiful","option_c":"Ancient","option_d":"Fragile",
     "correct_answer":"B",
     "explanation":"'Abundant' means existing in large quantities. 'Plentiful' is its synonym — both mean more than enough. Antonyms include 'scarce' and 'rare.'"},

    {"subject":"English","topic":"Vocabulary","difficulty":"easy",
     "question_text":"What is the antonym (opposite) of 'timid'?",
     "option_a":"Shy","option_b":"Nervous","option_c":"Fearful","option_d":"Bold",
     "correct_answer":"D",
     "explanation":"'Timid' means shy, nervous, or lacking confidence. Its antonym is 'bold' — showing confidence and courage without fear."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Reading Comprehension (12 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Reading Comprehension","difficulty":"easy",
     "question_text":"Read: 'Scientists discovered a fish called the snailfish living 8,000 meters below the ocean surface in the Mariana Trench. The fish adapted to survive crushing pressure that would destroy most creatures. Despite harsh conditions, researchers found them thriving in large numbers. This suggests life can exist in environments far more extreme than previously imagined.'\n\nWhat is the MAIN IDEA of this passage?",
     "option_a":"The Mariana Trench is a dangerous place","option_b":"Fish are difficult to study","option_c":"Scientists discovered deep-sea fish thriving in extreme conditions","option_d":"Most creatures cannot survive deep underwater",
     "correct_answer":"C",
     "explanation":"The main idea is the most important point. The passage focuses on the surprising discovery of fish surviving in extreme deep-sea conditions."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"medium",
     "question_text":"Read: 'Scientists discovered a fish called the snailfish living 8,000 meters below the ocean surface in the Mariana Trench. The fish adapted to survive crushing pressure that would destroy most creatures. Despite harsh conditions, researchers found them thriving in large numbers. This suggests life can exist in environments far more extreme than previously imagined.'\n\nWhat can be INFERRED from this discovery?",
     "option_a":"The ocean is fully explored","option_b":"Life may exist in more extreme environments than once thought","option_c":"Snailfish are the most common fish in the world","option_d":"Scientists have stopped exploring the deep ocean",
     "correct_answer":"B",
     "explanation":"An inference uses text clues plus your knowledge. The passage says the discovery 'suggests life can exist in more extreme environments' — directly supporting this inference."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"medium",
     "question_text":"Read: 'Scientists discovered a fish called the snailfish living 8,000 meters below the ocean surface in the Mariana Trench. The fish adapted to survive crushing pressure that would destroy most creatures.'\n\nBased on context, 'adapted' most likely means:",
     "option_a":"Refused to change","option_b":"Slowly disappeared","option_c":"Changed over time to survive in a specific environment","option_d":"Moved to a new location",
     "correct_answer":"C",
     "explanation":"Context clue: adapted allowed the fish to 'survive crushing pressure.' This shows that 'adapted' means changed or adjusted to fit the environment."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"easy",
     "question_text":"Read: 'The empty lot on Oak Street had been an eyesore for years. When residents decided to transform it into a community garden, they faced obstacles: no funding, rocky soil, and skeptical neighbors. Through bake sales and hard work, the garden flourished. By summer's end, 300 pounds of vegetables were donated to local food banks.'\n\nWhich obstacle did residents face?",
     "option_a":"Too many plants","option_b":"No funding","option_c":"Government opposition","option_d":"Too much water",
     "correct_answer":"B",
     "explanation":"The passage directly states the obstacles: 'no funding, rocky soil, and skeptical neighbors.' No funding is listed as the first challenge."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"medium",
     "question_text":"Read: 'The empty lot on Oak Street had been an eyesore for years. When residents decided to transform it into a community garden, they faced obstacles: no funding, rocky soil, and skeptical neighbors.'\n\nWhat does 'eyesore' most likely mean?",
     "option_a":"Something beautiful","option_b":"Something that is painful","option_c":"Something ugly or unpleasant to look at","option_d":"Something that stings the eyes",
     "correct_answer":"C",
     "explanation":"Context clue: the residents wanted to 'transform' the lot, suggesting it was undesirable. An 'eyesore' is something ugly or unpleasant to look at."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"hard",
     "question_text":"Read: 'The empty lot on Oak Street had been an eyesore for years. When residents decided to transform it into a community garden, they faced obstacles: no funding, rocky soil, and skeptical neighbors. Through bake sales and hard work, the garden flourished. By summer's end, 300 pounds of vegetables were donated to local food banks.'\n\nWhat was the author's PRIMARY purpose?",
     "option_a":"To warn people about empty lots","option_b":"To persuade readers to start a garden","option_c":"To inform readers about one community's problem-solving success","option_d":"To entertain with a funny story",
     "correct_answer":"C",
     "explanation":"Author's purpose: this passage presents facts about a real community effort without pushing an opinion (not persuasive) or telling a fictional story. It informs about a success story."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"easy",
     "question_text":"Read: 'Johannes Gutenberg invented the printing press in 1440, revolutionizing the spread of information. Before this, books had to be copied by hand, making them expensive and rare. With the printing press, books were produced quickly and cheaply. Historians credit this invention with enabling the Renaissance, the Reformation, and the Scientific Revolution.'\n\nWhat was one EFFECT of the printing press?",
     "option_a":"Books became more expensive","option_b":"Only wealthy people could read","option_c":"Ideas spread more quickly across Europe","option_d":"Fewer books were written",
     "correct_answer":"C",
     "explanation":"The passage states books could be 'produced quickly and cheaply, allowing ideas to spread.' This is a direct effect mentioned in the text."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"easy",
     "question_text":"Read: 'Johannes Gutenberg invented the printing press in 1440, revolutionizing the spread of information. Before this, books had to be copied by hand, making them expensive and rare.'\n\nWhy were books expensive before the printing press?",
     "option_a":"Paper was very rare","option_b":"They had to be copied by hand","option_c":"Writers demanded high payment","option_d":"The government taxed books",
     "correct_answer":"B",
     "explanation":"The passage directly states: 'books had to be copied by hand, making them expensive and rare.' This is a detail question answered explicitly in the text."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"medium",
     "question_text":"Read: 'Johannes Gutenberg invented the printing press in 1440, revolutionizing the spread of information. Before this, books had to be copied by hand, making them expensive and rare. With the printing press, books were produced quickly and cheaply. Historians credit this invention with enabling the Renaissance, the Reformation, and the Scientific Revolution.'\n\nWhich text structure does this passage MAINLY use?",
     "option_a":"Problem-solution","option_b":"Compare-contrast","option_c":"Cause and effect","option_d":"Description",
     "correct_answer":"C",
     "explanation":"The passage shows how the printing press (cause) led to cheap books, the spread of ideas, and major historical movements (effects). Signal words: 'revolutionizing,' 'allowing,' 'enabling.'"},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"easy",
     "question_text":"Read: 'Rainforests cover only 6% of Earth's surface, yet they are home to more than half of the world's plant and animal species. The Amazon alone produces 20% of the world's oxygen. Despite their importance, rainforests are disappearing due to deforestation. Scientists predict they could vanish within 100 years.'\n\nWhat percentage of Earth's species live in rainforests?",
     "option_a":"6%","option_b":"20%","option_c":"More than 50%","option_d":"100%",
     "correct_answer":"C",
     "explanation":"The passage states rainforests are 'home to more than half of the world's plant and animal species.' More than half = more than 50%."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"medium",
     "question_text":"Read: 'Rainforests cover only 6% of Earth's surface, yet they are home to more than half of the world's plant and animal species. The Amazon alone produces 20% of the world's oxygen. Despite their importance, rainforests are disappearing due to deforestation. Scientists predict they could vanish within 100 years.'\n\nWhat INFERENCE can be made from the last sentence?",
     "option_a":"Rainforests are growing rapidly","option_b":"Scientists are optimistic about rainforest preservation","option_c":"Human activity must change to protect rainforests","option_d":"Deforestation is helpful for the environment",
     "correct_answer":"C",
     "explanation":"The passage implies a problem (disappearing rainforests) without stating a direct solution. Inferring that human action is needed is supported by the urgency of the text."},

    {"subject":"English","topic":"Reading Comprehension","difficulty":"hard",
     "question_text":"Read: 'Rainforests cover only 6% of Earth's surface, yet they are home to more than half of the world's plant and animal species. The Amazon alone produces 20% of the world's oxygen. Despite their importance, rainforests are disappearing due to deforestation. Scientists predict they could vanish within 100 years.'\n\nWhich word BEST describes the author's tone?",
     "option_a":"Humorous","option_b":"Indifferent","option_c":"Urgent and concerned","option_d":"Celebratory",
     "correct_answer":"C",
     "explanation":"Tone is the author's attitude. Words like 'despite their importance,' 'disappearing,' and 'could vanish' signal urgency and concern about a serious environmental problem."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Literary Devices (12 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Literary Devices","difficulty":"easy",
     "question_text":"'Her smile was as bright as the sun.' What literary device is used?",
     "option_a":"Metaphor","option_b":"Simile","option_c":"Personification","option_d":"Alliteration",
     "correct_answer":"B",
     "explanation":"A simile compares two things using 'like' or 'as.' Here the smile is compared to the sun using 'as.'"},

    {"subject":"English","topic":"Literary Devices","difficulty":"easy",
     "question_text":"'Life is a rollercoaster.' What literary device is used?",
     "option_a":"Simile","option_b":"Hyperbole","option_c":"Metaphor","option_d":"Alliteration",
     "correct_answer":"C",
     "explanation":"A metaphor makes a direct comparison without 'like' or 'as.' Life is directly called a rollercoaster."},

    {"subject":"English","topic":"Literary Devices","difficulty":"easy",
     "question_text":"'The leaves danced in the breeze.' What literary device is used?",
     "option_a":"Simile","option_b":"Onomatopoeia","option_c":"Alliteration","option_d":"Personification",
     "correct_answer":"D",
     "explanation":"Personification gives human qualities to non-human things. Leaves cannot actually dance — this gives them a human action."},

    {"subject":"English","topic":"Literary Devices","difficulty":"easy",
     "question_text":"'She sells seashells by the seashore.' What literary device is this?",
     "option_a":"Hyperbole","option_b":"Simile","option_c":"Alliteration","option_d":"Metaphor",
     "correct_answer":"C",
     "explanation":"Alliteration is the repetition of the same consonant sound at the beginning of nearby words. The 's' sound is repeated throughout."},

    {"subject":"English","topic":"Literary Devices","difficulty":"easy",
     "question_text":"'The clock tick-tocked quietly.' What literary device is used?",
     "option_a":"Metaphor","option_b":"Alliteration","option_c":"Personification","option_d":"Onomatopoeia",
     "correct_answer":"D",
     "explanation":"Onomatopoeia is when a word imitates the sound it describes. 'Tick-tocked' sounds like the actual sound a clock makes."},

    {"subject":"English","topic":"Literary Devices","difficulty":"medium",
     "question_text":"'I have a million things to do today!' What literary device is this?",
     "option_a":"Understatement","option_b":"Personification","option_c":"Hyperbole","option_d":"Irony",
     "correct_answer":"C",
     "explanation":"Hyperbole is extreme exaggeration to make a point. The speaker does not literally have a million things — it expresses feeling very busy."},

    {"subject":"English","topic":"Literary Devices","difficulty":"medium",
     "question_text":"In a novel, a character notices storm clouds gathering on the day of a wedding, hinting something bad will happen. What is this?",
     "option_a":"Irony","option_b":"Flashback","option_c":"Foreshadowing","option_d":"Allusion",
     "correct_answer":"C",
     "explanation":"Foreshadowing is when an author hints at future events. Storm clouds suggest trouble ahead — the reader senses something bad is coming."},

    {"subject":"English","topic":"Literary Devices","difficulty":"hard",
     "question_text":"A character says 'Oh great, another Monday' after waking up to a pile of problems. What literary device is this?",
     "option_a":"Simile","option_b":"Verbal irony","option_c":"Understatement","option_d":"Personification",
     "correct_answer":"B",
     "explanation":"Verbal irony occurs when someone says the opposite of what they mean. 'Oh great' is said sarcastically — they do not actually think it is great."},

    {"subject":"English","topic":"Literary Devices","difficulty":"hard",
     "question_text":"Sarah says 'no big deal' about 4 hours of homework. This is an example of:",
     "option_a":"Hyperbole","option_b":"Allusion","option_c":"Understatement","option_d":"Metaphor",
     "correct_answer":"C",
     "explanation":"Understatement is the opposite of hyperbole — making something seem much less significant than it is. 4 hours of homework is a big deal, so calling it 'no big deal' is understatement."},

    {"subject":"English","topic":"Literary Devices","difficulty":"medium",
     "question_text":"Which sentence contains a SIMILE?",
     "option_a":"The sun is a giant fireball.","option_b":"The moon smiled down at the sleeping city.","option_c":"Running like a cheetah, she crossed the finish line first.","option_d":"Thunder clapped above the mountains.",
     "correct_answer":"C",
     "explanation":"Option C contains a simile — comparing her running to a cheetah using the word 'like.' Option A is a metaphor; option B is personification."},

    {"subject":"English","topic":"Literary Devices","difficulty":"medium",
     "question_text":"In a story, a white dove appears whenever two characters reconcile, representing peace. This is:",
     "option_a":"Foreshadowing","option_b":"Alliteration","option_c":"Symbolism","option_d":"Hyperbole",
     "correct_answer":"C",
     "explanation":"Symbolism is when an object represents a larger idea. The white dove traditionally symbolizes peace and reconciliation beyond its literal meaning."},

    {"subject":"English","topic":"Literary Devices","difficulty":"hard",
     "question_text":"A story follows a girl who overcomes poverty to become a scientist. The central message is that determination can overcome any obstacle. This is called:",
     "option_a":"The setting","option_b":"The plot","option_c":"The theme","option_d":"The mood",
     "correct_answer":"C",
     "explanation":"The theme is the central message or universal lesson of a story — what the author wants readers to take away. Plot is what happens; theme is what it means."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Figurative Language (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Figurative Language","difficulty":"easy",
     "question_text":"What does the idiom 'it's raining cats and dogs' mean?",
     "option_a":"Cats and dogs are falling from the sky","option_b":"It is raining very heavily","option_c":"Cats and dogs do not like rain","option_d":"The weather is unpredictable",
     "correct_answer":"B",
     "explanation":"An idiom means something different from its literal words. 'Raining cats and dogs' is an expression meaning it's raining very hard."},

    {"subject":"English","topic":"Figurative Language","difficulty":"easy",
     "question_text":"If someone says 'break a leg' before your performance, they mean:",
     "option_a":"Be careful not to get hurt","option_b":"Good luck and do your best","option_c":"Leave quickly","option_d":"Stop performing",
     "correct_answer":"B",
     "explanation":"'Break a leg' is an idiom wishing someone good luck, especially in theater. The literal meaning (injure your leg) is the opposite of the intended meaning."},

    {"subject":"English","topic":"Figurative Language","difficulty":"medium",
     "question_text":"'Don't judge a book by its cover' means:",
     "option_a":"Books with colorful covers are better","option_b":"Do not read books you haven't researched","option_c":"Do not judge people or things only by their appearance","option_d":"Library books should not be judged",
     "correct_answer":"C",
     "explanation":"This proverb means you should not form an opinion about something based only on outward appearance — true quality is deeper than looks."},

    {"subject":"English","topic":"Figurative Language","difficulty":"medium",
     "question_text":"Which sentence uses figurative language?",
     "option_a":"The tree is 12 feet tall.","option_b":"She has two blue eyes.","option_c":"He is the lion of the team.","option_d":"The car is red.",
     "correct_answer":"C",
     "explanation":"'He is the lion of the team' is a metaphor — comparing him to a lion to suggest strength and leadership. Options A, B, and D are literal statements."},

    {"subject":"English","topic":"Figurative Language","difficulty":"medium",
     "question_text":"'The stars were like tiny diamonds scattered across the sky.' This sentence contains:",
     "option_a":"A metaphor","option_b":"A simile","option_c":"Personification","option_d":"An idiom",
     "correct_answer":"B",
     "explanation":"A simile compares using 'like' or 'as.' Stars are being compared to diamonds using 'like.'"},

    {"subject":"English","topic":"Figurative Language","difficulty":"medium",
     "question_text":"'The hungry computer devoured all my files.' What literary device is used?",
     "option_a":"Simile","option_b":"Alliteration","option_c":"Personification","option_d":"Onomatopoeia",
     "correct_answer":"C",
     "explanation":"Personification gives human or animal qualities to non-human things. A computer cannot be 'hungry' or 'devour' — these are human/animal traits."},

    {"subject":"English","topic":"Figurative Language","difficulty":"easy",
     "question_text":"'I'm so hungry I could eat a horse.' This is an example of:",
     "option_a":"Simile","option_b":"Symbolism","option_c":"Hyperbole","option_d":"Irony",
     "correct_answer":"C",
     "explanation":"Hyperbole is wild exaggeration for effect. You cannot literally eat a horse — the speaker is exaggerating to show extreme hunger."},

    {"subject":"English","topic":"Figurative Language","difficulty":"medium",
     "question_text":"'The thunder roared angrily.' What literary device is used?",
     "option_a":"Simile","option_b":"Personification","option_c":"Onomatopoeia","option_d":"Alliteration",
     "correct_answer":"B",
     "explanation":"Personification gives thunder the human emotion of anger ('angrily') and the human action of roaring. Thunder cannot actually feel angry."},

    # ══════════════════════════════════════════════════════════════
    # ENGLISH — Text Structure (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"English","topic":"Text Structure","difficulty":"easy",
     "question_text":"Which words are SIGNAL WORDS for cause-and-effect text structure?",
     "option_a":'"first," "next," "finally"',"option_b":'"similarly," "in contrast," "however"',
     "option_c":'"because," "as a result," "therefore"',"option_d":'"for example," "such as," "including"',
     "correct_answer":"C",
     "explanation":"Cause-and-effect signal words show a relationship between reasons and results: because (cause), as a result / therefore (effect)."},

    {"subject":"English","topic":"Text Structure","difficulty":"medium",
     "question_text":"'Due to the drought, crops failed across the region. As a result, food prices rose sharply.' Which text structure is this?",
     "option_a":"Compare and contrast","option_b":"Problem and solution","option_c":"Cause and effect","option_d":"Sequence",
     "correct_answer":"C",
     "explanation":"'Due to' signals a cause (drought), and 'as a result' signals the effect (rising prices). This is classic cause-and-effect structure."},

    {"subject":"English","topic":"Text Structure","difficulty":"easy",
     "question_text":"Which signal words indicate a COMPARE-AND-CONTRAST text structure?",
     "option_a":'"because," "since," "consequently"',"option_b":'"first," "second," "then"',
     "option_c":'"likewise," "on the other hand," "in contrast"',"option_d":'"for instance," "to illustrate"',
     "correct_answer":"C",
     "explanation":"Compare-and-contrast signal words show similarities (likewise, similarly) or differences (on the other hand, in contrast, however)."},

    {"subject":"English","topic":"Text Structure","difficulty":"medium",
     "question_text":"A text describes how snakes and lizards are both reptiles but differ because snakes have no legs. What structure is this?",
     "option_a":"Problem and solution","option_b":"Compare and contrast","option_c":"Cause and effect","option_d":"Description",
     "correct_answer":"B",
     "explanation":"The text shows both similarities (both are reptiles) and differences (legs vs. no legs) — the hallmark of compare-and-contrast structure."},

    {"subject":"English","topic":"Text Structure","difficulty":"medium",
     "question_text":"Which text structure BEST fits an article about 'how scientists solved the problem of disappearing bees'?",
     "option_a":"Sequence","option_b":"Description","option_c":"Cause and effect","option_d":"Problem and solution",
     "correct_answer":"D",
     "explanation":"The article presents a problem (disappearing bees) and explains solutions — that is the problem-and-solution text structure."},

    {"subject":"English","topic":"Text Structure","difficulty":"easy",
     "question_text":"A recipe that lists steps in the order they must be followed uses which text structure?",
     "option_a":"Description","option_b":"Problem and solution","option_c":"Sequence","option_d":"Cause and effect",
     "correct_answer":"C",
     "explanation":"A recipe follows steps in order: first, second, then, finally. This ordered, step-by-step organization is the sequence (chronological) text structure."},

    {"subject":"English","topic":"Text Structure","difficulty":"easy",
     "question_text":"Which words signal a SEQUENCE / CHRONOLOGICAL text structure?",
     "option_a":'"although," "despite," "however"',"option_b":'"first," "next," "after that," "finally"',
     "option_c":'"for example," "such as"',"option_d":'"because," "therefore"',
     "correct_answer":"B",
     "explanation":"Sequence signal words show the order of events or steps: first, next, then, after that, finally, subsequently."},

    {"subject":"English","topic":"Text Structure","difficulty":"medium",
     "question_text":"A paragraph describes how a frog looks, feels, and behaves without comparing or showing cause/effect. What structure?",
     "option_a":"Problem and solution","option_b":"Sequence","option_c":"Compare and contrast","option_d":"Description",
     "correct_answer":"D",
     "explanation":"Description text structure presents detailed information about a topic's characteristics — what it looks like, how it behaves — without focusing on time order, comparisons, or causes."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Cells (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Cells","difficulty":"easy",
     "question_text":"Which organelle is called the 'powerhouse of the cell' because it produces energy (ATP)?",
     "option_a":"Nucleus","option_b":"Ribosome","option_c":"Mitochondria","option_d":"Vacuole",
     "correct_answer":"C",
     "explanation":"Mitochondria produce ATP through cellular respiration. ATP is the main energy currency used by cells to carry out their functions."},

    {"subject":"Science","topic":"Cells","difficulty":"medium",
     "question_text":"Which structure is found in plant cells but NOT in animal cells?",
     "option_a":"Cell membrane","option_b":"Nucleus","option_c":"Chloroplast","option_d":"Mitochondria",
     "correct_answer":"C",
     "explanation":"Chloroplasts contain chlorophyll and perform photosynthesis — a process only in plants (and some algae). Animal cells lack chloroplasts."},

    {"subject":"Science","topic":"Cells","difficulty":"easy",
     "question_text":"What is the PRIMARY function of the cell membrane?",
     "option_a":"To produce energy for the cell","option_b":"To control what enters and exits the cell","option_c":"To make proteins for the cell","option_d":"To store genetic information",
     "correct_answer":"B",
     "explanation":"The cell membrane is a flexible barrier that regulates what enters and exits the cell, maintaining homeostasis. It acts like a gatekeeper."},

    {"subject":"Science","topic":"Cells","difficulty":"easy",
     "question_text":"Which organelle is called the 'control center' of the cell because it contains DNA?",
     "option_a":"Mitochondria","option_b":"Ribosome","option_c":"Nucleus","option_d":"Vacuole",
     "correct_answer":"C",
     "explanation":"The nucleus contains DNA, which carries the instructions for all cellular activities. It controls what proteins are made and directs cell functions."},

    {"subject":"Science","topic":"Cells","difficulty":"medium",
     "question_text":"What is the main job of ribosomes?",
     "option_a":"They produce energy through respiration","option_b":"They package and ship proteins out of the cell","option_c":"They synthesize (build) proteins","option_d":"They break down cellular waste",
     "correct_answer":"C",
     "explanation":"Ribosomes are the cell's protein factories. They read instructions from DNA (via mRNA) and assemble amino acids into proteins."},

    {"subject":"Science","topic":"Cells","difficulty":"medium",
     "question_text":"In plant cells, the large central vacuole primarily:",
     "option_a":"Produces chlorophyll","option_b":"Stores water, nutrients, and waste; provides structural support","option_c":"Creates energy through photosynthesis","option_d":"Digests old cell parts",
     "correct_answer":"B",
     "explanation":"The large central vacuole stores water, helping the plant cell maintain shape and rigidity. It also stores nutrients and waste products."},

    {"subject":"Science","topic":"Cells","difficulty":"medium",
     "question_text":"Which statement about the cell wall is correct?",
     "option_a":"Both plant and animal cells have cell walls","option_b":"Only animal cells have cell walls","option_c":"The cell wall is made of cholesterol","option_d":"Only plant cells have cell walls, made of cellulose",
     "correct_answer":"D",
     "explanation":"Plant cells have a rigid cell wall made of cellulose that provides extra support and shape. Animal cells have only a flexible cell membrane."},

    {"subject":"Science","topic":"Cells","difficulty":"hard",
     "question_text":"What is the key difference between prokaryotic and eukaryotic cells?",
     "option_a":"Prokaryotes are larger than eukaryotes","option_b":"Eukaryotic cells have a membrane-bound nucleus; prokaryotic cells do not","option_c":"Prokaryotes have more organelles than eukaryotes","option_d":"Eukaryotes do not have DNA",
     "correct_answer":"B",
     "explanation":"Prokaryotes (like bacteria) lack a membrane-bound nucleus — their DNA floats freely in the cytoplasm. Eukaryotes (animals, plants, fungi) have a nucleus surrounded by a membrane."},

    {"subject":"Science","topic":"Cells","difficulty":"hard",
     "question_text":"Which of the following is NOT part of the cell theory?",
     "option_a":"All living things are made of cells","option_b":"Cells are the basic unit of life","option_c":"New cells come only from existing cells","option_d":"All cells have a cell wall",
     "correct_answer":"D",
     "explanation":"Cell theory has three principles: (1) all living things are made of cells, (2) cells are the basic unit of life, and (3) all cells come from pre-existing cells. Not all cells have cell walls."},

    {"subject":"Science","topic":"Cells","difficulty":"medium",
     "question_text":"A cell placed in a very salty solution loses water and shrivels. This movement of water across the cell membrane is called:",
     "option_a":"Diffusion","option_b":"Active transport","option_c":"Osmosis","option_d":"Photosynthesis",
     "correct_answer":"C",
     "explanation":"Osmosis is the movement of water across a semi-permeable membrane from high water concentration to lower water concentration. The cell shrinks because water moves out into the salty solution."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Genetics (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Genetics","difficulty":"easy",
     "question_text":"What does DNA stand for, and what is its function?",
     "option_a":"Dynamic Nuclear Acid; produces energy","option_b":"Deoxyribonucleic Acid; carries genetic information","option_c":"Double Nucleic Acid; helps cells divide","option_d":"Deoxyribonucleic Acid; produces proteins directly",
     "correct_answer":"B",
     "explanation":"DNA (Deoxyribonucleic Acid) is the molecule that carries the genetic blueprint for all living organisms, determining traits and instructing cells how to function."},

    {"subject":"Science","topic":"Genetics","difficulty":"easy",
     "question_text":"What is a gene?",
     "option_a":"A type of protein in the bloodstream","option_b":"A segment of DNA that codes for a specific trait or protein","option_c":"The entire chromosome of an organism","option_d":"A chemical that turns genes on or off",
     "correct_answer":"B",
     "explanation":"A gene is a specific sequence of DNA that contains instructions for making a protein or controlling a trait. Humans have approximately 20,000–25,000 genes."},

    {"subject":"Science","topic":"Genetics","difficulty":"easy",
     "question_text":"If a dominant allele is present with a recessive allele, which trait will appear?",
     "option_a":"The recessive trait","option_b":"A blend of both traits","option_c":"Neither trait","option_d":"The dominant trait",
     "correct_answer":"D",
     "explanation":"A dominant allele masks the effect of a recessive allele when both are present. The dominant trait shows in the organism's appearance (phenotype)."},

    {"subject":"Science","topic":"Genetics","difficulty":"medium",
     "question_text":"Two parents who are both Tt (heterozygous) cross. What percentage of offspring will show the dominant trait?",
     "option_a":"25%","option_b":"50%","option_c":"75%","option_d":"100%",
     "correct_answer":"C",
     "explanation":"A Tt × Tt cross produces: TT (25%), Tt (50%), tt (25%). Offspring with at least one T (75%) show the dominant trait. Only tt (25%) shows the recessive trait."},

    {"subject":"Science","topic":"Genetics","difficulty":"medium",
     "question_text":"What is the difference between phenotype and genotype?",
     "option_a":"Genotype is the physical appearance; phenotype is the genetic makeup","option_b":"Phenotype is the physical appearance; genotype is the genetic makeup","option_c":"They mean the same thing","option_d":"Genotype only applies to recessive traits",
     "correct_answer":"B",
     "explanation":"Genotype is the actual genetic code (like TT or Tt). Phenotype is the observable physical trait that results from that genetic code (like brown eyes)."},

    {"subject":"Science","topic":"Genetics","difficulty":"medium",
     "question_text":"Which of the following is an ACQUIRED trait (not inherited from parents)?",
     "option_a":"Eye color","option_b":"Blood type","option_c":"A scar from an injury","option_d":"Natural hair texture",
     "correct_answer":"C",
     "explanation":"Acquired traits develop during a person's lifetime due to environment or experience — like scars, calluses, or a learned skill. Inherited traits are passed through DNA from parents."},

    {"subject":"Science","topic":"Genetics","difficulty":"medium",
     "question_text":"How many chromosomes does a typical human body cell contain?",
     "option_a":"23","option_b":"46","option_c":"2","option_d":"92",
     "correct_answer":"B",
     "explanation":"Human body cells (somatic cells) contain 46 chromosomes arranged in 23 pairs. You inherit one chromosome in each pair from your mother and one from your father."},

    {"subject":"Science","topic":"Genetics","difficulty":"hard",
     "question_text":"A mutation in DNA is best described as:",
     "option_a":"The successful passing of traits from parent to offspring","option_b":"A change in the DNA sequence that may or may not affect the organism","option_c":"The process of making new cells","option_d":"A disease caused by bacteria",
     "correct_answer":"B",
     "explanation":"A mutation is a change in the DNA sequence. Some mutations are harmful, some beneficial, and many are neutral. Mutations are the source of genetic variation in a population."},

    {"subject":"Science","topic":"Genetics","difficulty":"medium",
     "question_text":"What are alleles?",
     "option_a":"Sections of the cell membrane that control gene expression","option_b":"The different versions of a gene (e.g., brown eye gene vs. blue eye gene)","option_c":"The 46 chromosomes in human cells","option_d":"Proteins produced by ribosomes",
     "correct_answer":"B",
     "explanation":"Alleles are different versions of the same gene. For example, the gene for eye color has alleles for brown, blue, green, etc. You typically have two alleles for each gene — one from each parent."},

    {"subject":"Science","topic":"Genetics","difficulty":"easy",
     "question_text":"Heredity is best defined as:",
     "option_a":"The study of the human brain","option_b":"The process by which traits are passed from parents to offspring","option_c":"The ability of cells to divide and reproduce","option_d":"Changes in organisms due to the environment",
     "correct_answer":"B",
     "explanation":"Heredity is the biological process through which traits and characteristics are passed from parents to their children through genes in DNA."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Ecosystems (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Ecosystems","difficulty":"easy",
     "question_text":"In a food chain, which organisms are the producers?",
     "option_a":"Animals that eat plants","option_b":"Animals that eat other animals","option_c":"Green plants and algae","option_d":"Bacteria that break down dead matter",
     "correct_answer":"C",
     "explanation":"Producers make their own food through photosynthesis. Green plants and algae convert sunlight into glucose, forming the base of most food chains."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"medium",
     "question_text":"What is the role of decomposers in an ecosystem?",
     "option_a":"They produce energy from sunlight.","option_b":"They hunt and eat herbivores.","option_c":"They break down dead organisms and return nutrients to the soil.","option_d":"They convert nitrogen gas into plant food.",
     "correct_answer":"C",
     "explanation":"Decomposers like bacteria and fungi break down dead plants and animals, releasing nutrients back into the soil for plants to use again."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"easy",
     "question_text":"An animal that eats ONLY plants is called a:",
     "option_a":"Carnivore","option_b":"Omnivore","option_c":"Decomposer","option_d":"Herbivore",
     "correct_answer":"D",
     "explanation":"Herbivores eat only plants (primary consumers). Carnivores eat only animals. Omnivores eat both plants and animals."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"medium",
     "question_text":"How does a food web differ from a food chain?",
     "option_a":"A food web only includes plants","option_b":"A food chain shows many interconnected relationships; a food web shows just one","option_c":"A food web shows multiple, interconnected feeding relationships; a food chain shows one linear path","option_d":"They are the same thing",
     "correct_answer":"C",
     "explanation":"A food chain shows a single linear sequence (grass → rabbit → fox). A food web shows many overlapping food chains, more accurately representing complex ecosystem feeding relationships."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"medium",
     "question_text":"In an energy pyramid, which level contains the MOST energy?",
     "option_a":"Top predators","option_b":"Secondary consumers","option_c":"Primary consumers","option_d":"Producers",
     "correct_answer":"D",
     "explanation":"Producers (plants) capture energy from the sun and contain the most energy in an ecosystem. Only about 10% of energy passes to the next level — energy decreases moving up the pyramid."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"easy",
     "question_text":"Which of the following is an ABIOTIC (non-living) factor in an ecosystem?",
     "option_a":"Mushrooms","option_b":"Bacteria in soil","option_c":"Temperature","option_d":"Grass",
     "correct_answer":"C",
     "explanation":"Abiotic factors are non-living components: temperature, sunlight, water, soil, and air. Biotic factors are all living organisms (plants, animals, bacteria, fungi)."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"medium",
     "question_text":"If the rabbit population in a field decreases, what would MOST LIKELY happen to the fox population (foxes eat rabbits)?",
     "option_a":"The fox population would increase","option_b":"The fox population would decrease","option_c":"The fox population would stay the same","option_d":"The foxes would grow larger",
     "correct_answer":"B",
     "explanation":"Foxes depend on rabbits for food. Fewer rabbits (prey) means less food for foxes (predators), so the fox population would also decrease — a classic predator-prey relationship."},

    {"subject":"Science","topic":"Ecosystems","difficulty":"hard",
     "question_text":"What is the 'carrying capacity' of an ecosystem?",
     "option_a":"The amount of water an ecosystem can hold","option_b":"The maximum population size an ecosystem can sustainably support with available resources","option_c":"The total weight of all organisms in an ecosystem","option_d":"The number of different species in an ecosystem",
     "correct_answer":"B",
     "explanation":"Carrying capacity is the maximum population size that an environment can sustainably support given available food, water, shelter, and other resources. Exceeding it causes population decline."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Photosynthesis (6 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Photosynthesis","difficulty":"medium",
     "question_text":"What are the raw materials (inputs) needed for photosynthesis?",
     "option_a":"Oxygen and glucose","option_b":"Carbon dioxide and water","option_c":"Nitrogen and sunlight","option_d":"Carbon dioxide and oxygen",
     "correct_answer":"B",
     "explanation":"Photosynthesis uses CO₂ (from air) and water (from soil) plus light energy to produce glucose and oxygen. Equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂."},

    {"subject":"Science","topic":"Photosynthesis","difficulty":"medium",
     "question_text":"In which part of the plant cell does photosynthesis mainly take place?",
     "option_a":"Mitochondria","option_b":"Nucleus","option_c":"Cell wall","option_d":"Chloroplast",
     "correct_answer":"D",
     "explanation":"Chloroplasts contain chlorophyll, which captures light energy. This is where both the light-dependent and light-independent reactions of photosynthesis occur."},

    {"subject":"Science","topic":"Photosynthesis","difficulty":"easy",
     "question_text":"What gas is RELEASED as a byproduct of photosynthesis?",
     "option_a":"Carbon dioxide","option_b":"Nitrogen","option_c":"Hydrogen","option_d":"Oxygen",
     "correct_answer":"D",
     "explanation":"During photosynthesis, plants produce glucose and oxygen. The oxygen is released through the leaves (via stomata) into the atmosphere."},

    {"subject":"Science","topic":"Photosynthesis","difficulty":"easy",
     "question_text":"Why do most plant leaves appear green?",
     "option_a":"They absorb all colors including green","option_b":"Chlorophyll absorbs red and blue light but reflects green light","option_c":"Green is the color of water inside leaf cells","option_d":"Leaves contain a green liquid called sap",
     "correct_answer":"B",
     "explanation":"Chlorophyll absorbs red and blue light energy for photosynthesis but reflects green light back to our eyes — which is why leaves look green."},

    {"subject":"Science","topic":"Photosynthesis","difficulty":"hard",
     "question_text":"During the light-dependent reactions of photosynthesis, what is the primary role of light energy?",
     "option_a":"To build glucose from carbon dioxide","option_b":"To release water from the soil","option_c":"To split water molecules and generate ATP","option_d":"To create oxygen from carbon dioxide",
     "correct_answer":"C",
     "explanation":"In the light-dependent reactions, light energy splits water molecules (photolysis), generating ATP (energy) and releasing oxygen as a byproduct. This ATP is then used to build glucose."},

    {"subject":"Science","topic":"Photosynthesis","difficulty":"medium",
     "question_text":"A plant produces glucose through photosynthesis. What can the plant use glucose for?",
     "option_a":"Only for making new cells","option_b":"For energy (respiration), building cell walls, and making stored starch","option_c":"Only for releasing oxygen","option_d":"For absorbing water from the soil",
     "correct_answer":"B",
     "explanation":"Glucose is the plant's food. It can be: (1) broken down in respiration for energy, (2) used to build cellulose for cell walls, or (3) converted to starch for long-term storage."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Water Cycle (6 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Water Cycle","difficulty":"easy",
     "question_text":"What is the process called when liquid water turns into water vapor?",
     "option_a":"Condensation","option_b":"Precipitation","option_c":"Evaporation","option_d":"Transpiration",
     "correct_answer":"C",
     "explanation":"Evaporation occurs when liquid water absorbs heat energy and changes into water vapor (gas). It is the main way water enters the atmosphere from oceans, lakes, and rivers."},

    {"subject":"Science","topic":"Water Cycle","difficulty":"medium",
     "question_text":"Which step in the water cycle involves water vapor cooling and turning into liquid droplets to form clouds?",
     "option_a":"Evaporation","option_b":"Condensation","option_c":"Precipitation","option_d":"Runoff",
     "correct_answer":"B",
     "explanation":"Condensation is the opposite of evaporation. As warm moist air rises and cools, water vapor condenses onto tiny particles to form water droplets that cluster into clouds."},

    {"subject":"Science","topic":"Water Cycle","difficulty":"easy",
     "question_text":"What is precipitation?",
     "option_a":"Water vapor rising into the atmosphere","option_b":"Water droplets cooling to form clouds","option_c":"Any form of water that falls from clouds to Earth's surface","option_d":"Water soaking into the ground",
     "correct_answer":"C",
     "explanation":"Precipitation is any form of water falling from the atmosphere to Earth's surface: rain, snow, sleet, and hail. It occurs when water droplets in clouds become too heavy to stay suspended."},

    {"subject":"Science","topic":"Water Cycle","difficulty":"medium",
     "question_text":"What is transpiration in the water cycle?",
     "option_a":"Water evaporating from ocean surfaces","option_b":"Water vapor released by plants through their leaves","option_c":"Water seeping through layers of rock","option_d":"Ice melting at the poles",
     "correct_answer":"B",
     "explanation":"Transpiration is the process by which plants release water vapor through tiny pores called stomata in their leaves. Together with evaporation, it is called evapotranspiration."},

    {"subject":"Science","topic":"Water Cycle","difficulty":"medium",
     "question_text":"Place the water cycle steps in correct order: (I) Precipitation  (II) Evaporation  (III) Condensation",
     "option_a":"I → II → III","option_b":"II → III → I","option_c":"III → I → II","option_d":"II → I → III",
     "correct_answer":"B",
     "explanation":"The basic water cycle: (II) Water evaporates from oceans/rivers → (III) Water vapor cools and condenses to form clouds → (I) Water precipitates as rain or snow back to Earth."},

    {"subject":"Science","topic":"Water Cycle","difficulty":"medium",
     "question_text":"When rainwater soaks into the soil and collects underground in permeable rock layers, it forms:",
     "option_a":"A reservoir","option_b":"Runoff","option_c":"Groundwater","option_d":"Condensation",
     "correct_answer":"C",
     "explanation":"Groundwater is water that infiltrates (soaks into) the ground and fills spaces in soil and rock, collecting in underground layers called aquifers — a vital freshwater source."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Weather & Climate (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Weather & Climate","difficulty":"easy",
     "question_text":"What is the difference between weather and climate?",
     "option_a":"Weather is long-term patterns; climate is day-to-day conditions","option_b":"Weather is day-to-day atmospheric conditions; climate is the average weather pattern over many years","option_c":"Weather only includes temperature; climate includes all elements","option_d":"They are the same thing",
     "correct_answer":"B",
     "explanation":"Weather is what's happening outside today (temperature, wind, rain). Climate is the long-term average over 30+ years. 'Climate is what you expect; weather is what you get.'"},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"easy",
     "question_text":"Fluffy, white, flat-bottomed clouds that form on fair-weather days are called:",
     "option_a":"Cirrus clouds","option_b":"Stratus clouds","option_c":"Cumulus clouds","option_d":"Nimbus clouds",
     "correct_answer":"C",
     "explanation":"Cumulus clouds are the classic puffy clouds forming on sunny days when warm air rises and cools. Cirrus are thin and wispy (high altitude). Stratus form flat gray layers."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"medium",
     "question_text":"What typically happens when a cold front passes through an area?",
     "option_a":"Temperatures rise gradually and skies become sunny","option_b":"The area experiences only light fog","option_c":"Temperatures drop suddenly and storms may occur","option_d":"Nothing changes in the weather",
     "correct_answer":"C",
     "explanation":"A cold front occurs when cold air pushes under warmer air, forcing the warm air up rapidly. This creates cumulonimbus clouds, storms, and a sudden temperature drop after the front passes."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"easy",
     "question_text":"Humidity refers to:",
     "option_a":"The speed at which wind moves","option_b":"The amount of water vapor in the air","option_c":"The weight of air pressing down on Earth","option_d":"The difference in temperature between day and night",
     "correct_answer":"B",
     "explanation":"Humidity is the amount of water vapor present in the air. High humidity makes it feel warmer and more uncomfortable because sweat evaporates more slowly."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"medium",
     "question_text":"A falling barometer (decreasing air pressure) usually indicates:",
     "option_a":"Clear, calm weather is on the way","option_b":"Stormy or rainy weather is likely approaching","option_c":"Temperature will rise significantly","option_d":"Wind speeds will decrease",
     "correct_answer":"B",
     "explanation":"Air pressure drops when warm, less dense air rises — associated with cloud formation and storms. Rising pressure typically indicates clearing, stable weather."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"medium",
     "question_text":"As altitude increases, what generally happens to air temperature?",
     "option_a":"Temperature increases","option_b":"Temperature stays the same","option_c":"Temperature decreases","option_d":"Temperature fluctuates randomly",
     "correct_answer":"C",
     "explanation":"As altitude increases, the atmosphere becomes thinner with fewer air molecules to absorb and retain heat. Temperature decreases approximately 6.5°C per 1,000 meters gained."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"medium",
     "question_text":"Wind is primarily caused by:",
     "option_a":"The rotation of the moon","option_b":"Differences in air pressure between two locations","option_c":"Ocean currents pushing air","option_d":"Gravity pulling air downward",
     "correct_answer":"B",
     "explanation":"Wind is air moving from high pressure to low pressure. The greater the pressure difference, the stronger the wind. Pressure differences are caused by uneven heating of Earth's surface."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"medium",
     "question_text":"What is the greenhouse effect?",
     "option_a":"The process of growing plants in glass buildings","option_b":"The way certain gases in the atmosphere trap heat from the sun, warming Earth","option_c":"The cooling of Earth due to deforestation","option_d":"A layer of the atmosphere that blocks all solar radiation",
     "correct_answer":"B",
     "explanation":"Greenhouse gases (CO₂, methane, water vapor) absorb heat radiated from Earth's surface and re-radiate it back, keeping Earth warm enough to support life."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"hard",
     "question_text":"Which human activity contributes MOST to current climate change?",
     "option_a":"Farming and agriculture","option_b":"Air travel","option_c":"Burning fossil fuels (coal, oil, natural gas)","option_d":"Building construction",
     "correct_answer":"C",
     "explanation":"Burning fossil fuels releases large amounts of CO₂ and other greenhouse gases, enhancing the greenhouse effect and causing global average temperatures to rise."},

    {"subject":"Science","topic":"Weather & Climate","difficulty":"hard",
     "question_text":"Which biome receives the least annual rainfall, creating extreme day-night temperature differences?",
     "option_a":"Tropical rainforest","option_b":"Tundra","option_c":"Temperate forest","option_d":"Desert",
     "correct_answer":"D",
     "explanation":"Deserts receive less than 25 cm (10 inches) of rain per year. With little vegetation and low humidity, they lose heat rapidly at night, creating dramatic day-night temperature swings."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Earth & Geology (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Earth & Geology","difficulty":"easy",
     "question_text":"The rock cycle describes:",
     "option_a":"How rocks roll down mountains","option_b":"The continuous process by which rocks form, break down, and reform over time","option_c":"The study of ancient fossils","option_d":"How minerals grow inside rocks",
     "correct_answer":"B",
     "explanation":"The rock cycle is the continuous process through which rocks change from one type to another (igneous → sedimentary → metamorphic) through melting, cooling, weathering, and pressure."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"easy",
     "question_text":"What are the three main types of rocks?",
     "option_a":"Hard, soft, and medium","option_b":"Granite, limestone, and marble","option_c":"Igneous, sedimentary, and metamorphic","option_d":"Volcanic, ocean, and land",
     "correct_answer":"C",
     "explanation":"The three rock types are: (1) Igneous — formed from cooled magma/lava, (2) Sedimentary — formed from compressed layers of sediment, (3) Metamorphic — formed when existing rocks are changed by heat and pressure."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"easy",
     "question_text":"How are igneous rocks formed?",
     "option_a":"By layers of sediment being pressed together over time","option_b":"When magma or lava cools and solidifies","option_c":"When rocks are subjected to extreme heat and pressure without melting","option_d":"Through the fossilization of plant material",
     "correct_answer":"B",
     "explanation":"Igneous rocks form when magma (underground molten rock) or lava (magma that reaches the surface) cools and solidifies. Granite and basalt are common examples."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"Which process is most important in forming sedimentary rock?",
     "option_a":"Melting and resolidifying of minerals","option_b":"Extreme heat and pressure deep underground","option_c":"Deposition and compaction of sediment layers over time","option_d":"Volcanic activity",
     "correct_answer":"C",
     "explanation":"Sedimentary rocks form when layers of sediment (sand, mud, shells, organic matter) are deposited, buried, and compressed over time. Limestone and sandstone are common examples."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"Which condition creates metamorphic rock?",
     "option_a":"Lava cooling on Earth's surface","option_b":"Sediment piling up at the bottom of a lake","option_c":"Existing rock changed by intense heat and pressure (without melting)","option_d":"Wind erosion of granite",
     "correct_answer":"C",
     "explanation":"Metamorphic rocks form when existing rocks are subjected to intense heat and pressure deep underground without melting. Marble (from limestone) and slate (from shale) are examples."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"According to plate tectonics, Earth's outer shell is:",
     "option_a":"One solid, unbroken layer of rock","option_b":"Made entirely of ocean floor","option_c":"Divided into large moving pieces called tectonic plates","option_d":"Fixed and completely stationary",
     "correct_answer":"C",
     "explanation":"Earth's lithosphere (outer shell) is divided into about 15 major tectonic plates that move very slowly (a few centimeters per year) on the semi-fluid asthenosphere below."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"easy",
     "question_text":"What causes most earthquakes?",
     "option_a":"Heavy rainfall eroding the ground","option_b":"Volcanoes erupting underground","option_c":"Tectonic plates slipping and releasing stored energy along fault lines","option_d":"Meteorites hitting Earth's surface",
     "correct_answer":"C",
     "explanation":"Earthquakes occur when tectonic plates slip along fault lines, releasing stored energy as seismic waves. The point underground where it starts is the focus; the surface point above is the epicenter."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"Where are most of the world's active volcanoes located?",
     "option_a":"In the middle of tectonic plates, far from edges","option_b":"Only in the ocean","option_c":"Along the boundaries of tectonic plates","option_d":"Randomly distributed across all continents",
     "correct_answer":"C",
     "explanation":"Most volcanoes occur at tectonic plate boundaries where magma can escape to the surface. The 'Ring of Fire' around the Pacific Ocean has 75% of the world's active volcanoes."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"What is the difference between weathering and erosion?",
     "option_a":"Erosion breaks rock down; weathering moves the pieces away","option_b":"Weathering breaks rock into smaller pieces; erosion moves those pieces to a new location","option_c":"They describe the same process","option_d":"Weathering only happens in water; erosion only with wind",
     "correct_answer":"B",
     "explanation":"Weathering is the breakdown of rock into smaller pieces (by water, wind, ice, or chemicals). Erosion is the transport of those weathered materials to a new location by wind, water, gravity, or ice."},

    {"subject":"Science","topic":"Earth & Geology","difficulty":"medium",
     "question_text":"How do most fossils form?",
     "option_a":"Living organisms are quickly frozen in ice","option_b":"Organisms are dried out by the sun","option_c":"Organisms die, are buried in sediment, and their hard parts are slowly replaced by minerals","option_d":"Living organisms dig into rock to shelter",
     "correct_answer":"C",
     "explanation":"Fossils typically form when organisms die and are rapidly buried in sediment. Over millions of years, the sediment hardens into rock, and minerals replace the organism's hard parts (bones, shells, teeth)."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Forces & Motion (8 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Forces & Motion","difficulty":"medium",
     "question_text":"According to Newton's First Law of Motion, what happens to an object at rest if no net force acts on it?",
     "option_a":"It slowly speeds up.","option_b":"It moves in a circle.","option_c":"It remains at rest.","option_d":"It falls toward the ground.",
     "correct_answer":"C",
     "explanation":"Newton's First Law (Inertia): an object at rest stays at rest, and an object in motion stays in motion, unless acted upon by a net external force."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"hard",
     "question_text":"A 10 N force and a 4 N force act on an object in opposite directions. What is the net force?",
     "option_a":"14 N","option_b":"40 N","option_c":"6 N","option_d":"2.5 N",
     "correct_answer":"C",
     "explanation":"When forces act in opposite directions, subtract the smaller from the larger: 10 N − 4 N = 6 N in the direction of the larger force."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"easy",
     "question_text":"What is gravity?",
     "option_a":"A force that makes objects float away from Earth","option_b":"A force that repels magnets","option_c":"The force of attraction between objects with mass","option_d":"A force created only by the Sun",
     "correct_answer":"C",
     "explanation":"Gravity is a force of attraction between any two objects that have mass. The greater the mass, the stronger the gravity. Earth's gravity pulls objects toward its center, giving us weight."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"medium",
     "question_text":"Using F = ma: if a 10 kg object has a net force of 30 N acting on it, what is its acceleration?",
     "option_a":"300 m/s²","option_b":"0.33 m/s²","option_c":"3 m/s²","option_d":"20 m/s²",
     "correct_answer":"C",
     "explanation":"Newton's Second Law: a = F/m = 30 N ÷ 10 kg = 3 m/s². Greater force produces greater acceleration; greater mass requires more force to accelerate."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"medium",
     "question_text":"When you jump off a boat onto a dock, the boat moves away. This demonstrates Newton's Third Law, which states:",
     "option_a":"Objects at rest stay at rest","option_b":"Force equals mass times acceleration","option_c":"For every action, there is an equal and opposite reaction","option_d":"Heavier objects fall faster",
     "correct_answer":"C",
     "explanation":"Newton's Third Law: when you push off the boat (action), the boat pushes back with equal force in the opposite direction (reaction). This is why the boat moves away."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"easy",
     "question_text":"Friction is a force that:",
     "option_a":"Makes objects speed up","option_b":"Pulls objects toward Earth","option_c":"Opposes motion between two surfaces in contact","option_d":"Pushes objects apart",
     "correct_answer":"C",
     "explanation":"Friction is a resistance force that acts against motion between two surfaces, converting kinetic energy into heat. Without friction, we couldn't walk and cars couldn't brake."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"medium",
     "question_text":"What is the difference between speed and velocity?",
     "option_a":"Speed includes direction; velocity does not","option_b":"Velocity includes direction; speed does not","option_c":"They are exactly the same thing","option_d":"Speed is in meters; velocity in kilometers",
     "correct_answer":"B",
     "explanation":"Speed is a scalar quantity — only how fast (e.g., 60 km/h). Velocity is a vector — speed AND direction (e.g., 60 km/h north). Two cars at the same speed can have different velocities."},

    {"subject":"Science","topic":"Forces & Motion","difficulty":"hard",
     "question_text":"A car goes from 0 to 60 m/s in 10 seconds. What is its acceleration?",
     "option_a":"600 m/s²","option_b":"70 m/s²","option_c":"6 m/s²","option_d":"0.17 m/s²",
     "correct_answer":"C",
     "explanation":"Acceleration = change in velocity ÷ time = (60 − 0) ÷ 10 = 6 m/s². Acceleration measures how quickly velocity changes."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Energy (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Energy","difficulty":"easy",
     "question_text":"A ball sitting at the top of a hill has which type of energy?",
     "option_a":"Kinetic energy","option_b":"Thermal energy","option_c":"Potential energy","option_d":"Chemical energy",
     "correct_answer":"C",
     "explanation":"Potential energy is stored energy due to position. A ball at the top of a hill has gravitational potential energy — it has the potential to move and do work when it rolls down."},

    {"subject":"Science","topic":"Energy","difficulty":"medium",
     "question_text":"A stretched rubber band has which type of potential energy?",
     "option_a":"Gravitational potential energy","option_b":"Elastic potential energy","option_c":"Chemical potential energy","option_d":"Thermal energy",
     "correct_answer":"B",
     "explanation":"Elastic potential energy is stored in objects that are stretched, compressed, or deformed — like rubber bands, springs, and archery bows. When released, it converts to kinetic energy."},

    {"subject":"Science","topic":"Energy","difficulty":"medium",
     "question_text":"The Law of Conservation of Energy states that:",
     "option_a":"Energy is constantly being created in the sun","option_b":"Energy cannot be created or destroyed — it can only change form","option_c":"Hot objects always cool to room temperature","option_d":"All energy eventually becomes heat",
     "correct_answer":"B",
     "explanation":"The Law of Conservation of Energy is a fundamental principle: the total amount of energy in a closed system remains constant. Energy transforms from one form to another but is never created or destroyed."},

    {"subject":"Science","topic":"Energy","difficulty":"easy",
     "question_text":"Mechanical energy is:",
     "option_a":"Energy produced by burning fuel","option_b":"Energy stored in chemical bonds","option_c":"The sum of kinetic and potential energy of an object","option_d":"Energy from electricity",
     "correct_answer":"C",
     "explanation":"Mechanical energy is the energy associated with motion and position. It equals kinetic energy (energy of motion) + potential energy (stored energy). A rolling ball has mechanical energy."},

    {"subject":"Science","topic":"Energy","difficulty":"medium",
     "question_text":"What is the key difference between thermal energy and temperature?",
     "option_a":"Temperature is the total thermal energy; thermal energy measures average kinetic energy","option_b":"Thermal energy is the total kinetic energy of all particles; temperature measures the average kinetic energy of particles","option_c":"They measure the same thing","option_d":"Temperature only applies to liquids",
     "correct_answer":"B",
     "explanation":"Temperature measures the average kinetic energy of particles. Thermal energy is the total energy of ALL particles. A large pot of lukewarm water has more thermal energy than a small boiling pot, even at lower temperature."},

    {"subject":"Science","topic":"Energy","difficulty":"easy",
     "question_text":"Which example shows electrical energy being converted to light energy?",
     "option_a":"A battery powering a toy car","option_b":"A light bulb turning on","option_c":"A gas stove burning","option_d":"A falling boulder",
     "correct_answer":"B",
     "explanation":"A light bulb converts electrical energy into light energy (and some heat). This is an energy transformation — electrical energy changes form to become light."},

    {"subject":"Science","topic":"Energy","difficulty":"easy",
     "question_text":"Which is the BEST example of chemical energy?",
     "option_a":"A spinning top","option_b":"A waterfall","option_c":"Food that your body digests for fuel","option_d":"A flying airplane",
     "correct_answer":"C",
     "explanation":"Chemical energy is stored in the bonds between atoms. Food contains chemical energy stored in carbohydrates, fats, and proteins, released through digestion and cellular respiration."},

    {"subject":"Science","topic":"Energy","difficulty":"medium",
     "question_text":"When you rub your hands together quickly, which energy transformation occurs?",
     "option_a":"Chemical energy → thermal energy","option_b":"Kinetic energy → thermal energy (heat)","option_c":"Potential energy → kinetic energy","option_d":"Electrical energy → light energy",
     "correct_answer":"B",
     "explanation":"Friction between your hands converts kinetic energy (motion) into thermal energy (heat). You can feel your hands get warmer — kinetic energy transforming into heat."},

    {"subject":"Science","topic":"Energy","difficulty":"easy",
     "question_text":"Which energy source is RENEWABLE?",
     "option_a":"Coal","option_b":"Natural gas","option_c":"Solar energy","option_d":"Petroleum (oil)",
     "correct_answer":"C",
     "explanation":"Solar energy is renewable — it comes from the sun, which produces energy continuously. Fossil fuels (coal, oil, natural gas) are non-renewable because they take millions of years to form."},

    {"subject":"Science","topic":"Energy","difficulty":"medium",
     "question_text":"How do solar panels generate electricity?",
     "option_a":"By burning sunlight at high temperatures","option_b":"By converting light energy from the sun into electrical energy using photovoltaic cells","option_c":"By using the heat of the sun to spin a turbine","option_d":"By collecting sun rays and storing them as chemical energy",
     "correct_answer":"B",
     "explanation":"Solar panels contain photovoltaic (PV) cells made of silicon. When photons of light hit the silicon, they knock electrons loose, creating an electric current — light energy directly into electrical energy."},

    # ══════════════════════════════════════════════════════════════
    # SCIENCE — Matter & Chemistry (10 questions)
    # ══════════════════════════════════════════════════════════════
    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"easy",
     "question_text":"Which correctly lists the three main states of matter?",
     "option_a":"Gas, plasma, and energy","option_b":"Solid, liquid, and gas","option_c":"Hard, soft, and flowing","option_d":"Hot, cold, and warm",
     "correct_answer":"B",
     "explanation":"The three main states of matter are solid (definite shape and volume), liquid (definite volume, no definite shape), and gas (no definite shape or volume)."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"easy",
     "question_text":"At what temperature does pure water melt (change from ice to liquid) at standard atmospheric pressure?",
     "option_a":"100°C","option_b":"0°C","option_c":"-10°C","option_d":"37°C",
     "correct_answer":"B",
     "explanation":"Pure water melts (and freezes) at 0°C (32°F) at standard pressure. The melting point and freezing point are the same temperature."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"easy",
     "question_text":"Which of the following is a PHYSICAL change?",
     "option_a":"Iron rusting","option_b":"Wood burning","option_c":"Ice melting into water","option_d":"Bread baking",
     "correct_answer":"C",
     "explanation":"A physical change alters the form or appearance of matter but not its chemical composition. Ice melting is still H₂O — just a different state. Rusting, burning, and baking are chemical changes."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"Which observation BEST indicates that a chemical change has occurred?",
     "option_a":"A solid dissolves in water","option_b":"Water changes from liquid to steam","option_c":"A new substance forms with different properties (gas produced, color change, light/heat given off)","option_d":"Ice cubes are broken into smaller pieces",
     "correct_answer":"C",
     "explanation":"Chemical changes produce new substances. Signs include: change in color, production of gas (bubbling), formation of a precipitate, or release of heat and light. These cannot easily be reversed."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"What is the difference between an element and a compound?",
     "option_a":"Elements have more atoms than compounds","option_b":"An element contains only one type of atom; a compound contains two or more different types of atoms chemically combined","option_c":"Elements are liquids; compounds are solids","option_d":"Compounds can be found in nature; elements are man-made",
     "correct_answer":"B",
     "explanation":"An element (like O₂) is a pure substance made of only one type of atom. A compound (like H₂O) is formed when two or more different elements are chemically bonded in fixed ratios."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"easy",
     "question_text":"What is an atom?",
     "option_a":"The smallest unit of a compound","option_b":"The smallest unit of an element that retains the properties of that element","option_c":"A group of molecules bonded together","option_d":"The largest particle in chemistry",
     "correct_answer":"B",
     "explanation":"An atom is the smallest unit of an element that still has the chemical properties of that element. Atoms are the building blocks of all matter."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"What are the three main subatomic particles in an atom?",
     "option_a":"Neutrons, electrons, and molecules","option_b":"Protons, electrons, and compounds","option_c":"Protons, neutrons, and electrons","option_d":"Atoms, molecules, and ions",
     "correct_answer":"C",
     "explanation":"Atoms consist of: protons (positive charge, in nucleus), neutrons (no charge, in nucleus), and electrons (negative charge, orbiting the nucleus). The number of protons determines which element it is."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"Using density = mass/volume: which substance sinks when placed in water (density = 1 g/cm³)?",
     "option_a":"Wood (density ~0.5 g/cm³)","option_b":"Plastic foam (density ~0.03 g/cm³)","option_c":"Ice (density ~0.92 g/cm³)","option_d":"Iron (density ~7.9 g/cm³)",
     "correct_answer":"D",
     "explanation":"Objects denser than water (density > 1 g/cm³) sink. Iron at ~7.9 g/cm³ is much denser than water, so it sinks. Wood, foam, and ice are all less dense than water, so they float."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"Which of the following is a CHEMICAL property?",
     "option_a":"Color","option_b":"Melting point","option_c":"Density","option_d":"Flammability",
     "correct_answer":"D",
     "explanation":"Chemical properties describe how a substance reacts or changes with other substances. Flammability (ability to burn) is a chemical property. Color, melting point, and density are physical properties."},

    {"subject":"Science","topic":"Matter & Chemistry","difficulty":"medium",
     "question_text":"What is the difference between a mixture and a solution?",
     "option_a":"A mixture contains only two substances; a solution contains many","option_b":"In a solution, substances are uniformly distributed; in a mixture, they may not be evenly combined","option_c":"Solutions are solid; mixtures are liquid","option_d":"A mixture involves a chemical change; a solution does not",
     "correct_answer":"B",
     "explanation":"A mixture combines substances without a chemical change (like trail mix — you can see and separate parts). A solution is a homogeneous mixture where one substance dissolves evenly in another (like salt water)."},
]

# ══════════════════════════════════════════════════════════════════
# ACHIEVEMENTS (15 total)
# ══════════════════════════════════════════════════════════════════
ACHIEVEMENTS = [
    {"slug": "first-quiz",     "name": "First Quiz",       "description": "Complete your very first quiz session.",                          "icon_emoji": "🎉"},
    {"slug": "perfect-score",  "name": "Perfect Score",    "description": "Get 100% on any quiz session.",                                   "icon_emoji": "⭐"},
    {"slug": "on-a-roll",      "name": "On a Roll",        "description": "Complete 5 quiz sessions.",                                       "icon_emoji": "🔥"},
    {"slug": "quiz-marathon",  "name": "Quiz Marathon",    "description": "Complete 10 quiz sessions total.",                                "icon_emoji": "🏃"},
    {"slug": "half-century",   "name": "Half Century",     "description": "Answer 50 questions total.",                                      "icon_emoji": "🎖️"},
    {"slug": "century",        "name": "Century",          "description": "Answer 100 questions total.",                                     "icon_emoji": "🥇"},
    {"slug": "streak-3",       "name": "3-Day Streak",     "description": "Study 3 days in a row.",                                         "icon_emoji": "📅"},
    {"slug": "streak-7",       "name": "Week Warrior",     "description": "Study 7 days in a row.",                                         "icon_emoji": "🌟"},
    {"slug": "science-star",   "name": "Science Star",     "description": "Score 80% or higher on 5 Science quizzes.",                      "icon_emoji": "🔬"},
    {"slug": "word-wizard",    "name": "Word Wizard",      "description": "Score 80% or higher on 5 English quizzes.",                      "icon_emoji": "📖"},
    {"slug": "topic-master",   "name": "Topic Master",     "description": "Reach 'Mastered' level on any topic.",                           "icon_emoji": "🏆"},
    {"slug": "comeback-kid",   "name": "Comeback Kid",     "description": "Score 80%+ after previously scoring below 60% in a subject.",    "icon_emoji": "💪"},
    {"slug": "ace-english",    "name": "English Ace",      "description": "Get 100% on an English quiz.",                                   "icon_emoji": "🅰️"},
    {"slug": "ace-science",    "name": "Science Ace",      "description": "Get 100% on a Science quiz.",                                    "icon_emoji": "🧬"},
    {"slug": "dedicated",      "name": "Dedicated Learner","description": "Complete quizzes on 7 different calendar days.",                  "icon_emoji": "📚"},
]

# ══════════════════════════════════════════════════════════════════
# LESSON CARDS
# ══════════════════════════════════════════════════════════════════
LESSON_CARDS = [
    {
        "subject": "English", "topic": "Parts of Speech",
        "title": "The 8 Parts of Speech",
        "content": "Every word in a sentence plays a role. The 8 parts of speech classify words by their function: nouns name people/places/things/ideas, pronouns replace nouns, verbs show action or state, adjectives describe nouns, adverbs describe verbs or adjectives, prepositions show relationships, conjunctions connect ideas, and interjections express emotion.",
        "key_points": ["Nouns: person, place, thing, or idea (dog, city, happiness)", "Verbs: action or state of being (run, is, seems)", "Adjectives modify nouns; adverbs modify verbs/adjectives", "Prepositions show relationship (on, in, under, beside)", "Conjunctions connect: coordinating (FANBOYS), subordinating (because, although)"],
        "example": "In 'The quick brown fox jumps over the lazy dog' — quick/brown/lazy are adjectives, fox/dog are nouns, jumps is a verb, over is a preposition.",
    },
    {
        "subject": "English", "topic": "Grammar",
        "title": "Grammar Rules That Matter",
        "content": "Grammar rules help us communicate clearly. Key rules include subject-verb agreement, consistent verb tense, avoiding dangling modifiers, using parallel structure, and writing complete sentences with both a subject and predicate.",
        "key_points": ["Subject-verb agreement: singular subject → singular verb (The dog runs)", "With 'neither...nor,' the verb agrees with the nearest subject", "Dangling modifiers: the modifier must clearly describe a word in the sentence", "Parallel structure: items in a list should have the same grammatical form", "Complete sentences need both a subject AND a predicate"],
        "example": "✓ 'She likes swimming, hiking, and running' (parallel). ✗ 'She likes swimming, hiking, and to run' (not parallel).",
    },
    {
        "subject": "English", "topic": "Punctuation",
        "title": "Punctuation Guide",
        "content": "Punctuation marks signal to readers how to read a sentence. Key rules: use a comma before a coordinating conjunction joining two independent clauses, use an apostrophe for possessives and contractions, use a semicolon between two related independent clauses, and use a colon before a list.",
        "key_points": ["Comma + FANBOYS joins two independent clauses", "Apostrophe in possessives: cat's (one cat), cats' (multiple cats)", "Apostrophe in contractions: it's = it is; they're = they are", "Semicolon joins two related independent clauses (no conjunction needed)", "Colon introduces a list: 'I need three things: milk, eggs, and bread'"],
        "example": "'She studied hard; therefore, she passed the test.' (semicolon + conjunctive adverb + comma)",
    },
    {
        "subject": "English", "topic": "Vocabulary",
        "title": "Building Your Vocabulary",
        "content": "A strong vocabulary helps you read and write more effectively. You can figure out word meanings by analyzing roots, prefixes, and suffixes, or by using context clues in surrounding sentences.",
        "key_points": ["Common prefixes: un- (not), mis- (wrongly), pre- (before), re- (again)", "Common suffixes: -tion (act/state of), -ology (study of), -ful (full of)", "Latin roots: aud (hear), port (carry), scrib (write), vis (see)", "Context clues: look for definitions, examples, or contrasting words nearby", "Synonyms = same meaning; Antonyms = opposite meaning"],
        "example": "'Auditorium' contains root 'aud' (hear) — a place where you hear performances.",
    },
    {
        "subject": "English", "topic": "Reading Comprehension",
        "title": "Smart Reading Strategies",
        "content": "Strong readers think about what they read. Key strategies include identifying the main idea, making inferences, understanding author's purpose, and using context clues for unknown words.",
        "key_points": ["Main idea = the most important point (often in first or last sentence)", "Supporting details back up the main idea", "Inference = use text clues + your knowledge to figure out unstated information", "Author's purpose: to inform (facts), to persuade (opinion), to entertain (story)", "Tone = the author's attitude (urgent, hopeful, concerned, humorous)"],
        "example": "If a passage lists problems and explains how they were fixed, it uses the problem-solution text structure. Look for signal words!",
    },
    {
        "subject": "English", "topic": "Literary Devices",
        "title": "Common Literary Devices",
        "content": "Authors use literary devices to make their writing more vivid and meaningful. Learning to recognize these tools helps you understand and analyze any text more deeply.",
        "key_points": ["Simile: compares using 'like' or 'as' ('fast as lightning')", "Metaphor: direct comparison without 'like' or 'as' ('Life is a journey')", "Personification: giving human traits to non-human things ('The wind whispered')", "Hyperbole: extreme exaggeration ('I'm so hungry I could eat a horse')", "Foreshadowing: hints at what will happen later in the story"],
        "example": "'The old clock groaned as midnight approached' uses both personification (groaned) and foreshadowing (something is about to happen).",
    },
    {
        "subject": "English", "topic": "Figurative Language",
        "title": "Figurative vs. Literal Language",
        "content": "Figurative language means something different from the literal words. When someone says 'it's raining cats and dogs,' they don't mean animals are falling! Learn to recognize idioms, similes, metaphors, personification, and hyperbole.",
        "key_points": ["Literal language means exactly what it says", "Figurative language creates an image or meaning beyond the literal words", "Idioms: expressions where words together mean something different ('break a leg')", "Simile compares with 'like' or 'as'; metaphor compares directly", "Hyperbole exaggerates wildly to make a point"],
        "example": "'He has a heart of gold' is a metaphor meaning he is very kind — his heart is not literally made of gold!",
    },
    {
        "subject": "English", "topic": "Text Structure",
        "title": "Types of Text Structure",
        "content": "Authors organize information in different ways depending on their purpose. Recognizing text structure helps you understand and remember what you read. The five main types are: description, sequence, cause/effect, compare/contrast, and problem/solution.",
        "key_points": ["Description: details about a topic (looks like, feels like, sounds like)", "Sequence/Chronological: events in order (first, next, then, finally)", "Cause and Effect: reasons and results (because, therefore, as a result)", "Compare and Contrast: similarities and differences (similarly, however, on the other hand)", "Problem and Solution: a problem is presented and solutions are offered"],
        "example": "'Due to overcrowding in schools, the district opened three new campuses.' — Cause-and-effect structure (overcrowding → new campuses).",
    },
    {
        "subject": "Science", "topic": "Cells",
        "title": "Cell Structure & Function",
        "content": "The cell is the basic unit of all life. Every living thing is made of cells, and each part of a cell (organelle) has a specific job. Understanding cell structure helps you understand how all living things function.",
        "key_points": ["Cell membrane: controls what enters/exits (all cells)", "Nucleus: control center containing DNA (eukaryotes only)", "Mitochondria: produces ATP energy through cellular respiration", "Ribosomes: builds proteins from amino acids", "Chloroplast: performs photosynthesis (plant cells only)", "Cell wall: extra rigid support layer (plant cells only, made of cellulose)"],
        "example": "Think of the cell as a city — the nucleus is city hall, mitochondria are power plants, cell membrane is the city border, and ribosomes are factories.",
    },
    {
        "subject": "Science", "topic": "Genetics",
        "title": "Introduction to Genetics",
        "content": "Genetics is the study of heredity — how traits are passed from parents to offspring through DNA. Every cell in your body contains a complete copy of your DNA, organized into 46 chromosomes.",
        "key_points": ["DNA (Deoxyribonucleic Acid) contains the genetic code for all life", "Genes are segments of DNA that code for specific traits", "Alleles are different versions of the same gene (brown eyes vs blue eyes)", "Dominant alleles mask recessive alleles (written as capital letters)", "Genotype = actual genetic code (TT, Tt, tt); Phenotype = what you see"],
        "example": "A Tt × Tt cross produces: 25% TT, 50% Tt, 25% tt. If T is dominant, 75% show the dominant trait.",
    },
    {
        "subject": "Science", "topic": "Ecosystems",
        "title": "Ecosystems & Food Webs",
        "content": "An ecosystem includes all living organisms (biotic) and non-living factors (abiotic) in an area. Energy flows through ecosystems in food chains and food webs, from producers through consumers to decomposers.",
        "key_points": ["Producers (plants) capture sunlight and make food via photosynthesis", "Primary consumers (herbivores) eat producers", "Secondary/tertiary consumers eat other animals", "Decomposers (fungi, bacteria) break down dead matter and recycle nutrients", "Only ~10% of energy transfers from one trophic level to the next"],
        "example": "Grass → Rabbit → Fox → Decomposers. Remove the rabbits and fox numbers decline; grass grows unchecked.",
    },
    {
        "subject": "Science", "topic": "Photosynthesis",
        "title": "How Photosynthesis Works",
        "content": "Photosynthesis converts light energy into chemical energy (glucose) using carbon dioxide and water. It takes place in chloroplasts and produces oxygen as a byproduct.",
        "key_points": ["Equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂", "Inputs: carbon dioxide (from air), water (from roots), light energy", "Outputs: glucose (stored food) and oxygen (released)", "Chloroplasts contain chlorophyll — the green pigment that captures light", "Chlorophyll absorbs red and blue light; reflects green (why leaves look green)"],
        "example": "On a sunny day, a large tree absorbs CO₂ and releases oxygen — helping clean our air!",
    },
    {
        "subject": "Science", "topic": "Water Cycle",
        "title": "The Water Cycle",
        "content": "The water cycle (hydrological cycle) describes the continuous movement of water on, above, and below Earth's surface. The same water has been cycling through Earth's systems for billions of years.",
        "key_points": ["Evaporation: liquid water → water vapor (from oceans, lakes, rivers)", "Transpiration: water vapor released by plants through stomata", "Condensation: water vapor cools and forms clouds", "Precipitation: water falls as rain, snow, sleet, or hail", "Infiltration: water soaks into ground to form groundwater"],
        "example": "The water you drink today may have once flowed through an ancient river, evaporated into clouds, and fallen as rain thousands of miles away!",
    },
    {
        "subject": "Science", "topic": "Weather & Climate",
        "title": "Weather vs. Climate",
        "content": "Weather is the day-to-day condition of the atmosphere. Climate is the long-term pattern of weather in an area over 30+ years. Understanding both helps us predict future conditions and understand environmental changes.",
        "key_points": ["Weather: temperature, humidity, precipitation, wind on any given day", "Climate: long-term averages and patterns (tropical, desert, tundra biomes)", "Cold front: cold air pushes under warm air → storms and temperature drop", "Greenhouse gases (CO₂, methane) trap heat, affecting global climate", "Global warming: enhanced greenhouse effect from human pollution"],
        "example": "'It's snowing in Denver today' = weather. 'Denver gets 50+ inches of snow per year on average' = climate.",
    },
    {
        "subject": "Science", "topic": "Earth & Geology",
        "title": "Rock Cycle & Plate Tectonics",
        "content": "Earth's surface is constantly changing through the rock cycle, plate tectonics, and erosion. Rocks cycle through igneous, sedimentary, and metamorphic forms over millions of years.",
        "key_points": ["Igneous: formed from cooling magma/lava (granite, basalt)", "Sedimentary: formed from compressed sediment layers (limestone, sandstone)", "Metamorphic: formed when rocks are changed by heat/pressure (marble, slate)", "Plate tectonics: Earth's crust is divided into ~15 moving plates", "Plate boundaries: divergent (separating), convergent (colliding), transform (sliding)"],
        "example": "The Himalayan Mountains formed when the Indian Plate collided with the Eurasian Plate — a process that began ~50 million years ago and continues today!",
    },
    {
        "subject": "Science", "topic": "Forces & Motion",
        "title": "Newton's Laws of Motion",
        "content": "Sir Isaac Newton described three fundamental laws of motion that explain how forces affect objects. These laws apply everywhere — from a falling apple to a rocket launching into space.",
        "key_points": ["First Law (Inertia): objects stay at rest or in motion unless a net force acts on them", "Second Law: F = ma (Force = mass × acceleration)", "Third Law: for every action there is an equal and opposite reaction", "Gravity: attractive force between objects with mass", "Friction: force opposing motion between surfaces; converts kinetic energy to heat"],
        "example": "When a car brakes suddenly, passengers lurch forward (First Law — inertia keeps them moving). Friction from brakes applies force opposite to motion.",
    },
    {
        "subject": "Science", "topic": "Energy",
        "title": "Types and Conservation of Energy",
        "content": "Energy is the ability to do work. It exists in many forms and can transform from one type to another, but it can never be created or destroyed — this is the Law of Conservation of Energy.",
        "key_points": ["Kinetic energy: energy of motion", "Potential energy: stored energy due to position (gravitational) or condition (elastic)", "Chemical energy: stored in molecular bonds (food, fuel, batteries)", "Thermal energy: total kinetic energy of all particles in a substance", "Energy transformations: chemical → kinetic (eating → running), kinetic → thermal (friction)"],
        "example": "A roller coaster at the top has maximum potential energy. As it descends, potential converts to kinetic energy. Speed is maximum at the bottom.",
    },
    {
        "subject": "Science", "topic": "Matter & Chemistry",
        "title": "States of Matter & Properties",
        "content": "Matter is anything that has mass and takes up space. It exists in different states (solid, liquid, gas) and has physical and chemical properties that help us identify and use materials.",
        "key_points": ["Solid: definite shape and volume; particles vibrate in place", "Liquid: definite volume, no definite shape; particles slide past each other", "Gas: no definite shape or volume; particles move freely and fast", "Physical change: changes appearance but not composition (melting ice)", "Chemical change: forms a new substance (burning wood → ash + gases)"],
        "example": "Water at -10°C is ice (solid). At 25°C, liquid water. At 110°C, steam (gas). Same H₂O molecule, different states — a physical change!",
    },
]


def seed():
    db = SessionLocal()
    try:
        # ── Questions ────────────────────────────────────────────
        existing_count = db.query(Question).count()
        if existing_count < len(QUESTIONS):
            if existing_count > 0:
                print(f"Clearing {existing_count} old questions to load expanded set...")
                db.query(Question).delete()
                db.commit()
            for q in QUESTIONS:
                db.add(Question(**q))
            db.commit()
            print(f"Seeded {len(QUESTIONS)} questions across {len(set(q['topic'] for q in QUESTIONS))} topics.")
        else:
            print(f"Questions already seeded ({existing_count} found). Skipping.")

        # ── Achievements (upsert by slug) ────────────────────────
        added = 0
        for a in ACHIEVEMENTS:
            if not db.query(Achievement).filter(Achievement.slug == a["slug"]).first():
                db.add(Achievement(**a))
                added += 1
        db.commit()
        print(f"Achievements synced ({len(ACHIEVEMENTS)} total, {added} newly added).")

        # ── Lesson Cards ─────────────────────────────────────────
        existing_lessons = db.query(LessonCard).count()
        if existing_lessons < len(LESSON_CARDS):
            if existing_lessons > 0:
                db.query(LessonCard).delete()
                db.commit()
            for lc in LESSON_CARDS:
                db.add(LessonCard(
                    subject=lc["subject"],
                    topic=lc["topic"],
                    title=lc["title"],
                    content=lc["content"],
                    key_points=json.dumps(lc["key_points"]),
                    example=lc.get("example"),
                ))
            db.commit()
            print(f"Seeded {len(LESSON_CARDS)} lesson cards.")
        else:
            print(f"Lesson cards already seeded ({existing_lessons} found). Skipping.")

        print("\nDone! Study Buddy is ready.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
