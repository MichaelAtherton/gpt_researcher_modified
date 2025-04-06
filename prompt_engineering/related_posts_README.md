# Related Posts Implementation Guide

## Overview

This guide explains how to implement the functionality of `related_posts.ts` in Python to compare current topic reports and identify redundant or related content. The implementation will help analyze research reports across different dates and highlight new information while avoiding duplication.

## Core Functionality

The original TypeScript implementation uses TF-IDF (Term Frequency-Inverse Document Frequency) to identify similarities between content. The Python implementation will maintain this approach with these core features:

1. **Content similarity analysis** between reports
2. **Multi-metric evaluation** system for relationship scoring 
3. **Weighted matrix generation** for relationship strength
4. **Time-aware comparison** to prioritize recent content

## Required Libraries

```python
# Core libraries needed
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any

# For TF-IDF similarity analysis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Optional for more advanced NLP (if needed)
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
```

## Data Structures

These data structures will be needed to replicate the functionality:

```python
# Types for strongly-typed Python
class FrontMatter:
    """Metadata from the top of markdown files"""
    def __init__(self, title: str, date: Optional[str] = None, 
                 tags: List[str] = None, categories: List[str] = None,
                 description: Optional[str] = None):
        self.title = title
        self.date = date
        self.tags = tags or []
        self.categories = categories or []
        self.description = description

class RelatedPosts:
    """Container for related posts data"""
    def __init__(self, slugs: List[str], frontmatters: List[Optional[FrontMatter]], 
                 categories: Optional[List[str]] = None):
        self.slugs = slugs
        self.frontmatters = frontmatters
        self.categories = categories

class DistanceMatrix:
    """Matrix of similarity/distance scores"""
    def __init__(self, identifiers: List[str], matrix: List[List[float]], 
                 strongest_categories: Optional[List[List[int]]] = None):
        self.identifiers = identifiers
        self.matrix = matrix
        self.strongest_categories = strongest_categories

class StrengthVector:
    """Vector of strength scores"""
    def __init__(self, identifiers: List[str], vector: List[float]):
        self.identifiers = identifiers
        self.vector = vector

class Metric:
    """Definition of a similarity metric"""
    def __init__(self, id: str, description: str, multiplier: float, threshold: float):
        self.id = id
        self.description = description
        self.multiplier = multiplier
        self.threshold = threshold
```

## Implementation Steps

### 1. File Management

```python
def read_markdown_file(file_path: str) -> Tuple[FrontMatter, str]:
    """
    Read a markdown file and extract frontmatter and content
    For current_topics reports, this would parse the markdown files in outputs/current_topics/
    """
    # Implementation to parse markdown and extract frontmatter and content
    # Return frontmatter as FrontMatter object and content as string

def get_all_reports(directory: str = "outputs/current_topics") -> List[Dict[str, Any]]:
    """
    Get all current_topics reports from the specified directory
    """
    reports = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            frontmatter, content = read_markdown_file(file_path)
            reports.append({
                "slug": filename.replace(".md", ""),
                "frontmatter": frontmatter,
                "content": content,
                "file_path": file_path
            })
    return reports
```

### 2. Similarity Analysis

```python
def create_corpus(reports: List[Dict[str, Any]], content_field: str) -> Tuple[List[str], List[str]]:
    """
    Create a corpus for TF-IDF analysis
    content_field specifies which report field to use (title, content, etc.)
    """
    slugs = [report["slug"] for report in reports]
    contents = [report[content_field] for report in reports]
    return slugs, contents

def compute_similarity_matrix(slugs: List[str], contents: List[str]) -> DistanceMatrix:
    """
    Compute similarity between documents using TF-IDF and cosine similarity
    """
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(contents)
    
    # Compute cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    return DistanceMatrix(slugs, similarity_matrix.tolist())
```

### 3. Multi-Metric System

