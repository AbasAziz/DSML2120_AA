import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Your Name"
PROGRAM = "Your Program / Major / Role"
INTRO = (
    "Write 2–3 sentences about yourself: what you’re studying/working on, "
    "what excites you about data visualization or computing, etc."
)
FUN_FACTS = [
    "I love …",
    "I’m learning …",
    "I want to build …",
]
PHOTO_PATH = "your_photo.jpg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
