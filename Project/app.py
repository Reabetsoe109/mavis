"""
Streamlit app to visualize sorting algorithms implemented in `algorithms.py`.

Usage:
    pip install -r requirements.txt
    streamlit run app.py

Controls:
 - Choose algorithm
 - Adjust array size and speed
 - Randomize array
 - Start / Stop / Step
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    random_array,
)

ALGORITHMS = {
    'Bubble Sort': bubble_sort,
    'Selection Sort': selection_sort,
    'Insertion Sort': insertion_sort,
    'Merge Sort': merge_sort,
    'Quick Sort': quick_sort,
}

st.set_page_config(page_title='Sorting Visualizer', layout='wide')

st.title('Sorting Algorithm Visualizer (Python + Streamlit)')

# Sidebar controls
with st.sidebar.form('controls'):
    algo_name = st.selectbox('Algorithm', list(ALGORITHMS.keys()))
    size = st.slider('Array size', min_value=5, max_value=200, value=40, step=1)
    speed = st.slider('Speed (steps per second)', min_value=1, max_value=60, value=10)
    seed = st.number_input('Random seed (0 = random)', value=0, step=1)
    randomize = st.form_submit_button('Randomize array')
    start = st.form_submit_button('Start')
    stop = st.form_submit_button('Stop')
    step_btn = st.form_submit_button('Step')

# Session state for persistent controls between reruns
if 'array' not in st.session_state:
    if seed != 0:
        np.random.seed(seed)
    st.session_state.array = random_array(size, 1, 100)
    st.session_state.generator = None
    st.session_state.running = False
    st.session_state.last_snapshot = (st.session_state.array.copy(), {'active': [], 'sorted': []})

# Handle Randomize
if randomize:
    if seed != 0:
        np.random.seed(seed)
    st.session_state.array = random_array(size, 1, 100)
    st.session_state.generator = None
    st.session_state.running = False
    st.session_state.last_snapshot = (st.session_state.array.copy(), {'active': [], 'sorted': []})

# Update size change: regenerate array if size changed
if len(st.session_state.array) != size:
    st.session_state.array = random_array(size, 1, 100)
    st.session_state.generator = None
    st.session_state.running = False
    st.session_state.last_snapshot = (st.session_state.array.copy(), {'active': [], 'sorted': []})

# Start/Stop/Step logic
if start:
    st.session_state.generator = ALGORITHMS[algo_name](st.session_state.array.copy())
    st.session_state.running = True

if stop:
    st.session_state.running = False
    st.session_state.generator = None

if step_btn:
    # create generator if not present
    if st.session_state.generator is None:
        st.session_state.generator = ALGORITHMS[algo_name](st.session_state.array.copy())
    try:
        snapshot = next(st.session_state.generator)
        st.session_state.last_snapshot = snapshot
    except StopIteration:
        st.session_state.generator = None
        st.session_state.running = False

# Placeholder for the chart
chart_placeholder = st.empty()

# Function to draw a snapshot

def draw_snapshot(snapshot):
    arr, info = snapshot
    arr = list(arr)
    active = info.get('active', []) or []
    sorted_idx = info.get('sorted', []) or []
    label = info.get('label', '')

    fig, ax = plt.subplots(figsize=(12, 4))
    bars = ax.bar(range(len(arr)), arr, color='skyblue')

    for idx in active:
        if 0 <= idx < len(bars):
            bars[idx].set_color('red')
    for idx in sorted_idx:
        if 0 <= idx < len(bars):
            bars[idx].set_color('green')

    ax.set_title(f"{algo_name} — {label}")
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_ylim(0, max(1, max(arr) * 1.1))
    plt.tight_layout()
    chart_placeholder.pyplot(fig)
    plt.close(fig)

# If running, iterate through generator and animate
if st.session_state.running and st.session_state.generator is not None:
    try:
        # Iterate until generator exhausted or Stop requested
        delay = 1.0 / max(1, speed)
        while True:
            snapshot = next(st.session_state.generator)
            st.session_state.last_snapshot = snapshot
            draw_snapshot(snapshot)
            time.sleep(delay)
            # if stop was pressed by user, Streamlit will rerun and stop due to session_state.running being False
            if not st.session_state.running:
                break
    except StopIteration:
        st.session_state.running = False
        st.session_state.generator = None

# Always show the last snapshot (either initial or most recent)
if st.session_state.last_snapshot is not None:
    draw_snapshot(st.session_state.last_snapshot)

st.markdown('---')
st.markdown('Tips: Use smaller array sizes for slower machines. Try each algorithm to compare the number of swaps/comparisons and behavior.')