```python
def normalize_vector(vector: List[float]) -> List[float]:
    """Normalize a vector to range [0, 1]"""
    max_val = max(vector)
    min_val = min(vector)
    
    if max_val == min_val:
        return [0.5] * len(vector)  # Default to mid-value if no variation
        
    return [(val - min_val) / (max_val - min_val) for val in vector]

def custom_sigmoid(x: float) -> float:
    """Custom sigmoid function to shape the values"""
    return 1.0 / (1.0 + np.exp(-8.0 * (x - 0.5)))

def invert_normalized(x: float) -> float:
    """Invert a normalized value"""
    return 1.0 - x

def apply_threshold(matrix: Union[DistanceMatrix, StrengthVector], threshold: float) -> Union[DistanceMatrix, StrengthVector]:
    """Apply threshold to matrix or vector"""
    if isinstance(matrix, DistanceMatrix):
        new_matrix = []
        for row in matrix.matrix:
            new_row = [val if not np.isnan(val) and val <= threshold else 1.0 for val in row]
            new_matrix.append(new_row)
        return DistanceMatrix(matrix.identifiers, new_matrix, matrix.strongest_categories)
    else:
        new_vector = [val if not np.isnan(val) and val <= threshold else 1.0 for val in matrix.vector]
        return StrengthVector(matrix.identifiers, new_vector)
```

### 4. Computing Metrics

```python
def compute_metrics(reports: List[Dict[str, Any]], metrics: List[Metric]) -> Dict[str, Union[DistanceMatrix, StrengthVector]]:
    """
    Compute all metrics for the reports
    """
    metric_data = {}
    
    # Process each metric
    for metric in metrics:
        if metric.id == 'titles':
            # Compute similarity between titles
            slugs, titles = create_corpus(reports, "frontmatter.title + frontmatter.description")
            metric_data[metric.id] = compute_similarity_matrix(slugs, titles)
            
        elif metric.id == 'content':
            # Compute similarity between full content
            slugs, contents = create_corpus(reports, "content")
            metric_data[metric.id] = compute_similarity_matrix(slugs, contents)
            
        elif metric.id == 'tagCats':
            # Compute similarity between tags and categories
            slugs = [report["slug"] for report in reports]
            tag_cats = []
            
            for report in reports:
                tags = " ".join(report["frontmatter"].tags) if report["frontmatter"].tags else ""
                categories = " ".join(report["frontmatter"].categories) if report["frontmatter"].categories else ""
                combined = f"{tags} {categories}".strip()
                if not combined:
                    combined = f"{report['frontmatter'].title} {report['frontmatter'].description or ''}".strip()
                tag_cats.append(combined)
                
            metric_data[metric.id] = compute_similarity_matrix(slugs, tag_cats)
            
        elif metric.id == 'recency':
            # Compute recency scores
            slugs = [report["slug"] for report in reports]
            now = datetime.now().timestamp()
            
            # Get timestamps of reports
            timestamps = []
            for report in reports:
                if report["frontmatter"].date:
                    try:
                        date = datetime.strptime(report["frontmatter"].date, "%Y-%m-%d").timestamp()
                    except ValueError:
                        date = 0
                else:
                    date = 0
                timestamps.append(now - date)
            
            # Normalize and apply sigmoid
            normalized = normalize_vector(timestamps)
            vector = [custom_sigmoid(val) for val in normalized]
            
            metric_data[metric.id] = StrengthVector(slugs, vector)
        
        # Apply threshold and invert
        metric_data[metric.id] = apply_threshold(metric_data[metric.id], metric.threshold)
        
        # Invert normalized values (so 1 is most related, 0 is least)
        if isinstance(metric_data[metric.id], DistanceMatrix):
            new_matrix = [[invert_normalized(val) for val in row] for row in metric_data[metric.id].matrix]
            metric_data[metric.id] = DistanceMatrix(
                metric_data[metric.id].identifiers, 
                new_matrix,
                metric_data[metric.id].strongest_categories
            )
        else:
            new_vector = [invert_normalized(val) for val in metric_data[metric.id].vector]
            metric_data[metric.id] = StrengthVector(metric_data[metric.id].identifiers, new_vector)
    
    return metric_data
```

### 5. Combining Metrics

