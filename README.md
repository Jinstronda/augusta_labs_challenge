# Semantic Matching for Government Incentives

The problem this solves is simple to state but hard to solve: given a government incentive program, find the companies that should apply for it.

The naive approach is keyword matching. If an incentive mentions "software" and a company has "software" in its description, they match. This fails immediately. A company that does "enterprise resource planning systems" should match an incentive for "digital transformation" even though they share no words.

What you need is semantic matching - matching by meaning, not by words. This is what modern embedding models do well. They convert text to vectors in a way that preserves semantic relationships. Texts with similar meanings end up close together in vector space.

## Architecture

The system has two main components: embedding and matching.

### Embedding

The embedding pipeline converts 250,000 Portuguese companies into vectors. Each company is represented by combining three fields: name, CAE classification (industry category), and business activities. These are fed into a multilingual sentence transformer that outputs a 384-dimensional vector.

The vectors are stored in Qdrant, a vector database optimized for similarity search. Qdrant can search 250,000 vectors in under a second on modest hardware.

The key architectural decision here is what to embed. We embed the combination of name, classification, and activities because that's what captures what a company does. The name alone isn't enough - "ACME Corp" tells you nothing. The activities alone are too verbose and noisy. The combination works.

### Matching

The matching pipeline takes an incentive and finds the best companies for it. This happens in two stages.

First, we do fast approximate search using Qdrant. We convert the incentive's sector and eligible actions into a query vector and find the 20 nearest company vectors. This is fast - under a second - but approximate. The 20th result might be better than the 5th.

Second, we rerank these 20 candidates using a cross-encoder model (BGE Reranker v2-m3). Unlike the bi-encoder used for embedding, a cross-encoder sees both the query and document together. This lets it capture subtle semantic relationships that bi-encoders miss. It's much slower - you couldn't run it on 250,000 companies - but much more accurate.

The result is a list of 5 companies with scores from 0 to 1. Scores above 0.8 indicate strong matches. In testing, the top result typically has a score above 0.9 when the match is good.

## Why This Works

The interesting thing is how simple the query generation is. We just concatenate the incentive's sector and eligible actions. No prompt engineering, no LLM calls, no complex query expansion. This works because the embedding model already understands semantic relationships.

We initially tried using GPT to generate better queries. It made things worse. The LLM would try to be clever - expanding terms, adding synonyms, restructuring the text. But the embedding model doesn't need this. It already knows that "railway transport" and "urban passenger transport" are related. Adding more words just adds noise.

This is a general pattern in ML systems: the simpler approach often works better. The complexity should be in the model, not in the code around it.

## Two-Stage Retrieval

The two-stage architecture (fast search + precise reranking) is standard in modern search systems. You see it in Google, in recommendation systems, in RAG applications. The reason is fundamental: you can't run expensive models on millions of items, but you can't get good results with cheap models either.

The solution is to use a cheap model to narrow down to hundreds of candidates, then use an expensive model to pick the best ones. The cheap model (bi-encoder) is fast because it encodes queries and documents independently. The expensive model (cross-encoder) is accurate because it sees them together.

The specific numbers - 20 candidates, top 5 results - are somewhat arbitrary. We could retrieve 50 and return 10. But 20 and 5 work well in practice. Twenty is enough that the reranker has good candidates to choose from. Five is few enough that a human can review them.

## Implementation Details

The system is implemented in Python using standard libraries. The embedding model is sentence-transformers, specifically paraphrase-multilingual-MiniLM-L12-v2. This model handles Portuguese and English, which matters because company descriptions are in Portuguese but CAE classifications are in English.

The reranker is BAAI/bge-reranker-v2-m3, which is currently state-of-the-art for cross-lingual reranking. It's a 568M parameter model, so it's slow, but that's fine because we only run it on 20 items.

Qdrant runs locally with no server required. It stores vectors in ./qdrant_storage. For 250,000 companies, this takes about 400MB. You could use Qdrant Cloud for production, but local storage works fine for this scale.

