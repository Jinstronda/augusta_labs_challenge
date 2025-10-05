# 🔗 How Qdrant Links to PostgreSQL Companies

## ✅ YES - Qdrant embeddings are DIRECTLY linked to your companies!

## 🎯 The Connection Mechanism

### **PostgreSQL (Structured Data)**
```sql
company_id | company_name | cae_primary_label | activities
-----------|--------------|-------------------|------------
1          | DANIJO       | Mass production   | Confeção de vestuário...
2          | TAXIGÁS      | Wholesale         | Comércio a retalho...
3          | BLKW         | Non-specialised   | Consultoria...
```

### **Qdrant (Vector + Metadata)**
```python
Point(
    id=1,  # ← SAME as PostgreSQL company_id!
    vector=[0.123, -0.456, 0.789, ...],  # 768-dim embedding
    payload={
        "company_name": "DANIJO",
        "cae_primary_label": "Mass production",
        "website": "www.danijo.pt",
        "has_website": True
    }
)
```

## 🔄 How the Linking Works

### **During Indexing (embed_companies_qdrant.py):**

```python
# 1. Load from PostgreSQL
cursor.execute("SELECT company_id, company_name, cae, activities FROM companies")
companies = cursor.fetchall()

# 2. Embed each company
for company in companies:
    company_id, name, cae, activities = company
    
    # Create text
    text = f"{name} {cae} {activities}"
    
    # Generate embedding
    embedding = model.encode(text)
    
    # 3. Store in Qdrant with SAME ID
    client.upsert(
        collection_name="companies",
        points=[PointStruct(
            id=company_id,  # ← PostgreSQL company_id becomes Qdrant point ID
            vector=embedding.tolist(),
            payload={
                "company_name": name,
                "cae_primary_label": cae,
                # Store key metadata for quick access
            }
        )]
    )
```

### **During Search:**

```python
# 1. Search Qdrant by semantic similarity
query_text = "software development cloud computing"
query_vector = model.encode(query_text)

results = qdrant_client.search(
    collection_name="companies",
    query_vector=query_vector,
    limit=40
)

# 2. Results contain both vector similarity AND metadata
for result in results:
    print(f"Company ID: {result.id}")  # ← Links to PostgreSQL
    print(f"Name: {result.payload['company_name']}")
    print(f"CAE: {result.payload['cae_primary_label']}")
    print(f"Similarity: {result.score}")

# 3. If you need MORE data, query PostgreSQL with the IDs
company_ids = [r.id for r in results]
cursor.execute("""
    SELECT * FROM companies
    WHERE company_id IN %s
""", (tuple(company_ids),))

full_data = cursor.fetchall()
```

## 💡 Two Ways to Access Company Data

### **Option 1: Use Qdrant Payload (Faster) ⚡**
```python
# Everything you need is in the payload!
for result in results:
    company_name = result.payload['company_name']
    cae = result.payload['cae_primary_label']
    website = result.payload['website']
    # No database query needed!
```

**Use when:** You only need basic info (name, CAE, website)

### **Option 2: Query PostgreSQL (More Complete) 📊**
```python
# Get IDs from Qdrant, fetch full data from PostgreSQL
company_ids = [r.id for r in results]

cursor.execute("""
    SELECT 
        company_id, company_name, cae_primary_label,
        trade_description_native, website,
        location_address, location_region  -- Full data including location
    FROM companies
    WHERE company_id IN %s
""", (tuple(company_ids),))

companies = cursor.fetchall()
```

**Use when:** You need complete data (full activities, location, etc.)

## 🎯 Best Practice: Hybrid Approach

```python
class CompanyRetriever:
    def __init__(self):
        self.qdrant_client = QdrantClient(path="./qdrant_storage")
        self.db_conn = psycopg2.connect(...)
    
    def search_companies(self, query, limit=40):
        # Step 1: Fast semantic search in Qdrant
        query_vector = self.model.encode(query)
        qdrant_results = self.qdrant_client.search(
            collection_name="companies",
            query_vector=query_vector,
            limit=limit
        )
        
        # Step 2: Quick access to basic info from payload
        basic_info = [
            {
                "id": r.id,
                "name": r.payload['company_name'],
                "cae": r.payload['cae_primary_label'],
                "score": r.score
            }
            for r in qdrant_results
        ]
        
        # Step 3: Fetch full data from PostgreSQL (only when needed)
        if need_full_details:
            company_ids = [r.id for r in qdrant_results]
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT * FROM companies WHERE company_id IN %s
            """, (tuple(company_ids),))
            full_data = cursor.fetchall()
            return full_data
        
        return basic_info
```

## 📊 Performance Comparison

| Method | Speed | Data Available | Use Case |
|--------|-------|---------------|----------|
| **Qdrant Payload Only** | ⚡ 15ms | Basic metadata | Quick filtering, UI display |
| **Qdrant + PostgreSQL** | 🟡 30-50ms | Complete data | Detailed analysis, final output |
| **PostgreSQL Only** | 🐌 500ms | Complete data | No semantic search |

## ✅ Summary

**The connection is simple:**
1. ✅ Qdrant `point.id` = PostgreSQL `company_id`
2. ✅ Qdrant `payload` = Quick metadata cache
3. ✅ PostgreSQL = Full data source of truth
4. ✅ Best of both worlds: Fast semantic search + Complete structured data

**Your pipeline will:**
```
Query → Qdrant (semantic search, 15ms) → Get top 40 company IDs
  ↓
  PostgreSQL (fetch full details, 10ms) → Complete company data
  ↓
  LLM Reranking → Top 5 matches
```

**Total time per incentive: ~40-60ms** ⚡

This is the standard architecture for production RAG systems! 🚀
