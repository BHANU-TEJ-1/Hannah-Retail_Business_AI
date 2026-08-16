from app.rag.embeddings import embedding_model

text = "Retail inventory management"

embedding = embedding_model.embed_query(text)

print(f"Embedding Dimension : {len(embedding)}")
print()
print(embedding[:10])