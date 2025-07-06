#!/usr/bin/env python3
"""
Dataset Quality Validator and Enhancement Suggestions
for Medical Study Assistant Training Data
"""

import json
import re
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class DatasetQualityValidator:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.data = self.load_data()
        
    def load_data(self):
        """Load the comprehensive dataset."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
    
    def validate_completeness(self):
        """Check for missing or incomplete data."""
        issues = []
        
        for i, entry in enumerate(self.data):
            # Check required fields
            required_fields = ['instruction', 'output', 'task_type', 'subject', 'topic']
            missing_fields = [field for field in required_fields if not entry.get(field)]
            
            if missing_fields:
                issues.append(f"Entry {i}: Missing fields: {missing_fields}")
            
            # Check for very short responses
            if len(entry.get('output', '')) < 100:
                issues.append(f"Entry {i}: Very short response ({len(entry.get('output', ''))} chars)")
            
            # Check for non-medical content
            output_text = entry.get('output', '').lower()
            medical_keywords = [
                'diagnosis', 'treatment', 'symptoms', 'disease', 'infection',
                'therapy', 'clinical', 'patient', 'medical', 'pathology',
                'etiology', 'prognosis', 'antibiotic', 'medication'
            ]
            
            if not any(keyword in output_text for keyword in medical_keywords):
                issues.append(f"Entry {i}: Potentially non-medical content")
        
        return issues
    
    def analyze_diversity(self):
        """Analyze dataset diversity and balance."""
        
        # Task type distribution
        task_types = [entry['task_type'] for entry in self.data]
        task_distribution = Counter(task_types)
        
        # Topic distribution
        topics = [entry['topic'] for entry in self.data]
        topic_distribution = Counter(topics)
        
        # Text length distribution
        text_lengths = [len(entry['output']) for entry in self.data]
        
        # Response type analysis
        response_types = []
        for entry in self.data:
            output = entry['output'].lower()
            if 'list' in output or '•' in output or '-' in output:
                response_types.append('list')
            elif len(output.split('.')) > 5:
                response_types.append('detailed')
            else:
                response_types.append('brief')
        
        response_type_distribution = Counter(response_types)
        
        return {
            'task_distribution': task_distribution,
            'topic_distribution': topic_distribution,
            'text_lengths': text_lengths,
            'response_types': response_type_distribution
        }
    
    def assess_quality_metrics(self):
        """Assess various quality metrics."""
        
        quality_scores = []
        
        for entry in self.data:
            score = 0
            output = entry['output']
            
            # Length score (optimal range: 200-2000 chars)
            length = len(output)
            if 200 <= length <= 2000:
                score += 1
            elif 100 <= length < 200 or 2000 < length <= 3000:
                score += 0.5
            
            # Medical terminology score
            medical_terms = [
                'diagnosis', 'treatment', 'symptoms', 'pathogenesis',
                'etiology', 'prognosis', 'therapy', 'clinical',
                'pathology', 'epidemiology', 'prevention'
            ]
            
            medical_term_count = sum(1 for term in medical_terms if term in output.lower())
            if medical_term_count >= 3:
                score += 1
            elif medical_term_count >= 1:
                score += 0.5
            
            # Structure score (presence of clear organization)
            structure_indicators = [':', '-', '•', '1.', '2.', '3.']
            if any(indicator in output for indicator in structure_indicators):
                score += 1
            
            # Specificity score (presence of specific medical details)
            specific_terms = [
                'mg', 'ml', 'days', 'weeks', 'months', 'years',
                'acute', 'chronic', 'severe', 'mild', 'moderate'
            ]
            
            if any(term in output.lower() for term in specific_terms):
                score += 1
            
            quality_scores.append(score / 4)  # Normalize to 0-1
        
        return quality_scores
    
    def generate_enhancement_suggestions(self):
        """Generate suggestions for dataset enhancement."""
        
        diversity_analysis = self.analyze_diversity()
        quality_scores = self.assess_quality_metrics()
        
        suggestions = []
        
        # Balance suggestions
        task_counts = diversity_analysis['task_distribution']
        if len(task_counts) > 1:
            min_count = min(task_counts.values())
            max_count = max(task_counts.values())
            
            if max_count > min_count * 2:
                suggestions.append(
                    f"⚖️ Balance task types: {dict(task_counts)}"
                )
        
        # Topic balance
        topic_counts = diversity_analysis['topic_distribution']
        topic_std = np.std(list(topic_counts.values()))
        
        if topic_std > 2:
            suggestions.append(
                f"📚 Balance topics: Add more examples for under-represented topics"
            )
        
        # Length optimization
        lengths = diversity_analysis['text_lengths']
        very_short = sum(1 for l in lengths if l < 100)
        very_long = sum(1 for l in lengths if l > 3000)
        
        if very_short > len(lengths) * 0.1:
            suggestions.append(
                f"📏 Expand {very_short} short responses (< 100 chars)"
            )
        
        if very_long > len(lengths) * 0.1:
            suggestions.append(
                f"✂️ Shorten {very_long} long responses (> 3000 chars)"
            )
        
        # Quality improvements
        avg_quality = np.mean(quality_scores)
        low_quality_count = sum(1 for score in quality_scores if score < 0.5)
        
        if avg_quality < 0.7:
            suggestions.append(
                f"🔧 Improve overall quality: {low_quality_count} entries need enhancement"
            )
        
        # Diversity suggestions
        response_types = diversity_analysis['response_types']
        if len(response_types) < 3:
            suggestions.append(
                f"🎭 Add response variety: Include lists, detailed explanations, and brief answers"
            )
        
        # Medical domain enhancement
        suggestions.extend([
            f"🏥 Add more differential diagnosis examples",
            f"💊 Include more treatment protocols and drug information",
            f"🔬 Add laboratory and imaging interpretation examples",
            f"📊 Include epidemiological data and statistics",
            f"🧬 Add pathophysiology explanations",
            f"📈 Include case-based scenarios",
            f"🎯 Add board exam-style questions",
            f"📚 Include medical abbreviations and terminology",
            f"🔍 Add clinical reasoning examples",
            f"⚠️ Include contraindications and adverse effects"
        ])
        
        return suggestions
    
    def create_quality_report(self):
        """Create a comprehensive quality report."""
        
        completeness_issues = self.validate_completeness()
        diversity_analysis = self.analyze_diversity()
        quality_scores = self.assess_quality_metrics()
        suggestions = self.generate_enhancement_suggestions()
        
        report = f"""
