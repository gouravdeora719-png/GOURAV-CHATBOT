import streamlit as st
import sqlite3
import hashlib
from huggingface_hub import InferenceClient

st.set_page_config(page_title="GOURAV AI CHATBOT", page_icon="🤖", layout="wide")

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        content TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except:
        return False

def login_user(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    user = cur.fetchone()
    conn.close()
    return user is not None

def save_chat(username, role, content):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chats(username,role,content) VALUES(?,?,?)",
        (username, role, content)
    )
    conn.commit()
    conn.close()

def load_chat(username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT role,content FROM chats WHERE username=? ORDER BY id",
        (username,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_chat(username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM chats WHERE username=?", (username,))
    conn.commit()
    conn.close()

init_db()

st.markdown("<h1 style='text-align:center;'>🤖 GOURAV AI CHATBOT</h1>", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")

        if st.button("Login"):
            if login_user(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("Create Username")
        new_pwd = st.text_input("Create Password", type="password")

        if st.button("Register"):
            if register_user(new_user, new_pwd):
                st.success("Registration successful. Login now.")
            else:
                st.error("Username already exists")

    st.stop()

HF_API_KEY = st.secrets["HF_API_KEY"]
client = InferenceClient(api_key=HF_API_KEY)

with st.sidebar:
    st.title("⚙️ Settings")
    st.success(f"Logged in: {st.session_state.username}")

    model_name = st.selectbox(
        "Model",
        [
            "meta-llama/Llama-3.1-8B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3"
        ]
    )

    if st.button("Clear My Chat"):
        clear_chat(st.session_state.username)
        st.rerun()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.caption("Created by Gourav Tailor")

history = load_chat(st.session_state.username)

messages = [{
    "role":"system",
    "content":"You are GOURAV AI CHATBOT. Give clear, accurate and detailed answers."
}]

for role, content in history:
    messages.append({"role": role, "content": content})

for role, content in history:
    with st.chat_message(role):
        st.markdown(content)

prompt = st.chat_input("Ask anything...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    save_chat(st.session_state.username, "user", prompt)
    messages.append({"role":"user","content":prompt})

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=700,
                temperature=0.7
            )

            answer = response.choices[0].message.content

            st.markdown(answer)

            save_chat(st.session_state.username, "assistant", answer)

        except Exception as e:
            st.error(f"Error: {e}")
