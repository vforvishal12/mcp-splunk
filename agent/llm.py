from openai import OpenAI

client = OpenAI(
    api_key="YOUR_OPENROUTER_KEY",
    base_url="https://openrouter.ai/api/v1"
)

def ask_llm(prompt):
    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
