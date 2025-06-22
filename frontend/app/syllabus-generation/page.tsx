'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { 
  BookOpen, 
  GraduationCap, 
  Target, 
  Clock, 
  User, 
  Building, 
  FileText,
  Download,
  Loader2,
  CheckCircle,
  AlertCircle,
  Plus,
  X,
  Calendar,
  BookMarked,
  Users,
  PenTool,
  Award,
  Library,
  ChevronRight,
  ExternalLink,
  TrendingUp
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/lib/auth-context';
import { academicAPI, type SyllabusRequest, type AcademicResponse } from '@/lib/api';
import AuthComponent from '@/components/auth-component';

const syllabusSchema = z.object({
  courseName: z.string().min(2, 'Course name must be at least 2 characters'),
  courseCode: z.string().min(2, 'Course code is required'),
  courseDescription: z.string().min(10, 'Description must be at least 10 characters'),
  credits: z.number().min(1).max(12),
  level: z.enum(['beginner', 'intermediate', 'advanced']),
  department: z.string().optional(),
  instructor: z.string().optional(),
  learningObjectives: z.array(z.string()).min(1, 'At least one learning objective is required'),
  studentLevel: z.enum(['undergraduate', 'graduate', 'professional']),
  durationWeeks: z.number().min(1).max(52),
  teachingStyle: z.enum(['lecture', 'seminar', 'lab', 'project', 'mixed']).optional(),
  assessmentTypes: z.array(z.string()).optional(),
  contentFormat: z.enum(['traditional', 'modern', 'practical', 'theoretical']).optional(),
  includeResources: z.boolean().optional(),
});

type SyllabusFormData = z.infer<typeof syllabusSchema>;

