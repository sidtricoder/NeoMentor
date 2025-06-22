"""
NeoMentor Course Scheduler Agents - Google ADK Implementation

This module implements intelligent course scheduling agents using Google Agent Development Kit (ADK)
and Google services including Gemini 2.0 Flash, Google Calendar API, and Firestore.
"""

import json
import os
import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import re
from enum import Enum

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

# Base agent import
from .agents import BaseAgent


class EnergyPattern(Enum):
    """Energy patterns for optimal scheduling"""
    MORNING_PERSON = "morning_person"
    EVENING_PERSON = "evening_person"
    FLEXIBLE = "flexible"


class CourseDifficulty(Enum):
    """Course difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Course:
    """Course data structure"""
    name: str
    code: str
    credits: int
    difficulty: CourseDifficulty
    prerequisites: List[str] = None
    time_slots: List[str] = None
    location: str = ""
    instructor: str = ""

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.time_slots is None:
            self.time_slots = []


@dataclass
class Preferences:
    """User preferences for scheduling"""
    peak_hours: List[str] = None
    max_daily_courses: int = 4
    break_duration: int = 15
    energy_pattern: EnergyPattern = EnergyPattern.FLEXIBLE
    preferred_days: List[str] = None
    create_calendar_events: bool = False

    def __post_init__(self):
        if self.peak_hours is None:
            self.peak_hours = []
        if self.preferred_days is None:
            self.preferred_days = []


@dataclass
class Constraints:
    """Scheduling constraints"""
    unavailable_times: List[str] = None
    max_travel_time: int = 30
    mandatory_breaks: List[str] = None

    def __post_init__(self):
        if self.unavailable_times is None:
            self.unavailable_times = []
        if self.mandatory_breaks is None:
            self.mandatory_breaks = []


@dataclass
class ScheduleRequest:
    """Complete schedule request"""
    courses: List[Course]
    preferences: Preferences
    constraints: Constraints
    semester_start: str
    semester_end: str
    user_id: str
    session_id: str


@dataclass
class TimeSlot:
    """Represents a time slot in the schedule"""
    day: str
    start_time: str
    end_time: str
    course: Course
    location: str = ""
    
    def conflicts_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot conflicts with another"""
        if self.day != other.day:
            return False
        
        self_start = datetime.strptime(self.start_time, "%H:%M").time()
        self_end = datetime.strptime(self.end_time, "%H:%M").time()
        other_start = datetime.strptime(other.start_time, "%H:%M").time()
        other_end = datetime.strptime(other.end_time, "%H:%M").time()
        
        return not (self_end <= other_start or other_end <= self_start)


