import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def p_to_stars(p_value):
    # -------------------------------------------------------
    # Convert p-values to significance stars
    # -------------------------------------------------------
    if pd.isna(p_value):
        return ""

    if p_value < 0.0001:
        return "****"
    elif p_value < 0.001:
        return "***"
    elif p_value < 0.01:
        return "**"
    elif p_value < 0.05:
        return "*"
    else:
        return "ns"


def add_bracket(ax, x1, x2, y, height, text):
    # -------------------------------------------------------
    # Function to draw one significance bracket
    # -------------------------------------------------------
    ax.plot(
        [x1, x1, x2, x2],
        [y, y + height, y + height, y],
        color="black",
        linewidth=1.2,
        clip_on=False,
    )

    ax.text(
        (x1 + x2) / 2,
        y + height,
        text,
        ha="center",
        va="bottom",
        fontsize=11,
    )


def boxplot_with_statistics(data_plot,
                            sample_order,
                            var,
                            stats_plot,
                            y_axis = "",
                            save_dir = ".",
                            save_name = "",
                            ext = "png"):
    # Create figure
    fig, ax = plt.subplots(figsize=(9, 6))
    
    # Prepare groups and labeles
    groups = []
    labels = []
    
    for sample in sample_order:
        values = data_plot.loc[
        data_plot["Sample_name"] == sample,
        var
    ]
        groups.append(values)
        labels.append(sample)
    
   # Draw boxplot
    bp = plt.boxplot(
        groups,
        patch_artist=True,
        showfliers=False,
        widths=0.6,
        medianprops={
            "color": "black",
            "linewidth": 1.5,
        },
        whiskerprops={
            "color": "black",
            "linewidth": 1.2,
        },
        capprops={
            "color": "black",
            "linewidth": 1.2,
        },
    )

    for box in bp["boxes"]:
        box.set(
            facecolor="#4C72B0",
            alpha=0.6,
            edgecolor="black",
            linewidth=1.2,
        )

    # -------------------------------------------------------
    # Add jittered individual values
    # -------------------------------------------------------
    rng = np.random.default_rng(seed=42)

    for position, values in enumerate(groups, start=1):
        x_jitter = rng.normal(
            loc=position,
            scale=0.05,
            size=len(values),
        )

        ax.scatter(
            x_jitter,
            values,
            s=20,
            color="black",
            alpha=0.7,
            zorder=3,
        )

    # -------------------------------------------------------
    # Add significance brackets
    # -------------------------------------------------------
    sample_positions = {
        sample: position
        for position, sample in enumerate(sample_order, start=1)
    }

    data_min = data_plot[var].min()
    data_max = data_plot[var].max()
    data_range = data_max - data_min

    if data_range == 0:
        data_range = 1

    bracket_height = data_range * 0.025
    bracket_step = data_range * 0.10
    current_y = data_max + data_range * 0.08

    # Sort comparisons by distance between groups.
    # Shorter brackets are drawn first.
    stats_plot["span"] = stats_plot.apply(
        lambda row: abs(
            sample_positions[row["Group_2"]]
            - sample_positions[row["Group_1"]]
        ),
        axis=1,
    )

    stats_plot = stats_plot.sort_values("span")


    for _, row in stats_plot.iterrows():
        group1 = row["Group_1"]
        group2 = row["Group_2"]
        p_value = row["p-value"]

        x1 = sample_positions[group1]
        x2 = sample_positions[group2]

        add_bracket(
            ax=ax,
            x1=x1,
            x2=x2,
            y=current_y,
            height=bracket_height,
            text=p_to_stars(p_value),
        )

        current_y += bracket_step

    # -------------------------------------------------------
    # Format axes
    # -------------------------------------------------------
    ax.set_ylabel(y_axis, fontsize=12)
    ax.set_xlabel("")

    ax.set_xticks(range(1, len(sample_order) + 1))
    ax.set_xticklabels(sample_order)

    plt.grid(axis="y", linestyle="--", alpha=0.4)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    bottom_limit = data_min - data_range * 0.05
    top_limit = current_y + bracket_step * 0.3
    ax.set_ylim(
        bottom=bottom_limit,
        top=top_limit,
    )

    plt.tight_layout()

    # -------------------------------------------------------
    # Save figure
    # -------------------------------------------------------
    output_file = f"{save_dir}/{save_name}.{ext}"

    fig.savefig(
        output_file,
        dpi=600,
        bbox_inches="tight",
    )

    print(f"Plot saved to: {output_file}")

    plt.show()