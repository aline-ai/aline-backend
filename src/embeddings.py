import time

import modal
from loguru import logger

model_name = "multi-qa-MiniLM-L6-cos-v1"
CACHE_PATH = "/root/model_cache"

stub = modal.Stub("utils")
image = modal.Image.debian_slim().pip_install(
    "sentence-transformers",
    "loguru"
)
volume = modal.SharedVolume().persist(model_name)


class Embeddings:
    def __enter__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name, cache_folder=CACHE_PATH)

    @stub.function(image=image, shared_volumes={CACHE_PATH: volume}, gpu="any")
    def encode(self, text: str | list[str]) -> str:
        start = time.time()
        embeddings = self.model.encode(text)
        logger.info(f"Embedding took {time.time() - start}")
        return embeddings