```python
def convolute_metrics(metric_data: Dict[str, Union[DistanceMatrix, StrengthVector]], 
                      metrics: List[Metric]) -> DistanceMatrix:
    """
    Combine all metrics into a final matrix
    """
    # Initialize with zeros
    base_matrix = DistanceMatrix(
        metric_data[metrics[0].id].identifiers,
        [[0.0 for _ in range(len(metric_data[metrics[0].id].identifiers))] 
         for _ in range(len(metric_data[metrics[0].id].identifiers))]
    )
    
    # Track which metric has the strongest influence
    strongest_categories = [[None for _ in range(len(base_matrix.identifiers))] 
                            for _ in range(len(base_matrix.identifiers))]
    
    # Add each metric with its multiplier
    for i, metric in enumerate(metrics):
        data = metric_data[metric.id]
        
        if isinstance(data, DistanceMatrix):
            # Apply matrix to base matrix
            for r in range(len(base_matrix.matrix)):
                for c in range(len(base_matrix.matrix[r])):
                    weighted_val = data.matrix[r][c] * metric.multiplier
                    base_matrix.matrix[r][c] += weighted_val
                    
                    # Track strongest category
                    if strongest_categories[r][c] is None or strongest_categories[r][c][1] < weighted_val:
                        strongest_categories[r][c] = (i, weighted_val)
        else:
            # Apply vector to base matrix
            for r in range(len(base_matrix.matrix)):
                for c in range(len(base_matrix.matrix[r])):
                    weighted_val = data.vector[c] * metric.multiplier
                    base_matrix.matrix[r][c] += weighted_val
                    
                    # Track strongest category
                    if strongest_categories[r][c] is None or strongest_categories[r][c][1] < weighted_val:
                        strongest_categories[r][c] = (i, weighted_val)
    
    # Convert strongest categories to just the category indices
    strongest_indices = [[cat[0] if cat is not None else 0 for cat in row] for row in strongest_categories]
    base_matrix.strongest_categories = strongest_indices
    
    return base_matrix
```

### 6. Finding Related Content

```python
def get_related_reports(report_slug: str, metric_data: Dict[str, Union[DistanceMatrix, StrengthVector]], 
                        metrics: List[Metric], reports: List[Dict[str, Any]]) -> Dict[str, RelatedPosts]:
    """
    Find reports related to the specified report
    """
    related_reports = {}
    
    for metric_type, data in metric_data.items():
        try:
            # Find the index of the report
            slug_index = data.identifiers.index(report_slug)
            
            if isinstance(data, DistanceMatrix):
                # Get scores from matrix
                scores = []
                for i, score in enumerate(data.matrix[slug_index]):
                    if i != slug_index and score > 0:
                        scores.append({"score": score, "index": i})
                
                # Sort by score (highest first)
                scores.sort(key=lambda x: x["score"], reverse=True)
                
                # Create related posts object
                slugs = [data.identifiers[score["index"]] for score in scores]
                
                # Get frontmatters for related reports
                frontmatters = []
                for slug in slugs:
                    for report in reports:
                        if report["slug"] == slug:
                            frontmatters.append(report["frontmatter"])
                            break
                    else:
                        frontmatters.append(None)
                
                related_reports[metric_type] = RelatedPosts(slugs, frontmatters)
                
                # Add categories if available
                if data.strongest_categories:
                    categories = []
                    for score in scores:
                        cat_index = data.strongest_categories[slug_index][score["index"]]
                        categories.append(metrics[cat_index].description)
                    related_reports[metric_type].categories = categories
                    
            else:  # StrengthVector
                # Get all scores
                scores = [{"score": score, "index": i} 
                         for i, score in enumerate(data.vector)]
                
                # Sort by score (highest first)
                scores.sort(key=lambda x: x["score"], reverse=True)
                
                # Create related posts object
                slugs = [data.identifiers[score["index"]] for score in scores]
                
                # Get frontmatters for related reports
                frontmatters = []
                for slug in slugs:
                    for report in reports:
                        if report["slug"] == slug:
                            frontmatters.append(report["frontmatter"])
                            break
                    else:
                        frontmatters.append(None)
                
                related_reports[metric_type] = RelatedPosts(slugs, frontmatters)
                
        except ValueError:
            # Report not found in this metric
            continue
            
    return related_reports
```

### 7. Main Functions

