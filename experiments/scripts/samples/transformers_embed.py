import os

import faiss
import torch
from src.utils import SyllabusParser
from torch import Tensor
from transformers import AutoModel, AutoTokenizer

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")


def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


query_texts = ["query: 機械学習を学べる科目は?"]
passage_texts = []
for root, dirs, files in os.walk("data/raws"):
    for file in files:
        if file.endswith(".html"):
            path_to_html = os.path.join(root, file)
            with open(path_to_html, "r", encoding="utf-8") as f:
                html = f.read()
            parser = SyllabusParser(html)
            passage_texts.append("passage: " + parser.get_text())

            if len(passage_texts) == 10:
                break
    if len(passage_texts) == 10:
        break

input_texts = query_texts + passage_texts

tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-small")
model = AutoModel.from_pretrained("intfloat/multilingual-e5-small").to(device)

# Tokenize the input texts
batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors="pt")

with torch.no_grad():
    outputs = model(**batch_dict.to(device))
embeddings = average_pool(outputs.last_hidden_state, batch_dict["attention_mask"])

embeddings_np = embeddings.cpu().detach().numpy()
dimension = embeddings_np.shape[1]

# IndexFlatL2
index_flat_l2 = faiss.IndexFlatL2(dimension)
index_flat_l2.add(embeddings_np[len(query_texts) :])

# search
K = 2
D, I = index_flat_l2.search(embeddings_np[: len(query_texts)], K)  # noqa

# display results
for i in range(len(D)):
    print(f"Query: {query_texts[i]}")
    for k in range(K):
        print(f"  Rank: {k+1}, Index: {I[i][k]}, Distance: {D[i][k]}, Text: '{passage_texts[I[i][k]]}")
