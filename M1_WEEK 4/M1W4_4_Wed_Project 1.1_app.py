import streamlit as st

st.title("Mint trying to understand the coding world")

import time

st.header("Analyse text")
st.header("Demo functions of streamlit")
st.subheader("Translation result")
st.text("I go to school")
st.markdown("**Streamlit** support *Markdown*")
st.latex(r"p(y|x) = \frac{p(x|y)p(y)}{p(x)}")

label = "Positive"
st.write(label)
st.write("I go to school")

code = '''
def process(text):
    return text.lower()
'''

st.code(code,language="Python")
with st.echo():
    text = "NLP.demo".lower()
    st.write("Result: ", text)

st.logo("logo.jpeg")

st.subheader("All audio, music, picture, video in this website is picked for self learning (trying to understand coding and streamlit) only and are not for commercial distribution!")

st.image("hedgehog.jpeg", 
         caption = "This is me! My nickname is hedgehog")
st.audio("audio.mp3")
st.video("video.mp4")

option = st.selectbox(
    "Select a NLP function",
    ["Summarize", "Translation", "Q&A"]
)
st.write("Please select: ", option)

status = st.checkbox("Show the text")
if status:
    st.write(status)

st.slider("Value range", min_value=1.0, max_value=10.0, step=0.5)
name = st.text_input("Your name is: ")
st.write(name)

age = st.number_input("Your age is: ")
st.write(age)

if st.button("Run"):
    st.write(name, age)

uploaded_file = st.file_uploader("Please upload your file!", type = ['txt', 'csv', 'pdf'])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.write(content[:10])

if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("Input your question here: ")
if prompt:
    st.session_state.messages.append(
        {"role":"user", "content":prompt}
    )
    response = "This is a NLP model"
    st.session_state.messages.append(
        {"role":"assistant","content":response}
    )

for messages in st.session_state.messages:
    with st.chat_message(messages["role"]):
        st.write(messages["content"])

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write("Count: ", st.session_state.count)

with st.form("nlp_form"):
    name = st.text_area("Input name")
    task = st.selectbox("Select task",
                        ["A", "B", "C"])
    submitted = st.form_submit_button("Run")

if submitted:
    st.write(name)
    st.write(task)

@st.cache_resource(show_spinner=False)

def load_heavy_resource():
    time.sleep(3)
    return {"status":"loaded"}

resource = load_heavy_resource()
st.write("Resource", resource)