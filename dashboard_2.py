import streamlit as st

from data_models import Evaluation


def render_overview(evaluation: Evaluation):
    st.write("")

    st.header("Evaluation overview")
    st.caption("High-level details of the evaluation run")

    st.divider()

    st.write("")

    st.write("Evaluation")
    st.write(f"Name: {evaluation.name}")
    st.write(f"Version: {evaluation.version}")
    st.write(f"Description: {evaluation.description}")
