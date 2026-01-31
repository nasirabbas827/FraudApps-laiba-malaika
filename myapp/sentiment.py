from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag

def analyze_sentiment_sentiwordnet(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)

    score = 0
    count = 0

    print(f"{'Word':<15}{'POS':<10}{'PosScore':<10}{'NegScore':<10}{'NetScore':<10}")
    print("-" * 55)

    for word, tag in tagged:
        wn_tag = None
        if tag.startswith('N'):
            wn_tag = wordnet.NOUN
        elif tag.startswith('V'):
            wn_tag = wordnet.VERB
        elif tag.startswith('J'):
            wn_tag = wordnet.ADJ
        elif tag.startswith('R'):
            wn_tag = wordnet.ADV

        if wn_tag:
            synsets = list(swn.senti_synsets(word, wn_tag))
            if synsets:
                syn = synsets[0]  # Take the first synset
                pos_score = syn.pos_score()
                neg_score = syn.neg_score()
                net_score = pos_score - neg_score

                # print wn_tag directly as string
                print(f"{word:<15}{wn_tag:<10}{pos_score:<10.2f}{neg_score:<10.2f}{net_score:<10.2f}")

                score += net_score
                count += 1

    final_score = score / count if count else 0

    if final_score > 0.05:
        sentiment = 'positive'
    elif final_score < -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    print("-" * 55)
    print(f"Average Sentiment Score: {final_score:.2f} => {sentiment}\n")

    return sentiment, final_score

 