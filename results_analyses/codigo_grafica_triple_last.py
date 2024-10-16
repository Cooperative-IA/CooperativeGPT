import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Load JSON data
with open('results_red_over_yellow.json', 'r') as file:
    red_over_yellow = json.load(file)
    
with open('results_explore_when_red.json', 'r') as file:
    explore_when_red = json.load(file)


defect_percentages_data ={
    'CoTAgent': {
        'gpt4o_mini': [el/100 for el in results['GPT4o_mini']['CotAgent']['defect_percentages']],
        'gpt4o':  [el/100 for el in results['GPT4o']['CotAgent']['defect_percentages']]
    },
    'GenerativeAgents': {
        'gpt4o_mini': [el/100 for el in results['GPT4o_mini']['GenerativeAgents']['defect_percentages']],
        'gpt4o':  [el/100 for el in results['GPT4o']['GenerativeAgents']['defect_percentages']]
    }
}

# Extract the first elements from each tuple for each agent-model combination
def extract_first_elements(data):
    return {
        agent: {model: [val[0] for val in values] for model, values in models.items()}
        for agent, models in data.items()
    }

# Extract data for the second and third plots
data_second = extract_first_elements(red_over_yellow)
data_third = extract_first_elements(explore_when_red)

# Colors for each specific model (orange for GPT4o-mini and blue for GPT4o)
subcat_colors = [
    {"facecolor": "#ffcc99", "color": "#cc6600"},  # GPT4o-mini (CoTAgents y GenAgents)
    {"facecolor": "#66b3ff", "color": "#003366"}   # GPT4o (CoTAgents y GenAgents)
]

# Labels for the legend (GPT4o-mini and GPT4o)
legend_labels = [
    "GPT4o-mini",
    "GPT4o"
]

# Create subplots for each scenario with improved graphics
fig, axs = plt.subplots(1, 3, figsize=(12, 6))

# Define labels and positions
labels = ['CoTAgent-GPT4o_mini', 'CoTAgent-GPT4o', 'GenAgents-GPT4o_mini', 'GenAgents-GPT4o']
positions = [1, 2, 3, 4]

# Function to plot boxplots with individual legends and titles
def plot_boxplot(ax, data, title, colors, use_legend = True):
    all_data = []
    for agent in data:
        for model in data[agent]:
            all_data.append(data[agent][model])
    
    # Create boxplots for each model with custom colors
    for idx, model_data in enumerate(all_data):
        color_idx = idx % 2  # Alternate colors between GPT4o_mini and GPT4o
        boxprops = colors[color_idx]
        ax.boxplot(model_data, positions=[positions[idx]], patch_artist=True,
                   boxprops=dict(facecolor=boxprops["facecolor"], color=boxprops["color"]),
                   medianprops=dict(color=boxprops["color"]), showmeans=True)
    
    ax.set_title(title, fontsize=14)
    ax.set_xticks([1.5, 3.5])  # Position the ticks between the grouped models
    ax.set_xticklabels(['CoTAgents', 'GenAgents'], fontsize=14)
    ax.grid(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Add a legend
    legend_elements = [
        Patch(facecolor=colors[0]['facecolor'], edgecolor=colors[0]['color'], label="GPT4o-Mini"),
        Patch(facecolor=colors[1]['facecolor'], edgecolor=colors[1]['color'], label="GPT4o")
    ]
    if use_legend:
        ax.legend(handles=legend_elements, loc='upper right', fontsize=14)

# Plot each indicator
plot_boxplot(axs[0], defect_percentages_data, "Defect Percentage\n Across Scenarios", subcat_colors)
plot_boxplot(axs[1], data_second, "Proportion of Red Coins\n Taken Over Yellow Coins", subcat_colors, use_legend=False)
plot_boxplot(axs[2], data_third, "Proportion of Explore or Stay\n Actions When Red Coin Visible", subcat_colors, use_legend=False)


# Add a common y-axis label
#fig.text(0.04, 0.5, 'Performance', va='center', rotation='vertical', fontsize=12)

# Add overall labels and title
#fig.suptitle("Coins Scenario 1 - Agents Performance Indicators", fontsize=18)
axs[0].set_ylabel("Indicator value", fontsize=14)

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig("boxplot_comparison.png", dpi=800)
plt.show()
