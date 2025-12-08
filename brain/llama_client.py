from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

class LlamaClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response from Llama 3"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that responds in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=1024
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    def generate_json(self, prompt: str) -> dict:
        """Generate and parse JSON response"""
        response = self.generate(prompt, temperature=0.3)
        if response:
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                return json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Response was: {response}")
                return None
        return None
