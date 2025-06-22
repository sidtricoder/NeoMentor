#!/usr/bin/env python3
"""
Test script for the SyllabusFormatterAgent
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.core.academic_agents import SyllabusFormatterAgent, AcademicContext
    print("✓ Successfully imported SyllabusFormatterAgent")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

async def test_formatter():
    """Test the formatter agent with mock data"""
    print("\n🧪 Testing SyllabusFormatterAgent...")
    
    # Create formatter agent
    formatter = SyllabusFormatterAgent()
    
    # Create mock raw response (simulating inconsistent Gemini output)
    raw_response = {
        "course_content": {
            "description": "A comprehensive course on machine learning",
            "topics": ["Linear Regression", "Neural Networks", "Deep Learning"]
        },
        "weeks": {
            "week1": {
                "content": "Introduction to ML",
                "activities": ["Lecture", "Lab"]
            },
            "week2": {
                "content": "Supervised Learning",
                "activities": ["Workshop", "Assignment"]
            }
        },
        "evaluation": {
            "tests": ["Midterm", "Final"],
            "projects": ["ML Project"]
        }
    }
    
    # Create context
    context = AcademicContext(
        user_id="test_user",
        session_id="test_session",
        request_type="generate_syllabus",
        data={
            "course_info": {
                "name": "Machine Learning Fundamentals",
                "code": "CS 401",
                "description": "Introduction to machine learning concepts and applications",
                "credits": 3,
                "instructor": "Dr. Jane Smith"
            },
            "learning_objectives": [
                "Understand core ML algorithms",
                "Apply ML to real-world problems",
                "Implement basic neural networks"
            ],
            "student_level": "undergraduate",
            "duration_weeks": 16
        }
    )
    
    print("📝 Input raw response:")
    print(json.dumps(raw_response, indent=2))
    
    # Test formatting
    try:
        formatted_context = await formatter.format_syllabus_response(raw_response, context)
        
        if formatted_context.result:
            print("\n✅ Formatting successful!")
            print("\n📋 Formatted output structure:")
            
            result = formatted_context.result
            
            # Check top-level structure
            if 'syllabus' in result:
                print("  ✓ Contains 'syllabus' key")
                syllabus = result['syllabus']
                
                required_sections = [
                    'course_overview', 'structure', 'methodology', 
                    'policies', 'support', 'weekly_schedule', 
                    'assessments', 'resources'
                ]
                
                for section in required_sections:
                    if section in syllabus:
                        print(f"  ✓ Contains '{section}' section")
                    else:
                        print(f"  ✗ Missing '{section}' section")
                
                # Check weekly schedule structure
                if 'weekly_schedule' in syllabus:
                    weekly_schedule = syllabus['weekly_schedule']
                    if weekly_schedule and isinstance(weekly_schedule, dict):
                        schedule_key = list(weekly_schedule.keys())[0] if weekly_schedule else None
                        if schedule_key and isinstance(weekly_schedule[schedule_key], dict):
                            week_data = weekly_schedule[schedule_key]
                            sample_week = list(week_data.keys())[0] if week_data else None
                            if sample_week:
                                week_info = week_data[sample_week]
                                required_week_fields = ['topics', 'learning_activities', 'readings_resources', 'assessments_milestones', 'progressive_skill_building']
                                print(f"  📅 Sample week ({sample_week}) structure:")
                                for field in required_week_fields:
                                    if field in week_info:
                                        print(f"    ✓ Contains '{field}'")
                                    else:
                                        print(f"    ✗ Missing '{field}'")
            
            # Check metadata
            if 'customization_level' in result:
                print(f"  ✓ Customization level: {result['customization_level']}")
            
            if 'adaptation_score' in result:
                print(f"  ✓ Adaptation score: {result['adaptation_score']}")
            
            # Save formatted output for inspection
            output_file = "/home/siddharth/Desktop/NeoMentor/Final/test_formatted_output.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Full formatted output saved to: {output_file}")
            
        else:
            print("\n❌ Formatting failed - no result returned")
            
    except Exception as e:
        print(f"\n❌ Error during formatting: {e}")
        import traceback
        traceback.print_exc()

def test_imports():
    """Test that all necessary imports work"""
    print("🔍 Testing imports...")
    
    try:
        import json
        print("  ✓ json")
    except ImportError:
        print("  ✗ json")
    
    try:
        import asyncio
        print("  ✓ asyncio")
    except ImportError:
        print("  ✗ asyncio")
    
    try:
        from datetime import datetime
        print("  ✓ datetime")
    except ImportError:
        print("  ✗ datetime")

if __name__ == "__main__":
    print("🚀 Starting SyllabusFormatterAgent Test")
    print("=" * 50)
    
    test_imports()
    
    try:
        asyncio.run(test_formatter())
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed")
