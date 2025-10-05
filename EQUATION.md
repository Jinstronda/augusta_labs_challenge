# 🧮 Universal Company Match Formula

## Final Score Calculation

```
FINAL SCORE = 0.50S + 0.20M + 0.10G + 0.15O′ + 0.05W
```

**Output**: Single continuous number in [0, 1], directly comparable across incentives.

---

## ⚙️ Variable Definitions

### S - Semantic Similarity (Weight: 0.50)
- **Range**: 0–1
- **Computation**: Standardize cosine similarity within the top N (e.g., 5) companies per incentive:
  ```
  S_i = (s_i - min(s)) / (max(s) - min(s))
  ```
- **Meaning**: Measures how semantically close the company's description is to the incentive text.

### M - CAE / Activity Overlap (Weight: 0.20)
- **Range**: 0–1
- **Computation**: Compute Jaccard similarity between the incentive text keywords and the company's cae_classification + activities_preview keywords:
  ```
  M = |K_inc ∩ K_company| / |K_inc ∪ K_company|
  ```
- **Meaning**: Measures sectoral and activity alignment.

### G - Geographic Fit (Weight: 0.10)
- **Range**: 0, 0.5, or 1
- **Computation**: Compare company's address to incentive's target regions:
  - Inside region → 1
  - Unknown → 0.5
  - Outside → 0
- **Meaning**: Measures location suitability.

### O - Organizational Capacity (Base) (Weight: 0.15)
- **Range**: 0–1
- **Computation**: Determined from legal form:
  - "S.A." → 1.00
  - "Cooperativa", "Associação", "Fundação", "Misericórdia", "Centro Social" → 1.00
  - "SGPS" → 0.60
  - "LDA" (not Unipessoal) → 0.70
  - "Unipessoal" → 0.40
  - Unknown → 0.50
- **Meaning**: Proxy for company size/maturity.

### O′ - Contextual Organizational Fit (Weight: 0.15)
- **Range**: 0–1
- **Computation**: Adjust O by incentive direction:
  - `org_direction = +1` (prefers large/institutional): `O′ = O`
  - `org_direction = -1` (prefers small/startups): `O′ = 1 - O`
  - `org_direction = 0` (prefers social/nonprofit): `O′ = 1` if associative type, else 0.5
- **Meaning**: Contextualizes company size for the incentive goal.

### W - Website Presence (Weight: 0.05)
- **Range**: 0 or 1
- **Computation**: 1 if valid URL in website, else 0
- **Meaning**: Proxy for digital/operational maturity.

---

## 📊 Weights Summary

| Variable | Weight | Purpose |
|----------|--------|---------|
| S | 0.50 | Core semantic alignment |
| M | 0.20 | Sectoral / CAE relevance |
| G | 0.10 | Geographic eligibility |
| O′ | 0.15 | Organizational suitability |
| W | 0.05 | Online presence indicator |
| **Total** | **1.00** | |

---

## ✅ Example 1: Incentive Prefers Large Companies

**Incentive Context:**
- `org_direction`: +1
- `allowed_regions`: ["Portugal Continental"]

**Company Variables:**

| Variable | Value | Explanation |
|----------|-------|-------------|
| S | 0.82 | Normalized cosine similarity |
| M | 0.60 | CAE/activity overlap |
| G | 1.0 | Inside target region |
| O | 1.00 | S.A. (large company) |
| O′ | 1.00 | O′ = O (direction = +1) |
| W | 1.0 | Has website |

**Calculation:**
```
FINAL SCORE = 0.50×0.82 + 0.20×0.60 + 0.10×1 + 0.15×1 + 0.05×1
            = 0.410 + 0.120 + 0.100 + 0.150 + 0.050
            = 0.835
```

**Result**: ✅ **Excellent match** (0.835)

---

## ✅ Example 2: Incentive Prefers Small Businesses

**Incentive Context:**
- `org_direction`: -1 (small companies favored)

**Company Variables:**

| Variable | Value | Explanation |
|----------|-------|-------------|
| S | 0.70 | Normalized cosine similarity |
| M | 0.55 | CAE/activity overlap |
| G | 1.0 | Inside target region |
| O | 1.00 | S.A. (large company) |
| O′ | 0.00 | O′ = 1 - O = 0 (penalized for being large) |
| W | 1.0 | Has website |

**Calculation:**
```
FINAL SCORE = 0.50×0.70 + 0.20×0.55 + 0.10×1 + 0.15×0.00 + 0.05×1
            = 0.350 + 0.110 + 0.100 + 0.000 + 0.050
            = 0.565
```

**Result**: ⚠️ **Moderate match** (0.565) - Big company penalized because incentive wants small ones

---

## ✅ Example 3: Incentive Prefers Social / Nonprofits

**Incentive Context:**
- `org_direction`: 0 (social/nonprofit favored)

**Company Variables:**

| Variable | Value | Explanation |
|----------|-------|-------------|
| S | 0.68 | Normalized cosine similarity |
| M | 0.50 | CAE/activity overlap |
| G | 1.0 | Inside target region |
| O | 1.00 | Associação (nonprofit) |
| O′ | 1.00 | O′ = 1 (associative type, direction=0) |
| W | 0.0 | No website |

**Calculation:**
```
FINAL SCORE = 0.50×0.68 + 0.20×0.50 + 0.10×1 + 0.15×1 + 0.05×0
            = 0.340 + 0.100 + 0.100 + 0.150 + 0.000
            = 0.715
```

**Result**: ✅ **Strong match** (0.715)

---

## 🤖 LLM Input/Output Format

### Input to GPT-5-mini:
```json
{
  "s": 0.63,
  "m": 0.41,
  "g": 1.0,
  "o": 0.70,
  "org_direction": -1,
  "w": 1
}
```

### Expected Output:
```json
{
  "final_score": 0.565
}
```

---

## 📝 Implementation Notes

1. **Semantic Similarity (S)**: Comes from BGE reranker scores, normalized within top 5
2. **CAE Overlap (M)**: Computed via Jaccard similarity on keywords
3. **Geographic Fit (G)**: Already computed by GPT-5-mini geographic analyzer
4. **Organizational Capacity (O)**: Extracted from company legal form
5. **Contextual Org Fit (O′)**: Adjusted based on incentive's org_direction
6. **Website (W)**: Simple boolean check

---

## 🎯 Score Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 0.80 - 1.00 | Excellent match - Highly recommended |
| 0.65 - 0.79 | Strong match - Recommended |
| 0.50 - 0.64 | Moderate match - Consider with caution |
| 0.35 - 0.49 | Weak match - Not recommended |
| 0.00 - 0.34 | Poor match - Avoid |

---

**Formula Version**: 1.0  
**Last Updated**: January 2025
