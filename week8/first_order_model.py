import random
from collections import defaultdict

class FirstOrderARLM:
    def __init__(self):
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.probabilities = defaultdict(dict)
        
    def train(self, tokenized_sentences):
        for sentence in tokenized_sentences:
            for i in range(len(sentence) - 1):
                current_token = sentence[i]
                next_token = sentence[i+1]
                self.transitions[current_token][next_token] += 1
                
        for current_token, next_tokens in self.transitions.items():
            total_transitions = sum(next_tokens.values())
            for next_token, count in next_tokens.items():
                self.probabilities[current_token][next_token] = count / total_transitions
                
    def get_probabilities(self, token):
        return self.probabilities.get(token, {})
            
    def predict_greedy(self, token):
        if token in self.probabilities:
            dist = self.probabilities[token]
            return max(dist, key=dist.get)
        return None
        
    def generate_sentence(self, mode="sampling"):
        current_token = "<START>"
        sentence = []
        
        while current_token != "<END>":
            if current_token not in self.probabilities:
                break 
                
            dist = self.probabilities[current_token]
            next_tokens = list(dist.keys())
            
            if mode == "greedy":
                next_token = max(dist, key=dist.get)
            else:
                probs = list(dist.values())
                next_token = random.choices(next_tokens, weights=probs, k=1)[0]
            
            if next_token != "<END>":
                sentence.append(next_token)
                
            current_token = next_token
            
        return " ".join(sentence)

    def test_normalization(self):
        print("--- Probability Normalization Test ---")
        for word, next_words in self.probabilities.items():
            total = sum(next_words.values())
            print(f"Token '{word}': Sum of probabilities = {total:.4f}")

if __name__ == "__main__":
    corpus = [
        "the cat sat on the mat", "the cat sat on the rug",
        "the dog sat on the mat", "the dog ran to the park",
        "the cat ran to the park", "the dog sat on the rug"
    ]
    training_data = [["<START>"] + s.split() + ["<END>"] for s in corpus]
    
    model = FirstOrderARLM()
    model.train(training_data)
    model.test_normalization()
    
    print("\n--- Greedy Generation ---")
    for _ in range(3): print(model.generate_sentence(mode="greedy"))
    
    print("\n--- Sampling Generation ---")
    for _ in range(3): print(model.generate_sentence(mode="sampling"))