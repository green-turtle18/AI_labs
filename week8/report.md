# Laboratory: Bayesian Networks and Autoregressive Language Models

## Deliverable 3: Conditional Probability Tables
Based on the provided 6-sentence corpus, here are the CPTs for the requested contexts:
*   **P(next | 'the'):** cat (3/12 = 0.25), dog (3/12 = 0.25), mat (2/12 ≈ 0.167), rug (2/12 ≈ 0.167), park (2/12 ≈ 0.167)
*   **P(next | 'cat'):** sat (2/3 ≈ 0.667), ran (1/3 ≈ 0.333)
*   **P(next | 'dog'):** sat (2/3 ≈ 0.667), ran (1/3 ≈ 0.333)
*   **P(next | 'sat'):** on (4/4 = 1.0)
*   **P(next | 'ran'):** to (2/2 = 1.0)
*   *Zero-probability transitions:* P(park | sat) = 0, P(dog | cat) = 0.

## Deliverable 4: Examples of Generated Text
**First-Order Sampling:**
1. the cat ran to the rug
2. the dog sat on the park
3. the cat sat on the mat

**First-Order Greedy:**
1. the cat sat on the cat sat on the cat... (gets stuck in an infinite loop without an END token)

**Second-Order Sampling:**
1. the dog ran to the park
2. the cat sat on the rug
3. the dog sat on the mat

## Deliverable 5: Probability Normalization Test
The output of `test_normalization()` confirms that the sum of probabilities for every state equals 1.0:
*   Token '<START>': Sum of probabilities = 1.0000
*   Token 'the': Sum of probabilities = 1.0000
*   Token 'cat': Sum of probabilities = 1.0000
... (all contexts sum perfectly to 1.0)

## Deliverable 6: Answers to Questions 1–14
**Q1:** This decomposition is useful because it aligns perfectly with how text is generated: one word at a time, based on what has already been said[cite: 4].
**Q2:** $P(X_t \vert{} X_1, ..., X_{t-1}) \approx P(X_t \vert{} X_{t-1})$. This makes the Markov assumption that the future depends only on the immediate past[cite: 4].
**Q3:** (Answered in Deliverable 3 above).
**Q4:** The transition counts are stored in the nested `defaultdict` named `self.transitions`.
**Q5:** It is computed in the `train()` method by dividing each transition count by the sum of all outgoing transition counts for a given state.
**Q6:** The program samples from the probability distribution using `random.choices(weights=probs)`. This allows generation proportional to probability, rather than just forcing the maximum probability (greedy) every time.
**Q7:** If the program encounters a word with no transitions, the code `break`s the loop, effectively halting sentence generation early to prevent a crash.
**Q8:** If the total is 0.87, it indicates a bug in the implementation where probability mass is "leaking" (e.g., the counts weren't tallied correctly, or a state was skipped). The sum must mathematically be exactly 1.0[cite: 4].
**Q9:** The predictions are constrained entirely by the tiny dataset. While a human might expect "the" to be followed by a vast vocabulary, the model firmly predicts "cat" or "dog" because that is its entire universe. 
**Q10:** Sampling produces variation because it draws from a distribution. Greedy generation produces the exact same sentence every single time, often resulting in deterministic infinite loops if a cycle exists (e.g., "the cat sat on the cat...").
**Q11:** 
1. Graph structure: $X_{t-2} \rightarrow X_t \leftarrow X_{t-1}$[cite: 4].
2. CPT: Conditioned on a tuple of two words instead of one.
3. Context: Looking two words back instead of one[cite: 4].
4. Data: Exponentially more data is required to observe all pairs.
**Q12:** Increasing context improves prediction because it resolves ambiguity (e.g., "to the" implies "park", whereas just "the" is ambiguous). However, the CPT grows exponentially, leading to many zero-probability contexts if the dataset is small[cite: 4].
**Q13:** Approach B is preferable because it clearly specifies the mathematical rules, invariants, and behaviour. Asking for "a language model" might yield a Blackbox ML library, whereas specifying the probabilistic constraints ensures the engineer actually understands and builds the specific intelligent system requested[cite: 4].
**Q14:** Thinking of the language model as a Bayesian Network gives: 1) a clear visual representation of dependencies; 2) a strict mathematical factorisation of the joint distribution; 3) a principled, logical method for generation via ancestral sampling[cite: 4].

## Deliverable 7: Reflection on LLM Usage
I used the LLM (Approach B) to generate the structural boilerplate of the counting loops and probability assignments. I validated the output by writing and running the `test_normalization()` function to guarantee the CPTs were mathematically sound[cite: 4]. 

**Correction Example:** When I asked the LLM to generate the second-order model, its initial code crashed on `generate_sentence()` because it didn't know how to supply the first *two* tokens to kick off the generation loop. I had to manually inspect the LLM-generated logic and correct it by hardcoding the initial `context = ("<START>", "the")` tuple so the second-order model had enough context to begin sampling properly.