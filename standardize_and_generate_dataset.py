#!/usr/bin/env python3
"""
Standardize file naming and generate comprehensive JSONL datasets
for medical study assistant training.
"""

import os
import json
import re
from pathlib import Path
import PyPDF2
from typing import Dict, List, Tuple, Optional

class MedicalDatasetGenerator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.infectious_diseases_path = self.base_path / "infectious diseases - data"
        self.study_guides_path = self.base_path / "study_guides"
        self.data_path = self.base_path / "data"
        
        # Standardized topic mappings
        self.topic_mappings = {
            # Lecture files -> standardized names
            "L1-TB.pdf": "tuberculosis",
            "L2-Non-Tuberculous_Mycobacteria.pdf": "non_tuberculous_mycobacteria", 
            "L3-STDs.pdf": "sexually_transmitted_diseases",
            "brain_abscess.pdf": "brain_abscess",
            "CNS_infections.pdf": "cns_infections",
            "fungal_infections.pdf": "fungal_infections",
            "HIV.pdf": "hiv",
            "infective_endocarditis.pdf": "infective_endocarditis",
            "meningitis.pdf": "meningitis",
            "osteomyelitis.pdf": "osteomyelitis",
            "Tropical_Diseases.pdf": "tropical_diseases",
            
            # EMA summary files -> standardized names
            "TB.md": "tuberculosis",
            "Non-Tuberculous Mycobacteria (NTM).md": "non_tuberculous_mycobacteria",
            "STDs.md": "sexually_transmitted_diseases",
            "Brain abscess.md": "brain_abscess",
            "CNS infections.md": "cns_infections",
            "Fungal Infections.md": "fungal_infections",
            "HIV.md": "hiv",
            "Infective Endocarditis.md": "infective_endocarditis",
            "osteomyelitis.md": "osteomyelitis",
            "Tropical Diseases.md": "tropical_diseases",
        }
        
        # Create reverse mapping for standardized names to display names
        self.display_names = {
            "tuberculosis": "Tuberculosis (TB)",
            "non_tuberculous_mycobacteria": "Non-Tuberculous Mycobacteria (NTM)",
            "sexually_transmitted_diseases": "Sexually Transmitted Diseases (STDs)",
            "brain_abscess": "Brain Abscess",
            "cns_infections": "CNS Infections",
            "fungal_infections": "Fungal Infections",
            "hiv": "HIV",
            "infective_endocarditis": "Infective Endocarditis",
            "meningitis": "Meningitis",
            "osteomyelitis": "Osteomyelitis",
            "tropical_diseases": "Tropical Diseases",
        }

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return self.clean_text(text)
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing artifacts."""
        # Remove page numbers, headers, and other artifacts
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Page numbers
        text = re.sub(r'\n\s*Page \d+.*\n', '\n', text)  # Page headers
        text = re.sub(r'\n\s*\d+/\d+\s*\n', '\n', text)  # Page x/y
        text = re.sub(r'\n\s*\w+day,.*\d{4}\s*\n', '\n', text)  # Date headers
        text = re.sub(r'\n\s*\d{1,2}:\d{2}.*\n', '\n', text)  # Time stamps
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)  # Remove special chars
        return text.strip()

    def read_markdown_file(self, md_path: Path) -> str:
        """Read and return markdown file content."""
        try:
            with open(md_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
            return ""

    def generate_qa_pairs(self, topic: str, lecture_text: str, summary_text: str) -> List[Dict]:
        """Generate Q&A pairs from lecture and summary content."""
        qa_pairs = []
        display_name = self.display_names.get(topic, topic.replace('_', ' ').title())
        
        # Basic Q&A templates
        qa_templates = [
            {
                "question": f"What are the key clinical features of {display_name}?",
                "answer": f"Based on the lecture content, the key clinical features include: {self.extract_key_points(lecture_text, 'clinical features|symptoms|signs|presentation')}"
            },
            {
                "question": f"What is the recommended treatment approach for {display_name}?",
                "answer": f"The treatment approach involves: {self.extract_key_points(lecture_text, 'treatment|therapy|management|antibiotics|drugs')}"
            },
            {
                "question": f"How is {display_name} diagnosed?",
                "answer": f"Diagnosis is based on: {self.extract_key_points(lecture_text, 'diagnosis|diagnostic|testing|laboratory|imaging')}"
            },
            {
                "question": f"What are the risk factors for {display_name}?",
                "answer": f"Risk factors include: {self.extract_key_points(lecture_text, 'risk factors|predisposing|causes|etiology')}"
            },
        ]
        
        # Add summary-based Q&A
        if summary_text:
            qa_pairs.append({
                "question": f"Provide a concise summary of {display_name} for exam preparation.",
                "answer": summary_text
            })
        
        # Filter out empty answers
        qa_pairs = [qa for qa in qa_templates if qa["answer"] and len(qa["answer"]) > 50]
        
        return qa_pairs

    def extract_key_points(self, text: str, keywords: str) -> str:
        """Extract key points from text based on keywords."""
        if not text:
            return "Content not available from lecture transcript."
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Find sentences containing keywords
        keyword_pattern = re.compile(keywords, re.IGNORECASE)
        relevant_sentences = []
        
        for sentence in sentences:
            if keyword_pattern.search(sentence) and len(sentence.strip()) > 20:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Take top 3 most relevant sentences
            return ". ".join(relevant_sentences[:3]) + "."
        else:
            # Fallback: take first few sentences if no keyword matches
            return ". ".join([s.strip() for s in sentences[:2] if len(s.strip()) > 20]) + "."

    def generate_study_guide_entries(self, topic: str, summary_text: str) -> List[Dict]:
        """Generate study guide entries."""
        if not summary_text:
            return []
        
        display_name = self.display_names.get(topic, topic.replace('_', ' ').title())
        
        return [{
            "instruction": f"Create a comprehensive study guide for {display_name} optimized for medical exam preparation.",
            "input": f"Topic: {display_name}",
            "output": summary_text,
            "task_type": "study_guide_generation",
            "subject": "infectious_diseases",
            "topic": topic
        }]

    def process_all_files(self) -> Tuple[List[Dict], List[Dict]]:
        """Process all files and generate datasets."""
        qa_dataset = []
        study_guide_dataset = []
        
        # Get all unique topics
        topics = set(self.topic_mappings.values())
        
        for topic in topics:
            print(f"Processing topic: {topic}")
            
            # Find corresponding files
            lecture_file = None
            summary_file = None
            
            # Find lecture file
            lecture_dir = self.infectious_diseases_path / "lecture transcript - infectious diseases"
            for filename, mapped_topic in self.topic_mappings.items():
                if mapped_topic == topic and filename.endswith('.pdf'):
                    lecture_path = lecture_dir / filename
                    if lecture_path.exists():
                        lecture_file = lecture_path
                        break
            
            # Find summary file
            summary_dir = self.infectious_diseases_path / "ema summary - infectious diseases"
            for filename, mapped_topic in self.topic_mappings.items():
                if mapped_topic == topic and filename.endswith('.md'):
                    summary_path = summary_dir / filename
                    if summary_path.exists():
                        summary_file = summary_path
                        break
            
            # Process files
            lecture_text = ""
            summary_text = ""
            
            if lecture_file:
                print(f"  - Extracting lecture: {lecture_file.name}")
                lecture_text = self.extract_pdf_text(lecture_file)
            
            if summary_file:
                print(f"  - Reading summary: {summary_file.name}")
                summary_text = self.read_markdown_file(summary_file)
            
            # Generate datasets
            if lecture_text or summary_text:
                # Generate Q&A pairs
                qa_pairs = self.generate_qa_pairs(topic, lecture_text, summary_text)
                for qa in qa_pairs:
                    qa_dataset.append({
                        "instruction": qa["question"],
                        "input": "",
                        "output": qa["answer"],
                        "task_type": "question_answering",
                        "subject": "infectious_diseases",
                        "topic": topic
                    })
                
                # Generate study guide entries
                study_entries = self.generate_study_guide_entries(topic, summary_text)
                study_guide_dataset.extend(study_entries)
            
            print(f"  - Generated {len(qa_pairs)} Q&A pairs")
        
        return qa_dataset, study_guide_dataset

    def save_datasets(self, qa_dataset: List[Dict], study_guide_dataset: List[Dict]):
        """Save datasets to JSONL files."""
        # Ensure data directory exists
        self.data_path.mkdir(exist_ok=True)
        
        # Save Q&A dataset
        qa_file = self.data_path / "medical_qa_comprehensive.jsonl"
        with open(qa_file, 'w', encoding='utf-8') as f:
            for entry in qa_dataset:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # Save study guide dataset
        study_file = self.data_path / "study_summaries_comprehensive.jsonl"
        with open(study_file, 'w', encoding='utf-8') as f:
            for entry in study_guide_dataset:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"Saved {len(qa_dataset)} Q&A entries to {qa_file}")
        print(f"Saved {len(study_guide_dataset)} study guide entries to {study_file}")

    def generate_file_mapping_report(self):
        """Generate a report of file mappings and missing files."""
        print("\n=== FILE MAPPING REPORT ===")
        
        topics = set(self.topic_mappings.values())
        
        for topic in sorted(topics):
            print(f"\nTopic: {topic} ({self.display_names.get(topic, topic)})")
            
            # Check for lecture file
            lecture_found = False
            lecture_dir = self.infectious_diseases_path / "lecture transcript - infectious diseases"
            for filename, mapped_topic in self.topic_mappings.items():
                if mapped_topic == topic and filename.endswith('.pdf'):
                    lecture_path = lecture_dir / filename
                    if lecture_path.exists():
                        print(f"  ✓ Lecture: {filename}")
                        lecture_found = True
                        break
            
            if not lecture_found:
                print(f"  ✗ Lecture: MISSING")
            
            # Check for summary file
            summary_found = False
            summary_dir = self.infectious_diseases_path / "ema summary - infectious diseases"
            for filename, mapped_topic in self.topic_mappings.items():
                if mapped_topic == topic and filename.endswith('.md'):
                    summary_path = summary_dir / filename
                    if summary_path.exists():
                        print(f"  ✓ Summary: {filename}")
                        summary_found = True
                        break
            
            if not summary_found:
                print(f"  ✗ Summary: MISSING")

def main():
    # Initialize generator
    base_path = "/Users/emmanu3l/Documents/my apps/mymedassist1"
    generator = MedicalDatasetGenerator(base_path)
    
    # Generate file mapping report
    generator.generate_file_mapping_report()
    
    # Process all files and generate datasets
    print("\n=== PROCESSING FILES ===")
    qa_dataset, study_guide_dataset = generator.process_all_files()
    
    # Save datasets
    print("\n=== SAVING DATASETS ===")
    generator.save_datasets(qa_dataset, study_guide_dataset)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total Q&A pairs generated: {len(qa_dataset)}")
    print(f"Total study guide entries generated: {len(study_guide_dataset)}")
    print(f"Total training examples: {len(qa_dataset) + len(study_guide_dataset)}")

if __name__ == "__main__":
    main()
