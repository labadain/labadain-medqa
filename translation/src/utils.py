import os
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset

_ = load_dotenv()

class Utils:
    
    def __init__(self):
        pass
    
    def get_gemini_model(self):
        """Gemini Flash model from Google Generative AI."""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables.")

        try:
            import google.generativeai as genai
        except Exception as e:
            raise ImportError(
                "google.generativeai is required. Install it with `pip install google-generativeai`"
            ) from e

        model = genai.GenerativeModel("gemini-2.5-flash")
        
        return model

    def read_markdown(self, file_path: str) -> str:
        """Read a markdown file and return its content as a string."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text(encoding="utf-8")

    def load_dataset_from_huggingface(self, dataset_name: str, split: str = 'train'):
        """Load a dataset from Hugging Face."""
        try:
            dataset = load_dataset(dataset_name, split=split)
            return dataset
        except Exception as e:
            raise ValueError(f"Error loading dataset {dataset_name}: {e}")