export default function SyllabusGenerationPage() {
  const { currentUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AcademicResponse | null>(null);
  const [objectiveInput, setObjectiveInput] = useState('');
  const [assessmentInput, setAssessmentInput] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    reset,
  } = useForm<SyllabusFormData>({
    resolver: zodResolver(syllabusSchema),
    defaultValues: {
      credits: 3,
      level: 'intermediate',
      studentLevel: 'undergraduate',
      durationWeeks: 16,
      teachingStyle: 'mixed',
      contentFormat: 'modern',
      includeResources: true,
      learningObjectives: [],
      assessmentTypes: [],
    },
  });

  const learningObjectives = watch('learningObjectives') || [];
  const assessmentTypes = watch('assessmentTypes') || [];

  const addLearningObjective = () => {
    if (objectiveInput.trim()) {
      setValue('learningObjectives', [...learningObjectives, objectiveInput.trim()]);
      setObjectiveInput('');
    }
  };

  const removeLearningObjective = (index: number) => {
    setValue('learningObjectives', learningObjectives.filter((_, i) => i !== index));
  };

  const addAssessmentType = () => {
    if (assessmentInput.trim() && !assessmentTypes.includes(assessmentInput.trim())) {
      setValue('assessmentTypes', [...assessmentTypes, assessmentInput.trim()]);
      setAssessmentInput('');
    }
  };

  const removeAssessmentType = (index: number) => {
    setValue('assessmentTypes', assessmentTypes.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: SyllabusFormData) => {
    if (!currentUser) {
      toast({
        title: 'Authentication Required',
        description: 'Please sign in to generate a syllabus.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const token = await currentUser.getIdToken();
      
      const request: SyllabusRequest = {
        course_info: {
          name: data.courseName,
          code: data.courseCode,
          description: data.courseDescription,
          credits: data.credits,
          level: data.level,
          department: data.department || '',
          instructor: data.instructor || '',
        },
        learning_objectives: data.learningObjectives,
        student_level: data.studentLevel,
        duration_weeks: data.durationWeeks,
        preferences: {
          teaching_style: data.teachingStyle,
          assessment_types: data.assessmentTypes,
          content_format: data.contentFormat,
          include_resources: data.includeResources,
        },
      };

      const response = await academicAPI.generateSyllabus(request, token);
      setResult(response);
      
      toast({
        title: 'Success!',
        description: 'Syllabus generated successfully.',
      });
    } catch (error: any) {
      console.error('Error generating syllabus:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to generate syllabus. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    reset();
    setResult(null);
    setObjectiveInput('');
    setAssessmentInput('');
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
        <div className="container mx-auto px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Syllabus Generation
            </h1>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Please sign in to access the AI-powered syllabus generation tool.
            </p>
          </motion.div>
          
          <div className="max-w-md mx-auto">
            <AuthComponent />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
      <div className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <BookOpen className="h-10 w-10 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Syllabus Generation
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Create comprehensive, AI-powered course syllabi tailored to your educational objectives and requirements.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Course Information
              </CardTitle>
              <CardDescription>
                Provide basic information about your course
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="courseName">Course Name *</Label>
                    <Input
                      id="courseName"
                      {...register('courseName')}
                      placeholder="Introduction to Machine Learning"
                      disabled={isLoading}
                    />
                    {errors.courseName && (
                      <p className="text-sm text-red-500">{errors.courseName.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="courseCode">Course Code *</Label>
                    <Input
                      id="courseCode"
                      {...register('courseCode')}
                      placeholder="CS 4XX"
                      disabled={isLoading}
                    />
                    {errors.courseCode && (
                      <p className="text-sm text-red-500">{errors.courseCode.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="credits">Credits *</Label>
                    <Input
                      id="credits"
                      type="number"
                      {...register('credits', { valueAsNumber: true })}
                      min="1"
                      max="12"
                      disabled={isLoading}
                    />
                    {errors.credits && (
                      <p className="text-sm text-red-500">{errors.credits.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="level">Course Level *</Label>
                    <select
                      id="level"
                      {...register('level')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                      disabled={isLoading}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input
                      id="department"
                      {...register('department')}
                      placeholder="Computer Science"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="instructor">Instructor</Label>
                    <Input
                      id="instructor"
                      {...register('instructor')}
                      placeholder="Dr. Jane Smith"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="courseDescription">Course Description *</Label>
                  <Textarea
                    id="courseDescription"
                    {...register('courseDescription')}
                    placeholder="Describe the course content, objectives, and what students will learn..."
                    rows={4}
                    disabled={isLoading}
                  />
                  {errors.courseDescription && (
                    <p className="text-sm text-red-500">{errors.courseDescription.message}</p>
                  )}
                </div>

                <div className="space-y-4">
                  <Label>Learning Objectives *</Label>
                  <div className="flex gap-2">
                    <Input
                      value={objectiveInput}
                      onChange={(e) => setObjectiveInput(e.target.value)}
                      placeholder="Add a learning objective..."
                      disabled={isLoading}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLearningObjective())}
                    />
                    <Button type="button" onClick={addLearningObjective} disabled={isLoading} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {learningObjectives.length > 0 && (
                    <div className="space-y-2">
                      {learningObjectives.map((objective, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <Target className="h-4 w-4 text-blue-500" />
                          <span className="flex-1">{objective}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeLearningObjective(index)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  {errors.learningObjectives && (
                    <p className="text-sm text-red-500">{errors.learningObjectives.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="studentLevel">Student Level *</Label>
                    <select
                      id="studentLevel"
                      {...register('studentLevel')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                      disabled={isLoading}
                    >
                      <option value="undergraduate">Undergraduate</option>
                      <option value="graduate">Graduate</option>
                      <option value="professional">Professional</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="durationWeeks">Duration (Weeks) *</Label>
                    <Input
                      id="durationWeeks"
                      type="number"
                      {...register('durationWeeks', { valueAsNumber: true })}
                      min="1"
                      max="52"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="teachingStyle">Teaching Style</Label>
                    <select
                      id="teachingStyle"
                      {...register('teachingStyle')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                      disabled={isLoading}
                    >
                      <option value="lecture">Lecture</option>
                      <option value="seminar">Seminar</option>
                      <option value="lab">Laboratory</option>
                      <option value="project">Project-based</option>
                      <option value="mixed">Mixed</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Assessment Types</Label>
                  <div className="flex gap-2">
                    <Input
                      value={assessmentInput}
                      onChange={(e) => setAssessmentInput(e.target.value)}
                      placeholder="Add assessment type (e.g., Midterm Exam, Final Project)..."
                      disabled={isLoading}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAssessmentType())}
                    />
                    <Button type="button" onClick={addAssessmentType} disabled={isLoading} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {assessmentTypes.length > 0 && (
                    <div className="space-y-2">
                      {assessmentTypes.map((assessment, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="flex-1">{assessment}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeAssessmentType(index)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="contentFormat">Content Format</Label>
                    <select
                      id="contentFormat"
                      {...register('contentFormat')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                      disabled={isLoading}
                    >
                      <option value="traditional">Traditional</option>
                      <option value="modern">Modern</option>
                      <option value="practical">Practical</option>
                      <option value="theoretical">Theoretical</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        {...register('includeResources')}
                        disabled={isLoading}
                      />
                      Include Learning Resources
                    </Label>
                  </div>
                </div>

                <div className="flex gap-4 pt-6">
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating Syllabus...
                      </>
                    ) : (
                      <>
                        <BookOpen className="mr-2 h-4 w-4" />
                        Generate Syllabus
                      </>
                    )}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={resetForm}
                    disabled={isLoading}
                  >
                    Reset
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {result && <SyllabusResults result={result} />}
        </div>
      </div>
    </div>
  );
}

// Helper function to get week color based on week number
function getWeekColor(weekNum: number): string {
  const colors = [
    'from-blue-500 to-blue-600',
    'from-green-500 to-green-600', 
    'from-purple-500 to-purple-600',
    'from-orange-500 to-orange-600',
    'from-pink-500 to-pink-600',
    'from-indigo-500 to-indigo-600',
    'from-teal-500 to-teal-600',
    'from-red-500 to-red-600',
  ];
  return colors[weekNum % colors.length];
}

// Component to display syllabus results in an interactive format
function SyllabusResults({ result }: { result: AcademicResponse }) {
  const [activeTab, setActiveTab] = useState<'overview' | 'schedule' | 'assessments' | 'resources'>('overview');
  const [selectedWeek, setSelectedWeek] = useState<string | null>(null);

  if (!result.result) return null;

  const syllabusData = result.result;
  console.log('Syllabus Data:', syllabusData); // Debug log
  
  // Extract data using the standardized format
  const syllabus = syllabusData.syllabus || {};
  const weeklySchedule = syllabus.weekly_schedule || {};
  const courseOverview = syllabus.course_overview || {};
  const assessments = syllabus.assessments || {};
  const resources = syllabus.resources || {};
  const courseStructure = syllabus.structure || {};
  const methodology = syllabus.methodology || {};
  const policies = syllabus.policies || {};
  const support = syllabus.support || {};
  
  // Get the actual weekly schedule data (handle the direct structure from backend)
  const actualWeeklySchedule = weeklySchedule || {};
  
  console.log('Raw Weekly Schedule:', weeklySchedule); // Debug log
  console.log('Processed Weekly Schedule:', actualWeeklySchedule); // Debug log
  console.log('Weekly Schedule Keys:', Object.keys(actualWeeklySchedule)); // Debug log
  console.log('Course Overview:', courseOverview); // Debug log

  const downloadSyllabus = () => {
    const syllabusContent = JSON.stringify(syllabusData, null, 2);
    const blob = new Blob([syllabusContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `syllabus_${result.session_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Success Header */}
      <Card className="border-green-200 bg-green-50/50 dark:bg-green-900/10 dark:border-green-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Syllabus Generated Successfully
          </CardTitle>
          <CardDescription className="text-green-700 dark:text-green-300">
            {result.message} • Session ID: {result.session_id}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Navigation Tabs */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'overview', label: 'Course Overview', icon: BookOpen },
              { id: 'schedule', label: 'Weekly Schedule', icon: Calendar },
              { id: 'assessments', label: 'Assessments', icon: Award },
              { id: 'resources', label: 'Resources', icon: Library },
            ].map(({ id, label, icon: Icon }) => (
              <Button
                key={id}
                variant={activeTab === id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveTab(id as any)}
                className="flex items-center gap-2"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Button>
            ))}
            <div className="ml-auto">
              <Button onClick={downloadSyllabus} variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Course Overview Tab */}
          {activeTab === 'overview' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              {/* Debug information */}
              <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs">
                <details>
                  <summary className="cursor-pointer font-semibold mb-2">Debug Info (Click to expand)</summary>
                  <pre className="whitespace-pre-wrap overflow-x-auto">
                    {JSON.stringify(syllabusData, null, 2)}
                  </pre>
                </details>
              </div>

              {/* Course Description */}
              {courseOverview.description ? (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">Course Description</h3>
                  <p className="text-blue-800 dark:text-blue-300">{courseOverview.description}</p>
                </div>
              ) : (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <h3 className="font-semibold text-yellow-900 dark:text-yellow-200 mb-2">Course Overview</h3>
                  <p className="text-yellow-800 dark:text-yellow-300">
                    Your personalized syllabus has been generated! Use the tabs above to explore different sections.
                  </p>
                </div>
              )}

              {/* Prerequisites */}
              {courseOverview.prerequisites && (
                <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                  <h3 className="font-semibold text-orange-900 dark:text-orange-200 mb-2">Prerequisites</h3>
                  <p className="text-orange-800 dark:text-orange-300">{courseOverview.prerequisites}</p>
                </div>
              )}

              {/* Learning Outcomes */}
              {courseOverview.learning_outcomes && courseOverview.learning_outcomes.length > 0 && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <h3 className="font-semibold text-green-900 dark:text-green-200 mb-3">Learning Outcomes</h3>
                  <ul className="space-y-2">
                    {courseOverview.learning_outcomes.map((outcome: string, index: number) => (
                      <li key={index} className="flex items-start gap-2 text-green-800 dark:text-green-300">
                        <Target className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>{outcome}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Course Structure */}
                {courseStructure && Object.keys(courseStructure).length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Building className="h-4 w-4" />
                      Course Structure
                    </h3>
                    <div className="space-y-2">
                      {courseStructure.major_topics && (
                        <div>
                          <h4 className="font-medium text-sm">Major Topics:</h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-400 ml-4">
                            {courseStructure.major_topics.map((topic: string, index: number) => (
                              <li key={index} className="list-disc">{topic}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {courseStructure.learning_progression && (
                        <div>
                          <h4 className="font-medium text-sm">Learning Progression:</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{courseStructure.learning_progression}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Teaching Methodology */}
                {methodology && Object.keys(methodology).length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      Teaching Methodology
                    </h3>
                    <div className="space-y-2">
                      {methodology.strategies && (
                        <div>
                          <h4 className="font-medium text-sm">Teaching Strategies:</h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-400 ml-4">
                            {methodology.strategies.map((strategy: string, index: number) => (
                              <li key={index} className="list-disc">{strategy}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {methodology.technology && (
                        <div>
                          <h4 className="font-medium text-sm">Technology Used:</h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-400 ml-4">
                            {methodology.technology.map((tech: string, index: number) => (
                              <li key={index} className="list-disc">{tech}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Policies */}
                {policies && Object.keys(policies).length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Course Policies
                    </h3>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      {policies.attendance && (
                        <div>
                          <strong>Attendance:</strong> {policies.attendance}
                        </div>
                      )}
                      {policies.late_work && (
                        <div>
                          <strong>Late Work:</strong> {policies.late_work}
                        </div>
                      )}
                      {policies.integrity && (
                        <div>
                          <strong>Academic Integrity:</strong> {policies.integrity}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Support */}
                {support && Object.keys(support).length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      Student Support
                    </h3>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      {support.office_hours && (
                        <div>
                          <strong>Office Hours:</strong> {support.office_hours}
                        </div>
                      )}
                      {support.resources && support.resources.length > 0 && (
                        <div>
                          <strong>Support Resources:</strong>
                          <ul className="ml-4">
                            {support.resources.map((resource: string, index: number) => (
                              <li key={index} className="list-disc">{resource}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Show adaptation score if available */}
              {syllabusData.adaptation_score && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <h3 className="font-semibold text-green-900 dark:text-green-200 mb-2">Customization Quality</h3>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-green-200 dark:bg-green-800 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${syllabusData.adaptation_score}%` }}
                      ></div>
                    </div>
                    <span className="text-green-800 dark:text-green-300 font-semibold">
                      {syllabusData.adaptation_score}%
                    </span>
                  </div>
                  <p className="text-sm text-green-700 dark:text-green-400 mt-2">
                    Your syllabus has been highly customized to your preferences!
                  </p>
                </div>
              )}
            </motion.div>
          )}

          {/* Weekly Schedule Tab */}
          {activeTab === 'schedule' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <h3 className="text-lg font-semibold mb-2">Interactive Weekly Calendar</h3>
                <p className="text-gray-600 dark:text-gray-400">Click on any week to see detailed content</p>
              </div>

              {Object.keys(actualWeeklySchedule).length > 0 ? (
                <>
                  <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm">
                    <strong>Debug Info:</strong> Found {Object.keys(actualWeeklySchedule).length} weeks: {Object.keys(actualWeeklySchedule).join(', ')}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {Object.entries(actualWeeklySchedule).map(([weekKey, weekData]: [string, any], index) => {
                      const weekNum = parseInt(weekKey.replace('Week_', '').replace(/\D/g, '')) || index + 1;
                      const isSelected = selectedWeek === weekKey;
                      
                      // Handle standardized data structure
                      const topics = weekData.topics || [];
                      const activities = weekData.learning_activities || [];
                      const assessments = weekData.assessments_milestones || [];
                      const skillBuilding = weekData.progressive_skill_building || [];
                      const title = `Week ${weekNum}`;
                      
                      return (
                        <motion.div
                          key={weekKey}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className={`relative cursor-pointer transition-all duration-200 ${
                            isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
                          }`}
                          onClick={() => setSelectedWeek(isSelected ? null : weekKey)}
                        >
                          <Card className={`h-full bg-gradient-to-br ${getWeekColor(index)} text-white border-0 shadow-lg`}>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-lg font-bold">
                                Week {weekNum}
                              </CardTitle>
                              <div className="text-sm font-medium text-white/90 line-clamp-2">
                                {topics.length > 0 ? topics[0] : 'Course Content'}
                              </div>
                              <div className="flex items-center gap-1 text-white/80">
                                <Calendar className="h-3 w-3" />
                                <span className="text-xs">
                                  {topics.length || 0} topics
                                </span>
                              </div>
                            </CardHeader>
                            <CardContent className="space-y-2">
                              {topics && topics.slice(0, 2).map((topic: string, i: number) => (
                                <div key={i} className="text-xs bg-white/20 rounded px-2 py-1 backdrop-blur-sm line-clamp-2">
                                  {topic}
                                </div>
                              ))}
                              {topics && topics.length > 2 && (
                                <div className="text-xs text-white/70">
                                  +{topics.length - 2} more topics
                                </div>
                              )}
                              {assessments && assessments.length > 0 && assessments.some((a: string) => a && a.trim()) && (
                                <div className="flex items-center gap-1 mt-2">
                                  <Award className="h-3 w-3" />
                                  <span className="text-xs font-semibold">Assessment Due</span>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </motion.div>
                      );
                    })}
                  </div>

                  {/* Detailed Week View */}
                  {selectedWeek && actualWeeklySchedule[selectedWeek] && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6"
                    >
                      <Card className="border-2 border-blue-200 dark:border-blue-800">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <BookMarked className="h-5 w-5 text-blue-600" />
                            {selectedWeek.replace('Week_', 'Week ')} Details
                          </CardTitle>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedWeek(null)}
                            className="absolute top-4 right-4"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </CardHeader>
                        <CardContent className="space-y-6">
                          {/* Topics */}
                          {actualWeeklySchedule[selectedWeek].topics && actualWeeklySchedule[selectedWeek].topics.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <BookOpen className="h-4 w-4" />
                                Topics Covered
                              </h4>
                              <ul className="space-y-2">
                                {actualWeeklySchedule[selectedWeek].topics.map((topic: string, index: number) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <ChevronRight className="h-4 w-4 mt-0.5 text-blue-500 flex-shrink-0" />
                                    <span className="text-sm">{topic}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Learning Activities */}
                          {actualWeeklySchedule[selectedWeek].learning_activities && actualWeeklySchedule[selectedWeek].learning_activities.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <Users className="h-4 w-4" />
                                Learning Activities
                              </h4>
                              <ul className="space-y-2">
                                {actualWeeklySchedule[selectedWeek].learning_activities.map((activity: string, index: number) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <PenTool className="h-4 w-4 mt-0.5 text-green-500 flex-shrink-0" />
                                    <span className="text-sm">{activity}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Readings & Resources */}
                          {actualWeeklySchedule[selectedWeek].readings_resources && actualWeeklySchedule[selectedWeek].readings_resources.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <Library className="h-4 w-4" />
                                Readings & Resources
                              </h4>
                              <ul className="space-y-2">
                                {actualWeeklySchedule[selectedWeek].readings_resources.map((resource: string, index: number) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <BookMarked className="h-4 w-4 mt-0.5 text-purple-500 flex-shrink-0" />
                                    <span className="text-sm">{resource}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Assessments & Milestones */}
                          {actualWeeklySchedule[selectedWeek].assessments_milestones && actualWeeklySchedule[selectedWeek].assessments_milestones.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <Award className="h-4 w-4" />
                                Assessments & Milestones
                              </h4>
                              <ul className="space-y-2">
                                {actualWeeklySchedule[selectedWeek].assessments_milestones.filter((assessment: string) => assessment && assessment.trim()).map((assessment: string, index: number) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <Award className="h-4 w-4 mt-0.5 text-yellow-500 flex-shrink-0" />
                                    <span className="text-sm">{assessment}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Progressive Skill Building */}
                          {actualWeeklySchedule[selectedWeek].progressive_skill_building && actualWeeklySchedule[selectedWeek].progressive_skill_building.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <TrendingUp className="h-4 w-4" />
                                Skill Development
                              </h4>
                              <ul className="space-y-2">
                                {actualWeeklySchedule[selectedWeek].progressive_skill_building.map((skill: string, index: number) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <TrendingUp className="h-4 w-4 mt-0.5 text-indigo-500 flex-shrink-0" />
                                    <span className="text-sm">{skill}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </>
              ) : (
                <div className="text-center py-12">
                  <Calendar className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Weekly Schedule Available</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    The syllabus was generated but doesn't contain detailed weekly breakdowns.
                  </p>
                  <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm text-left">
                    <strong>Debug Info:</strong>
                    <br />Weekly Schedule Keys: {Object.keys(actualWeeklySchedule).length}
                    <br />Raw Weekly Schedule: {JSON.stringify(weeklySchedule, null, 2).slice(0, 200)}...
                    <br />Actual Weekly Schedule: {JSON.stringify(actualWeeklySchedule, null, 2).slice(0, 200)}...
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Assessments Tab */}
          {activeTab === 'assessments' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Weight Distribution */}
                {assessments.assessment_plan?.weight_distribution && (
                  <Card className="border-purple-200 bg-purple-50/50 dark:bg-purple-900/10 dark:border-purple-800">
                    <CardHeader>
                      <CardTitle className="text-purple-800 dark:text-purple-200">Grade Distribution</CardTitle>
                      <CardDescription className="text-purple-600 dark:text-purple-400">
                        How your final grade is calculated
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {Object.entries(assessments.assessment_plan.weight_distribution).map(([type, weight]: [string, any]) => (
                        <div key={type} className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded border">
                          <span className="font-medium capitalize">{type.replace('_', ' ')}</span>
                          <span className="font-semibold text-purple-600">{weight}</span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Assessment Overview */}
                {assessments.assessment_plan?.overview && (
                  <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-900/10 dark:border-blue-800">
                    <CardHeader>
                      <CardTitle className="text-blue-800 dark:text-blue-200">Assessment Overview</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-blue-700 dark:text-blue-300">{assessments.assessment_plan.overview}</p>
                    </CardContent>
                  </Card>
                )}

                {/* Formative Assessments */}
                {assessments.assessment_plan?.formative_assessments && assessments.assessment_plan.formative_assessments.length > 0 && (
                  <Card className="border-green-200 bg-green-50/50 dark:bg-green-900/10 dark:border-green-800">
                    <CardHeader>
                      <CardTitle className="text-green-800 dark:text-green-200">Formative Assessments</CardTitle>
                      <CardDescription className="text-green-600 dark:text-green-400">
                        Ongoing evaluation and feedback
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {assessments.assessment_plan.formative_assessments.map((assessment: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{assessment.assessment_type}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {assessment.description}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-500">
                            Weight: {assessment.weight} • Frequency: {assessment.frequency} • Timing: {assessment.timing}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Summative Assessments */}
                {assessments.assessment_plan?.summative_assessments && assessments.assessment_plan.summative_assessments.length > 0 && (
                  <Card className="border-orange-200 bg-orange-50/50 dark:bg-orange-900/10 dark:border-orange-800">
                    <CardHeader>
                      <CardTitle className="text-orange-800 dark:text-orange-200">Summative Assessments</CardTitle>
                      <CardDescription className="text-orange-600 dark:text-orange-400">
                        Major evaluations and grading
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {assessments.assessment_plan.summative_assessments.map((assessment: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{assessment.assessment_type}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {assessment.description}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-500">
                            Weight: {assessment.weight} • Timing: {assessment.timing}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </div>
            </motion.div>
          )}

          {/* Resources Tab */}
          {activeTab === 'resources' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Required Textbooks */}
                {resources.resources?.required_textbooks_and_materials && resources.resources.required_textbooks_and_materials.length > 0 && (
                  <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-900/10 dark:border-blue-800">
                    <CardHeader>
                      <CardTitle className="text-blue-800 dark:text-blue-200">Required Textbooks</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.required_textbooks_and_materials.map((book: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{book.title || 'Textbook'}</div>
                          {book.author && <div className="text-sm text-gray-600 dark:text-gray-400">by {book.author}</div>}
                          {book.notes && <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">{book.notes}</div>}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Supplementary Readings */}
                {resources.resources?.supplementary_readings && resources.resources.supplementary_readings.length > 0 && (
                  <Card className="border-green-200 bg-green-50/50 dark:bg-green-900/10 dark:border-green-800">
                    <CardHeader>
                      <CardTitle className="text-green-800 dark:text-green-200">Supplementary Readings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.supplementary_readings.map((reading: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{reading.title || 'Reading Material'}</div>
                          {reading.author && <div className="text-sm text-gray-600 dark:text-gray-400">by {reading.author}</div>}
                          {reading.notes && <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">{reading.notes}</div>}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Online Resources */}
                {resources.resources?.online_resources_and_tools && resources.resources.online_resources_and_tools.length > 0 && (
                  <Card className="border-purple-200 bg-purple-50/50 dark:bg-purple-900/10 dark:border-purple-800">
                    <CardHeader>
                      <CardTitle className="text-purple-800 dark:text-purple-200">Online Resources</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.online_resources_and_tools.map((resource: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold flex items-center gap-2">
                            <ExternalLink className="h-4 w-4" />
                            {resource.name || 'Online Resource'}
                          </div>
                          {resource.description && <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{resource.description}</div>}
                          {resource.url && (
                            <div className="text-xs text-purple-600 dark:text-purple-400 mt-1 truncate">
                              {resource.url}
                            </div>
                          )}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Multimedia Content */}
                {resources.resources?.multimedia_content && resources.resources.multimedia_content.length > 0 && (
                  <Card className="border-orange-200 bg-orange-50/50 dark:bg-orange-900/10 dark:border-orange-800">
                    <CardHeader>
                      <CardTitle className="text-orange-800 dark:text-orange-200">Multimedia Content</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.multimedia_content.map((content: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{content.title || content.type || 'Multimedia'}</div>
                          {content.description && <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{content.description}</div>}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Research Databases */}
                {resources.resources?.research_databases && resources.resources.research_databases.length > 0 && (
                  <Card className="border-indigo-200 bg-indigo-50/50 dark:bg-indigo-900/10 dark:border-indigo-800">
                    <CardHeader>
                      <CardTitle className="text-indigo-800 dark:text-indigo-200">Research Databases</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.research_databases.map((database: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold flex items-center gap-2">
                            <Library className="h-4 w-4" />
                            {database.name || 'Research Database'}
                          </div>
                          {database.description && <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{database.description}</div>}
                          {database.url && (
                            <div className="text-xs text-indigo-600 dark:text-indigo-400 mt-1 truncate">
                              {database.url}
                            </div>
                          )}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Study Materials */}
                {resources.resources?.study_guides_and_practice_materials && resources.resources.study_guides_and_practice_materials.length > 0 && (
                  <Card className="border-teal-200 bg-teal-50/50 dark:bg-teal-900/10 dark:border-teal-800">
                    <CardHeader>
                      <CardTitle className="text-teal-800 dark:text-teal-200">Study Materials</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {resources.resources.study_guides_and_practice_materials.map((material: any, i: number) => (
                        <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded border">
                          <div className="font-semibold">{material.title || material.type || 'Study Material'}</div>
                          {material.description && <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{material.description}</div>}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
