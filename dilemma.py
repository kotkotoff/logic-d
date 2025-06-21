import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Nodes and initial distinctions in the extended scene
N_0 = {'g1', 'g2', 'r', 'b1', 'b2', 'b3', 'b4'}  # g1, g2 – goals; r – resource; b1–b4 – background nodes
D_0 = [
    ('g1', 'g2', 'alpha_utility'),    # Conflict between goals
    ('g1', 'r', 'alpha_utility'),     # g1 depends on resource
    ('g2', 'r', 'alpha_utility'),     # g2 depends on resource
    ('g1', 'b1', 'alpha_reward'),     # g1 linked to reward b1
    ('g2', 'b2', 'alpha_reward'),     # g2 linked to reward b2
    ('g1', 'b3', 'alpha_priority'),   # g1 linked to priority b3
    ('g2', 'b4', 'alpha_value')       # g2 linked to value b4
]
A_0 = {'alpha_utility', 'alpha_reward', 'alpha_priority', 'alpha_value', 'alpha_time'}  # Available aspects
w = 0.3  # Weight used in coherence function

# Coherence function for a single distinction
def coherence_advanced(D, D_set):
    x, y, a = D
    total = 0
    for x2, y2, a2 in D_set:
        if (x, y, a) == (x2, y2, a2):
            continue
        connected = (x in {x2, y2} or y in {x2, y2})
        aspect_diff = a != a2
        total += w * connected * aspect_diff
    return total

# Total coherence of a scene
def C_scene_advanced(D_set):
    return sum(coherence_advanced(D, D_set) for D in D_set) / len(D_set) if D_set else 0

# Differentiation with context-sensitive strategies
def differentiate_contextualized(conflict_D, D_0_set, beta):
    alpha_conflict = conflict_D[2]
    x, y, _ = conflict_D
    D_new_set = [d for d in D_0_set if coherence_advanced(d, D_0_set) >= 0.3]  # Retain coherent distinctions

    # Strategy depends on the selected beta-aspect
    if beta == 'alpha_reward':
        alpha_new = 'alpha_reward_balanced'
        D_star = (x, y, alpha_new)
        new_links = [(x, 'b1', alpha_new), (y, 'b2', alpha_new)]  # Emphasize reward links
    elif beta == 'alpha_priority':
        alpha_new = 'alpha_priority_focus'
        D_star = (x, 'b3', alpha_new)  # Redirect focus to priority
        new_links = [(y, 'b3', alpha_new)]
    elif beta == 'alpha_value':
        alpha_new = 'alpha_value_optimized'
        D_star = (y, 'b4', alpha_new)  # Emphasize g2’s value
        new_links = [(x, 'b4', alpha_new)]
    elif beta == 'alpha_time':
        alpha_new = 'alpha_time_efficient'
        D_star = (x, y, alpha_new)  # Temporal resolution
        new_links = []

    D_new = D_new_set + [D_star] + new_links
    C_new = C_scene_advanced(D_new)
    delta_C = C_new - C_scene_advanced(D_0_set)  # Coherence improvement
    preference_score = delta_C * (1 + 0.1 * len(new_links))  # Score = ΔC + bonus for added structure
    return beta, alpha_new, D_star, new_links, C_new, preference_score

# Conflict distinction to resolve
conflict_D = ('g1', 'g2', 'alpha_utility')

# Iterate over all candidate beta-aspects
results = []
for beta in A_0 - {'alpha_utility'}:
    beta, alpha_new, D_star, new_links, C_new, score = differentiate_contextualized(conflict_D, D_0, beta)
    results.append((beta, alpha_new, D_star, new_links, C_new, score))

# Build result table and select best resolution
df = pd.DataFrame(results, columns=["β", "α_new", "D*", "New Links", "C(S_1)", "Preference Score"])
df["C(S_0)"] = C_scene_advanced(D_0)
df["ΔC"] = df["C(S_1)"] - df["C(S_0)"]
df["Total Score"] = df["Preference Score"]
preferred_solution = df.loc[df["Total Score"].idxmax()]

print("Preferred Solution:")
print(preferred_solution)
print("\nAll Results:")
print(df)

# Visualize preferred solution
_, _, D_star, new_links, _, _ = differentiate_contextualized(conflict_D, D_0, preferred_solution["β"])
D_new = [d for d in D_0 if coherence_advanced(d, D_0) >= 0.3] + [D_star] + new_links
draw_scene(D_new, f"Preferred Scene with β={preferred_solution['β']}")

# Graph rendering function
def draw_scene(D_set, title):
    G = nx.DiGraph()
    for x, y, a in D_set:
        G.add_edge(x, y, aspect=a)
    pos = nx.spring_layout(G, seed=42)
    edge_colors = ['red' if d['aspect'] == 'alpha_utility' else
                   'blue' if 'reward' in d['aspect'] else
                   'green' if 'priority' in d['aspect'] else
                   'orange' if 'value' in d['aspect'] else
                   'purple' for _, _, d in G.edges(data=True)]
    plt.figure(figsize=(8, 5))
    nx.draw(G, pos, with_labels=True, edge_color=edge_colors, node_color='lightgray')
    edge_labels = {(u, v): d['aspect'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title(title)
    plt.show()