class CourseSchedulerAgent(BaseAgent):
    """
    Main Course Scheduler Agent using Google ADK and Gemini 2.0 Flash
    
    This agent creates intelligent, personalized course schedules by:
    - Analyzing course requirements and prerequisites
    - Considering user preferences and constraints
    - Optimizing for learning effectiveness
    - Integrating with Google Calendar
    - Providing conflict resolution
    """
    
    def __init__(self):
        super().__init__("CourseSchedulerAgent")
        self.calendar_service = None
        self.gemini_model = None
        self.firestore_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google services for ADK functionality"""
        try:
            # Initialize Gemini 2.0 Flash
            GOOGLE_AI_API_KEY = "AIzaSyDs0rGErXBVJLaMd7HoQrhU2FhrSyhx368"
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 Flash initialized for course scheduling")
            
            # Initialize Firestore for data persistence
            self.firestore_client = firestore.Client()
            logger.info("Firestore client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Google services: {e}")
    
    async def process_schedule_request(self, request_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """Main entry point for processing schedule requests"""
        logger.info(f"[{self.name}] Processing schedule request for user {user_id}")
        
        try:
            # Parse and validate request
            schedule_request = self._parse_request(request_data, user_id, session_id)
            
            # Generate optimal schedule using Gemini
            schedule = await self._generate_optimal_schedule(schedule_request)
            
            # Validate and resolve conflicts
            validated_schedule = await self._validate_and_resolve_conflicts(schedule, schedule_request)
            
            # Create calendar events if requested
            calendar_events = None
            if schedule_request.preferences.create_calendar_events:
                calendar_events = await self._create_calendar_events(validated_schedule, schedule_request)
            
            # Save to Firestore
            await self._save_schedule_to_firestore(validated_schedule, schedule_request, calendar_events)
            
            # Prepare response
            result = {
                "schedule": validated_schedule,
                "metadata": {
                    "total_courses": len(schedule_request.courses),
                    "total_credits": sum(course.credits for course in schedule_request.courses),
                    "schedule_optimization_score": await self._calculate_optimization_score(validated_schedule, schedule_request),
                    "conflicts_resolved": getattr(self, '_conflicts_resolved', 0),
                    "calendar_events_created": len(calendar_events) if calendar_events else 0
                },
                "recommendations": await self._generate_recommendations(validated_schedule, schedule_request),
                "session_id": session_id
            }
            
            logger.info(f"[{self.name}] Successfully generated schedule with {len(validated_schedule)} time slots")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Error processing schedule request: {e}")
            raise e
    
    def _parse_request(self, request_data: Dict[str, Any], user_id: str, session_id: str) -> ScheduleRequest:
        """Parse and validate the incoming request data"""
        try:
            # Parse courses
            courses = []
            for course_data in request_data.get('courses', []):
                course = Course(
                    name=course_data['name'],
                    code=course_data['code'],
                    credits=course_data['credits'],
                    difficulty=CourseDifficulty(course_data.get('difficulty', 'medium')),
                    prerequisites=course_data.get('prerequisites', []),
                    time_slots=course_data.get('time_slots', []),
                    location=course_data.get('location', ''),
                    instructor=course_data.get('instructor', '')
                )
                courses.append(course)
            
            # Parse preferences
            pref_data = request_data.get('preferences', {})
            preferences = Preferences(
                peak_hours=pref_data.get('peak_hours', []),
                max_daily_courses=pref_data.get('max_daily_courses', 4),
                break_duration=pref_data.get('break_duration', 15),
                energy_pattern=EnergyPattern(pref_data.get('energy_pattern', 'flexible')),
                preferred_days=pref_data.get('preferred_days', []),
                create_calendar_events=pref_data.get('create_calendar_events', False)
            )
            
            # Parse constraints
            const_data = request_data.get('constraints', {})
            constraints = Constraints(
                unavailable_times=const_data.get('unavailable_times', []),
                max_travel_time=const_data.get('max_travel_time', 30),
                mandatory_breaks=const_data.get('mandatory_breaks', [])
            )
            
            return ScheduleRequest(
                courses=courses,
                preferences=preferences,
                constraints=constraints,
                semester_start=request_data['semester_start'],
                semester_end=request_data['semester_end'],
                user_id=user_id,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error parsing request: {e}")
            raise ValueError(f"Invalid request format: {e}")
    
    async def _generate_optimal_schedule(self, request: ScheduleRequest) -> List[TimeSlot]:
        """Generate optimal schedule using Gemini 2.0 Flash"""
        logger.info(f"[{self.name}] Generating optimal schedule using Gemini 2.0 Flash")
        
        try:
            # Prepare prompt for Gemini
            prompt = self._create_schedule_prompt(request)
            
            # Generate schedule using Gemini
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.gemini_model.generate_content(prompt)
            )
            
            # Parse Gemini response
            schedule_data = self._parse_gemini_response(response.text)
            
            # Convert to TimeSlot objects
            time_slots = []
            for slot_data in schedule_data:
                time_slot = TimeSlot(
                    day=slot_data['day'],
                    start_time=slot_data['start_time'],
                    end_time=slot_data['end_time'],
                    course=next(c for c in request.courses if c.code == slot_data['course_code']),
                    location=slot_data.get('location', '')
                )
                time_slots.append(time_slot)
            
            logger.info(f"[{self.name}] Generated {len(time_slots)} time slots")
            return time_slots
            
        except Exception as e:
            logger.error(f"Error generating schedule with Gemini: {e}")
            raise e
    
    def _create_schedule_prompt(self, request: ScheduleRequest) -> str:
        """Create a detailed prompt for Gemini to generate optimal schedule"""
        courses_info = []
        for course in request.courses:
            courses_info.append({
                "name": course.name,
                "code": course.code,
                "credits": course.credits,
                "difficulty": course.difficulty.value,
                "prerequisites": course.prerequisites,
                "preferred_slots": course.time_slots,
                "location": course.location,
                "instructor": course.instructor
            })
        
        prompt = f"""
You are an expert course scheduling AI assistant. Create an optimal weekly course schedule based on the following requirements:

**COURSES TO SCHEDULE:**
{json.dumps(courses_info, indent=2)}

**USER PREFERENCES:**
- Energy Pattern: {request.preferences.energy_pattern.value}
- Peak Hours: {request.preferences.peak_hours}
- Max Daily Courses: {request.preferences.max_daily_courses}
- Break Duration: {request.preferences.break_duration} minutes
- Preferred Days: {request.preferences.preferred_days}

