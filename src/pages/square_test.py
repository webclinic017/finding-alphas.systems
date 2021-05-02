import streamlit as st
import time

def app():
    st.title("Square test")

    st.write("""
    # First application
    test
    """)
    x = st.slider('x')
    time.sleep(3)
    st.write(x, 'squared is ', x*x)