# Medical Study Assistant Dataset Quality Report

## 📊 Dataset Overview
- **Total entries**: {len(self.data)}
- **Average quality score**: {np.mean(quality_scores):.2f} / 1.0
- **Completeness issues**: {len(completeness_issues)}

## 🎯 Task Distribution
"""
        
        for task_type, count in diversity_analysis['task_distribution'].items():
            percentage = (count / len(self.data)) * 100
            report += f"- {task_type}: {count} entries ({percentage:.1f}%)\n"
        
        report += f"""
## 📚 Topic Distribution
"""
        
        for topic, count in diversity_analysis['topic_distribution'].most_common():
            percentage = (count / len(self.data)) * 100
            report += f"- {topic.replace('_', ' ').title()}: {count} entries ({percentage:.1f}%)\n"
        
        report += f"""
## 📏 Text Length Statistics
- **Average length**: {np.mean(diversity_analysis['text_lengths']):.0f} characters
- **Median length**: {np.median(diversity_analysis['text_lengths']):.0f} characters
- **Min length**: {min(diversity_analysis['text_lengths'])} characters
- **Max length**: {max(diversity_analysis['text_lengths'])} characters

## 🔍 Quality Issues Found
"""
        
        if completeness_issues:
            report += f"### Completeness Issues ({len(completeness_issues)} total)\n"
            for issue in completeness_issues[:10]:  # Show first 10
                report += f"- {issue}\n"
            if len(completeness_issues) > 10:
                report += f"- ... and {len(completeness_issues) - 10} more issues\n"
        else:
            report += "✅ No major completeness issues found!\n"
        
        report += f"""
