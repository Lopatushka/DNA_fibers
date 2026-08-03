import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Function for significance bars
# ---------------------------------------------------------
def p_to_stars(p):
    """
    Convert a p-value to a significance label.

    Parameters
    ----------
    p : float
        P-value.

    Returns
    -------
    str
        One of: "ns", "*", "**", "***", "****".
    """
    if p < 0.0001:
        return "****"
    elif p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "n.s."
    
def add_significance_bar(
    ax,
    x1,
    x2,
    y,
    text,
    bar_height=2,
    text_offset=1,
    linewidth=1.3,
    fontsize=13
):
    ax.plot(
        [x1, x1, x2, x2],
        [y, y + bar_height, y + bar_height, y],
        color="black",
        linewidth=linewidth,
        clip_on=False
    )

    ax.text(
        (x1 + x2) / 2,
        y + bar_height + text_offset,
        text,
        ha="center",
        va="bottom",
        fontsize=fontsize
    )


def boxplot_with_statistics(data,
                            var, # "Sample_name", "IOD_kb"
                            sample_order,
                            sample_labels,
                            sample_colors,
                            sample_markers,
                            figsize = (4.5, 5.5),
                            stats = ["n.s."], # "****", "n.s."
                            y_axis = "",
                            save_dir = ".",
                            save_name = "",
                            ext = "png"):
    
    # ---------------------------------------------------------
    # Process dataframe for plotting
    # ---------------------------------------------------------
    # Keep only the columns needed for plotting
    plot_data = data[['Sample_name', var]].copy()
    
    # Make sure IOD_kb is numeric
    plot_data[var] = pd.to_numeric(
        plot_data[var],
        errors="coerce"
    )
    
    # Remove rows with missing values
    plot_data = plot_data.dropna(
        subset=["Sample_name", var]
    )

    # ---------------------------------------------------------
    # Create plot
    # ---------------------------------------------------------
    x_positions = np.arange(len(sample_order))
    fig, ax = plt.subplots(figsize=figsize)
    rng = np.random.default_rng(4)
    
    # Iteration over samples to plot individual points and median lines
    for x, sample in zip(x_positions, sample_order):
        values = plot_data.loc[
            plot_data["Sample_name"] == sample,
            "IOD_kb"
        ].to_numpy()

        if len(values) == 0:
            print("Warning: no values found for sample:", sample)
            continue

        # Horizontal jitter
        jitter = rng.normal(
            loc=0,
            scale=0.08,
            size=len(values)
        )

        ax.scatter(
            x + jitter,
            values,
            s=20,
            marker=sample_markers.get(sample, "o"),
            color=sample_colors.get(sample, "gray"),
            edgecolors="none",
            alpha=0.9,
            zorder=2
        )

        # Median line
        median_value = np.median(values)

        ax.plot(
            [x - 0.24, x + 0.24],
            [median_value, median_value],
            color="red",
            linewidth=2,
            zorder=3
        )

    # ---------------------------------------------------------
    # Add statistical annotation manually
    # Adjust y according to your data
    # ---------------------------------------------------------
    max_value = plot_data.loc[
            plot_data["Sample_name"].isin(sample_order),
            var
        ].max()

    annotation_y = max_value + 10

    # Add significance bars for each comparison
    for stat in stats:
        add_significance_bar(
            ax,
            x1=stat["group1"],
            x2=stat["group2"],
            y=annotation_y,
            text=p_to_stars(stat["p_value"]),
        )

    # ---------------------------------------------------------
    # Axis formatting
    # ---------------------------------------------------------
    ax.set_xticks(x_positions)

    ax.set_xticklabels(
        [
            sample_labels.get(sample, sample)
            for sample in sample_order
        ],
        fontsize=13
    )

    ax.set_ylabel(
        y_axis,
        fontsize=14
    )

    ax.set_xlim(-0.6, len(sample_order) - 0.4)

    ax.set_ylim(
        0,
        annotation_y + 15
    )

    ax.tick_params(
        axis="y",
        labelsize=12,
        width=1.2,
        length=7,
        direction="out"
    )

    ax.tick_params(
        axis="x",
        width=1.2,
        length=7,
        direction="out",
        pad=7
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)  

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
    
    plt.tight_layout()
    plt.show()