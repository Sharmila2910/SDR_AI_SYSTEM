from ctransformers import AutoModelForCausalLM
import logging

model = None

def load_model():
    global model
    if model is None:
        try:
            model = AutoModelForCausalLM.from_pretrained(
                'TheBloke/Llama-2-7B-Chat-GGML',
                model_file='llama-2-7b-chat.ggmlv3.q4_K_S.bin'
            )
            logging.info("Model loaded successfully!")
        except Exception as e:
            logging.error(f"Failed to load the model: {e}")
            raise

def get_model():
    if model is None:
        load_model()
    return model