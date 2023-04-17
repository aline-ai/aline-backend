import time
import modal

embeddings = modal.Function.lookup("utils", "Embeddings.encode")

def test_embeddings():
    start = time.time()
    embeddings.call("hello world")
    print(f"Embedding took {time.time() - start}")
    embeddings.call(["hello world", "hello world"])
    print(f"Embedding took {time.time() - start}")
