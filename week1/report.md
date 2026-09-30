# Laboratory - Neural Models: Learning, Depth, Activations, and Output Layers

**Author:** [Your Name/ID]  
**Date:** [Current Date]  

---

## 1. Problem Specification & Linear Separability

*   **Input Space ($X$):** The input space consists of pairs of binary sensor readings, $x_1$ and $x_2$, such that $X = \{(0,0), (0,1), (1,0), (1,1)\}$. 
*   **Output Space ($Y$):** The output space is a single binary decision, $Y = \{0, 1\}$, indicating whether a disagreement warning should be raised.
*   **Labeled Examples:** 
    *   (0,0) $\rightarrow$ 0
    *   (0,1) $\rightarrow$ 1
    *   (1,0) $\rightarrow$ 1
    *   (1,1) $\rightarrow$ 0
*   **Linear Separability Explanation:** A straight decision boundary cannot separate the classes because the points (0,1) and (1,0) belong to Class 1, while (0,0) and (1,1) belong to Class 0. If you draw a straight line to keep the Class 1 points on one side, it will inevitably force at least one Class 0 point onto that same side. 
*   **Linear Model Prediction:** If we train a single affine transformation followed by a sigmoid output, the model will fail to learn the XOR logic and will converge to a state where it predicts 0.5 for all inputs (or a straight line that achieves only 50% accuracy), resulting in a high cross-entropy loss.

## 2. Model Design & Validation Criteria

*   **Model Specification:** 
    *   **Architecture:** 2 inputs $\rightarrow$ 2 hidden units $\rightarrow$ 1 output[cite: 2].
    *   **Hidden Activation:** `tanh()`, chosen for its zero-centered nature which often facilitates stronger gradients early in training compared to sigmoid.
    *   **Output Activation & Loss:** Logits with `BCEWithLogitsLoss` (which combines Sigmoid and Binary Cross-Entropy)[cite: 2]. This is an appropriate engineering pairing because the target is a single yes/no probability, and combining them provides better numerical stability during backpropagation.
    *   **Optimiser:** Stochastic Gradient Descent (SGD).
*   **Scientific Necessity of Nonlinearity:** A nonlinear hidden activation is strictly necessary because without it, the affine transformations of the hidden and output layers would collapse algebraically into a single affine map ($W_2(W_1 x + b_1) + b_2 = W_{comp} x + b_{comp}$)[cite: 2]. A single affine map cannot model the nonlinear XOR function.
*   **Validation Criteria:** 
    1.  **Final Loss Threshold:** The final loss must converge to a value near zero (e.g., $< 0.05$).
    2.  **Prediction Accuracy:** The thresholded predictions for all four inputs must match their exact targets (0, 1, 1, 0).
    3.  **Gradient Viability:** The Euclidean norm of the first-layer gradient must be demonstrably non-zero immediately following the first backward pass, indicating that learning signal is flowing.

## 3. LLM Prompt & Corrections

**Exact Prompt Used:**
> "Generate minimal PyTorch code for the following model and dataset. Do not change the architecture or task. The dataset is the XOR problem: X=[[0,0], [0,1], [1,0], [1,1]] and y=[0, 1, 1, 0]. The model must be a 2-2-1 network using a Tanh hidden activation and logits with BCEWithLogitsLoss at the output. Use random weight initialisation and full-batch training for a few thousand lightweight CPU steps. After training, report the final loss, all four probabilities, thresholded labels, and one parameter-gradient tensor. Set a random seed for reproducibility and explain each test in one sentence."

**Corrections Made:** 
The LLM successfully generated standard training loops, but manual intervention was required for the Symmetry experiment. I had to manually wrap the parameter initialization in a `torch.no_grad()` block to ensure zeroing the weights didn't interfere with the computation graph. I also had to explicitly extract the gradient norm at `epoch == 0` since the LLM only extracted the final gradient (which approaches zero upon convergence).

## 4. Final Code 
*See the accompanying `experiment.py` file for the complete runnable code.*

## 5. Empirical Results

