import numpy as np
data = np.load('vectorized_features.npz')
vectors = data['vectors']
ids = data['ids']

print(f"Vectors shape: {vectors.shape}")

print("Vectors and IDs:")
for vector, id in zip(vectors, ids):
    print(f"ID: {id}, Vector: {vector}")
