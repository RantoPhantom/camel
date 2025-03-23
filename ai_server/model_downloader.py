from huggingface_hub import snapshot_download

snapshot_download(
        repo_id="NousResearch/Llama-2-7b-chat-hf",
        local_dir="./models/",
        )
