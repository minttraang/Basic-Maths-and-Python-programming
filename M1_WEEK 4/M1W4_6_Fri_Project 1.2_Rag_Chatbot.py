#######openAI#######

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() # Load variables from the .env file

# OpenAI automatically looks for the OPENAI_API_KEY environment variable,
# so you don't even need to pass api_key=... manually!
client = OpenAI()

messages = []
messages.append({"role":"user", "content":"hi"})
resp = client.chat.completions.create(
    model = 'gpt-4o-mini',
    messages=messages,
    temperature=0
)

print(resp.choices[0].message.content)

#Jupyter Notebooks vs. standard Python .py scripts:
### Jupyter Notebook: The notebook automatically prints/displays the evaluation of the final line in a code cell.
### Python Scripts: When executing a .py file via the terminal, Python executes statements but does not automatically print values unless you explicitly wrap them in a print() function.


####### STREAMLIT #######
import streamlit as st
import ollama

model = "vicuna:7b-v1.5-q5_1"
st.title("Simple Chatbot App")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Please input your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.chat_message("user").write(prompt)
    resp = ollama.chat(
        model = model,
        messages = st.session_state.messages,
        options = {"temperature": 0}
    )

    answer = resp.message.content
    st.session_state.messages.append({"role": "assistant",
                                      "content": answer})
    st.chat_message("assistant").write(answer)


####### CHATBOT WITH A FILE #######
import pypdf

reader = pypdf.PdfReader("YOLOv10_Tutorials.pdf")

full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

len(reader.pages)

import streamlit as st
import ollama
import pypdf
import chromadb

def read_file(file):
    reader = pypdf.PdfReader(file)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return full_text

model = "vicuna:7b-v1.5-q5_1"
st.title("Chatbot With a File App")
uploaded = st.file_uploader("Upload pdf file", type = "pdf")

if uploaded:
    text = read_file(uploaded)
    st.success(f"Read file {len(text)} characters")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        st.chat_message(m["role"]).write(m["content"])

    if prompt := st.chat_input("Please input prompt..."):
        st.session_state.messages.append({"role":"user", "content":prompt})

        st.chat_message("user").write(prompt)
        full_prompt = f"""Use this document to answer the question.
        
        Document:
        {text[:250]}

        Question:
        {prompt}

        Answer:
        """

        resp = ollama.chat(
            model = model,
            messages = [{"role": "user",
                         "content": full_prompt}],
            options={"temperature": 0,
            "num_ctx": 4097}
        )

        answer = resp.message.content
        st.session_state.messages.append({"role":"assistant",
                                          "content": answer,
                                          })

        st.chat_message("assistant").write(answer)

####### RAG CHATBOT #######

client = chromadb.Client()
LLM_MODEL = "vicuna:7b-v1.5-q5_1"
EMBED_MODEL = "nge-m3"
PROMPT = """You are a Q&A assistant. Use the provided context excerpts to answer the question.
If the context does not contain the information, state that you do not know; do not make things up.
Provide concise, accurate answers in Vietnamese.

Context:
{context}

Question: {question}

Answer:
"""

for k, v in {"collection": None, "pdf_name": "", "chat_history": []}.items():
    st.session_state.setdefault(k,v)

def embed(texts):
    return ollama.embed(
        model=EMBED_MODEL,
        input=texts
    )["embeddings"]

def chunk_text(text, size = 1000, overlap = 200):
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    #page 1 \n page 2

    chunks, cur = [], ""
    for p in paras:
        # Nếu một đoạn dài hơn size, cắt nhỏ đoạn đó (vẫn giữ overlap)
        while len(p) > size:
            # pages 1: 2000 => 1000 (-200) => 800
            if cur:
                chunks.append(cur.strip())
                cur = ""

            chunks.append(p[:size].strip())
            p = p[size - overlap:]

        if len(cur) + len(p) + 1 <= size:
            cur += p + "\n"

        else:
            if cur:
                chunks.append(cur.strip())

            cur = (cur[-overlap:] + p + "\n") if overlap else (p + "\n")
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def read_file(file):
    reader = pypdf.PdfReader(file)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return full_text

def process_pdf(uploaded_file):
    text = read_file(uploaded_file)
    chunks = chunk_text(text)

    col = client.get_or_create_collection("rag_col")
    col.add(
        ids=[str(i) for i in range(len(chunks))], documents = chunks, embeddings=embed(chunks)
    )
    return col, len(chunks)

def rag(question, col, k=2):
    res = col.query(query_embeddings=embed([question]), n_results=k
    )

    context = "\n".join(res["documents"][0])
    resp = ollama.chat(model = LLM_MODEL,
                       messages = [{
                           "role":"user",
                           "content":PROMPT.format(context=context, question=question)
                       }])
    return resp.message.content

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide", initial_sidebar_state="expanded")
st.title("PDF RAG Assistant")

with st.sidebar:
    st.subheader("📄 Upload document")
    f = st.file_uploader("Select file PDF", type = "pdf")
    if f and st.button("🔄 Processing PDF", use_container_width=True):
        with st.spinner("Processing..."):
            st.session_state.collection, n = process_pdf(f)
            st.session_state.pdf_name = f.name
            st.session_state.chat_history = []

        st.success(f"✅ {n} chunks")
    st.info(f"📄 {st.session_state.pdf_name}" if st.session_state.pdf_name else "📄 Have not received document yet!")

    if st.button("🗑️ Delete chat history", use_container_width=True):
        st.session_state.chat_history = []

for m in st.session_state.chat_history:
    with st.chat_message(m["role"]):st.write(m["content"])

if st.session_state.collection is None: #DB
    st.info("🔄 Upload and process PDF before chatt.")
    st.chat_input("Input your question...", disabled=True)
else:
    q = st.chat_input("Please input your question...")
    if q:
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                ans = rag(q, st.session_state.collection)
                st.write(ans)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})


####### STREAMLIT #######
import subprocess, time, requests

def ollama_up():
    try:
        return requests.get("http://localhost:11434", timeout=2).ok
    except Exception:
        return False
if not ollama_up():
    subprocess.Popen(["ollama", "serve"]); time.sleep(8)

print("Ollama running:", ollama_up())

import time; time.sleep(8)
print("Streamlit is running at gate 8501")