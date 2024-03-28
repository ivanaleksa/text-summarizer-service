from transformers import pipeline


class Model:
    def __init__(self):
        self.__summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    def make_prediction(self, input_text: str, min_len: int = 30, max_len: int = 130) -> str:
        return self.__summarizer(input_text, max_length=max_len, min_length=min_len, do_sample=False)
