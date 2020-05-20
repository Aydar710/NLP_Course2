import pandas
import pandas as pd
from keras import Sequential
from keras.callbacks import ModelCheckpoint
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer
import numpy as np

NUM_WORDS = 10000
EPOCHS = 25
model_filepath = "model_weights.hdf5"

df = pandas.read_csv("reviews.csv", encoding="utf-8")
reviews = df['text']

# tokenizing
tokenizer = Tokenizer(num_words=NUM_WORDS)
tokenizer.fit_on_texts(reviews.values)
sequences = tokenizer.texts_to_sequences(reviews.values)
text = [item for sublist in sequences for item in sublist]

sentence_len = 15
pred_len = 5
train_len = sentence_len - pred_len
seq = []
for i in range(len(text) - sentence_len):
    seq.append(text[i:i + sentence_len])
reverse_word_map = dict(map(reversed, tokenizer.word_index.items()))

trainX = []
trainY = []
for i in seq:
    trainX.append(i[:train_len])
    trainY.append(i[train_len])

# Build model
model = Sequential([
    Embedding(NUM_WORDS, 50, input_length=train_len),
    LSTM(100, return_sequences=True),
    LSTM(100),
    Dense(100, activation='relu'),
    Dropout(0.1),
    Dense(NUM_WORDS - 1, activation='softmax')
])

# Train model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

checkpoint = ModelCheckpoint(model_filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]

history = model.fit(np.asarray(trainX),
                    pd.get_dummies(np.asarray(trainY)),
                    epochs=EPOCHS,
                    batch_size=32,
                    callbacks=callbacks_list,
                    verbose=1)


def gen(model, seq, max_len=5):
    tokenized_sent = tokenizer.texts_to_sequences([seq])
    max_len = max_len + len(tokenized_sent[0])
    while len(tokenized_sent[0]) < max_len:
        padded_sentence = pad_sequences(tokenized_sent[-10:], maxlen=10)
        op = model.predict(np.asarray(padded_sentence).reshape(1, -1))
        tokenized_sent[0].append(op.argmax() + 1)

    return " ".join(map(lambda x: reverse_word_map[x], tokenized_sent[0]))


sentences = [
    "Согласитесь большинство современных фильмов и сериалов имеют одну ярковыраженную особенность",
    "Все, что можно сказать касательно данного сериала, уже сказали до",
    "Нередко очень разрекламированные проекты я встречаю с немалой долей скептицизма",
    "Посмотрев первый сезон, понимаешь, несмотря на все существующие огрехи, которые",
    "Мне сложно представить того человека, кто примет этот ошмёток, лишь",
    "До того как познакомиться с сим сериалом я не был",
    "Недавно посмотрела сериал от Netflix. Отмечу, что я отношусь к",
    "Что за мода пошла, собрать кучу народа в кинотеатры и",
    "Безусловно можно назвать одним из самых резонансных сериалов ушедшего года",
    "Сразу скажу, что сериал мне не понравился от слова совсем",
    "Крайне расстроен тем, каким вышел Ведьмак. Сразу скажу я не ",
    "После просмотра первой серии Ведьмака я пошла читать книги Сапковского",
    "Решив наплевать на критиков, я всё же посмотрел этот сериал",
    "Данный сериал от Нетфликс стал одним из самых обсуждаемых этой",
    "Сразу отмечу, что книг, по которым снят фильм, не читал",
    "Первая претензия именно к сценаристу, потому что он поди краткий",
    "У нас есть каноны: первоисточник и не менее великолепная игрушка",
    "Я знаю, что сейчас большинство, обматерив меня, полистает дальше, к",
    "Это самая худшая адаптация из всех, что я смотрела. Не",
    "Являюсь большим поклонником серии книг и игр по ведьмаку. Прошел",
    "Только представьте, что смотрите затяжной выпуск экстренных новостей, в которых"
]

for sen in sentences:
    print(gen(model, sen) + "\n")
