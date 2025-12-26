"""Simple math-based CAPTCHA for form protection."""

import random

import streamlit as st


def check_captcha() -> bool:
    """
    Check if CAPTCHA has been passed. If not, display CAPTCHA and stop execution.

    Returns:
        bool: True if CAPTCHA passed, False otherwise (but st.stop() is called).
    """
    if "captcha_passed" not in st.session_state:
        st.session_state.captcha_passed = False

    if st.session_state.captcha_passed:
        return True

    if "captcha_answer" not in st.session_state:
        a, b = random.randint(1, 9), random.randint(1, 9)
        st.session_state.captcha_question = f"{a} + {b}"
        st.session_state.captcha_answer = str(a + b)

    st.markdown("### Please solve this to begin:")
    st.write(f"**{st.session_state.captcha_question} = ?**")
    captcha_input = st.text_input("Answer:")

    if st.button("Verify CAPTCHA", key="captcha_button"):
        if captcha_input.strip() == st.session_state.captcha_answer:
            st.success("CAPTCHA passed!")
            st.session_state.captcha_passed = True
            del st.session_state["captcha_answer"]
            del st.session_state["captcha_question"]
            st.rerun()
        else:
            st.error("Incorrect answer. Please try again.")

    st.stop()
    return False
