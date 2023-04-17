# Similarity Checker

Group a large set of articles based on their topic.

## Possible Algorithms

- Cosine similarity - requires checking all articles against all others
(Implemented for now)
- DBSCAN - requires fiddling with and testing parameters
- Latent Dirichlet Allocation - No fiddling or supervising of parameters, only
massaging of the dataset

### Performance

Because a rather naive algorithm is used, that can only check pairs of articles
and because all articles in the database are checked against eachother, the
matcher is quite slow. In our tests, checking a thousand articles against
each other took nearly 15 minutes. Matched articles are therefor immediately
inserted into the database and not waited untill the algorithm completes.

## Stemming

Stemming of words has been tried, but is ultimately removed for missing python
stub files. In our limited tests, stemming did not improve the result by a
significant amount. If later on an different library is found, it will be used.

## Leftover files

The [`articles`](./articles) folder is a leftover folder from testing the
similarity checker. It is not removed as a reference to the type texts that are
successfully matched.
