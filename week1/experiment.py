import torch
import torch.nn as nn
import torch.optim as optim

# Dataset
X = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y_bin = torch.tensor([[0.0], [1.0], [1.0], [0.0]])
y_multi = torch.tensor([0, 1, 1, 2])

# --- Binary XOR Experiment ---
torch.manual_seed(42)
model_bin = nn.Sequential(
    nn.Linear(2, 2),
    nn.Tanh(),
    nn.Linear(2, 1)
)
criterion_bin = nn.BCEWithLogitsLoss()
optimizer_bin = optim.SGD(model_bin.parameters(), lr=1.0)

for epoch in range(2000):
    optimizer_bin.zero_grad()
    logits = model_bin(X)
    loss = criterion_bin(logits, y_bin)
    loss.backward()
    
    if epoch == 0:
        early_grad_norm = model_bin[0].weight.grad.norm().item()
        
    optimizer_bin.step()

with torch.no_grad():
    final_probs = torch.sigmoid(model_bin(X))
    preds = (final_probs > 0.5).int()

# --- Three-Class Extension ---
torch.manual_seed(42)
model_multi = nn.Sequential(
    nn.Linear(2, 2),
    nn.Tanh(),
    nn.Linear(2, 3)
)
criterion_multi = nn.CrossEntropyLoss()
optimizer_multi = optim.SGD(model_multi.parameters(), lr=1.0)

for epoch in range(2000):
    optimizer_multi.zero_grad()
    logits_multi = model_multi(X)
    loss_multi = criterion_multi(logits_multi, y_multi)
    loss_multi.backward()
    optimizer_multi.step()

with torch.no_grad():
    probs_multi = torch.softmax(model_multi(X), dim=1)