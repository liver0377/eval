from huggingface_hub import snapshot_download

# This will download the entire repository to your local folder
snapshot_download(
    repo_id="allenai/IFBench_multi-turn",
    repo_type="dataset",
    local_dir="./IFBench_multi-turn"
)
print("Download complete!")