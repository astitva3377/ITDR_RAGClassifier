from openai import OpenAI

class EmbeddingService:
	def __init__(
			self,
			base_url: str = "http://localhost:1234/v1",
			api_key: str = "lm-studio",
			model: str = "text-embedding-nomic-embed-text-v1.5"
	) -> None:
		self.client = OpenAI(
			base_url=base_url,
			api_key=api_key
		)
		self.model = model

	def embed(self, text: str) -> list[float]:
		response = self.client.embeddings.create(
			model=self.model,
			input=text
		)
		return response.data[0].embedding