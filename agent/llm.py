from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

def ask_llm(prompt):
    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
