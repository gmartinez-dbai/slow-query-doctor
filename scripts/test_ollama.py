import ollama

response = ollama.chat(
    model="llama2", messages=[{"role": "user", "content": "Hello, Ollama!"}]
)
print(response)
