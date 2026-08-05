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
                            figsize = (5, 6),
                            stats = None,
                            y_axis = "",
                            save_dir = ".",
                            save_name = "",
                            ext = "png"):
    
    """
    Plot individual observations, median lines, and significance brackets.

    stats should be a list of dictionaries, for example:

    stats = [
        {"group1": "NC", "group2": "Apt3", "p_value": 0.08},
        {"group1": "NC", "group2": "Apt4", "p_value": 0.00001},
    ]
    """
    
    if stats is None:
        stats = []


    # ---------------------------------------------------------
    # Process dataframe for plotting
    # ---------------------------------------------------------
    required_columns = {"Sample_name", var}
    
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(
            "Missing dataframe columns: {}".format(
                ", ".join(sorted(missing_columns))
            )
        )
        
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
    
    # Convert sample names to numeric x-axis positions
    x_lookup = {
        sample: i
        for i, sample in enumerate(sample_order)
    }
    
    # Check that all statistical groups are valid
    for stat in stats:
        group1 = stat["group1"]
        group2 = stat["group2"]

        if group1 not in x_lookup:
            raise ValueError(
                "Group '{}' is not present in sample_order.".format(group1)
            )

        if group2 not in x_lookup:
            raise ValueError(
                "Group '{}' is not present in sample_order.".format(group2)
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
            var,
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
    selected_values = plot_data.loc[
        plot_data["Sample_name"].isin(sample_order),
        var,
    ]

    if selected_values.empty:
        raise ValueError("No data found for the selected samples.")
    
    data_min = selected_values.min()
    data_max = selected_values.max()
    data_range = data_max - data_min

    if data_range == 0:
        data_range = max(abs(data_max), 1)

    first_annotation_y = data_max + 0.06 * data_range
    annotation_step = 0.15 * data_range
    bar_height = 0.035 * data_range
    text_offset = 0.018 * data_range
    
    
    for i, stat in enumerate(stats):
        group1 = stat["group1"]
        group2 = stat["group2"]
        p_value = stat["p_value"]
        
        
        # Convert sample names to numeric positions
        x1 = x_lookup[group1]
        x2 = x_lookup[group2]
        
        label = p_to_stars(p_value)
        
        # Put each bracket at a different height
        annotation_y = first_annotation_y + i * annotation_step
             
        add_significance_bar(
            ax,
            x1=x1,
            x2=x2,
            y=annotation_y,
            bar_height=bar_height,
            text_offset = text_offset,
            text=label,
            linewidth=1.2,
            fontsize=13
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

    if stats:
        upper_limit = (
                first_annotation_y
                + len(stats) * annotation_step
                + bar_height
                + text_offset
           )
    else:
        upper_limit = data_max + 0.1 * data_range

    lower_limit = min(0, data_min - 0.05 * data_range)

    ax.set_ylim(
        lower_limit,
        upper_limit,
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
    
    # Apply layout before saving
    fig.tight_layout()  

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
    
    return fig, ax