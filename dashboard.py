from pathlib import Path
from typing import Optional, Union

import streamlit as st

from data_models import Evaluation
from json_utils import deserialize_data_model


def inject_global_styles():
    """Inject global CSS to enhance visuals without changing displayed data."""
    st.markdown(
        """
        <style>
        :root {
            --bg-0: #0b1120;
            --bg-1: #0f172a;
            --surface: rgba(148, 163, 184, 0.06);
            --border: rgba(148, 163, 184, 0.18);
            --text: #e5e7eb;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --accent-2: #22d3ee;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --radius: 12px;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji" !important;
        }

        /* App background and header */
        .stApp {
            background: radial-gradient(1200px 600px at 50% -100px, rgba(56,189,248,0.08), transparent),
                        linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
            color: var(--text);
        }
        [data-testid="stHeader"] {
            background-color: rgba(2, 6, 23, 0.5);
            backdrop-filter: saturate(120%) blur(8px);
            border-bottom: 1px solid var(--border);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(2,6,23,0.7) 0%, rgba(2,8,23,0.5) 100%);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: var(--text); }

        /* Typography & spacing */
        h1, h2, h3, h4, h5, h6 { color: var(--text); letter-spacing: .2px; }
        .stMarkdown, .stMarkdown p { color: #cbd5e1; }
        .stCaption { color: var(--muted) !important; }
        .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

        /* Badges */
        .af-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            font-weight: 600;
        }
        .af-badge small { color: #93c5fd; font-weight: 500; }

        /* Metrics */
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 12px 14px;
        }
        [data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #93c5fd !important; font-weight: 600; }

        /* Progress bar */
        [data-testid="stProgress"] > div > div {
            height: 12px;
            border-radius: 999px;
            background-image: linear-gradient(90deg, var(--accent), #3b82f6);
        }

        /* Code blocks */
        pre, code {
            background: rgba(2, 6, 23, 0.6) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
        }

        /* Alerts */
        .stAlert { border-radius: var(--radius); border: 1px solid var(--border); }

        /* Tabs */
        .stTabs [role="tablist"] { gap: 8px; }
        .stTabs [role="tab"] { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; color: #cbd5e1; }
        .stTabs [aria-selected="true"] { border-color: var(--accent); color: var(--text); }

        /* Inputs */
        .stSelectbox, .stTextInput, [data-baseweb="input"], [data-baseweb="select"] { background: var(--surface); border-radius: 10px; }
        .stTextInput input, [data-baseweb="input"] input { color: var(--text); }
        [data-baseweb="select"] div { color: var(--text); white-space: normal !important; }

        /* Dividers */
        hr { border: none; height: 1px; background: linear-gradient(90deg, rgba(148,163,184,0), rgba(148,163,184,0.4), rgba(148,163,184,0)); }

        /* Expanders */
        [data-testid="stExpander"] { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: rgba(148,163,184,0.05); }
        [data-testid="stExpander"] [data-testid="stExpanderToggle"] svg { color: #93c5fd; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.25); border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.35); }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
            border: 1px solid var(--border);
            color: #ecfeff;
            border-radius: 10px;
            padding: 0.4rem 0.9rem;
        }
        .stButton > button:hover { filter: brightness(1.05); }

        /* Make select dropdown wider so long filenames are visible */
        [data-baseweb="menu"] { max-width: 90vw; width: 480px; }
        /* Preserve spaces and use monospace in select options so we can align status to the right */
        [data-baseweb="menu"] [role="option"] {
            white-space: pre;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_detail_styles():
    st.markdown(
        """
        <style>
        .af-status {
            display: inline-flex;
            align-items: center;
            padding: 16px 28px;
            border-radius: 999px;
            font-weight: 800;
            letter-spacing: .35px;
            border: 1px solid var(--border);
            background: var(--surface);
            font-size: 20px;
        }
        .af-status.af-pass {
            color: #10b981;
            background: linear-gradient(180deg, rgba(16,185,129,.12), rgba(16,185,129,.06));
            border-color: rgba(16,185,129,.35);
        }
        .af-status.af-fail {
            color: #ef4444;
            background: linear-gradient(180deg, rgba(239,68,68,.12), rgba(239,68,68,.06));
            border-color: rgba(239,68,68,.35);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_entity_info(entity_data: dict, title: str, icon: str = ""):
    """Display entity information in minimal text format, styled as a badge."""
    icon_part = f"{icon} " if icon else ""
    st.markdown(
        f"<span class='af-badge'>{icon_part}<strong>{title}:</strong> {entity_data['name']} <small>v{entity_data['version']}</small></span>",
        unsafe_allow_html=True,
    )
    st.write(f"_{entity_data['description']}_")


def render_overview_section(data: dict):
    # Push the overview down from the very top of the page
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.header("Evaluation Overview")
    st.caption("High-level details of the evaluation run")

    st.divider()

    # vertical space between heading and information
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    display_entity_info(data, "Evaluation", "🔬")

    # Language and Library
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["language"], "Language", "🔤")
    with col2:
        display_entity_info(data["library"], "Library", "📚")

    # Model and Agent
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["model"], "Model", "🤖")
    with col2:
        display_entity_info(data["agent"], "Agent", "🕵️")

    # Taskset and Testset with task counts
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["taskset"], "Taskset", "🧩")

    with col2:
        display_entity_info(data["testset"], "Testset", "🧪")


