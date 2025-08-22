import streamlit as st
import google.generativeai as genai

# ------------------------------
# CONFIGURE GEMINI API
# ------------------------------
GEMINI_API_KEY = "AIzaSyD06uV8lvIOj7deXP_z3WZ9ddZfc-1sd8k"  # Replace with your key
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------------
# STREAMLIT PAGE CONFIG (Dark Mode)
# ------------------------------
st.set_page_config(page_title="✨ AI Story Forge", layout="wide", initial_sidebar_state="expanded")

# Inject CSS for dark theme
st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: white;
    }
    textarea, input {
        background-color: #1E1E1E !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# INITIALIZE SESSION STATE
# ------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------
# SIDEBAR SETTINGS
# ------------------------------
st.sidebar.header("⚙️ Settings")
prompt_type = st.sidebar.selectbox(
    "Prompting Type",
    ["Zero-shot", "Few-shot", "Chain-of-Thought", "Role Prompting", "Tree-of-Thought"]
)
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.8, 0.1)
max_tokens = st.sidebar.slider("Max Tokens", 50, 500, 150, 10)

if st.sidebar.button("🗑 Clear All History"):
    st.session_state.history.clear()

# ------------------------------
# MAIN UI
# ------------------------------
st.markdown("<h1 style='color: #FFD700;'>✨ AI Story Forge</h1>", unsafe_allow_html=True)

example_stories = [
    "It was a dark and stormy night. Alex heard a faint knock at the door...",
    "The last train had left the station, but one passenger still waited on the platform.",
    "Deep in the ancient library, a candle flickered near an open book bound in red leather.",
    "Maya woke up to find a strange glowing envelope on her bedside table.",
    "The robot paused, looking at the sunset as if it understood beauty for the first time."
]

story_choice = st.selectbox("Choose an example story beginning:", ["✍️ Write my own"] + example_stories)

if story_choice == "✍️ Write my own":
    story_input = st.text_area("Enter your story beginning:", st.session_state.get("last_input", ""))
else:
    story_input = story_choice

# ------------------------------
# GENERATE STORY
# ------------------------------
if st.button("✨ Generate Completion"):
    st.session_state.last_input = story_input

    # Token limit instruction so story is complete
    token_instruction = f"Write a complete and meaningful story in under {max_tokens} tokens."

    # PROMPT FORMULATION
    if prompt_type == "Zero-shot":
        prompt = f"""{token_instruction} Ensure it has a proper ending and flows naturally.\nStory: {story_input}"""

    elif prompt_type == "Few-shot":
        prompt = f"""{token_instruction}\n
Example 1: Story: The forest was silent until the leaves began to rustle. Completion: A hidden fox emerged from the bushes, its amber eyes reflecting the moonlight.

Example 2: Story: Sarah opened the old, dusty book and a slip of paper fell out. Completion: It was a love letter dated over a century ago, addressed to someone with her own name.

Now complete this: Story: {story_input}"""

    elif prompt_type == "Chain-of-Thought":
        prompt = f"""{token_instruction}\n
Story: {story_input}\nReasoning: 
1. Identify possible directions for the story. 
2. Choose one that gives a satisfying twist. 
3. Build suspense with gradual clues. 
4. Conclude with a strong emotional or surprising impact. 

Final Story:"""

    elif prompt_type == "Role Prompting":
        prompt = f"""{token_instruction}\n
You are a **master storyteller** with expertise in suspense and emotional writing. Write the continuation of the following story in your own narrative style, making it engaging and immersive.\n
Story: {story_input}\n
Final Story:"""

    elif prompt_type == "Tree-of-Thought":
        prompt = f"""{token_instruction}\n
Story: {story_input}\n
Think step by step like a decision tree:\n1. Generate at least 3 different possible continuations.\n2. Briefly evaluate each continuation (pros/cons for suspense, emotional impact, creativity).\n3. Select the best continuation.\n4. Expand it into a complete story with a proper ending.\n
Final Story:"""

    # ------------------------------
    # CALL GEMINI API
    # ------------------------------
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
    )

    generated_story = response.text
    st.session_state.history.append({"prompt_type": prompt_type, "input": story_input, "output": generated_story})

    st.subheader("Generated Story Completion")
    st.write(generated_story)

# ------------------------------
# DISPLAY HISTORY
# ------------------------------
if st.session_state.history:
    st.markdown("## 📜 Story History")
    for idx, entry in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{idx}. {entry['prompt_type']} - {entry['input'][:50]}..."):
            st.write("**Story Beginning:**", entry['input'])
            st.write("**Completion:**", entry['output'])
            if st.button(f"❌ Delete This Entry", key=f"del_{idx}"):
                st.session_state.history.remove(entry)
                st.experimental_rerun()
