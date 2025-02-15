from transformers import pipeline
enable_ai = False
model_path = "./model"
if enable_ai == True:
    pipe = pipeline(
            "text2text-generation",
            model = model_path,
            max_length=100
            )
