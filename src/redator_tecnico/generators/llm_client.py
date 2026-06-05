from groq import Groq


DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, temperature: float = 0.3):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate_documentation(self, prompt: str, max_tokens: int = 8192) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a technical documentation expert. "
                        "Given source code analysis data, generate clear, "
                        "well-structured Markdown documentation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
