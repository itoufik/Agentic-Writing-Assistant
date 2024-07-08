from sentence_transformers import SentenceTransformer
model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
model = SentenceTransformer(model_name)
model_path = "cross-encoder-model"
model.save(model_path)