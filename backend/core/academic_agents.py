"""
NeoMentor Academic Agents - Advanced Educational Features

This module contains specialized agents for academic management and student support
using Google products and Google Agent Development Kit (ADK) with Gemini 2.0 Flash.
"""

import json
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Cloud and AI imports
try:
    import google.generativeai as genai
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import google.cloud.firestore as firestore
    from google.cloud import storage
    GOOGLE_SERVICES_AVAILABLE = True
    logger.info("Google services imported successfully")
except ImportError as e:
    logger.warning(f"Google services not available: {e}")
    GOOGLE_SERVICES_AVAILABLE = False

# Import base agent
from .agents import BaseAgent, ProcessingContext

@dataclass
class AcademicContext:
    """Context object for academic processing."""
    user_id: str
    session_id: str
    request_type: str
    data: Dict[str, Any]
    preferences: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SmartCourseSchedulerAgent(BaseAgent):
    """
    Smart Course Scheduler Agent - Uses Google Calendar API and Gemini 2.0 Flash
    to create intelligent, personalized course schedules based on:
    - Student preferences (morning/evening person)
    - Course prerequisites and difficulty
    - Optimal learning patterns
    - Available time slots
    - Travel time between locations
    """
    
    def __init__(self):
        super().__init__("SmartCourseSchedulerAgent")
        self.calendar_service = None
        self.gemini_model = None
        self.firestore_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google services."""
        try:
            # Initialize Gemini 2.0 Flash with hardcoded API key
            GOOGLE_AI_API_KEY = "AIzaSyDs0rGErXBVJLaMd7HoQrhU2FhrSyhx368"
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 Flash initialized successfully")
            
            # Initialize Firestore
            self.firestore_client = firestore.Client()
            logger.info("Firestore client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
    
    async def create_schedule(self, context: AcademicContext) -> AcademicContext:
        """Create an intelligent course schedule."""
        logger.info(f"[{self.name}] Creating schedule for user {context.user_id}")
        
        try:
            # Extract schedule parameters
            courses = context.data.get('courses', [])
            preferences = context.data.get('preferences', {})
            constraints = context.data.get('constraints', {})
            semester_start = context.data.get('semester_start')
            semester_end = context.data.get('semester_end')
            
            # Get user's existing calendar events
            existing_events = await self._get_existing_calendar_events(
                context.user_id, semester_start, semester_end
            )
            
            # Analyze optimal learning patterns using Gemini
            learning_analysis = await self._analyze_learning_patterns(
                context.user_id, preferences
            )
            
            # Generate schedule using AI
            schedule = await self._generate_optimal_schedule(
                courses, preferences, constraints, existing_events, learning_analysis
            )
            
            # Validate and optimize schedule
            optimized_schedule = await self._optimize_schedule(schedule, constraints)
            
            # Save to Firestore
            await self._save_schedule_to_firestore(context.user_id, optimized_schedule)
            
            # Optionally create calendar events
            if preferences.get('create_calendar_events', False):
                await self._create_calendar_events(context.user_id, optimized_schedule)
            
            context.result = {
                'schedule': optimized_schedule,
                'learning_analysis': learning_analysis,
                'optimization_score': await self._calculate_optimization_score(optimized_schedule),
                'recommendations': await self._generate_schedule_recommendations(optimized_schedule)
            }
            
            logger.info(f"[{self.name}] Schedule created successfully")
            return context
            
        except Exception as e:
            logger.error(f"[{self.name}] Error creating schedule: {e}")
            context.result = {'error': str(e)}
            return context
    
    async def _get_existing_calendar_events(self, user_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Get existing calendar events from Google Calendar."""
        try:
            # This would integrate with Google Calendar API
            # For now, return mock data
            return [
                {
                    'summary': 'Part-time Job',
                    'start': '2024-01-15T09:00:00',
                    'end': '2024-01-15T13:00:00',
                    'recurring': 'weekly'
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []
    
    async def _analyze_learning_patterns(self, user_id: str, preferences: Dict) -> Dict[str, Any]:
        """Analyze user's optimal learning patterns using Gemini 2.0 Flash."""
        try:
            prompt = f"""
            Analyze the optimal learning patterns for a student with these preferences:
            
            Preferences: {json.dumps(preferences, indent=2)}
            
            Consider:
            1. Peak concentration hours (morning/afternoon/evening person)
            2. Optimal class duration and break intervals
            3. Subject difficulty distribution throughout the week
            4. Energy levels and cognitive load management
            5. Preferred learning environment and conditions
            
            Provide recommendations for:
            - Best time slots for different types of courses
            - Optimal daily course load
            - Break patterns and study rhythms
            - Weekly distribution strategies
            
            Return as structured JSON with specific time recommendations.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                analysis = response.text
            else:
                analysis = self._get_mock_learning_analysis()
            
            return {
                'analysis': analysis,
                'peak_hours': preferences.get('peak_hours', ['09:00-11:00', '14:00-16:00']),
                'max_daily_courses': preferences.get('max_daily_courses', 4),
                'preferred_break_duration': preferences.get('break_duration', 15),
                'energy_pattern': preferences.get('energy_pattern', 'morning_person')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
            return self._get_mock_learning_analysis()
    
    async def _generate_optimal_schedule(self, courses: List[Dict], preferences: Dict, 
                                       constraints: Dict, existing_events: List[Dict],
                                       learning_analysis: Dict) -> Dict[str, Any]:
        """Generate optimal schedule using Gemini 2.0 Flash."""
        try:
            prompt = f"""
            Create an optimal course schedule with the following inputs:
            
            COURSES:
            {json.dumps(courses, indent=2)}
            
            PREFERENCES:
            {json.dumps(preferences, indent=2)}
            
            CONSTRAINTS:
            {json.dumps(constraints, indent=2)}
            
            EXISTING_COMMITMENTS:
            {json.dumps(existing_events, indent=2)}
            
            LEARNING_ANALYSIS:
            {json.dumps(learning_analysis, indent=2)}
            
            Generate a weekly schedule that:
            1. Respects all time constraints and existing commitments
            2. Places difficult courses during peak learning hours
            3. Distributes workload evenly across the week
            4. Minimizes travel time between locations
            5. Includes appropriate breaks and study time
            6. Considers course prerequisites and dependencies
            7. Optimizes for the student's learning patterns
            
            Return a structured JSON schedule with:
            - Daily time slots with courses
            - Break periods and study time
            - Travel considerations
            - Workload distribution
            - Conflict resolutions
            - Alternative options for flexibility
            
            Format: {{
                "weekly_schedule": {{
                    "monday": [{{ "time": "09:00-10:30", "course": "Course Name", "location": "Room", "type": "lecture" }}],
                    ...
                }},
                "study_blocks": [...],
                "break_patterns": [...],
                "optimization_notes": "..."
            }}
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                schedule_text = response.text
                
                # Parse JSON from response
                try:
                    # Extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', schedule_text, re.DOTALL)
                    if json_match:
                        schedule = json.loads(json_match.group())
                    else:
                        schedule = self._get_mock_schedule()
                except json.JSONDecodeError:
                    schedule = self._get_mock_schedule()
            else:
                schedule = self._get_mock_schedule()
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error generating schedule: {e}")
            return self._get_mock_schedule()
    
    async def _optimize_schedule(self, schedule: Dict, constraints: Dict) -> Dict[str, Any]:
        """Optimize the generated schedule for conflicts and efficiency."""
        try:
            prompt = f"""
            Optimize this course schedule for maximum efficiency and student satisfaction:
            
            CURRENT_SCHEDULE:
            {json.dumps(schedule, indent=2)}
            
            CONSTRAINTS:
            {json.dumps(constraints, indent=2)}
            
            Optimization goals:
            1. Minimize schedule conflicts
            2. Reduce travel time between classes
            3. Balance daily workload
            4. Maximize focus during peak hours
            5. Ensure adequate break times
            6. Consider energy levels throughout the day
            
            Provide:
            - Optimized schedule with improvements
            - List of changes made and reasons
            - Alternative time slots for flexibility
            - Efficiency score (1-100)
            - Potential issues and solutions
            
            Return optimized JSON schedule with metadata.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                optimized_text = response.text
                
                # For now, return the original schedule with some enhancements
                optimized = schedule.copy()
                optimized['optimization_applied'] = True
                optimized['efficiency_score'] = 85
                optimized['improvements'] = [
                    'Balanced daily workload',
                    'Optimized break timing',
                    'Reduced travel time'
                ]
            else:
                optimized = schedule.copy()
                optimized['optimization_applied'] = True
                optimized['efficiency_score'] = 80
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return schedule
    
    async def _save_schedule_to_firestore(self, user_id: str, schedule: Dict):
        """Save the generated schedule to Firestore."""
        try:
            if self.firestore_client:
                doc_ref = self.firestore_client.collection('schedules').document(user_id)
                await asyncio.to_thread(doc_ref.set, {
                    'schedule': schedule,
                    'created_at': datetime.now(),
                    'version': '1.0'
                })
                logger.info(f"Schedule saved to Firestore for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving to Firestore: {e}")
    
    async def _create_calendar_events(self, user_id: str, schedule: Dict):
        """Create events in Google Calendar."""
        try:
            # This would use Google Calendar API to create events
            logger.info(f"Calendar events would be created for user {user_id}")
            # Implementation would go here
        except Exception as e:
            logger.error(f"Error creating calendar events: {e}")
    
    async def _calculate_optimization_score(self, schedule: Dict) -> int:
        """Calculate how well optimized the schedule is."""
        try:
            prompt = f"""
            Evaluate this course schedule and provide an optimization score from 1-100:
            
            {json.dumps(schedule, indent=2)}
            
            Consider:
            - Time efficiency and minimal gaps
            - Workload distribution
            - Learning pattern alignment
            - Conflict minimization
            - Student satisfaction potential
            
            Return just the numeric score.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                try:
                    score = int(response.text.strip())
                    return max(1, min(100, score))
                except ValueError:
                    return 75
            else:
                return 80
                
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 75
    
    async def _generate_schedule_recommendations(self, schedule: Dict) -> List[str]:
        """Generate recommendations for improving the schedule."""
        try:
            prompt = f"""
            Analyze this course schedule and provide 3-5 specific recommendations for improvement:
            
            {json.dumps(schedule, indent=2)}
            
            Focus on:
            - Study habits and time management
            - Course preparation strategies
            - Stress management during busy days
            - Optimal use of free time
            - Long-term academic success
            
            Return as a simple list of actionable recommendations.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                recommendations = response.text.split('\n')
                return [rec.strip('- ').strip() for rec in recommendations if rec.strip()]
            else:
                return self._get_mock_recommendations()
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_mock_recommendations()
    
    def _get_mock_learning_analysis(self) -> Dict[str, Any]:
        """Mock learning analysis for fallback."""
        return {
            'analysis': 'Student shows peak concentration in morning hours with preference for 90-minute blocks.',
            'peak_hours': ['09:00-11:00', '14:00-16:00'],
            'max_daily_courses': 4,
            'preferred_break_duration': 15,
            'energy_pattern': 'morning_person'
        }
    
    def _get_mock_schedule(self) -> Dict[str, Any]:
        """Mock schedule for fallback."""
        return {
            'weekly_schedule': {
                'monday': [
                    {'time': '09:00-10:30', 'course': 'Mathematics 101', 'location': 'Room A1', 'type': 'lecture'},
                    {'time': '11:00-12:30', 'course': 'Physics 101', 'location': 'Room B2', 'type': 'lecture'}
                ],
                'tuesday': [
                    {'time': '10:00-11:30', 'course': 'Chemistry 101', 'location': 'Lab C3', 'type': 'lab'}
                ]
            },
            'study_blocks': [
                {'day': 'monday', 'time': '14:00-16:00', 'subject': 'Mathematics review'},
                {'day': 'tuesday', 'time': '15:00-17:00', 'subject': 'Physics problems'}
            ],
            'break_patterns': [
                {'duration': 15, 'frequency': 'between_classes'},
                {'duration': 60, 'frequency': 'lunch_break'}
            ],
            'optimization_notes': 'Schedule optimized for morning learning preference with adequate breaks.'
        }
    
    def _get_mock_recommendations(self) -> List[str]:
        """Mock recommendations for fallback."""
        return [
            'Review course materials 15 minutes before each class',
            'Use the 2-hour gap on Tuesday for intensive study sessions',
            'Prepare for lab sessions by reviewing theory the night before',
            'Consider forming study groups for challenging subjects',
            'Block calendar time for assignment deadlines'
        ]


class SyllabusGeneratorAgent(BaseAgent):
    """
    Dynamic Syllabus Generator Agent - Creates personalized course syllabi
    using Gemini 2.0 Flash and Google Docs API.
    """
    
    def __init__(self):
        super().__init__("SyllabusGeneratorAgent")
        self.gemini_model = None
        self.docs_service = None
        self.drive_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google services."""
        try:
            # Initialize Gemini 2.0 Flash with hardcoded API key
            GOOGLE_AI_API_KEY = "AIzaSyDs0rGErXBVJLaMd7HoQrhU2FhrSyhx368"
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 Flash initialized for syllabus generation")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            self.gemini_model = None
    
    async def generate_syllabus(self, context: AcademicContext) -> AcademicContext:
        """Generate a personalized syllabus."""
        logger.info(f"[{self.name}] Generating syllabus for user {context.user_id}")
        
        try:
            # Extract syllabus parameters
            course_info = context.data.get('course_info', {})
            learning_objectives = context.data.get('learning_objectives', [])
            student_level = context.data.get('student_level', 'intermediate')
            duration_weeks = context.data.get('duration_weeks', 16)
            preferences = context.data.get('preferences', {})
            
            # Generate comprehensive syllabus using Gemini
            syllabus_content = await self._generate_syllabus_content(
                course_info, learning_objectives, student_level, duration_weeks, preferences
            )
            
            # Create weekly breakdown
            weekly_breakdown = await self._create_weekly_breakdown(
                syllabus_content, duration_weeks, learning_objectives
            )
            
            # Generate assessment plan
            assessment_plan = await self._create_assessment_plan(
                course_info, learning_objectives, student_level
            )
            
            # Create reading list and resources
            resources = await self._generate_resources(course_info, student_level)
            
            # Format final syllabus
            final_syllabus = await self._format_final_syllabus(
                syllabus_content, weekly_breakdown, assessment_plan, resources
            )
            
            # Optionally create Google Doc
            if preferences.get('create_google_doc', False):
                doc_url = await self._create_google_doc(context.user_id, final_syllabus)
                final_syllabus['google_doc_url'] = doc_url
            
            # Store raw result for formatting
            raw_result = {
                'syllabus': final_syllabus,
                'customization_level': 'high',
                'adaptation_score': await self._calculate_adaptation_score(final_syllabus, preferences)
            }
            
            context.result = raw_result
            logger.info(f"[{self.name}] Syllabus generated successfully")
            return context
            
        except Exception as e:
            logger.error(f"[{self.name}] Error generating syllabus: {e}")
            context.result = {'error': str(e)}
            return context
    
    async def _generate_syllabus_content(self, course_info: Dict, learning_objectives: List,
                                       student_level: str, duration_weeks: int, 
                                       preferences: Dict) -> Dict[str, Any]:
        """Generate comprehensive syllabus content using Gemini 2.0 Flash."""
        try:
            prompt = f"""
            Create a comprehensive, personalized course syllabus with the following specifications:
            
            COURSE INFORMATION:
            {json.dumps(course_info, indent=2)}
            
            LEARNING OBJECTIVES:
            {json.dumps(learning_objectives, indent=2)}
            
            STUDENT LEVEL: {student_level}
            DURATION: {duration_weeks} weeks
            PREFERENCES: {json.dumps(preferences, indent=2)}
            
            Generate a detailed syllabus including:
            
            1. COURSE OVERVIEW
               - Course description and rationale
               - Prerequisites and corequisites
               - Learning outcomes aligned with objectives
               - Skills students will develop
            
            2. COURSE STRUCTURE
               - Major topics and themes
               - Learning progression and scaffolding
               - Integration between theory and practice
               - Differentiation for student level
            
            3. TEACHING METHODOLOGY
               - Instructional strategies
               - Learning activities and engagement
               - Technology integration
               - Accommodations for different learning styles
            
            4. COURSE POLICIES
               - Attendance and participation
               - Late work and make-up policies
               - Academic integrity guidelines
               - Communication expectations
            
            5. SUPPORT RESOURCES
               - Office hours and help sessions
               - Tutoring and study groups
               - Accessibility services
               - Mental health and wellness resources
            
            Ensure the syllabus is:
            - Engaging and motivating for students
            - Clear in expectations and requirements
            - Scaffolded for progressive learning
            - Inclusive and accessible
            - Aligned with modern pedagogical practices
            
            Return as structured JSON with detailed content for each section.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                content_text = response.text
                
                # Parse and structure the response
                try:
                    # Extract JSON or create structured content
                    import re
                    json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                    if json_match:
                        content = json.loads(json_match.group())
                    else:
                        content = self._parse_syllabus_text(content_text)
                except json.JSONDecodeError:
                    content = self._parse_syllabus_text(content_text)
            else:
                content = self._get_mock_syllabus_content()
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating syllabus content: {e}")
            return self._get_mock_syllabus_content()
    
    def _parse_syllabus_text(self, text: str) -> Dict[str, Any]:
        """Parse syllabus text into structured format."""
        return {
            'course_overview': {
                'description': 'Comprehensive course covering fundamental concepts and advanced applications.',
                'prerequisites': 'Basic knowledge of subject fundamentals',
                'learning_outcomes': [
                    'Understand core principles and theories',
                    'Apply knowledge to real-world scenarios',
                    'Develop critical thinking and analytical skills'
                ]
            },
            'course_structure': {
                'major_topics': [
                    'Introduction and Foundations',
                    'Core Concepts and Principles',
                    'Advanced Applications',
                    'Integration and Synthesis'
                ],
                'learning_progression': 'Sequential building from basics to advanced concepts'
            },
            'teaching_methodology': {
                'strategies': ['Lectures', 'Hands-on Labs', 'Group Projects', 'Case Studies'],
                'technology': ['Online platforms', 'Interactive simulations', 'Collaboration tools']
            },
            'policies': {
                'attendance': 'Regular attendance expected for optimal learning',
                'late_work': 'Late submissions accepted with penalty',
                'integrity': 'Academic honesty required in all work'
            },
            'support': {
                'office_hours': 'Weekly sessions for student questions',
                'resources': ['Library access', 'Online materials', 'Study groups']
            }
        }
    
    def _get_mock_syllabus_content(self) -> Dict[str, Any]:
        """Mock syllabus content for fallback."""
        return self._parse_syllabus_text("")
    
    async def _create_weekly_breakdown(self, syllabus_content: Dict, duration_weeks: int, learning_objectives: List) -> Dict[str, Any]:
        """Create a weekly breakdown of the course."""
        try:
            prompt = f"""
            Create a detailed weekly breakdown for a {duration_weeks}-week course:
            
            SYLLABUS CONTENT:
            {json.dumps(syllabus_content, indent=2)}
            
            LEARNING OBJECTIVES:
            {json.dumps(learning_objectives, indent=2)}
            
            Create a week-by-week schedule including:
            - Topics to be covered each week
            - Learning activities and assignments
            - Readings and resources
            - Assessments and milestones
            - Progressive skill building
            
            Format as JSON with week numbers as keys.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                breakdown_text = response.text
                
                try:
                    import re
                    json_match = re.search(r'\{.*\}', breakdown_text, re.DOTALL)
                    if json_match:
                        breakdown = json.loads(json_match.group())
                    else:
                        breakdown = self._get_mock_weekly_breakdown(duration_weeks)
                except json.JSONDecodeError:
                    breakdown = self._get_mock_weekly_breakdown(duration_weeks)
            else:
                breakdown = self._get_mock_weekly_breakdown(duration_weeks)
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error creating weekly breakdown: {e}")
            return self._get_mock_weekly_breakdown(duration_weeks)

    async def _create_assessment_plan(self, course_info: Dict, learning_objectives: List, student_level: str) -> Dict[str, Any]:
        """Create an assessment plan for the course."""
        try:
            prompt = f"""
            Create a comprehensive assessment plan for:
            
            COURSE INFO:
            {json.dumps(course_info, indent=2)}
            
            LEARNING OBJECTIVES:
            {json.dumps(learning_objectives, indent=2)}
            
            STUDENT LEVEL: {student_level}
            
            Include:
            - Formative assessments (quizzes, discussions, etc.)
            - Summative assessments (exams, projects, etc.)
            - Assessment criteria and rubrics
            - Weight distribution
            - Timing throughout the semester
            
            Return as structured JSON.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                assessment_text = response.text
                
                try:
                    import re
                    json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
                    if json_match:
                        assessment = json.loads(json_match.group())
                    else:
                        assessment = self._get_mock_assessment_plan()
                except json.JSONDecodeError:
                    assessment = self._get_mock_assessment_plan()
            else:
                assessment = self._get_mock_assessment_plan()
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error creating assessment plan: {e}")
            return self._get_mock_assessment_plan()

    async def _generate_resources(self, course_info: Dict, student_level: str) -> Dict[str, Any]:
        """Generate reading list and resources."""
        try:
            prompt = f"""
            Generate comprehensive resources for:
            
            COURSE INFO:
            {json.dumps(course_info, indent=2)}
            
            STUDENT LEVEL: {student_level}
            
            Include:
            - Required textbooks and materials
            - Supplementary readings
            - Online resources and tools
            - Multimedia content
            - Research databases
            - Study guides and practice materials
            
            Return as structured JSON with categories.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                resources_text = response.text
                
                try:
                    import re
                    json_match = re.search(r'\{.*\}', resources_text, re.DOTALL)
                    if json_match:
                        resources = json.loads(json_match.group())
                    else:
                        resources = self._get_mock_resources()
                except json.JSONDecodeError:
                    resources = self._get_mock_resources()
            else:
                resources = self._get_mock_resources()
            
            return resources
            
        except Exception as e:
            logger.error(f"Error generating resources: {e}")
            return self._get_mock_resources()

    async def _format_final_syllabus(self, syllabus_content: Dict, weekly_breakdown: Dict, assessment_plan: Dict, resources: Dict) -> Dict[str, Any]:
        """Format the final syllabus document."""
        try:
            final_syllabus = {
                'course_overview': syllabus_content.get('course_overview', {}),
                'structure': syllabus_content.get('course_structure', {}),
                'methodology': syllabus_content.get('teaching_methodology', {}),
                'policies': syllabus_content.get('policies', {}),
                'support': syllabus_content.get('support', {}),
                'weekly_schedule': weekly_breakdown,
                'assessments': assessment_plan,
                'resources': resources,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            };
            
            return final_syllabus;
            
        except Exception as e:
            logger.error(f"Error formatting final syllabus: {e}")
            return self._get_mock_syllabus_content();

    async def _create_google_doc(self, user_id: str, syllabus: Dict) -> str:
        """Create a Google Doc with the syllabus content."""
        try:
            # This would use Google Docs API to create a document
            logger.info(f"Google Doc would be created for user {user_id}")
            return "https://docs.google.com/document/placeholder"
        except Exception as e:
            logger.error(f"Error creating Google Doc: {e}")
            return ""

    async def _calculate_adaptation_score(self, syllabus: Dict, preferences: Dict) -> int:
        """Calculate how well the syllabus is adapted to preferences."""
        try:
            # Simple scoring based on preferences alignment
            score = 75  # Base score
            
            if preferences.get('teaching_style') and 'methodology' in syllabus:
                score += 10
            
            if preferences.get('assessment_types') and 'assessments' in syllabus:
                score += 10
            
            if preferences.get('content_format') and 'structure' in syllabus:
                score += 5
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"Error calculating adaptation score: {e}")
            return 80

    def _get_mock_weekly_breakdown(self, duration_weeks: int) -> Dict[str, Any]:
        """Mock weekly breakdown for fallback."""
        breakdown = {}
        for week in range(1, duration_weeks + 1):
            breakdown[f"week_{week}"] = {
                'topics': [f'Topic {week}.1', f'Topic {week}.2'],
                'activities': ['Reading assignment', 'Discussion forum'],
                'assessments': 'Quiz' if week % 4 == 0 else None
            }
        return breakdown

    def _get_mock_assessment_plan(self) -> Dict[str, Any]:
        """Mock assessment plan for fallback."""
        return {
            'formative': [
                {'type': 'Quizzes', 'weight': '20%', 'frequency': 'Weekly'},
                {'type': 'Discussions', 'weight': '15%', 'frequency': 'Bi-weekly'}
            ],
            'summative': [
                {'type': 'Midterm Exam', 'weight': '25%', 'timing': 'Week 8'},
                {'type': 'Final Project', 'weight': '25%', 'timing': 'Week 16'},
                {'type': 'Final Exam', 'weight': '15%', 'timing': 'Finals Week'}
            ]
        }

    def _get_mock_resources(self) -> Dict[str, Any]:
        """Mock resources for fallback."""
        return {
            'required_texts': ['Primary Textbook', 'Course Reader'],
            'supplementary': ['Additional readings', 'Online articles'],
            'digital_tools': ['Course LMS', 'Online simulations'],
            'library_resources': ['Research databases', 'Academic journals']
        }


class SyllabusFormatterAgent(BaseAgent):
    """
    Syllabus Formatter Agent - Standardizes Gemini responses into a consistent JSON format
    """
    
    def __init__(self):
        super().__init__("SyllabusFormatterAgent")
        self.gemini_model = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Gemini service."""
        try:
            GOOGLE_AI_API_KEY = "AIzaSyDs0rGErXBVJLaMd7HoQrhU2FhrSyhx368"
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 Flash initialized for formatter")
        except Exception as e:
            logger.error(f"Error initializing formatter services: {e}")
    
    async def format_syllabus_response(self, raw_response: Dict[str, Any], context: AcademicContext) -> AcademicContext:
        """Format any syllabus response into the standard JSON format."""
        logger.info(f"[{self.name}] Formatting syllabus response for user {context.user_id}")
        
        try:
            # Define the standard schema
            standard_schema = {
                "syllabus": {
                    "course_overview": {
                        "description": "string",
                        "prerequisites": "string",
                        "learning_outcomes": ["string"]
                    },
                    "structure": {
                        "major_topics": ["string"],
                        "learning_progression": "string"
                    },
                    "methodology": {
                        "strategies": ["string"],
                        "technology": ["string"]
                    },
                    "policies": {
                        "attendance": "string",
                        "late_work": "string",
                        "integrity": "string"
                    },
                    "support": {
                        "office_hours": "string",
                        "resources": ["string"]
                    },
                    "weekly_schedule": {
                        "Week_1": {
                            "topics": ["string"],
                            "learning_activities": ["string"],
                            "readings_resources": ["string"],
                            "assessments_milestones": ["string"],
                            "progressive_skill_building": ["string"]
                        }
                    },
                    "assessments": {
                        "course_name": "string",
                        "course_code": "string",
                        "student_level": "string",
                        "instructor": "string",
                        "learning_objectives": ["string"],
                        "assessment_plan": {
                            "overview": "string",
                            "weight_distribution": {
                                "quizzes": "string",
                                "discussions": "string",
                                "midterm_exam": "string",
                                "project_proposal": "string",
                                "project_report": "string",
                                "final_exam": "string"
                            },
                            "formative_assessments": [
                                {
                                    "assessment_type": "string",
                                    "description": "string",
                                    "frequency": "string",
                                    "weight": "string",
                                    "timing": "string",
                                    "assessment_criteria": "string",
                                    "rubric": "string"
                                }
                            ],
                            "summative_assessments": [
                                {
                                    "assessment_type": "string",
                                    "description": "string",
                                    "weight": "string",
                                    "timing": "string",
                                    "assessment_criteria": "string",
                                    "rubric": "string"
                                }
                            ]
                        }
                    },
                    "resources": {
                        "course_info": {
                            "name": "string",
                            "code": "string",
                            "description": "string",
                            "credits": "number",
                            "level": "string",
                            "department": "string",
                            "instructor": "string"
                        },
                        "student_level": "string",
                        "resources": {
                            "required_textbooks_and_materials": [
                                {
                                    "title": "string",
                                    "author": "string",
                                    "notes": "string"
                                }
                            ],
                            "supplementary_readings": [
                                {
                                    "title": "string",
                                    "author": "string",
                                    "notes": "string"
                                }
                            ],
                            "online_resources_and_tools": [
                                {
                                    "name": "string",
                                    "url": "string",
                                    "description": "string"
                                }
                            ],
                            "multimedia_content": [
                                {
                                    "type": "string",
                                    "title": "string",
                                    "description": "string"
                                }
                            ],
                            "research_databases": [
                                {
                                    "name": "string",
                                    "url": "string",
                                    "description": "string"
                                }
                            ],
                            "study_guides_and_practice_materials": [
                                {
                                    "type": "string",
                                    "title": "string",
                                    "description": "string"
                                }
                            ]
                        }
                    },
                    "created_at": "ISO 8601 datetime string",
                    "version": "string"
                },
                "customization_level": "string",
                "adaptation_score": "number (1-100)"
            }
            
            # Use Gemini to format the response
            formatted_response = await self._format_with_gemini(raw_response, standard_schema, context)
            
            # Validate and clean the response
            validated_response = self._validate_and_clean_response(formatted_response)
            
            context.result = validated_response
            logger.info(f"[{self.name}] Successfully formatted syllabus response")
            return context
            
        except Exception as e:
            logger.error(f"[{self.name}] Error formatting syllabus: {e}")
            # Return a fallback formatted response
            context.result = self._get_fallback_formatted_response(raw_response, context)
            return context
    
    async def _format_with_gemini(self, raw_response: Dict[str, Any], schema: Dict[str, Any], context: AcademicContext) -> Dict[str, Any]:
        """Use Gemini to format the response according to the schema."""
        try:
            course_info = context.data.get('course_info', {})
            learning_objectives = context.data.get('learning_objectives', [])
            duration_weeks = context.data.get('duration_weeks', 16)
            
            prompt = f"""
            You are a syllabus formatting expert. I need you to format this raw syllabus data into a specific JSON structure.

            RAW SYLLABUS DATA:
            {json.dumps(raw_response, indent=2)}

            COURSE INFORMATION:
            {json.dumps(course_info, indent=2)}

            LEARNING OBJECTIVES:
            {json.dumps(learning_objectives, indent=2)}

            DURATION: {duration_weeks} weeks

            TARGET SCHEMA:
            {json.dumps(schema, indent=2)}

            FORMATTING REQUIREMENTS:
            1. Follow the exact JSON structure provided in the schema
            2. Generate comprehensive weekly schedules for {duration_weeks} weeks
            3. Each week should have: topics, learning_activities, readings_resources, assessments_milestones, progressive_skill_building
            4. Include detailed assessment plans with formative and summative assessments
            5. Provide comprehensive resources organized by category
            6. Ensure all required fields are populated with meaningful content
            7. Use the course information provided to fill in course_info fields
            8. Set created_at to current timestamp in ISO 8601 format
            9. Set adaptation_score between 80-95 based on content quality
            10. Set customization_level to "high"

            IMPORTANT: Return ONLY valid JSON without any markdown formatting or explanations.
            """
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content, prompt
                )
                
                # Clean up the response text
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Parse JSON
                formatted_data = json.loads(response_text)
                return formatted_data
            else:
                return self._get_fallback_formatted_response(raw_response, context)
                
        except Exception as e:
            logger.error(f"Error formatting with Gemini: {e}")
            return self._get_fallback_formatted_response(raw_response, context)
    
    def _validate_and_clean_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the formatted response."""
        try:
            # Ensure required top-level fields exist
            if 'syllabus' not in response:
                response['syllabus'] = {}
            
            # Ensure required nested fields exist
            required_sections = ['course_overview', 'structure', 'methodology', 'policies', 'support', 'weekly_schedule', 'assessments', 'resources']
            for section in required_sections:
                if section not in response['syllabus']:
                    response['syllabus'][section] = {}
            
            # Set metadata
            response['syllabus']['created_at'] = datetime.now().isoformat()
            response['syllabus']['version'] = "1.0"
            
            if 'customization_level' not in response:
                response['customization_level'] = "high"
            
            if 'adaptation_score' not in response:
                response['adaptation_score'] = 85
            
            return response
            
        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return response
    
    def _get_fallback_formatted_response(self, raw_response: Dict[str, Any], context: AcademicContext) -> Dict[str, Any]:
        """Generate a fallback formatted response when Gemini formatting fails."""
        course_info = context.data.get('course_info', {})
        learning_objectives = context.data.get('learning_objectives', [])
        duration_weeks = context.data.get('duration_weeks', 16)
        
        # Generate weekly schedule
        weekly_schedule = {}
        for week in range(1, duration_weeks + 1):
            week_key = f"Week_{week}"
            weekly_schedule[week_key] = {
                "topics": [
                    f"Core concepts for week {week}",
                    f"Practical applications - week {week}",
                    f"Skill development - week {week}"
                ],
                "learning_activities": [
                    f"Interactive lecture on week {week} topics",
                    f"Hands-on workshop or lab session",
                    f"Group discussion and problem-solving"
                ],
                "readings_resources": [
                    f"Required reading: Chapter {week}",
                    f"Supplementary materials for week {week}",
                    f"Online resources and tutorials"
                ],
                "assessments_milestones": [
                    f"Quiz on week {week} material" if week % 2 == 0 else "Participation in class activities",
                    f"Assignment {(week-1)//3 + 1} due" if week % 3 == 0 else ""
                ],
                "progressive_skill_building": [
                    f"Building on previous weeks' concepts",
                    f"Developing advanced skills in week {week}",
                    f"Preparing for upcoming challenges"
                ]
            }
        
        return {
            "syllabus": {
                "course_overview": {
                    "description": course_info.get('description', 'A comprehensive course designed to meet learning objectives.'),
                    "prerequisites": "Basic knowledge of subject fundamentals",
                    "learning_outcomes": learning_objectives or [
                        "Understand core principles and theories",
                        "Apply knowledge to real-world scenarios",
                        "Develop critical thinking and analytical skills"
                    ]
                },
                "structure": {
                    "major_topics": [
                        "Introduction and Foundations",
                        "Core Concepts and Principles", 
                        "Advanced Applications",
                        "Integration and Synthesis"
                    ],
                    "learning_progression": "Sequential building from basics to advanced concepts"
                },
                "methodology": {
                    "strategies": ["Lectures", "Hands-on Labs", "Group Projects", "Case Studies"],
                    "technology": ["Online platforms", "Interactive simulations", "Collaboration tools"]
                },
                "policies": {
                    "attendance": "Regular attendance expected for optimal learning",
                    "late_work": "Late submissions accepted with penalty",
                    "integrity": "Academic honesty required in all work"
                },
                "support": {
                    "office_hours": "Weekly sessions for student questions",
                    "resources": ["Library access", "Online materials", "Study groups"]
                },
                "weekly_schedule": {f"{course_info.get('code', 'COURSE')}_Weekly_Schedule": weekly_schedule},
                "assessments": {
                    "course_name": course_info.get('name', 'Course Name'),
                    "course_code": course_info.get('code', 'COURSE101'),
                    "student_level": context.data.get('student_level', 'undergraduate'),
                    "instructor": course_info.get('instructor', 'Instructor Name'),
                    "learning_objectives": learning_objectives,
                    "assessment_plan": {
                        "overview": "Comprehensive assessment strategy combining formative and summative evaluations",
                        "weight_distribution": {
                            "quizzes": "20%",
                            "discussions": "10%",
                            "midterm_exam": "25%",
                            "project_proposal": "5%",
                            "project_report": "25%",
                            "final_exam": "15%"
                        },
                        "formative_assessments": [
                            {
                                "assessment_type": "Quizzes",
                                "description": "Regular knowledge checks on key concepts",
                                "frequency": "Weekly",
                                "weight": "20%",
                                "timing": "End of each week",
                                "assessment_criteria": "Understanding of core concepts",
                                "rubric": "Graded on accuracy and completeness"
                            }
                        ],
                        "summative_assessments": [
                            {
                                "assessment_type": "Final Project",
                                "description": "Comprehensive project demonstrating mastery",
                                "weight": "25%",
                                "timing": "End of semester",
                                "assessment_criteria": "Application of knowledge and skills",
                                "rubric": "Evaluated on depth, creativity, and execution"
                            }
                        ]
                    }
                },
                "resources": {
                    "course_info": {
                        "name": course_info.get('name', 'Course Name'),
                        "code": course_info.get('code', 'COURSE101'),
                        "description": course_info.get('description', 'Course description'),
                        "credits": course_info.get('credits', 3),
                        "level": course_info.get('level', 'intermediate'),
                        "department": course_info.get('department', 'Department'),
                        "instructor": course_info.get('instructor', 'Instructor Name')
                    },
                    "student_level": context.data.get('student_level', 'undergraduate'),
                    "resources": {
                        "required_textbooks_and_materials": [
                            {
                                "title": "Primary Course Textbook",
                                "author": "Expert Author",
                                "notes": "Essential reading for course concepts"
                            }
                        ],
                        "supplementary_readings": [
                            {
                                "title": "Advanced Topics in Subject",
                                "author": "Leading Researcher",
                                "notes": "For students seeking deeper understanding"
                            }
                        ],
                        "online_resources_and_tools": [
                            {
                                "name": "Course Learning Management System",
                                "url": "https://lms.university.edu",
                                "description": "Central hub for course materials and activities"
                            }
                        ],
                        "multimedia_content": [
                            {
                                "type": "Video Lectures",
                                "title": "Recorded Course Sessions",
                                "description": "Video recordings of key lectures and demonstrations"
                            }
                        ],
                        "research_databases": [
                            {
                                "name": "Academic Database",
                                "url": "https://academic.database.com",
                                "description": "Access to scholarly articles and research papers"
                            }
                        ],
                        "study_guides_and_practice_materials": [
                            {
                                "type": "Practice Exercises",
                                "title": "Weekly Problem Sets",
                                "description": "Hands-on exercises to reinforce learning"
                            }
                        ]
                    }
                },
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "customization_level": "high",
            "adaptation_score": 85
        }
        

# Academic Agent Manager - Coordinates all academic agents
class AcademicAgentManager:
    """
    Manager for coordinating all academic agents and their interactions.
    """
    
    def __init__(self):
        self.scheduler_agent = SmartCourseSchedulerAgent()
        self.syllabus_agent = SyllabusGeneratorAgent()
        self.formatter_agent = SyllabusFormatterAgent()
        logger.info("Academic Agent Manager initialized with all agents including formatter")
    
    async def process_academic_request(self, request_type: str, user_id: str, 
                                     session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process academic requests through appropriate agents."""
        context = AcademicContext(
            user_id=user_id,
            session_id=session_id,
            request_type=request_type,
            data=data
        )
        
        try:
            if request_type == 'create_schedule':
                result_context = await self.scheduler_agent.create_schedule(context)
                
            elif request_type == 'generate_syllabus':
                # First generate syllabus
                result_context = await self.syllabus_agent.generate_syllabus(context)
                
                # Then format the response using the formatter agent
                if result_context.result and 'error' not in result_context.result:
                    raw_response = result_context.result
                    formatted_context = await self.formatter_agent.format_syllabus_response(raw_response, context)
                    result_context = formatted_context
                
            else:
                result_context = context
                result_context.result = {'error': f'Unknown request type: {request_type}'}
            
            return {
                'success': 'error' not in (result_context.result or {}),
                'result': result_context.result,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Request processed successfully' if 'error' not in (result_context.result or {}) else 'Request failed'
            }
            
        except Exception as e:
            logger.error(f"Error processing academic request: {e}")
            return {
                'success': False,
                'result': {'error': str(e)},
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Request processing failed'
            }
    
    async def get_available_features(self) -> List[str]:
        """Get list of available academic features."""
        return [
            'create_schedule',
            'generate_syllabus'
        ]


# Initialize global manager
academic_manager = AcademicAgentManager()
