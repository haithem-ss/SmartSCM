import json
import os
from langchain.tools import BaseTool
from paths import BASE_DIR
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
import io
import base64
from typing import List
import uuid
import matplotlib

matplotlib.use('Agg')

class DataVizInput(BaseModel):
    type: str = Field(..., description="Type of plot: 'line', 'bar', or 'scatter'")
    x: str = Field(..., description="Label for the x-axis")
    y: str = Field(..., description="Label for the y-axis")
    x_data: List = Field(..., description="List of data for x-axis")
    y_data: List = Field(..., description="List of data for y-axis")


class OneInputSchema(BaseModel):
    input: DataVizInput


def data_vizualization(type: str, x: str, y: str, x_data, y_data, labels=None) -> str:
    plt.style.use("seaborn-v0_8-colorblind")  # Nice color palette
    plt.figure(figsize=(12, 7))  # Bigger image

    is_multi = isinstance(y_data[0], (list, tuple))

    if type == "line":
        if is_multi:
            for idx, series in enumerate(y_data):
                label = labels[idx] if labels else f"Series {idx+1}"
                plt.plot(x_data, series, label=label, marker="o", linewidth=2)
        else:
            plt.plot(
                x_data,
                y_data,
                label=labels[0] if labels else y,
                marker="o",
                linewidth=2,
            )

    elif type == "bar":
        if is_multi:
            import numpy as np

            width = 0.8 / len(y_data)
            x_indexes = np.arange(len(x_data))
            for idx, series in enumerate(y_data):
                offset = (idx - len(y_data) / 2) * width + width / 2
                label = labels[idx] if labels else f"Series {idx+1}"
                plt.bar(x_indexes + offset, series, width=width, label=label)
            plt.xticks(x_indexes, x_data, fontsize=11)
        else:
            plt.bar(x_data, y_data, label=labels[0] if labels else y)

    elif type == "scatter":
        if is_multi:
            for idx, series in enumerate(y_data):
                label = labels[idx] if labels else f"Series {idx+1}"
                plt.scatter(x_data, series, label=label, s=80, edgecolors="k")
        else:
            plt.scatter(
                x_data, y_data, label=labels[0] if labels else y, s=80, edgecolors="k"
            )

    elif type == "pie":
        if is_multi:
            return "Pie chart does not support multiple data series."
        def make_autopct(values):
                    def my_autopct(pct):
                        total = sum(values)
                        val = int(round(pct * total / 100.0))
                        return f"{pct:.1f}%\n({val})"

                    return my_autopct

        explode = [0.05] * len(y_data)
        colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f"]
        plt.pie(
                y_data,
                labels=x_data,
                autopct=make_autopct(y_data),
                explode=explode,
                startangle=140,
                colors=colors[: len(y_data)],
                textprops={"fontsize": 12},
            )

    else:
        return f"Unsupported plot type: {type}"

    if type != "pie":
        plt.xlabel(x, fontsize=13)
        plt.ylabel(y, fontsize=13)
        plt.title(
            f"{type.capitalize()} Plot of {y} vs {x}", fontsize=16, fontweight="bold"
        )
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
        plt.legend(fontsize=11)
        plt.xticks(fontsize=11)
        plt.yticks(fontsize=11)

    plt.tight_layout()  # Avoid clipping

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return f"data:image/png;base64,{img_base64}"


class DataVisualizationTool(BaseTool):
    name: str = "data_vizualization"
    description: str = (
        "Generates a data visualization plot from structured JSON input using matplotlib. "
        "Supports four types of plots: 'line', 'bar', 'scatter', and 'pie'. This tool is ideal for use cases "
        "where a visual summary of numerical data is needed, such as dashboards, reports, or exploratory data analysis.\n\n"
        "Details by plot type:\n"
        "- 'line': Plots one or more y-series against a shared x-series using lines and markers.\n"
        "- 'bar': Plots single or grouped bar charts. Grouped bars are handled if multiple y-series are given.\n"
        "- 'scatter': Plots single or multiple y-series as scatter points.\n"
        "- 'pie': Plots a pie chart using x_data as labels and y_data as values. Only supports a single series.\n\n"
        "Styling:\n"
        "- Uses the 'seaborn-colorblind' palette for accessibility.\n"
        "- Applies gridlines, legend, labeled axes, and formatted title for non-pie charts.\n"
        "- Pie charts include percentage and absolute values with color-coded segments.\n\n"
        "Output:\n"
        "- The resulting plot is rendered and saved as a PNG file.\n"
        "- The image is saved to a temporary folder ('../temp') with a unique UUID-based filename.\n"
        "- The full path to the saved image file is returned as the result.\n"
    )

    def _run(self, input) -> str:
        parsed_input_data = input if isinstance(input, dict) else json.loads(input)
        if "input" in parsed_input_data:
            parsed_input_data = parsed_input_data["input"]
        image = data_vizualization(
            parsed_input_data["type"],
            parsed_input_data["x"],
            parsed_input_data["y"],
            parsed_input_data["x_data"],
            parsed_input_data["y_data"],
        )
        _, encoded = image.split(",", 1)

        # Decode the base64 string
        image_data = base64.b64decode(encoded)

        # Write the image to a file
        # Ensure the directory exists
        output_dir = os.path.join(BASE_DIR,"streamlit",".streamlit","static")
        os.makedirs(output_dir, exist_ok=True)

        # Write the image to a file
        output_image = str(uuid.uuid4())  # Generate a random unique name
        output_path = os.path.join(output_dir, f"{output_image}.png")
        with open(output_path, "wb") as f:
            f.write(image_data)

        return f"Image saved to http://localhost:8000/{output_image}.png"
