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

def build_visual_ranking_html(sorted_stops):
    """
    Creates an HTML visualization of the ranked shuttle stops.
    """
    if len(sorted_stops) == 0:
        return "<p style='color: #e5e7eb;'>No shuttle stops to display.</p>"

    max_crowd = max(stop["crowd_count"] for stop in sorted_stops)
    cards = []

    for index, stop in enumerate(sorted_stops, start=1):
        crowd = stop["crowd_count"]
        width_percent = 0 if max_crowd == 0 else int((crowd / max_crowd) * 100)

        if index == 1:
            badge = "🚍 Dispatch here first"
            border_color = "#2563eb"
            bg_color = "#eff6ff"
            shadow_color = "rgba(37, 99, 235, 0.18)"
        else:
            badge = f"Rank #{index}"
            border_color = "#c7d2fe"
            bg_color = "#eef2ff"
            shadow_color = "rgba(99, 102, 241, 0.10)"

        card_html = f"""
        <div style="
            border: 2px solid {border_color};
            background: {bg_color};
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px {shadow_color};
            color: #111827;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 700; font-size: 17px; color: #111827;">
                    {index}. {stop["stop_name"]}
                </div>
                <div style="
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 10px;
                    border-radius: 999px;
                    background: #e0e7ff;
                    color: #3730a3;
                ">
                    {badge}
                </div>
            </div>

            <div style="margin-bottom: 8px; font-size: 14px; color: #374151;">
                Crowd Count: <b style="color: #111827;">{crowd}</b>
            </div>

            <div style="
                width: 100%;
                height: 14px;
                background: #dbeafe;
                border-radius: 999px;
                overflow: hidden;
            ">
                <div style="
                    width: {width_percent}%;
                    height: 14px;
                    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                    border-radius: 999px;
                    transition: width 0.4s ease;
                "></div>
            </div>
        </div>
        """

        cards.append(card_html)

    return """
    <div style="margin-top: 8px;">
        <h3 style="margin-bottom: 12px; color: #f9fafb;">Visual Ranking</h3>
        {}
    </div>
    """.format("".join(cards))


def process_shuttle_data(raw_text):
    """
    Main function for the project logic.
    Returns:
    - original formatted list
    - final ranked list
    - step-by-step sorting log
    - visual ranking HTML
    """
    stops = parse_shuttle_stops(raw_text)
    steps = []

    sorted_stops = merge_sort_stops(stops, steps)

    original_output = build_original_output(stops)
    ranked_output = build_ranked_output(sorted_stops)
    steps_output = "\n".join(steps)
    visual_output = build_visual_ranking_html(sorted_stops)

    return original_output, ranked_output, steps_output, visual_output


def run_app(raw_text):
    """
    Wrapper function for the Gradio interface.
    It catches validation errors and returns user-friendly output.
    """
    try:
        original_output, ranked_output, steps_output, visual_output = process_shuttle_data(raw_text)
        return original_output, ranked_output, steps_output, visual_output
    except ValueError as error:
        return f"Error: {error}", "", "", ""


load_sound_js = """
function attachSortSound() {
    const btn = document.querySelector("#sort-btn button") || document.querySelector("#sort-btn");
    if (!btn || btn.dataset.soundBound === "1") return;

    btn.dataset.soundBound = "1";

    btn.addEventListener("click", () => {
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextClass) return;

            const ctx = new AudioContextClass();

            const playTone = () => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.type = "triangle";
                osc.frequency.setValueAtTime(880, ctx.currentTime);

                gain.gain.setValueAtTime(0.0001, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.01);
                gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.12);

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.start();
                osc.stop(ctx.currentTime + 0.12);
            };

            if (ctx.state === "suspended") {
                ctx.resume().then(playTone);
            } else {
                playTone();
            }
        } catch (e) {
            console.log("Sound unavailable:", e);
        }
    });
}

attachSortSound();
setTimeout(attachSortSound, 400);
setTimeout(attachSortSound, 1200);
"""


if __name__ == "__main__":
    sample_input = """ARC, 52
Douglas Library, 18
Victoria Hall, 39
Stauffer Library, 27"""

    custom_css = """
    .gradio-container {
        max-width: 1100px !important;
    }

    .hero {
        padding: 22px;
        border-radius: 18px;
        margin-bottom: 14px;
        background: linear-gradient(135deg, #1d4ed8 0%, #7c3aed 100%);
        color: white;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }

    .hero h1 {
        margin: 0 0 8px 0;
        font-size: 2rem;
    }

    .hero p {
        margin: 0;
        font-size: 1rem;
        opacity: 0.95;
    }

    .info-card {
        padding: 16px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .result-box textarea {
        border-radius: 14px !important;
        animation: fadeUp 0.35s ease;
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    """

    with gr.Blocks() as demo:
        gr.HTML(
            """
            <div class="hero">
                <h1> Antony's Shuttle Stop Crowd Ranking with Merge Sort</h1>
                <p>
                    Enter shuttle stops, sort them from highest crowd count to lowest,
                    and view the Merge Sort process in a more visual way.
                </p>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                input_box = gr.Textbox(
                    lines=10,
                    label="Shuttle Stop Input",
                    placeholder="One stop per line: stop_name, crowd_count",
                    value=sample_input
                )

                with gr.Row():
                    sort_button = gr.Button(
                        "Sort Shuttle Stops",
                        variant="primary",
                        size="lg",
                        elem_id="sort-btn"
                    )
                    clear_button = gr.Button("Clear", variant="secondary", size="lg")

            with gr.Column(scale=2):
                gr.HTML(
                    """
                    <div class="info-card">
                        <h3>How to Use</h3>
                        <ul>
                            <li>Enter one shuttle stop per line.</li>
                            <li>Use the format <b>stop_name, crowd_count</b>.</li>
                            <li>Click <b>Sort Shuttle Stops</b>.</li>
                            <li>Read the ranking, crowd bars, and step log.</li>
                        </ul>
                    </div>
                    """
                )

        with gr.Row():
            original_output_box = gr.Textbox(
                label="Original Shuttle Stop List",
                lines=8,
                elem_classes="result-box"
            )

            ranked_output_box = gr.Textbox(
                label="Final Ranked List",
                lines=8,
                elem_classes="result-box"
            )

        visual_output_box = gr.HTML()

        with gr.Accordion("Show Merge Sort Steps", open=False):
            steps_output_box = gr.Textbox(
                label="Merge Sort Steps",
                lines=18,
                elem_classes="result-box"
            )


        sort_button.click(
            fn=run_app,
            inputs=input_box,
            outputs=[original_output_box, ranked_output_box, steps_output_box, visual_output_box]
        )

        clear_button.click(
            fn=lambda: ("", "", "", "", ""),
            inputs=[],
            outputs=[input_box, original_output_box, ranked_output_box, steps_output_box, visual_output_box]
        )


    demo.launch(
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="violet"),
        css=custom_css,
        js=load_sound_js
    )