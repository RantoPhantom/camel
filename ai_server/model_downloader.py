from huggingface_hub import snapshot_download

snapshot_download(
        repo_id="Salesforce/blip2-opt-2.7b",
        local_dir="./models/Salesforce/blip2-opt-2.7b",
        )