```python
def generate_related_matrix(reports_dir: str = "outputs/current_topics", 
                           output_file: str = "related_matrix.json") -> None:
    """
    Generate the related reports matrix and save to file
    """
    # Define metrics
    metrics = [
        Metric("titles", "Similar", 8.0, 1.0),
        Metric("tagCats", "Same Category", 10.0, 1.0),
        Metric("content", "Similar", 8.0, 0.91),
        Metric("recency", "New", 1.0, 0.3)
    ]
    
    # Get all reports
    reports = get_all_reports(reports_dir)
    
    # Compute metrics
    metric_data = compute_metrics(reports, metrics)
    
    # Combine metrics
    final_matrix = convolute_metrics(metric_data, metrics)
    
    # Save to file
    metric_data["final"] = final_matrix
    with open(output_file, "w") as f:
        json.dump(metric_data, f)
    
    print(f"Related matrix saved to {output_file}")

def get_related_content(report_slug: str, matrix_file: str = "related_matrix.json", 
                       reports_dir: str = "outputs/current_topics") -> Dict[str, RelatedPosts]:
    """
    Get content related to the specified report
    """
    # Define metrics (must match those used in generate_related_matrix)
    metrics = [
        Metric("titles", "Similar", 8.0, 1.0),
        Metric("tagCats", "Same Category", 10.0, 1.0),
        Metric("content", "Similar", 8.0, 0.91),
        Metric("recency", "New", 1.0, 0.3)
    ]
    
    # Load matrix from file
    if not os.path.exists(matrix_file):
        generate_related_matrix(reports_dir, matrix_file)
        
    with open(matrix_file, "r") as f:
        metric_data = json.load(f)
    
    # Get all reports
    reports = get_all_reports(reports_dir)
    
    # Find related reports
    return get_related_reports(report_slug, metric_data, metrics, reports)
```

## Integration with current_topics_generator.py

To integrate this functionality into your current_topics_generator.py, add these steps:

1. **After research but before report generation**:
   - Use the related content system to find similar existing reports
   - Analyze what information is already covered in previous reports
   - Highlight new information for inclusion in the latest report

2. **During report generation**:
   - Add a "Related Topics" section that links to previous reports on the same topic
   - Mark information as "New since [date]" or "Updated from previous report"

3. **Example integration**:

```python
async def generate_current_topics(query: str, total_words: int = 1000, language: str = "english") -> str:
    """Generate current topics report for a given query."""
    # Initialize GPTResearcher
    researcher = GPTResearcher(
        query=query,
        report_type=ReportType.CustomReport.value,
        report_format="default",
        report_source="web",
        config_path=None
    )
    
    # Conduct research
    await researcher.conduct_research()
    
    # Find related previous reports
    sanitized_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
    related_reports = get_related_content(sanitized_query)
    
    # Modify the custom prompt to include information about previous reports
    previous_reports_info = ""
    if related_reports and "final" in related_reports:
        # Get the top 3 most related reports
        top_related = related_reports["final"].slugs[:3]
        
        # Add information about what was already covered
        for slug in top_related:
            report_path = f"outputs/current_topics/{slug}.md"
            if os.path.exists(report_path):
                with open(report_path, "r") as f:
                    previous_content = f.read()
                previous_reports_info += f"\n\nPrevious report on {slug}:\n{previous_content[:500]}...\n"
    
    # Generate custom prompt with awareness of previous reports
    custom_prompt = generate_current_topics_report_prompt(
        question=query,
        context="",  # Will be filled by researcher
        report_source="web",
        report_format="default",
        total_words=total_words,
        language=language
    )
    
    if previous_reports_info:
        custom_prompt += f"\n\nIMPORTANT: Consider these previous reports when creating this update:\n{previous_reports_info}\n\nFocus on NEW information that wasn't covered in previous reports."
    
    # Generate report with the custom prompt
    report = await researcher.write_report(custom_prompt=custom_prompt)
    
    # After generating the report, update the related matrix
    generate_related_matrix()
    
    return report
```

## Configuration Options

Adjust these metrics to control how content is compared:

1. **Title Similarity** (8x weight): How similar the titles and descriptions are
2. **Category/Tag Similarity** (10x weight): How similar the topics and categories are
3. **Content Similarity** (8x weight): How similar the actual content is
4. **Recency** (1x weight): How recent the content is

The thresholds control the sensitivity of each metric. Higher thresholds mean fewer matches will be considered related.

## Performance Considerations

For large numbers of reports:

1. Use sparse matrices for efficiency
2. Cache similarity calculations
3. Consider dimensionality reduction techniques
4. Update the matrix incrementally instead of rebuilding it each time

## Learning Over Time

The system can be enhanced to:

1. Track which sources are frequently cited
2. Monitor how topics evolve over time
3. Identify emerging trends vs. established information
4. Create knowledge graphs of related topics

## Next Steps

1. Implement the basic functionality
2. Test with a small set of reports
3. Fine-tune the metrics and weights
4. Integrate with the current_topics_generator.py
5. Add visualization of related topics 