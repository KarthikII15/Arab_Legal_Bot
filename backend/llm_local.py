import torch
from transformers import pipeline
import logging
import os

logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self, model_id="Qwen/Qwen2.5-1.5B-Instruct"):
        # Check if model exists locally in models/llm
        local_path = os.path.join(os.path.dirname(__file__), "models", "llm")
        if os.path.exists(local_path):
            self.model_id = local_path
            logger.info(f"Using local LLM path: {self.model_id}")
        else:
            self.model_id = model_id
            logger.info(f"Local path not found, using model ID: {self.model_id}")
            
        self.pipeline = None
        self.tokenizer = None
        
    def load_model(self):
        """Loads the model if not already loaded."""
        if self.pipeline:
            return

        logger.info(f"Loading local LLM: {self.model_id}...")
        try:
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Use pipeline for simplicity
            # For CPU, we stick to float32 to avoid issues, unless user has specific config
            torch_dtype = torch.float16 if device == "cuda" else torch.float32
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_id,
                device_map="auto" if device == "cuda" else None,
                torch_dtype=torch_dtype,
                model_kwargs={"low_cpu_mem_usage": True}
            )
            logger.info("Local LLM loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load Local LLM: {e}")
            # Fallback or re-raise? Re-raise to let caller handle it
            raise e

    def generate(self, prompt: str, system_prompt: str = None, max_new_tokens=1024) -> str:
        """
        Generates text from the prompt.
        Handles formatting for Instruct models if needed.
        """
        if not self.pipeline:
            self.load_model()
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            outputs = self.pipeline(
                messages,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
            # Extract the actual generated text
            # Pipeline returns list of dicts with 'generated_text' which is the messages list + response
            # Or if text-generation is used with chat template, it returns properly
            
            # The pipeline output format depends on version, but typically:
            generated = outputs[0]["generated_text"]
            if isinstance(generated, list):
                # It returns the full conversation. Last message is from assistant
                return generated[-1]["content"]
            elif isinstance(generated, str):
                return generated
            return str(generated)
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "عذراً، حدث خطأ أثناء إنشاء النص. (Model generation error)"
