'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  User, 
  GraduationCap,
  BookOpen,
  Target,
  Settings,
  Download,
  Loader2,
  CheckCircle,
  Plus,
  X,
  AlertCircle,
  Timer
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/lib/auth-context';
import { academicAPI, type CourseScheduleRequest, type AcademicResponse } from '@/lib/api';
import AuthComponent from '@/components/auth-component';

const courseSchema = z.object({
  name: z.string().min(2, 'Course name must be at least 2 characters'),
  code: z.string().min(2, 'Course code is required'),
  credits: z.number().min(1).max(12),
  difficulty: z.enum(['easy', 'medium', 'hard']),
  prerequisites: z.array(z.string()).optional(),
  time_slots: z.array(z.string()).optional(),
  location: z.string().optional(),
  instructor: z.string().optional(),
});

const scheduleSchema = z.object({
  courses: z.array(courseSchema).min(1, 'At least one course is required'),
  preferences: z.object({
    peak_hours: z.array(z.string()).optional(),
    max_daily_courses: z.number().min(1).max(8).default(4),
    break_duration: z.number().min(5).max(120).default(15),
    energy_pattern: z.enum(['morning_person', 'evening_person', 'flexible']).default('flexible'),
    preferred_days: z.array(z.string()).optional(),
    create_calendar_events: z.boolean().default(false),
  }),
  constraints: z.object({
    unavailable_times: z.array(z.string()).optional(),
    max_travel_time: z.number().min(0).max(120).optional(),
    mandatory_breaks: z.array(z.string()).optional(),
  }).optional(),
  semester_start: z.string().min(1, 'Semester start date is required'),
  semester_end: z.string().min(1, 'Semester end date is required'),
});

type CourseFormData = z.infer<typeof courseSchema>;
type ScheduleFormData = z.infer<typeof scheduleSchema>;

const defaultCourse: CourseFormData = {
  name: '',
  code: '',
  credits: 3,
  difficulty: 'medium',
  prerequisites: [],
  time_slots: [],
  location: '',
  instructor: '',
};

