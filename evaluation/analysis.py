import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import krippendorff

# =========================
# PATHS
# =========================

DATA_PATH_1 = os.path.join("data", "Data_Part1_cleaned.csv")
DATA_PATH_2 = os.path.join("data", "Data_Part2_cleaned.csv")
RESULTS_DIR = os.path.join("results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ===========================
# LATEX FIGURE CONFIGURATION
# ===========================

latex_width_pt = 418.25555 #in pt
latex_width = latex_width_pt / 72.27 #in inches

def set_size(width, fraction=1):
    """Set figure dimensions to avoid scaling in LaTeX."""

    fig_width_in = width * fraction
    fig_height_in = fig_width_in * 0.618 #Golden ratio
    return (fig_width_in, fig_height_in)

# =========================
# LIKERT CONVERSION
# =========================

LIKERT_MAP = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

LIKERT_LABELS = [
    label for label, _ in sorted(
        LIKERT_MAP.items(),
        key=lambda x: x[1]
    )
]

def convert_likert(value):
    """Convert Likert labels to numerical values."""

    if pd.isna(value):
        return np.nan
    if value in LIKERT_MAP:
        return LIKERT_MAP[value]
    try:
        return float(value)
    except:
        return np.nan


# =========================
# LOAD DATA
# =========================

def load_data(path):
    """Load data from cdv file into dataframe."""

    df = pd.read_csv(path, header=0)

    df = df.iloc[1:].reset_index(drop=True)

    for col in df.columns:
        df[col] = df[col].apply(convert_likert)

    return df


# =========================
# HELPERS
# =========================

def get_columns(df, prefix, round_id, x_values, y_value=None):
    """Get columns based on block, round, instance and criterion."""

    cols = []

    for x in x_values:
        if y_value is None:
            name = f"{prefix}{round_id}.{x}"
        else:
            name = f"{prefix}{round_id}.{x}_{y_value}"

        if name in df.columns:
            cols.append(name)

    return cols


def average_columns(df, columns):
    """Calculate average across columns."""

    if not columns:
        return None
    return df[columns].astype(float).mean(axis=1)


def round_seconds(series):
    """Round seconds to zero decimals."""

    return series.round(0).astype("Int64")


# =========================
# USER STUDY PART 1
# =========================

# =========================
# DIAGRAM 1 — DURATION
# =========================

def plot_time(df):
    """Plot average duration per participant per round."""

    cols_r1 = get_columns(df, "TIME", 1, [1, 2, 3])
    cols_r2 = get_columns(df, "TIME", 2, [1, 2, 3])

    r1 = (average_columns(df, cols_r1) / 60).round(2)
    r2 = (average_columns(df, cols_r2) / 60).round(2)

    width = latex_width * 0.6
    height = width * 1
    plt.figure(figsize=(width, height))

    x1 = np.ones(len(r1))
    x2 = np.ones(len(r2)) * 2

    for i in range(len(r1)):
        if pd.notna(r1[i]) and pd.notna(r2[i]):
            plt.scatter([1, 2], [r1[i], r2[i]], color=plt.cm.viridis(i / 5))
            plt.plot([1, 2], [r1[i], r2[i]], linestyle="--", color=plt.cm.viridis(i / 5))
            print(f"P{i+1}: 1 = {r1[i]:.2f} min, 2 = {r2[i]:.2f} min, D = {r2[i] - r1[i]:.2f}, T = {r2[i]/r1[i]:.2f}")

    plt.xticks([1, 2], ["1\n(without\nassistance)", "2\n(with\nbrowser extension)"], fontsize=9)
    plt.yticks(range(0, 9), fontsize=9)

    plt.xlabel("Round", fontsize=10, labelpad=10)
    plt.ylabel("Minutes", fontsize=10, labelpad=10)

    plt.xlim(0.75, 2.25)
    plt.ylim(0, 8)

    plt.grid(axis='y', linestyle=':', alpha=0.4)

    out = os.path.join(RESULTS_DIR, "time_dot_individual.png")
    plt.savefig(out, bbox_inches="tight")

    plt.close()


# ================================
# DIAGRAM 2 — WILLINGNESS TO POST
# ================================

def plot_willingness(df):
    """Plot average Willingness-to-post per participant per round."""

    cols_r1 = get_columns(df, "AUTH", 1, [1, 2, 3], 5)
    cols_r2 = get_columns(df, "AUTH", 2, [1, 2, 3], 5)

    r1 = average_columns(df, cols_r1)
    r2 = average_columns(df, cols_r2)

    width = latex_width * 0.6
    height = width * 1
    plt.figure(figsize=(width, height))

    x1 = np.ones(len(r1))
    x2 = np.ones(len(r2)) * 2

    for i in range(len(r1)):
        if pd.notna(r1[i]) and pd.notna(r2[i]):
            plt.scatter([1, 2], [r1[i], r2[i]], color=plt.cm.viridis(i / 5))
            plt.plot([1, 2], [r1[i], r2[i]], linestyle="--", color=plt.cm.viridis(i / 5))

    plt.xticks([1, 2], ["1\n(without\nassistance)", "2\n(with\nbrowser extension)"], fontsize=9)
    plt.yticks(range(1, len(LIKERT_LABELS) + 1), LIKERT_LABELS, fontsize=9)
    
    plt.xlabel("Round", fontsize=10, labelpad=10)
    plt.ylabel("Likert Scale", fontsize=10, labelpad=10)
    
    plt.xlim(0.75, 2.25)
    plt.ylim(0.75, 5.25)

    plt.grid(axis='y', linestyle=':', alpha=0.4)

    out = os.path.join(RESULTS_DIR, "willingness_dot_individual.png")
    plt.savefig(out, bbox_inches="tight")

    plt.close()


# ===============================================
# DIAGRAM 3 — AUTHENTICICITY EVALUATION (ROUND 2)
# ===============================================

def plot_authentic_dots(df):
    """Plot average Likert scale ratings per authenticity criterion per round."""

    AUTHENTICITY_ITEM_LABELS = [
        "Self-identity", 
        "Sense of Agency", 
        "Accountability", 
        "Naturalness", 
        "Willingness to Post"
    ]
    
    plt.figure(figsize=set_size(latex_width))
    
    dots_per_row = 3
    dot_spacing_y = 0.2
    dot_size = 45
    
    for i, label in enumerate(AUTHENTICITY_ITEM_LABELS):
        cols = get_columns(df, "AUTH", 2, [1, 2, 3], i + 1)
        values = df[cols].values.flatten()
        values = values[~np.isnan(values)]
        
        y_shift = -0.2
        
        for score in range(1, 6):
            count = np.sum(values == score)
            
            for dot_idx in range(int(count)):
                row_number = dot_idx // dots_per_row
                col_number = dot_idx % dots_per_row
                
                x_offset = (col_number - 1) * 0.125
                y_pos = i + y_shift + (row_number * dot_spacing_y)
                
                plt.scatter(
                    score + x_offset, 
                    y_pos,
                    color=plt.cm.viridis(i / len(AUTHENTICITY_ITEM_LABELS)), 
                    edgecolors='white', 
                    linewidth=0.7,
                    s=dot_size,
                    zorder=3
                )

    plt.yticks(range(len(AUTHENTICITY_ITEM_LABELS)), AUTHENTICITY_ITEM_LABELS, fontsize=9)

    ytick_labels = plt.gca().get_yticklabels()

    for i, label_obj in enumerate(ytick_labels):
        color = plt.cm.viridis(i / len(AUTHENTICITY_ITEM_LABELS))
        label_obj.set_color(color)
    
    LIKERT_LABELS_DISPLAY = ["Strongly\ndisagree", "Disagree", "Neutral", "Agree", "Strongly\nagree"]
    plt.xticks(range(1, 6), LIKERT_LABELS_DISPLAY, fontsize=9)

    plt.gca().invert_yaxis()

    plt.xlim(0.5, 5.5)
    plt.ylim(4.5, -0.5) #reversed because of axis inversion
    
    plt.xlabel("Likert Scale", fontsize=10, labelpad=10)
    plt.ylabel("Authenticity Criteria", fontsize=10, labelpad=10)
    
    plt.grid(axis='x', linestyle=':', alpha=0.4)

    out = os.path.join(RESULTS_DIR, "authentic_dots.png")
    plt.savefig(out, bbox_inches="tight")

    plt.close()


# =========================
# USER STUDY PART 2
# =========================

PARTICIPANTS = ["P1", "P2", "P3", "P4", "P5"]

EFFECTIVENESS_ITEM_LABELS = ['EMP', 'NTOX', 'REL', 'SPEC', 'PERS']

# =============================================
# TABLE 1 — EFFECTIVENESS (ROUND 1 vs. ROUND 2)
# =============================================

def compute_effectiveness_means(df):
    """Calculate average Likert scale ratings per effectiveness criterion per round."""                 

    results = {
        1: [],
        2: [],
    }

    for item in range(1, 6):

        for rnd in [1, 2]:
            sub = df[
                (df["Round"] == rnd) &
                (df["LikertItem"] == item)
            ]

            values = sub[PARTICIPANTS].values.flatten()
            values = values[~pd.isna(values)]

            mean_val = np.mean(values)

            results[rnd].append(mean_val)

    r1 = results[1]
    r2 = results[2]

    diff = [a2 - a1 for a1, a2 in zip(r1, r2)]

    table = pd.DataFrame(
        [
            [1] + r1,
            [2] + r2,
            ["$\Delta$"] + diff,
        ],
        columns=["Round"] + EFFECTIVENESS_ITEM_LABELS,
    )

    return table


def table_effectiveness(df):
    """Save effectiveness evaluation to LaTeX tabular."""

    table = compute_effectiveness_means(df)

    path = os.path.join(RESULTS_DIR, "table_effectiveness.tex")

    latex = table.to_latex(
        index=False,
        float_format="%.2f",
        column_format="lccccc",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(latex)


# ==========================================================
# TABLE 2 — INNER ANNOTATOR AGREEMENT (Krippendorff's alpha)
# ==========================================================

def calculate_alphas(df):
    """Calculate Krippendorff's alpha per effectiveness criterion."""
    
    results = {}
    
    mapping = dict(zip(range(1, 6), EFFECTIVENESS_ITEM_LABELS))
    
    for item_num, label in mapping.items():
        
        item_data = df[df['LikertItem'] == item_num][PARTICIPANTS]
        
        #Krippendorff expects (observers, items), so transpose (.T)
        reliability_data = item_data.values.T
        
        try:
            if reliability_data.size > 0:
                results[label] = krippendorff.alpha(
                    reliability_data=reliability_data, 
                    level_of_measurement='ordinal'
                )
            else:
                results[label] = np.nan
        except Exception:
            results[label] = np.nan

    results_df = pd.DataFrame([results])
    results_df.insert(0, '\textbf{Criterion}', r'\textbf{$\alpha$}')
            
    return results_df


def table_iaa(df):
    """Save IAA of effectiveness evaluation to LaTeX tabular."""
    
    table = calculate_alphas(df)

    path = os.path.join(RESULTS_DIR, "table_iaa.tex")

    latex = table.to_latex(
        index=False, 
        float_format="%.3f",
        column_format='lccccc'
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(latex)

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    df1 = load_data(DATA_PATH_1)
    df2 = load_data(DATA_PATH_2)

    plot_time(df1)
    plot_willingness(df1)
    plot_authentic_dots(df1)

    table_effectiveness(df2)
    table_iaa(df2)

    print("Done")