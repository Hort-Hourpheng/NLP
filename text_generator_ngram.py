import math
import string
import random
import time
from typing import List

# ideally we would use some smart text tokenizer, but for simplicity use this one
def tokenize(text: str) -> List[str]:
    """
    :param text: Takes input sentence
    :return: tokenized sentence
    """
    for punct in string.punctuation:
        text = text.replace(punct, ' '+punct+' ')
    t = text.split()
    return t

def get_ngrams(n: int, tokens: list) -> list:
    """
    :param n: n-gram size
    :param tokens: tokenized sentence
    :return: list of ngrams

    ngrams of tuple form: ((previous wordS!), target word)
    """
    # tokens.append('<END>')
    tokens = (n-1)*['<START>']+tokens
    l = [(tuple([tokens[i-p-1] for p in reversed(range(n-1))]), tokens[i]) for i in range(n-1, len(tokens))]
    return l


class NgramModel(object):

    def __init__(self, n):
        self.n = n

        # dictionary that keeps list of candidate words given context
        self.context = {}

        # keeps track of how many times ngram has appeared in the text before
        self.ngram_counter = {}

    def update(self, sentence: str) -> None:
        """
        Updates Language Model
        :param sentence: input text
        """
        n = self.n
        ngrams = get_ngrams(n, tokenize(sentence))
        for ngram in ngrams:
            if ngram in self.ngram_counter:
                self.ngram_counter[ngram] += 1.0
            else:
                self.ngram_counter[ngram] = 1.0

            prev_words, target_word = ngram
            if prev_words in self.context:
                self.context[prev_words].append(target_word)
            else:
                self.context[prev_words] = [target_word]

    def prob(self, context, token):
        """
        Calculates probability of a candidate token to be generated given a context
        :return: conditional probability
        """
        try:
            count_of_token = self.ngram_counter[(context, token)]
            count_of_context = float(len(self.context[context]))
            result = count_of_token / count_of_context

        except KeyError:
            result = 0.0
        return result

    def random_token(self, context):
        """
        Given a context, select the next word based on its probability
        :param context: context of previous words
        :return: selected word
        """
        token_of_interest = self.context.get(context, [])
        if not token_of_interest:
            return ''  # return empty string if context not found in model
        probabilities = [self.prob(context, token) for token in token_of_interest]
        selected_token = random.choices(token_of_interest, weights=probabilities, k=1)[0]
        return selected_token               


    def generate_text(self, token_count: int):
        """
        :param token_count: number of words to be produced
        :return: generated text
        """
        n = self.n
        context_queue = (n - 1) * ['<START>']
        result = []
        for _ in range(token_count):
            obj = self.random_token(tuple(context_queue))
            result.append(obj)
            if n > 1:
                context_queue.pop(0)
                if obj == '.':
                    context_queue = (n - 1) * ['<START>']
                else:
                    context_queue.append(obj)
        return ' '.join(result)

# class NGramInterpolator:
#     def __init__(self, n, lambdas):
#         self.n = n
#         self.lambdas = lambdas
#         self.model = []
#         for i in range(n):
#             self.model.append(NgramModel(i))

#     def update(self, text):
#         data = open(text, 'r')
#         contents = data.read()
#         sentences = contents.splitlines()
#         for i in range(self.n):
#             for s in sentences:
#                 self.model[i].update(s)

#     def prob(self, context, token):
#         """
#         Calculates probability of a candidate token to be generated given a context
#         :return: conditional probability
#         """
#         try:
#             count_of_token = self.ngram_counter[(context, token)]
#             count_of_context = float(len(self.context[context]))
#             result = count_of_token / count_of_context

#         except KeyError:
#             result = 0.0
#         return result
    
def create_ngram_model(n, path):
    m = NgramModel(n)
    with open(path, 'r',encoding='utf-8') as f:
        text = f.read()
        text = text.split('.')
        for sentence in text:
            # add back the fullstop
            sentence += '.'
            m.update(sentence)
    return m



if __name__ == "__main__":
    start = time.time()
    m = create_ngram_model(4, 'Moby_dick.txt')

    print (f'Language Model creating time: {time.time() - start}')
    start = time.time()
    random.seed(7)
    print(f'{"="*50}\nGenerated text:')
    print(m.generate_text(100))
    print(f'{"="*50}')
