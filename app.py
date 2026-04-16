import gradio as gr

def parse_shuttle_stops(raw_text):
    """
    Takes the user's raw text input and converts it into
    a list of shuttle stop records.

    Expected input format:
    stop_name, crowd_count
    One stop per line
    """

    if raw_text is None:
        raise ValueError("Please enter shuttle stop data.")

    cleaned_text = raw_text.strip()

    if cleaned_text == "":
        raise ValueError("Please enter at least one shuttle stop.")

    lines = cleaned_text.splitlines()
    stops = []

    for line_number, line in enumerate(lines, start=1):
        current_line = line.strip()

        # Skip completely empty lines
        if current_line == "":
            continue

        parts = current_line.split(",")

        if len(parts) != 2:
            raise ValueError(
                f"Line {line_number}: use the format 'stop_name, crowd_count'."
            )

        stop_name = parts[0].strip()
        crowd_text = parts[1].strip()

        if stop_name == "":
            raise ValueError(f"Line {line_number}: stop name cannot be empty.")

        try:
            crowd_count = int(crowd_text)
        except ValueError:
            raise ValueError(f"Line {line_number}: crowd count must be an integer.")

        if crowd_count < 0:
            raise ValueError(f"Line {line_number}: crowd count cannot be negative.")

        stop_record = {
            "stop_name": stop_name,
            "crowd_count": crowd_count
        }

        stops.append(stop_record)

    if len(stops) == 0:
        raise ValueError("Please enter at least one valid shuttle stop.")

    return stops


def format_stop_list(stop_list):
    """
    Converts a list of stop records into one readable string.
    Used for step-by-step messages.
    """
    if len(stop_list) == 0:
        return "(empty)"

    formatted_items = []

    for stop in stop_list:
        formatted_items.append(
            f"{stop['stop_name']} ({stop['crowd_count']})"
        )

    return ", ".join(formatted_items)


def merge_two_sorted_lists(left_half, right_half, steps):
    """
    Merges two already-sorted lists into one sorted list.
    Sort order: highest crowd count to lowest.
    """
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left_half) and right_index < len(right_half):
        left_stop = left_half[left_index]
        right_stop = right_half[right_index]

        steps.append(
            f"Compare {left_stop['stop_name']} ({left_stop['crowd_count']}) "
            f"with {right_stop['stop_name']} ({right_stop['crowd_count']})"
        )

        # Descending order: bigger crowd count comes first
        # If tied, take from the left half first
        if left_stop["crowd_count"] >= right_stop["crowd_count"]:
            merged.append(left_stop)
            steps.append(f"Take {left_stop['stop_name']} from the left half")
            left_index += 1
        else:
            merged.append(right_stop)
            steps.append(f"Take {right_stop['stop_name']} from the right half")
            right_index += 1

    while left_index < len(left_half):
        remaining_stop = left_half[left_index]
        merged.append(remaining_stop)
        steps.append(f"Append remaining stop from left half: {remaining_stop['stop_name']}")
        left_index += 1

    while right_index < len(right_half):
        remaining_stop = right_half[right_index]
        merged.append(remaining_stop)
        steps.append(f"Append remaining stop from right half: {remaining_stop['stop_name']}")
        right_index += 1

    return merged


def merge_sort_stops(stops, steps):
    """
    Recursively sorts shuttle stops by crowd count using Merge Sort.
    """
    if len(stops) <= 1:
        return stops

    middle = len(stops) // 2
    left_half = stops[:middle]
    right_half = stops[middle:]

    steps.append(f"Split list into: [{format_stop_list(left_half)}] and [{format_stop_list(right_half)}]")

    sorted_left = merge_sort_stops(left_half, steps)
    sorted_right = merge_sort_stops(right_half, steps)

    merged_result = merge_two_sorted_lists(sorted_left, sorted_right, steps)
    steps.append(f"Merged result: {format_stop_list(merged_result)}")

    return merged_result


def build_original_output(stops):
    """
    Creates a readable version of the original user input data.
    """
    lines = []

    for index, stop in enumerate(stops, start=1):
        lines.append(f"{index}. {stop['stop_name']} - crowd count: {stop['crowd_count']}")

    return "\n".join(lines)


def build_ranked_output(sorted_stops):
    """
    Creates a readable ranked list after sorting.
    """
    lines = []

    for index, stop in enumerate(sorted_stops, start=1):
        lines.append(f"{index}. {stop['stop_name']} - crowd count: {stop['crowd_count']}")

    return "\n".join(lines)


def process_shuttle_data(raw_text):
    """
    Main function for the project logic.
    Returns:
    - original formatted list
    - final ranked list
    - step-by-step sorting log
    """
    stops = parse_shuttle_stops(raw_text)
    steps = []

    sorted_stops = merge_sort_stops(stops, steps)

    original_output = build_original_output(stops)
    ranked_output = build_ranked_output(sorted_stops)
    steps_output = "\n".join(steps)

    return original_output, ranked_output, steps_output


def run_app(raw_text):
    """
    Wrapper function for the Gradio interface.
    It catches validation errors and returns user-friendly output.
    """
    try:
        original_output, ranked_output, steps_output = process_shuttle_data(raw_text)

        return original_output, ranked_output, steps_output
    except ValueError as error:
        return f"Error: {error}", "", ""

if __name__ == "__main__":
    sample_input = """ARC, 52
Douglas Library, 18
Victoria Hall, 39
Stauffer Library, 27"""

    with gr.Blocks() as demo:
        gr.Markdown("# Shuttle Stop Crowd Ranking with Merge Sort")
        gr.Markdown(
            """
            Enter shuttle stops one per line using this format:

            `stop_name, crowd_count`

            Example:
            ```
            ARC, 52
            Douglas Library, 18
            Victoria Hall, 39
            Stauffer Library, 27
            ```

            The app sorts the stops from highest crowd count to lowest using Merge Sort
            and shows the major steps of the sorting process.
            """
        )

        input_box = gr.Textbox(
            lines=10,
            label="Shuttle Stop Input",
            placeholder="One stop per line: stop_name, crowd_count",
            value=sample_input
        )

        with gr.Row():
            sort_button = gr.Button("Sort Shuttle Stops")
            clear_button = gr.Button("Clear")

        original_output_box = gr.Textbox(
            label="Original Shuttle Stop List",
            lines=8
        )

        ranked_output_box = gr.Textbox(
            label="Final Ranked List",
            lines=8
        )

        steps_output_box = gr.Textbox(
            label="Merge Sort Steps",
            lines=18
        )

        sort_button.click(
            fn=run_app,
            inputs=input_box,
            outputs=[original_output_box, ranked_output_box, steps_output_box]
        )

        clear_button.click(
            fn=lambda: ("", "", "", ""),
            inputs=[],
            outputs=[input_box, original_output_box, ranked_output_box, steps_output_box]
        )

    demo.launch(inbrowser=True)