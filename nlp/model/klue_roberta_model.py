
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch

model_name = "klue/roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

# text embedding
query_embedding = get_embedding(top_keywords).detach().numpy()
paper_embeddings = [get_embedding(paper['title']).detach().numpy() for paper in papers_data]

# Similarity
similarities = [cosine_similarity(query_embedding, paper_embedding) for paper_embedding in paper_embeddings]

similar_papers = sorted(
    [(paper, similarity[0][0]) for paper, similarity in zip(papers_data, similarities)],
    key=lambda x: x[1],
    reverse=True
)

print("유사한 문서들:")
for paper, similarity in similar_papers:
    print(f"{paper['title']}: similarity = {similarity:.4f}")
