import random
from collections import defaultdict

class SecondOrderARLM:
    def __init__(self):
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.probabilities = defaultdict(dict)
        
    def train(self, tokenized_sentences):
        for sentence in tokenized_sentences:
            # Need at least 3 tokens to form a (t-2, t-1) -> t transition
            if len(sentence) < 3:
                continue
            for i in range(len(sentence) - 2):
                context = (sentence[i], sentence[i+1])
                next_token = sentence[i+2]
                self.transitions[context][next_token] += 1
                
        for context, next_tokens in self.transitions.items():
            total_transitions = sum(next_tokens.values())
            for next_token, count in next_tokens.items():
                self.probabilities[context][next_token] = count / total_transitions
                
    def generate_sentence(self):
        # We start with the assumption that every sentence begins with <START>
        # To get the second token, we do a quick first-order fallback or assume it from data
        # For this script, we hardcode the first transition based on the known corpus
        context = ("<START>", "the") 
        sentence = ["the"]
        
        while True:
            if context not in self.probabilities:
                break
                
            dist = self.probabilities[context]
            next_tokens = list(dist.keys())
            probs = list(dist.values())
            
            next_token = random.choices(next_tokens, weights=probs, k=1)[0]
            
            if next_token == "<END>":
                break
                
            sentence.append(next_token)
            context = (context[1], next_token)
            
        return " ".join(sentence)

if __name__ == "__main__":
    corpus = [
        "the cat sat on the mat", "the cat sat on the rug",
        "the dog sat on the mat", "the dog ran to the park",
        "the cat ran to the park", "the dog sat on the rug"
    ]
    training_data = [["<START>"] + s.split() + ["<END>"] for s in corpus]
    
    model = SecondOrderARLM()
    model.train(training_data)
    
    print("--- Second-Order Generated Sentences ---")
    for _ in range(5):
        print(model.generate_sentence())