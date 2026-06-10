from ollama import chat

response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain binary search"
        }
    ]
)

print(response["message"]["content"])