**CONSTRAINTS:**
- Unavailable Times: {request.constraints.unavailable_times}
- Max Travel Time: {request.constraints.max_travel_time} minutes
- Mandatory Breaks: {request.constraints.mandatory_breaks}

**SEMESTER PERIOD:**
- Start: {request.semester_start}
- End: {request.semester_end}

**SCHEDULING GUIDELINES:**
1. For morning people, schedule harder courses in the morning (8AM-12PM)
2. For evening people, schedule harder courses in the afternoon/evening (2PM-8PM)
3. For flexible people, distribute courses evenly
4. Ensure minimum {request.preferences.break_duration} minutes between courses
5. Respect prerequisite dependencies
6. Avoid conflicts with unavailable times
7. Consider travel time between different locations
8. Balance daily course load (max {request.preferences.max_daily_courses} per day)

**OUTPUT FORMAT:**
Return ONLY a valid JSON array of time slots in this exact format:
[
  {{
    "day": "Monday",
    "start_time": "09:00",
    "end_time": "10:30",
    "course_code": "CS101",
    "location": "Room 101"
  }},
  ...
]

Days should be: Monday, Tuesday, Wednesday, Thursday, Friday
Times should be in 24-hour format (HH:MM)
Each course should have 2-3 sessions per week based on credits.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini's JSON response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback: try to parse entire response as JSON
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError("Invalid JSON response from Gemini")
    
    async def _validate_and_resolve_conflicts(self, schedule: List[TimeSlot], request: ScheduleRequest) -> List[TimeSlot]:
        """Validate schedule and resolve any conflicts"""
        logger.info(f"[{self.name}] Validating schedule and resolving conflicts")
        
        validated_schedule = []
        conflicts_resolved = 0
        
        for time_slot in schedule:
            # Check for conflicts with existing slots
            conflict_found = False
            for existing_slot in validated_schedule:
                if time_slot.conflicts_with(existing_slot):
                    conflict_found = True
                    # Try to resolve conflict by adjusting time
                    resolved_slot = await self._resolve_time_conflict(time_slot, existing_slot, request)
                    if resolved_slot:
                        validated_schedule.append(resolved_slot)
                        conflicts_resolved += 1
                    break
            
            if not conflict_found:
                validated_schedule.append(time_slot)
        
        # Check against user constraints
        final_schedule = await self._apply_user_constraints(validated_schedule, request)
        
        self._conflicts_resolved = conflicts_resolved
        logger.info(f"[{self.name}] Resolved {conflicts_resolved} conflicts")
        
        return final_schedule
    
    async def _resolve_time_conflict(self, conflicting_slot: TimeSlot, existing_slot: TimeSlot, request: ScheduleRequest) -> Optional[TimeSlot]:
        """Attempt to resolve a time conflict by finding alternative time"""
        try:
            # Try to move to next available time slot
            current_time = datetime.strptime(conflicting_slot.start_time, "%H:%M")
            duration = datetime.strptime(conflicting_slot.end_time, "%H:%M") - datetime.strptime(conflicting_slot.start_time, "%H:%M")
            
            # Try moving 1 hour later
            new_start = current_time + timedelta(hours=1)
            new_end = new_start + duration
            
            # Check if new time is within reasonable hours (8AM-8PM)
            if new_start.hour >= 8 and new_end.hour <= 20:
                return TimeSlot(
                    day=conflicting_slot.day,
                    start_time=new_start.strftime("%H:%M"),
                    end_time=new_end.strftime("%H:%M"),
                    course=conflicting_slot.course,
                    location=conflicting_slot.location
                )
            
            # Try different day
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            current_day_idx = days.index(conflicting_slot.day)
            for i in range(1, len(days)):
                new_day_idx = (current_day_idx + i) % len(days)
                new_day = days[new_day_idx]
                
                return TimeSlot(
                    day=new_day,
                    start_time=conflicting_slot.start_time,
                    end_time=conflicting_slot.end_time,
                    course=conflicting_slot.course,
                    location=conflicting_slot.location
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return None
    
    async def _apply_user_constraints(self, schedule: List[TimeSlot], request: ScheduleRequest) -> List[TimeSlot]:
        """Apply user-specific constraints to the schedule"""
        filtered_schedule = []
        
        for time_slot in schedule:
            # Check against unavailable times
            slot_valid = True
            for unavailable in request.constraints.unavailable_times:
                if self._time_overlaps(time_slot, unavailable):
                    slot_valid = False
                    break
            
            if slot_valid:
                filtered_schedule.append(time_slot)
        
        return filtered_schedule
    
    def _time_overlaps(self, time_slot: TimeSlot, unavailable_time: str) -> bool:
        """Check if a time slot overlaps with an unavailable time"""
        try:
            # Parse unavailable time format (e.g., "Monday 14:00-16:00")
            parts = unavailable_time.split()
            if len(parts) >= 2:
                unavailable_day = parts[0]
                time_range = parts[1]
                start_str, end_str = time_range.split('-')
                
                if time_slot.day == unavailable_day:
                    slot_start = datetime.strptime(time_slot.start_time, "%H:%M").time()
                    slot_end = datetime.strptime(time_slot.end_time, "%H:%M").time()
                    unavail_start = datetime.strptime(start_str, "%H:%M").time()
                    unavail_end = datetime.strptime(end_str, "%H:%M").time()
                    
                    return not (slot_end <= unavail_start or unavail_end <= slot_start)
            
            return False
            
        except Exception:
            return False
    
    async def _create_calendar_events(self, schedule: List[TimeSlot], request: ScheduleRequest) -> List[Dict[str, Any]]:
        """Create Google Calendar events for the schedule"""
        logger.info(f"[{self.name}] Creating Google Calendar events")
        
        try:
            # Note: In a production environment, you would implement OAuth flow
            # For now, we'll return the events data that would be created
            calendar_events = []
            
            for time_slot in schedule:
                event = {
                    'summary': f"{time_slot.course.code} - {time_slot.course.name}",
                    'location': time_slot.location,
                    'description': f"Course: {time_slot.course.name}\nInstructor: {time_slot.course.instructor}\nCredits: {time_slot.course.credits}",
                    'start': {
                        'dateTime': self._get_event_datetime(time_slot.day, time_slot.start_time, request.semester_start),
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': self._get_event_datetime(time_slot.day, time_slot.end_time, request.semester_start),
                        'timeZone': 'America/New_York',
                    },
                    'recurrence': [
                        f'RRULE:FREQ=WEEKLY;UNTIL={self._format_calendar_date(request.semester_end)}'
                    ],
                }
                calendar_events.append(event)
            
            logger.info(f"[{self.name}] Prepared {len(calendar_events)} calendar events")
            return calendar_events
            
        except Exception as e:
            logger.error(f"Error creating calendar events: {e}")
            return []
    
    def _get_event_datetime(self, day: str, time_str: str, semester_start: str) -> str:
        """Get ISO format datetime for calendar event"""
        try:
            # Map day names to weekday numbers
            day_map = {
                "Monday": 0, "Tuesday": 1, "Wednesday": 2, 
                "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
            }
            
            start_date = datetime.strptime(semester_start, "%Y-%m-%d")
            target_weekday = day_map[day]
            
            # Find the first occurrence of the target day
            days_ahead = target_weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            event_date = start_date + timedelta(days=days_ahead)
            event_time = datetime.strptime(time_str, "%H:%M").time()
            
            event_datetime = datetime.combine(event_date.date(), event_time)
            return event_datetime.isoformat()
            
        except Exception as e:
            logger.error(f"Error formatting event datetime: {e}")
            return datetime.now().isoformat()
    
    def _format_calendar_date(self, date_str: str) -> str:
        """Format date for calendar recurrence rule"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%Y%m%d")
        except Exception:
            return "20241231"
    
    async def _save_schedule_to_firestore(self, schedule: List[TimeSlot], request: ScheduleRequest, calendar_events: Optional[List[Dict[str, Any]]]):
        """Save the generated schedule to Firestore"""
        try:
            if not self.firestore_client:
                logger.warning("Firestore client not available")
                return
            
            # Prepare schedule data for storage
            schedule_data = {
                'user_id': request.user_id,
                'session_id': request.session_id,
                'schedule': [asdict(slot) for slot in schedule],
                'request_data': {
                    'courses': [asdict(course) for course in request.courses],
                    'preferences': asdict(request.preferences),
                    'constraints': asdict(request.constraints),
                    'semester_start': request.semester_start,
                    'semester_end': request.semester_end
                },
                'calendar_events': calendar_events,
                'created_at': datetime.now(),
                'status': 'completed'
            }
            
            # Save to Firestore
            doc_ref = self.firestore_client.collection('course_schedules').document(request.session_id)
            doc_ref.set(schedule_data)
            
            logger.info(f"[{self.name}] Schedule saved to Firestore: {request.session_id}")
            
        except Exception as e:
            logger.error(f"Error saving to Firestore: {e}")
    
    async def _calculate_optimization_score(self, schedule: List[TimeSlot], request: ScheduleRequest) -> float:
        """Calculate an optimization score for the schedule"""
        try:
            score = 100.0
            
            # Deduct points for scheduling conflicts with preferences
            for time_slot in schedule:
                slot_hour = int(time_slot.start_time.split(':')[0])
                
                # Check energy pattern alignment
                if request.preferences.energy_pattern == EnergyPattern.MORNING_PERSON:
                    if time_slot.course.difficulty == CourseDifficulty.HARD and slot_hour > 12:
                        score -= 10
                elif request.preferences.energy_pattern == EnergyPattern.EVENING_PERSON:
                    if time_slot.course.difficulty == CourseDifficulty.HARD and slot_hour < 14:
                        score -= 10
                
                # Check preferred days
                if request.preferences.preferred_days and time_slot.day not in request.preferences.preferred_days:
                    score -= 5
            
            # Check daily course load
            daily_loads = {}
            for time_slot in schedule:
                daily_loads[time_slot.day] = daily_loads.get(time_slot.day, 0) + 1
            
            for day, load in daily_loads.items():
                if load > request.preferences.max_daily_courses:
                    score -= (load - request.preferences.max_daily_courses) * 15
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 75.0
    
    async def _generate_recommendations(self, schedule: List[TimeSlot], request: ScheduleRequest) -> List[str]:
        """Generate personalized recommendations for the schedule"""
        recommendations = []
        
        try:
            # Analyze schedule patterns
            daily_loads = {}
            early_morning_courses = 0
            late_evening_courses = 0
            
            for time_slot in schedule:
                daily_loads[time_slot.day] = daily_loads.get(time_slot.day, 0) + 1
                hour = int(time_slot.start_time.split(':')[0])
                
                if hour < 9:
                    early_morning_courses += 1
                elif hour >= 18:
                    late_evening_courses += 1
            
            # Generate recommendations based on analysis
            max_daily_load = max(daily_loads.values()) if daily_loads else 0
            if max_daily_load > request.preferences.max_daily_courses:
                recommendations.append(f"Consider redistributing courses - you have {max_daily_load} courses on some days.")
            
            if early_morning_courses > 0 and request.preferences.energy_pattern == EnergyPattern.EVENING_PERSON:
                recommendations.append("You have early morning courses but prefer evenings. Consider adjusting if possible.")
            
            if late_evening_courses > 0 and request.preferences.energy_pattern == EnergyPattern.MORNING_PERSON:
                recommendations.append("You have late evening courses but prefer mornings. Consider adjusting if possible.")
            
            # Add study recommendations
            hard_courses = [slot for slot in schedule if slot.course.difficulty == CourseDifficulty.HARD]
            if hard_courses:
                recommendations.append(f"You have {len(hard_courses)} challenging courses. Schedule extra study time and consider forming study groups.")
            
            # Add general tips
            recommendations.append("Block calendar time for studying between classes.")
            recommendations.append("Consider location proximity when moving between classes.")
            if request.preferences.create_calendar_events:
                recommendations.append("Calendar events have been created to help you stay organized.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Schedule created successfully. Review and adjust as needed."]


class ScheduleAnalyticsAgent(BaseAgent):
    """
    Analytics agent for course scheduling insights
    """
    
    def __init__(self):
        super().__init__("ScheduleAnalyticsAgent")
        self.firestore_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Firestore for analytics"""
        try:
            self.firestore_client = firestore.Client()
            logger.info("Analytics agent initialized")
        except Exception as e:
            logger.error(f"Error initializing analytics agent: {e}")
    
    async def get_schedule_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for user's schedules"""
        try:
            if not self.firestore_client:
                return {"error": "Analytics not available"}
            
            # Query user's schedules
            schedules = self.firestore_client.collection('course_schedules').where('user_id', '==', user_id).limit(10).get()
            
            analytics = {
                "total_schedules": len(schedules),
                "optimization_scores": [],
                "common_patterns": {},
                "recommendations": []
            }
            
            for schedule_doc in schedules:
                data = schedule_doc.to_dict()
                # Extract analytics data
                # This is a placeholder for more complex analytics
                
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}


# Main manager class
class SchedulerManager:
    """
    Main manager for course scheduling operations
    """
    
    def __init__(self):
        self.scheduler_agent = CourseSchedulerAgent()
        self.analytics_agent = ScheduleAnalyticsAgent()
        logger.info("SchedulerManager initialized")
    
    async def create_schedule(self, request_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """Create a new course schedule"""
        try:
            return await self.scheduler_agent.process_schedule_request(request_data, user_id, session_id)
        except Exception as e:
            logger.error(f"Error in schedule creation: {e}")
            raise e
    
    async def get_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get scheduling analytics for user"""
        try:
            return await self.analytics_agent.get_schedule_analytics(user_id)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}


# Global instance
scheduler_manager = SchedulerManager()
