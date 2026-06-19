from huggingface_hub import InferenceClient
import streamlit as st

client = InferenceClient(
    api_key=st.secrets["HF_TOKEN"]
)
# Chat History
chat_history = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant"
    }
]

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    # Add user message
    chat_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Generate response
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=chat_history,
        max_tokens=300
    )

    ai_response = response.choices[0].message.content

    print("AI:", ai_response)

    # Save AI response
    chat_history.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )

print("\nFull Chat History:\n")
print(chat_history)