def render_metrics_section(data: dict):
    """Render the performance metrics section"""
    # Push the performance section down from the very top of the page
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.header("Metrics")
    st.caption("At-a-glance performance")

    st.divider()

    # vertical space between heading and information
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Core size metrics
    st.subheader("Dataset sizes")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Taskset size",
            data["taskset"]["size"],
        )
    with col2:
        st.metric(
            "Testset size",
            data["testset"]["size"],
        )
    with col3:
        st.metric(
            "Answerset size",
            data["answerset"]["size"],
        )
    with col4:
        st.metric(
            "Resultset size",
            data["resultset"]["size"],
        )

    st.divider()

    # Benchmark performance
    st.subheader("Evaluation performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total tests", data["benchmark"]["total_size"])
    with col2:
        st.metric("Total passed", data["benchmark"]["number_passed"])
    with col3:
        st.metric(
            "Overall pass rate",
            f"{data['benchmark']['percentage_passed']:.1f}%",
        )


def render_detailed_view_section(data: dict):
    """Render the detailed view section"""

    inject_detail_styles()

    # vertical space between heading and information
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.header("Detailed view")
    st.caption("Inspect tasks, answers, tests, and results")

    st.divider()

    results = data["resultset"]["results"]
    left_parts = [
        f"Task {i + 1}: {r['answer']['task']['name']}" for i, r in enumerate(results)
    ]
    max_left_len = max((len(s) for s in left_parts), default=0)

    def status_text(passed: bool) -> str:
        return "🟢 PASSED" if passed else "🔴 FAILED"

    task_names = [
        f"{left.ljust(max_left_len + 2)}{status_text(r['passed'])}"
        for left, r in zip(left_parts, results)
    ]

    selected_task_idx = st.selectbox(
        "Select a task to explore in detail:",
        range(len(task_names)),
        format_func=lambda x: task_names[x],
    )

    st.write("")
    st.write("")

    if selected_task_idx is not None:
        result = results[selected_task_idx]

        # Task header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{result['answer']['task']['name']}")
        with col2:
            status_html = (
                "<span class='af-status af-pass'>PASSED</span>"
                if result["passed"]
                else "<span class='af-status af-fail'>FAILED</span>"
            )
            st.markdown(status_html, unsafe_allow_html=True)

        # Task details tabs
        st.markdown(
            """
        <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 18px;
            font-weight: 600;
            padding: 8px 16px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            height: 50px;
            padding: 0 24px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        tab1, tab2, tab3 = st.tabs(["Task", "Answer", "Test"])

        with tab1:
            # Restore original task textarea styling (black bg, white text)
            st.markdown(
                """
            <style>
            .stTextArea textarea {
                background-color: black !important;
                color: white !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "Task content:",
                result["answer"]["task"]["content"],
                height=150,
                disabled=True,
            )

            # Plain metadata (no styled cards)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Task name:** {result['answer']['task']['name']}")
                st.write(f"**Description:** {result['answer']['task']['description']}")
                st.write(f"**Library:** {result['answer']['task']['library']['name']}")
            with col2:
                st.write(f"**Version:** {result['answer']['task']['version']}")
                st.write(f"**Task number:** {selected_task_idx + 1}")

        with tab2:
            st.code(result["answer"]["content"])

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Agent:** {result['answer']['agent']['name']}")
                st.write(f"**Model:** {result['answer']['agent']['model']['name']}")
                st.write(f"**Prompt:** {result['answer']['agent']['prompt']}")
                st.write(f"**Scaffolding:** {result['answer']['agent']['scaffolding']}")
            with col2:
                st.write(f"**Version:** {result['answer']['agent']['version']}")
                st.write(
                    f"**Provider:** {result['answer']['agent']['model']['provider']}"
                )
                st.write(
                    f"**Configuration:** {result['answer']['agent']['configuration']}"
                )

        with tab3:
            st.code(result["test"]["content"])

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Test name:** {result['test']['name']}")
                st.write(f"**Test version:** {result['test']['version']}")
            with col2:
                st.write(f"**Test description:** {result['test']['description']}")


@st.cache_data
def load_evaluation_from_file(file_path: str) -> Optional[dict]:
    """Load evaluation data from JSON file"""
    try:
        evaluation = deserialize_data_model(file_path, Evaluation)
        return evaluation.model_dump()
    except Exception as e:
        st.error(f"Error loading evaluation: {e}")
        return None


def show_dashboard(evaluation_data: Optional[Union[dict, Evaluation]] = None):
    """
    Main dashboard function that can be called from evaluation.py

    Args:
        evaluation_data: Either an Evaluation object or dict, or None to load from file
    """
    st.set_page_config(
        page_title="Evaluation Dashboard",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Global styles
    inject_global_styles()

    # Removed main title per request

    # Handle different input types
    if evaluation_data is None:
        # File selection mode
        st.sidebar.header("File Selection")
        eval_files = list(Path(".").glob("Evaluation_*.json"))

        if not eval_files:
            st.error(
                "No evaluation files found! Make sure your JSON files are in the current directory."
            )
            return

        # Radio buttons are better for quick scanning of a short list
        selected_file = st.sidebar.radio(
            "",
            eval_files,
            format_func=lambda p: p.name,
            label_visibility="collapsed",
        )

        if selected_file:
            data = load_evaluation_from_file(str(selected_file))
            if not data:
                return
        else:
            return

    elif isinstance(evaluation_data, Evaluation):
        # Pydantic model input
        data = evaluation_data.model_dump()

    elif isinstance(evaluation_data, dict):
        # Dictionary input
        data = evaluation_data

    else:
        st.error(
            "Invalid evaluation data type. Expected Evaluation object, dict, or None."
        )
        return

    # Sidebar navigation
    # Navigation: use a menu that highlights the active page
    st.sidebar.header("Navigation")
    sections = [
        "Overview",
        "Metrics",
        "Detailed view",
    ]
    # Use radio for clear highlighting of the current page
    selected_section = st.sidebar.radio("", sections, label_visibility="collapsed")

    # Render selected section
    if selected_section == "Overview":
        render_overview_section(data)
    elif selected_section == "Metrics":
        render_metrics_section(data)
    elif selected_section == "Detailed view":
        render_detailed_view_section(data)


def main():
    """Main function for standalone usage"""
    show_dashboard()


if __name__ == "__main__":
    main()
