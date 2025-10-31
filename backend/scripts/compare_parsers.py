"""
Parser comparison tool to evaluate different resume parsing approaches.
Compares Parser A (main/NLP-based) vs Parser B (regex-based).
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.resumeparser import ResumeParser
from app.services.simple_parser import SimpleParser


class ParserComparison:
    """Compare two resume parser implementations."""
    
    def __init__(self):
        self.parser_a = ResumeParser()
        self.parser_b = SimpleParser()
        self.results = []
    
    def compare_resume(self, file_path: str) -> Dict[str, Any]:
        """Compare parsing results for a single resume."""
        print(f"\n📊 Comparing: {Path(file_path).name}")
        print("-" * 70)
        
        file_type = 'application/pdf' if file_path.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        result = {
            "file": Path(file_path).name,
            "parser_a": self._parse_with_timer(file_path, file_type, "A"),
            "parser_b": self._parse_with_timer(file_path, file_type, "B")
        }
        
        self._print_comparison(result)
        return result
    
    def _parse_with_timer(self, file_path: str, file_type: str, parser_name: str) -> Dict[str, Any]:
        """Parse resume and measure time."""
        try:
            start = time.time()
            
            if parser_name == "A":
                parsed_data = self.parser_a.parse_resume(file_path, file_type)
            else:
                parsed_data = self.parser_b.parse_resume(file_path, file_type)
            
            elapsed = (time.time() - start) * 1000
            
            return {
                "status": "success",
                "data": parsed_data,
                "time_ms": elapsed,
                "metrics": self._calculate_metrics(parsed_data)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "time_ms": 0,
                "metrics": {}
            }
    
    def _calculate_metrics(self, parsed_data: Dict) -> Dict[str, Any]:
        """Calculate metrics from parsed data."""
        return {
            "skills_count": len(parsed_data.get("skills", [])),
            "experience_years": parsed_data.get("experience_years", 0),
            "experience_entries": len(parsed_data.get("experience", [])),
            "education_entries": len(parsed_data.get("education", [])),
            "has_email": bool(parsed_data.get("personal_info", {}).get("email")),
            "has_phone": bool(parsed_data.get("personal_info", {}).get("phone")),
        }
    
    def _print_comparison(self, result: Dict):
        """Print side-by-side comparison."""
        parser_a = result["parser_a"]
        parser_b = result["parser_b"]
        
        print(f"\n✓ Parser A (NLP-based)")
        if parser_a["status"] == "success":
            m = parser_a["metrics"]
            print(f"  Skills:      {m['skills_count']}")
            print(f"  Experience:  {m['experience_years']} years")
            print(f"  Time:        {parser_a['time_ms']:.2f}ms")
        else:
            print(f"  ✗ Error: {parser_a['error']}")
        
        print(f"\n✓ Parser B (Regex-based)")
        if parser_b["status"] == "success":
            m = parser_b["metrics"]
            print(f"  Skills:      {m['skills_count']}")
            print(f"  Experience:  {m['experience_years']} years")
            print(f"  Time:        {parser_b['time_ms']:.2f}ms")
        else:
            print(f"  ✗ Error: {parser_b['error']}")
        
        if parser_a["status"] == "success" and parser_b["status"] == "success":
            time_diff = parser_a["time_ms"] - parser_b["time_ms"]
            if time_diff < 0:
                print(f"\n⚡ Parser A is {abs(time_diff):.2f}ms faster")
            else:
                print(f"\n⚡ Parser B is {time_diff:.2f}ms faster")
    
    def compare_all(self, test_dir: str = "tests/test_data") -> List[Dict]:
        """Compare all test resumes in directory."""
        test_path = Path(test_dir)
        
        if not test_path.exists():
            print(f"❌ Test directory not found: {test_dir}")
            return []
        
        resume_files = list(test_path.glob("*.pdf")) + list(test_path.glob("*.docx"))
        
        if not resume_files:
            print(f"❌ No test resumes found in {test_dir}")
            return []
        
        print(f"\n🚀 Resume Parser Comparison Tool")
        print("=" * 70)
        print(f"Comparing: Parser A (NLP) vs Parser B (Regex)")
        print(f"\n📄 Found {len(resume_files)} test resumes\n")
        
        results = []
        for resume_file in resume_files:
            result = self.compare_resume(str(resume_file))
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = "comparison.json"):
        """Generate comparison report."""
        report = {
            "total_resumes": len(results),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
            "summary": self._generate_summary(results)
        }
        
        # Create directory
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {output_file}")
        self._print_summary(report["summary"])
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics."""
        parser_a_success = sum(1 for r in results if r["parser_a"]["status"] == "success")
        parser_b_success = sum(1 for r in results if r["parser_b"]["status"] == "success")
        
        a_times = [r["parser_a"]["time_ms"] for r in results if r["parser_a"]["status"] == "success"]
        b_times = [r["parser_b"]["time_ms"] for r in results if r["parser_b"]["status"] == "success"]
        
        a_skills = [r["parser_a"]["metrics"]["skills_count"] for r in results if r["parser_a"]["status"] == "success"]
        b_skills = [r["parser_b"]["metrics"]["skills_count"] for r in results if r["parser_b"]["status"] == "success"]
        
        return {
            "parser_a": {
                "name": "Parser A (NLP-based)",
                "success": parser_a_success,
                "errors": len(results) - parser_a_success,
                "avg_time_ms": sum(a_times) / len(a_times) if a_times else 0,
                "avg_skills": sum(a_skills) / len(a_skills) if a_skills else 0
            },
            "parser_b": {
                "name": "Parser B (Regex-based)",
                "success": parser_b_success,
                "errors": len(results) - parser_b_success,
                "avg_time_ms": sum(b_times) / len(b_times) if b_times else 0,
                "avg_skills": sum(b_skills) / len(b_skills) if b_skills else 0
            }
        }
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print summary."""
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        for key in ["parser_a", "parser_b"]:
            p = summary[key]
            print(f"\n{p['name']}:")
            print(f"  ✓ Success:     {p['success']}")
            print(f"  ✗ Errors:      {p['errors']}")
            print(f"  ⏱ Avg Time:    {p['avg_time_ms']:.2f}ms")
            print(f"  🔧 Avg Skills: {p['avg_skills']:.1f}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare resume parsers")
    parser.add_argument("--resume", help="Single resume to compare")
    parser.add_argument("--compare-all", action="store_true", help="Compare all test resumes")
    parser.add_argument("--output", default="comparison.json", help="Output file")
    
    args = parser.parse_args()
    
    comparator = ParserComparison()
    
    if args.resume:
        if not os.path.exists(args.resume):
            print(f"❌ File not found: {args.resume}")
            return 1
        result = comparator.compare_resume(args.resume)
        comparator.generate_report([result], args.output)
    elif args.compare_all:
        results = comparator.compare_all()
        if results:
            comparator.generate_report(results, args.output)
        else:
            return 1
    else:
        parser.print_help()
        return 1
    
    print("\n✅ Done!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
