# Similarity Checker

Group a large set of articles based on their topic.

## Possible Algorithms

- Cosine similarity - requires checking all articles against all others
(Implemented for now)
- DBSCAN - requires fiddling with and testing parameters
- Latent Dirichlet Allocation - No fiddling or supervising of parameters, only
massaging of the dataset

## Stemming

Stemming of words has been tried, but is ultimately removed for missing python
stub files. In our limited tests, stemming did not improve the result by a
significant amount. If later on an different library is found, it will be used.