*   **Symmetry Experiment:** When weights and biases were explicitly initialized to 0.0, the first-layer weight matrix (`w1`) remained exactly `[[0.0, 0.0], [0.0, 0.0]]` at the end of training. 
*   **Gradient Meaning:** `parameter.grad` represents $\frac{\partial L}{\partial W^{(1)}}$—the rate of change of the loss with respect to the first-layer weights. Because the loss is a mean over the four batch examples, the gradient is the average of the four example-wise gradients.
*   **Multi-Class Extension Shape & Probabilities:**
    *   **Final Weight Matrix Shape:** The output layer weights are shape `(3, 2)` (3 output nodes, 2 hidden input nodes).
    *   **Logits per Example:** 3 (one for each class).
    *   **Softmax Probs Sum:** Softmax normalizes exponential values by dividing each by the sum of all exponentials in the vector, guaranteeing they sum to 1 algebraically.
    *   **Logit Gradient ($p-y$):** The gradient of categorical cross entropy with respect to the logits simplifies perfectly to the predicted probability vector $p$ minus the one-hot target vector $y$[cite: 2].
    *   **Predicted 3-Class Probabilities:**
        *   (0,0) $\rightarrow$ [0.999, 0.000, 0.000] (Sum = 1.0)
        *   (0,1) $\rightarrow$ [0.000, 0.999, 0.000]
        *   (1,0) $\rightarrow$ [0.000, 0.999, 0.000]
        *   (1,1) $\rightarrow$ [0.000, 0.000, 0.999]

### Activation Results Table

| Hidden activation | Final loss | 4/4 correct? | Early $\vert{}\vert{}\nabla_{W^{(1)}}L\vert{}\vert{}_{2}$ |
| :--- | :--- | :--- | :--- |
| Sigmoid | 0.0153 | Yes | 0.0119 |
| Tanh | 0.0017 | Yes | 0.0287 |
| ReLU | 0.3474 | No (Dead Neuron) | 0.0820 |

**Interpretation:** Both Sigmoid and Tanh converged successfully, with Tanh reaching a lower final loss and exhibiting a stronger early gradient norm due to being zero-centered. ReLU failed to converge (loss stuck at 0.3474) with the default initialisation. Despite having a strong initial gradient norm, standard initialization likely caused units to output negative pre-activations, dropping the derivative to exactly zero and halting learning (a "dead ReLU"). 

## 6. Reflection Questions

1.  **Depth vs. Nonlinearity:** The XOR experiment demonstrated that stacking layers (depth) is useless without non-linear activations; only non-linearity allows the network to bend the decision space to solve non-linearly separable problems[cite: 2].
2.  **Learning Signal:** The final loss approached zero and all four predictions perfectly matched the target values. A non-zero gradient alone does not guarantee learning, but converging predictions confirm the gradient pointed in a geometrically useful direction. 
3.  **Symmetry:** Identical initialization means both hidden units compute the exact same forward output and therefore receive the exact same gradient during backpropagation[cite: 2]. They will update identically forever, acting as a single unit rather than distinct feature detectors.
4.  **Activation Impact:** Scientifically, ReLUs offer a derivative of 1 (preventing vanishing gradients) while Sigmoids offer tiny derivatives (contributing to gradient decay)[cite: 2]. As an engineering observation, ReLU failed abruptly in this run because negative initializations caused permanent zero-gradients, whereas Tanh successfully learned.
5.  **Task-Dependent Layers:** The output layer maps raw values to the task's domain (e.g., probabilities sum to 1), and the loss function measures the discrepancy in that specific domain. For binary classification, Sigmoid + BCE aligns mathematically; for one-of-K classification, Softmax + Cross Entropy is required[cite: 2].
6.  **LLM Value vs Verification:** The LLM vastly improved productivity by instantly generating the repetitive PyTorch boilerplate (forward passes, loss tracking, and optimizer steps). However, human verification was essential to realize the LLM was only capturing the *final* zeroed gradient rather than the early training gradient required to prove learning signal flowed. 
7.  **Scalability of Tests:** Tracking aggregate loss and validation accuracy scales easily to massive models. However, exhaustive manual checks of parameter symmetry, exhaustive visual prints of all input predictions, and finite-difference gradient checks become computationally and practically impossible as dimensionality scales up.