## 🚀 Enhancement Suggestions

### Priority Improvements
"""
        
        for suggestion in suggestions[:5]:  # Top 5 suggestions
            report += f"- {suggestion}\n"
        
        report += f"""
### Additional Enhancements
"""
        
        for suggestion in suggestions[5:]:
            report += f"- {suggestion}\n"
        
        report += f"""
## 📈 Recommended Next Steps

1. **Immediate Actions**:
   - Fix completeness issues identified above
   - Balance task types and topics
   - Expand very short responses
   - Add more medical terminology

2. **Medium-term Improvements**:
   - Add 100-200 more training examples
   - Include more diverse medical scenarios
   - Add clinical case studies
   - Include board exam-style questions

3. **Long-term Enhancements**:
   - Add multi-modal content (images + text)
   - Include recent medical literature
   - Add specialist-specific content
   - Create evaluation benchmarks

## 🎯 Target Metrics
- **Minimum dataset size**: 200-500 examples
- **Quality score target**: >0.8
- **Topic balance**: <2 std dev in topic distribution
- **Response diversity**: Include lists, detailed explanations, brief answers
- **Medical accuracy**: Expert validation recommended

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def visualize_quality_metrics(self):
        """Create visualizations for quality metrics."""
        
        diversity_analysis = self.analyze_diversity()
        quality_scores = self.assess_quality_metrics()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dataset Quality Analysis', fontsize=16)
        
        # Task distribution
        task_data = diversity_analysis['task_distribution']
        axes[0, 0].bar(task_data.keys(), task_data.values())
        axes[0, 0].set_title('Task Type Distribution')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Text length distribution
        axes[0, 1].hist(diversity_analysis['text_lengths'], bins=20, alpha=0.7)
        axes[0, 1].set_title('Text Length Distribution')
        axes[0, 1].set_xlabel('Characters')
        axes[0, 1].set_ylabel('Frequency')
        
        # Quality scores
        axes[1, 0].hist(quality_scores, bins=10, alpha=0.7, color='green')
        axes[1, 0].set_title('Quality Score Distribution')
        axes[1, 0].set_xlabel('Quality Score (0-1)')
        axes[1, 0].set_ylabel('Count')
        
        # Topic distribution
        topic_data = diversity_analysis['topic_distribution']
        topic_names = [name.replace('_', ' ').title() for name in topic_data.keys()]
        axes[1, 1].barh(topic_names, list(topic_data.values()))
        axes[1, 1].set_title('Topic Distribution')
        axes[1, 1].set_xlabel('Count')
        
        plt.tight_layout()
        plt.savefig(self.data_path.parent / 'quality_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig

def main():
    """Main function to run quality validation."""
    
    # Path to your dataset
    data_path = Path("/Users/emmanu3l/Documents/my apps/mymedassist1/data/medical_dataset_kaggle.jsonl")
    
    if not data_path.exists():
        print(f"❌ Dataset not found at {data_path}")
        return
    
    # Initialize validator
    validator = DatasetQualityValidator(data_path)
    
    # Generate quality report
    print("📊 Generating quality report...")
    report = validator.create_quality_report()
    
    # Save report
    report_path = data_path.parent / 'quality_report.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"✅ Quality report saved to {report_path}")
    
    # Create visualizations
    print("📈 Creating quality visualizations...")
    try:
        validator.visualize_quality_metrics()
        print("✅ Quality visualizations created")
    except Exception as e:
        print(f"⚠️ Could not create visualizations: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("DATASET QUALITY SUMMARY")
    print("="*60)
    print(f"📊 Total entries: {len(validator.data)}")
    print(f"🎯 Average quality: {np.mean(validator.assess_quality_metrics()):.2f}/1.0")
    print(f"⚠️ Issues found: {len(validator.validate_completeness())}")
    print(f"📋 Enhancement suggestions: {len(validator.generate_enhancement_suggestions())}")
    print(f"📄 Full report: {report_path}")
    print("="*60)

if __name__ == "__main__":
    main()
