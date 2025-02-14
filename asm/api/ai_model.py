from transformers import pipeline
model_path = "./model"

pipe = pipeline(
        "text2text-generation",
        model = model_path,
        max_length=100
        )