export default function CourseSchedulerPage() {
  const { currentUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AcademicResponse | null>(null);
  const [prerequisites, setPrerequisites] = useState<string[]>([]);
  const [timeSlots, setTimeSlots] = useState<string[]>([]);
  const [unavailableTimes, setUnavailableTimes] = useState<string[]>([]);
  const [mandatoryBreaks, setMandatoryBreaks] = useState<string[]>([]);
  const [preferredDays, setPreferredDays] = useState<string[]>([]);
  const [peakHours, setPeakHours] = useState<string[]>([]);

  // Input states for adding items
  const [prerequisiteInput, setPrerequisiteInput] = useState('');
  const [timeSlotInput, setTimeSlotInput] = useState('');
  const [unavailableTimeInput, setUnavailableTimeInput] = useState('');
  const [mandatoryBreakInput, setMandatoryBreakInput] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors },
    reset,
  } = useForm<ScheduleFormData>({
    resolver: zodResolver(scheduleSchema),
    defaultValues: {
      courses: [{ ...defaultCourse }],
      preferences: {
        max_daily_courses: 4,
        break_duration: 15,
        energy_pattern: 'flexible',
        create_calendar_events: false,
      },
      constraints: {
        max_travel_time: 30,
      },
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "courses"
  });

  const addCourse = () => {
    append({ ...defaultCourse });
  };

  const removeCourse = (index: number) => {
    if (fields.length > 1) {
      remove(index);
    }
  };

  // Remove the updateCourse function since we're using form registration now

  const addToArray = (array: string[], setArray: (arr: string[]) => void, input: string, setInput: (val: string) => void) => {
    if (input.trim() && !array.includes(input.trim())) {
      setArray([...array, input.trim()]);
      setInput('');
    }
  };

  const removeFromArray = (array: string[], setArray: (arr: string[]) => void, index: number) => {
    setArray(array.filter((_, i) => i !== index));
  };

  const handleDayToggle = (day: string) => {
    if (preferredDays.includes(day)) {
      setPreferredDays(preferredDays.filter(d => d !== day));
    } else {
      setPreferredDays([...preferredDays, day]);
    }
  };

  const handlePeakHourToggle = (hour: string) => {
    if (peakHours.includes(hour)) {
      setPeakHours(peakHours.filter(h => h !== hour));
    } else {
      setPeakHours([...peakHours, hour]);
    }
  };

  const onSubmit = async (data: ScheduleFormData) => {
    console.log('onSubmit called with data:', data);
    console.log('Current user:', currentUser);

    if (!currentUser) {
      toast({
        title: 'Authentication Required',
        description: 'Please sign in to create a course schedule.',
        variant: 'destructive',
      });
      return;
    }

    // Validate that we have at least one course
    if (!data.courses || data.courses.length === 0) {
      toast({
        title: 'Validation Error',
        description: 'Please add at least one course.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const token = await currentUser.getIdToken();
      console.log('Got auth token');
      
      const request: CourseScheduleRequest = {
        courses: data.courses.map(course => ({
          ...course,
          prerequisites: prerequisites,
          time_slots: timeSlots,
        })),
        preferences: {
          ...data.preferences,
          peak_hours: peakHours,
          preferred_days: preferredDays,
        },
        constraints: {
          ...data.constraints,
          unavailable_times: unavailableTimes,
          mandatory_breaks: mandatoryBreaks,
        },
        semester_start: data.semester_start,
        semester_end: data.semester_end,
      };

      console.log('Sending request:', request);
      const response = await academicAPI.createSchedule(request, token);
      console.log('Got response:', response);
      setResult(response);
      
      toast({
        title: 'Success!',
        description: 'Course schedule created successfully.',
      });
    } catch (error: any) {
      console.error('Error creating schedule:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create schedule. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    reset({
      courses: [{ ...defaultCourse }],
      preferences: {
        max_daily_courses: 4,
        break_duration: 15,
        energy_pattern: 'flexible',
        create_calendar_events: false,
      },
      constraints: {
        max_travel_time: 30,
      },
    });
    setPrerequisites([]);
    setTimeSlots([]);
    setUnavailableTimes([]);
    setMandatoryBreaks([]);
    setPreferredDays([]);
    setPeakHours([]);
    setResult(null);
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-green-900/20 dark:to-blue-900/20">
        <div className="container mx-auto px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Course Scheduler
            </h1>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Please sign in to access the AI-powered course scheduling tool.
            </p>
          </motion.div>
          
          <div className="max-w-md mx-auto">
            <AuthComponent />
          </div>
        </div>
      </div>
    );
  }

  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const hourRanges = [
    '08:00-10:00', '10:00-12:00', '12:00-14:00', 
    '14:00-16:00', '16:00-18:00', '18:00-20:00'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-green-900/20 dark:to-blue-900/20">
      <div className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Calendar className="h-10 w-10 text-green-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Course Scheduler
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Create optimal course schedules using AI-powered planning that considers your preferences, constraints, and learning patterns.
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {/* Semester Period */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Semester Period
                </CardTitle>
                <CardDescription>
                  Define the start and end dates for your semester
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="semester_start">Semester Start Date *</Label>
                    <Input
                      id="semester_start"
                      type="date"
                      {...register('semester_start')}
                      disabled={isLoading}
                    />
                    {errors.semester_start && (
                      <p className="text-sm text-red-500">{errors.semester_start.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="semester_end">Semester End Date *</Label>
                    <Input
                      id="semester_end"
                      type="date"
                      {...register('semester_end')}
                      disabled={isLoading}
                    />
                    {errors.semester_end && (
                      <p className="text-sm text-red-500">{errors.semester_end.message}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Courses */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Courses
                </CardTitle>
                <CardDescription>
                  Add all the courses you need to schedule
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {fields.map((field, index) => (
                    <div key={field.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold">Course {index + 1}</h3>
                        {fields.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeCourse(index)}
                            className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Course Name *</Label>
                          <Input
                            {...register(`courses.${index}.name`)}
                            placeholder="Introduction to Computer Science"
                            disabled={isLoading}
                          />
                          {errors.courses?.[index]?.name && (
                            <p className="text-sm text-red-500">{errors.courses[index].name.message}</p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label>Course Code *</Label>
                          <Input
                            {...register(`courses.${index}.code`)}
                            placeholder="CS 101"
                            disabled={isLoading}
                          />
                          {errors.courses?.[index]?.code && (
                            <p className="text-sm text-red-500">{errors.courses[index].code.message}</p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label>Credits *</Label>
                          <Input
                            type="number"
                            {...register(`courses.${index}.credits`, { valueAsNumber: true })}
                            min="1"
                            max="12"
                            disabled={isLoading}
                          />
                          {errors.courses?.[index]?.credits && (
                            <p className="text-sm text-red-500">{errors.courses[index].credits.message}</p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label>Difficulty</Label>
                          <select
                            {...register(`courses.${index}.difficulty`)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 dark:border-gray-600 dark:bg-gray-700"
                            disabled={isLoading}
                          >
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                          </select>
                        </div>

                        <div className="space-y-2">
                          <Label>Location</Label>
                          <Input
                            {...register(`courses.${index}.location`)}
                            placeholder="Building A, Room 101"
                            disabled={isLoading}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label>Instructor</Label>
                          <Input
                            {...register(`courses.${index}.instructor`)}
                            placeholder="Dr. Jane Smith"
                            disabled={isLoading}
                          />
                        </div>
                      </div>
                    </div>
                  ))}

                  <Button type="button" onClick={addCourse} variant="outline" disabled={isLoading} className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Another Course
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Preferences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Preferences
                </CardTitle>
                <CardDescription>
                  Configure your scheduling preferences and learning patterns
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="max_daily_courses">Max Courses Per Day</Label>
                    <Input
                      id="max_daily_courses"
                      type="number"
                      {...register('preferences.max_daily_courses', { valueAsNumber: true })}
                      min="1"
                      max="8"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="break_duration">Break Duration (minutes)</Label>
                    <Input
                      id="break_duration"
                      type="number"
                      {...register('preferences.break_duration', { valueAsNumber: true })}
                      min="5"
                      max="120"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="energy_pattern">Energy Pattern</Label>
                    <select
                      id="energy_pattern"
                      {...register('preferences.energy_pattern')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 dark:border-gray-600 dark:bg-gray-700"
                      disabled={isLoading}
                    >
                      <option value="morning_person">Morning Person</option>
                      <option value="evening_person">Evening Person</option>
                      <option value="flexible">Flexible</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Preferred Days</Label>
                  <div className="flex flex-wrap gap-2">
                    {weekdays.map((day) => (
                      <Button
                        key={day}
                        type="button"
                        variant={preferredDays.includes(day) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleDayToggle(day)}
                        disabled={isLoading}
                        className={preferredDays.includes(day) 
                          ? "bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500" 
                          : "text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                        }
                      >
                        {day}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Peak Learning Hours</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {hourRanges.map((hour) => (
                      <Button
                        key={hour}
                        type="button"
                        variant={peakHours.includes(hour) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handlePeakHourToggle(hour)}
                        disabled={isLoading}
                        className={peakHours.includes(hour) 
                          ? "bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500" 
                          : "text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                        }
                      >
                        {hour}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      {...register('preferences.create_calendar_events')}
                      disabled={isLoading}
                    />
                    Create Google Calendar Events
                  </Label>
                </div>
              </CardContent>
            </Card>

            {/* Constraints */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Constraints
                </CardTitle>
                <CardDescription>
                  Define scheduling constraints and unavailable times
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="max_travel_time">Max Travel Time Between Classes (minutes)</Label>
                  <Input
                    id="max_travel_time"
                    type="number"
                    {...register('constraints.max_travel_time', { valueAsNumber: true })}
                    min="0"
                    max="120"
                    disabled={isLoading}
                  />
                </div>

                <div className="space-y-4">
                  <Label>Unavailable Times</Label>
                  <div className="flex gap-2">
                    <Input
                      value={unavailableTimeInput}
                      onChange={(e) => setUnavailableTimeInput(e.target.value)}
                      placeholder="e.g., Monday 10:00-12:00"
                      disabled={isLoading}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray(unavailableTimes, setUnavailableTimes, unavailableTimeInput, setUnavailableTimeInput))}
                    />
                    <Button 
                      type="button" 
                      onClick={() => addToArray(unavailableTimes, setUnavailableTimes, unavailableTimeInput, setUnavailableTimeInput)} 
                      disabled={isLoading} 
                      size="sm"
                      className="bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500"
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {unavailableTimes.length > 0 && (
                    <div className="space-y-2">
                      {unavailableTimes.map((time, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-red-50 dark:bg-red-900/20 rounded">
                          <Clock className="h-4 w-4 text-red-500" />
                          <span className="flex-1">{time}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFromArray(unavailableTimes, setUnavailableTimes, index)}
                            className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-100 dark:hover:bg-red-900/40"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <Label>Mandatory Breaks</Label>
                  <div className="flex gap-2">
                    <Input
                      value={mandatoryBreakInput}
                      onChange={(e) => setMandatoryBreakInput(e.target.value)}
                      placeholder="e.g., Lunch 12:00-13:00"
                      disabled={isLoading}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray(mandatoryBreaks, setMandatoryBreaks, mandatoryBreakInput, setMandatoryBreakInput))}
                    />
                    <Button 
                      type="button" 
                      onClick={() => addToArray(mandatoryBreaks, setMandatoryBreaks, mandatoryBreakInput, setMandatoryBreakInput)} 
                      disabled={isLoading} 
                      size="sm"
                      className="bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500"
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {mandatoryBreaks.length > 0 && (
                    <div className="space-y-2">
                      {mandatoryBreaks.map((breakTime, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                          <Timer className="h-4 w-4 text-blue-500" />
                          <span className="flex-1">{breakTime}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFromArray(mandatoryBreaks, setMandatoryBreaks, index)}
                            className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900/40"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Debug Section - Remove in production */}
            {Object.keys(errors).length > 0 && (
              <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
                <CardHeader>
                  <CardTitle className="text-red-600 dark:text-red-400">Form Validation Errors</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-sm text-red-600 dark:text-red-400">
                    {JSON.stringify(errors, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )}

            <div className="flex gap-4 pt-6">
              <Button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500"
                variant="default"
                onClick={() => {
                  console.log('Submit button clicked');
                  console.log('Form errors:', errors);
                  console.log('Current form values:', watch());
                }}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Schedule...
                  </>
                ) : (
                  <>
                    <Calendar className="mr-2 h-4 w-4" />
                    Create Schedule
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={resetForm}
                disabled={isLoading}
                className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                Reset
              </Button>
            </div>
          </form>

          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    Schedule Created Successfully
                  </CardTitle>
                  <CardDescription>
                    Session ID: {result.session_id}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <p className="text-green-800 dark:text-green-200">
                        <strong>Status:</strong> {result.status}
                      </p>
                      <p className="text-green-700 dark:text-green-300">
                        {result.message}
                      </p>
                    </div>

                    {result.result && (
                      <div className="space-y-4">
                        <div className="p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Calendar className="h-5 w-5" />
                            Generated Schedule
                          </h3>
                          <div className="prose dark:prose-invert max-w-none">
                            {typeof result.result === 'string' ? (
                              <pre className="whitespace-pre-wrap text-sm">{result.result}</pre>
                            ) : (
                              <pre className="whitespace-pre-wrap text-sm">
                                {JSON.stringify(result.result, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>

                        <div className="flex gap-4">
                          <Button
                            onClick={() => {
                              const scheduleContent = typeof result.result === 'string' 
                                ? result.result 
                                : JSON.stringify(result.result, null, 2);
                              const blob = new Blob([scheduleContent], { type: 'text/plain' });
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement('a');
                              a.href = url;
                              a.download = `schedule_${result.session_id}.txt`;
                              a.click();
                              URL.revokeObjectURL(url);
                            }}
                            variant="outline"
                            className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                          >
                            <Download className="mr-2 h-4 w-4" />
                            Download Schedule
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
