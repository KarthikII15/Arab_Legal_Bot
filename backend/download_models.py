import os
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def download_models():
    print(f"Downloading models to {MODEL_DIR}...")
    
    # 1. Similarity Model
    sim_model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    sim_path = os.path.join(MODEL_DIR, "similarity_model")
    print(f"Downloading {sim_model_name}...")
    model = SentenceTransformer(sim_model_name)
    model.save(sim_path)
    print(f"Saved to {sim_path}")

    # 2. Summarization Model
    # Switching to a fine-tuned summarization model as per user recommendation to fix hallucinations
    sum_model_name = "csebuetnlp/mT5_multilingual_XLSum"
    sum_path = os.path.join(MODEL_DIR, "summarizer_model")
    print(f"Downloading {sum_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(sum_model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(sum_model_name)
    
    tokenizer.save_pretrained(sum_path)
    model.save_pretrained(sum_path)
    print(f"Saved to {sum_path}")
    
    print("\n✅ All models downloaded successfully for offline use.")

if __name__ == "__main__":
    download_models()