The code uses GPU if available but falls back to CPU. GPU is 10-20x faster for embedding but not required. The reranker benefits more from GPU because it's a larger model.

## Data Flow

The complete flow from incentive to matches:

1. Load incentive from PostgreSQL (sector, eligible actions, etc.)
2. Create query by concatenating sector + eligible actions
3. Encode query to 384-dimensional vector using sentence transformer
4. Search Qdrant for 20 nearest company vectors (cosine similarity)
5. Fetch full company data from PostgreSQL using company IDs
6. Score each of 20 companies against query using BGE reranker
7. Sort by rerank score and return top 5

Steps 1-4 take about 1 second. Step 6 (reranking) takes 2-3 seconds. The bottleneck is the reranker, which is expected - it's doing deep semantic analysis.

## Results

In testing, the system produces high-quality matches. For a railway transport incentive, the top match was a company doing "urban and suburban passenger land transport" with a score of 0.90. The top 5 were all transport companies with scores from 0.44 to 0.90.

For a space technology incentive, it would find aerospace companies. For a digital transformation incentive, it would find software and consulting companies. The matches are semantically correct even when there's no keyword overlap.

The key metric is the rerank score. Scores above 0.8 are excellent matches - the company clearly does what the incentive is for. Scores from 0.5 to 0.8 are good matches - relevant but perhaps not perfect. Scores below 0.3 suggest the match is weak.

## Limitations

The system has some limitations worth noting.

First, it only matches on what companies do, not on eligibility criteria. An incentive might require companies to be in a specific region or size range. The semantic matching doesn't check this. You'd need additional filtering for that.

Second, the quality depends on the company data. If a company's activities field is empty or generic ("commercial activities"), the matching won't work well. Garbage in, garbage out.

Third, the system is monolingual in practice. The embedding model is multilingual, but all the company data is in Portuguese. If you had companies in multiple languages, you'd need to think about how to handle that.

Fourth, there's no explanation of why a match was made. The reranker outputs a score but not a reason. For some applications, you'd want to know which parts of the company description matched which parts of the incentive.

## Extensions

Several extensions would be useful for production:

Batch processing: Process all incentives at once instead of one at a time. This would let you build a complete incentive-company matching database.

Filtering: Add filters for geographic requirements, company size, industry codes, etc. The semantic matching finds relevant companies; filters ensure they're eligible.

Caching: Cache the query embeddings and reranker scores. If you're matching the same incentives repeatedly, you don't need to recompute everything.

Feedback loop: Let users mark matches as good or bad. Use this to fine-tune the reranker on your specific domain.

Explanation: Add a component that explains why a match was made. This could be as simple as highlighting matching phrases or as complex as using an LLM to generate explanations.

## Running the Code

To embed companies:

```bash
python embed_companies_qdrant.py          # Test with 2 companies
python embed_companies_qdrant.py --full   # Process all companies
```

To test matching:

```bash
python test_incentive_matching.py
```

The first run will download the models (about 2.5GB total). Subsequent runs use cached models.

## Dependencies

The system requires:
- Python 3.11+
- PostgreSQL with company and incentive data
- sentence-transformers for embeddings
- FlagEmbedding for reranking
- Qdrant for vector storage
- PyTorch (GPU optional but recommended)

See requirements.txt for specific versions.

## Conclusion

The core insight is that semantic matching works better than keyword matching for this problem. The implementation is straightforward: embed companies, store vectors, search by similarity, rerank for precision.

The surprising part is how simple the query generation can be. Just concatenating fields works better than complex prompt engineering. This suggests that the intelligence is in the models, not in the code around them.

The two-stage architecture (fast search + precise reranking) is the key to making this practical. You need both speed and accuracy, and you get them by using different models for different stages.

The result is a system that finds semantically relevant companies for incentives, even when they share no keywords. This is what you want: matching by meaning, not by words.
