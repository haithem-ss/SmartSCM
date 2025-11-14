# Evaluation Dataset Methodology

## 📋 Overview

This document describes the systematic approach used to create a comprehensive evaluation dataset for testing the SmartSCM Assistant's natural language query capabilities.

## 🎯 Objectives

The evaluation dataset was designed to:
1. **Test Query Understanding**: Assess how well the system interprets various question formulations
2. **Validate Data Analysis**: Ensure accurate pandas operations and aggregations
3. **Measure Complexity Handling**: Test simple to complex multi-step queries
4. **Identify Limitations**: Document out-of-scope questions the system cannot answer

## 📊 Dataset Structure

### Question Categories

The evaluation dataset consists of **99 questions** divided into three difficulty levels:

#### 1. Easy Questions (33 questions)
**Characteristics:**
- Single-table lookups
- Direct column filtering
- Simple aggregations (count, sum, unique)
- Basic date operations

**Examples:**
- "How many orders do we have in total?"
- "Show me the number of orders by customer"
- "What are the different product categories?"

#### 2. Medium Questions (33 questions)
**Characteristics:**
- Multiple conditions/filters
- Grouped aggregations
- Date-based filtering with calculations
- String matching and pattern detection
- Cross-column comparisons

**Examples:**
- "Which customers have more than 100 orders?"
- "How many orders were placed by customers who joined after 2024?"
- "What is the average order value by region?"

#### 3. Hard Questions (33 questions)
**Characteristics:**
- Multi-step analysis requiring temporary calculations
- Complex grouping with multiple aggregation functions
- Nested conditions and filtering
- Set operations (intersections, unions)
- Statistical calculations (percentages, ratios, distributions)

**Examples:**
- "For each customer, what is the average quantity per product across all their orders?"
- "Which regions have more than 50% of orders using express shipping?"
- "Show customers where orders contain more than 5 different products"

### Out-of-Scope Questions (20 questions)

These questions test the system's ability to recognize limitations:

**Categories:**
- **Missing Data**: Questions about columns/attributes not in the dataset
- **Temporal Boundaries**: Questions about dates outside the data range
- **Wrong Values**: Questions referencing non-existent categorical values
- **External Context**: Questions requiring domain knowledge not in data

**Examples:**
- "How many orders were cancelled?" (no cancellation status in data)
- "What's the average shipping cost?" (no cost data available)
- "Show orders from 2018" (data starts from 2024)

## 🔬 Question Generation Process

### Step 1: Schema Analysis
- Reviewed all available columns and data types
- Identified relationships between fields
- Noted value distributions and ranges

### Step 2: Query Pattern Identification
Common analytical patterns covered:
- **Counting**: Total records, distinct values, conditional counts
- **Aggregation**: Sum, average, min, max across groups
- **Filtering**: Single and multi-condition filters
- **Grouping**: Single and multi-level grouping
- **Temporal**: Date-based filtering, period grouping, date calculations
- **Text Analysis**: Pattern matching, string splitting, list operations
- **Statistical**: Percentages, ratios, distributions, correlations

### Step 3: Complexity Progression
Questions were designed to progressively increase in complexity:
1. Single operation → Multiple operations
2. One column → Multiple columns
3. Simple filter → Complex conditions
4. Direct answer → Calculated metrics

### Step 4: Natural Language Variation
Each question uses natural, conversational language to test:
- Different phrasings for same intent
- Various question formats (how many, show me, list, what is)
- Implicit vs explicit column references

## 📐 Evaluation Metrics

For each question, we tracked:

1. **Correctness**: Does the answer match expected result?
2. **Code Quality**: Is the generated pandas code efficient and idiomatic?
3. **Explanation Quality**: Does the agent explain its reasoning?
4. **Error Handling**: How does it handle ambiguous or impossible queries?

## 🔄 Testing Workflow

```
Question → Agent Processing → Code Generation → Execution → Validation
                ↓                    ↓              ↓           ↓
         Plan Creation    Pandas Code Review   Result Check  Comparison
```

### Validation Approach
- Ground truth answers pre-calculated using verified pandas code
- Automated comparison of agent results vs expected results
- Manual review of edge cases and complex queries

## 📊 Coverage Matrix

| Category | Column Usage | Operations | Date Handling | String Ops | Aggregations |
|----------|-------------|------------|---------------|------------|--------------|
| Easy | ✓ Single | ✓ Basic | ✓ Simple | ✓ Basic | ✓ Count/Sum |
| Medium | ✓ Multiple | ✓ Combined | ✓ Filtering | ✓ Pattern | ✓ Group |
| Hard | ✓ Complex | ✓ Multi-step | ✓ Calculations | ✓ Advanced | ✓ Statistical |

## 🎓 Key Insights from Evaluation

### Strengths Observed
- Strong performance on straightforward aggregations
- Good natural language understanding for common patterns
- Effective date/time handling

### Areas for Improvement
- Complex multi-step queries requiring intermediate calculations
- Ambiguous questions needing clarification
- Edge cases with missing or null data

### Out-of-Scope Detection
- System successfully identifies impossible queries
- Clear communication when data is unavailable
- Helpful suggestions for alternative questions

## 📝 Best Practices Discovered

1. **Clear Column References**: Questions mentioning specific fields perform better
2. **Explicit Grouping**: Stating "by customer" or "per region" improves accuracy
3. **Date Formats**: Natural date expressions work well (e.g., "in 2025", "last month")
4. **Avoid Ambiguity**: Specific metrics ("total count" vs "count") reduce errors

## 🔮 Future Enhancements

Potential expansions to the evaluation dataset:
- **Visualization requests**: Chart generation questions
- **Comparative analysis**: Year-over-year, period comparisons
- **Predictive questions**: Trend analysis, forecasting
- **Multi-table joins**: Questions requiring data from multiple sources
- **Real-time queries**: "Today", "this week" temporal references

## 📚 Related Files

- `/src/scripts/benchmark.py` - Automated evaluation runner
- `/src/scripts/dataset.csv` - Generated question dataset
- `/src/logs/` - Evaluation run logs and results
- `/src/notebooks/benchmarking/` - Analysis notebooks for results

---

**Note**: All evaluation questions in this project now use synthetic data. Original evaluation data containing company information has been replaced with anonymized examples.
