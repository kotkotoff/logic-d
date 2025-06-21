import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Initial nodes and distinctions
N = {'A', 'B', 'C', 'Agent'}
A_0 = {'alpha_causal', 'alpha_context'}
D_0 = [
    ('A', 'B', 'alpha_causal'),
    ('B', 'C', 'alpha_causal'),
    ('Agent', 'A', 'alpha_context')
]
w = 0.3

# Coherence function
def coherence(d, D_set):
    x, y, a = d
    score = 0
    for x2, y2, a2 in D_set:
        if (x, y, a) == (x2, y2, a2): continue
        connected = x in {x2, y2} or y in {x2, y2}
        aspect_diff = a != a2
        score += w * connected * aspect_diff
    return score

# Total scene coherence
def coherence_scene(D):
    return sum(coherence(d, D) for d in D) / len(D) if D else 0

# Differentiation function: generate new distinction
def differentiate(D_set, nodes, aspects):
    all_pairs = [(x, y) for x in nodes for y in nodes if x != y]
    random.shuffle(all_pairs)
    for x, y in all_pairs:
        if not any((x, y, _) in D_set or (y, x, _) in D_set for _ in aspects):
            a = random.choice(list(aspects))
            return (x, y, a)
    return None

# Run simulation
history = []
D = D_0[:]
nodes = set(N)
aspects = set(A_0)

for t in range(15):
    C_t = coherence_scene(D)
    history.append((t, len(D), round(C_t, 3)))

    if C_t < 0.4:
        new = differentiate(D, nodes, aspects)
        if new:
            D.append(new)
    elif C_t > 1.0 and t % 2 == 0:
        if len(D) > 3:
            D.pop(random.randint(0, len(D)-1))
    else:
        nodes.add(f"X{t}")
        for _ in range(2):
            new = differentiate(D, nodes, aspects)
            if new: D.append(new)

# Plot coherence over time
df_hist = pd.DataFrame(history, columns=["Step", "Num Distinctions", "Coherence"])
plt.plot(df_hist["Step"], df_hist["Coherence"], marker='o')
plt.title("Scene Coherence Over Time")
plt.xlabel("Step")
plt.ylabel("Coherence")
plt.grid(True)
plt.show()

print(df_hist)
