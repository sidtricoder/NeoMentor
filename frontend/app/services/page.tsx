"use client"

import Link from 'next/link';
import { motion } from 'framer-motion';

import { Button } from '@/components/ui/button';

const services = [
  {
    id: 'video-generation',
    icon: '🎬',
    title: 'Video Generation',
    description: 'Transform your educational content into engaging AI-powered videos with personalized avatars and voice synthesis.',
    features: [
      'AI-generated avatars',
      'Voice cloning & synthesis',
      'Custom duration control',
      'High-quality output'
    ],
    color: 'blue',
    cta: 'Get Started',
    href: '/video-generation'
  },
  {
    id: 'syllabus-generation',
    icon: '📚',
    title: 'Syllabus Generation',
    description: 'Create comprehensive, personalized course syllabi with AI-powered content structuring and learning objective alignment.',
    features: [
      'Learning objectives mapping',
      'Assessment planning',
      'Resource recommendations',
      'Flexible duration planning'
    ],
    color: 'green',
    cta: 'Create Syllabus',
    href: '/syllabus-generation'
  },
  {
    id: 'course-scheduler',
    icon: '📅',
    title: 'Course Scheduler',
    description: 'Optimize your academic schedule with AI-powered planning that considers preferences, constraints, and learning patterns.',
    features: [
      'Smart time optimization',
      'Conflict resolution',
      'Learning pattern analysis',
      'Calendar integration'
    ],
    color: 'purple',
    cta: 'Plan Schedule',
    href: '/course-scheduler'
  },
  {
    id: 'voice-cloning',
    icon: '🎤',
    title: 'Voice Cloning',
    description: 'Clone any voice using advanced F5-TTS technology. Upload reference audio and generate speech with that voice.',
    features: [
      'F5-TTS technology',
      'High-quality synthesis',
      'Custom voice training',
      'Multiple audio formats'
    ],
    color: 'pink',
    cta: 'Clone Voice',
    href: '/voice-cloning'
  },
  {
    id: 'analytics',
    icon: '📊',
    title: 'Learning Analytics',
    description: 'Detailed insights into learning progress and comprehension patterns to optimize study strategies and improve educational outcomes.',
    features: [
      'Performance tracking',
      'Usage pattern analysis',
      'AI-powered insights',
      'Progress visualization'
    ],
    color: 'indigo',
    cta: 'View Analytics',
    href: '/analytics'
  },
  {
    id: 'ai-tutor',
    icon: '🤖',
    title: 'AI Personal Tutor',
    description: 'Get personalized one-on-one tutoring with an AI that adapts to your learning style and provides instant feedback.',
    features: [
      'Personalized learning paths',
      'Real-time doubt clearing',
      'Adaptive difficulty levels',
      '24/7 availability'
    ],
    color: 'emerald',
    cta: 'Start Tutoring',
    href: '/coming-soon'
  },
  {
    id: 'skill-assessment',
    icon: '🎯',
    title: 'AI Skill Assessment',
    description: 'Comprehensive skill evaluation using AI-powered assessments that identify strengths, weaknesses, and learning gaps.',
    features: [
      'Multi-domain testing',
      'Adaptive questioning',
      'Detailed skill mapping',
      'Improvement recommendations'
    ],
    color: 'orange',
    cta: 'Take Assessment',
    href: '/coming-soon'
  },
  {
    id: 'content-generator',
    icon: '✍️',
    title: 'Smart Content Generator',
    description: 'Generate educational content including quizzes, flashcards, and study materials using advanced AI algorithms.',
    features: [
      'Auto-quiz generation',
      'Flashcard creation',
      'Study guides',
      'Practice problems'
    ],
    color: 'teal',
    cta: 'Generate Content',
    href: '/coming-soon'
  },
  {
    id: 'language-learning',
    icon: '🌐',
    title: 'AI Language Learning',
    description: 'Master new languages with AI-powered conversation practice, pronunciation coaching, and personalized lessons.',
    features: [
      'Conversation simulation',
      'Pronunciation analysis',
      'Grammar correction',
      'Cultural context learning'
    ],
    color: 'violet',
    cta: 'Learn Languages',
    href: '/coming-soon'
  },
  {
    id: 'research-assistant',
    icon: '🔬',
    title: 'AI Research Assistant',
    description: 'Accelerate your research with AI-powered literature review, citation management, and hypothesis generation.',
    features: [
      'Literature synthesis',
      'Citation automation',
      'Data analysis assistance',
      'Research methodology guidance'
    ],
    color: 'cyan',
    cta: 'Start Research',
    href: '/coming-soon'
  },
  {
    id: 'exam-prep',
    icon: '📝',
    title: 'Smart Exam Preparation',
    description: 'Prepare for exams with AI-generated practice tests, study schedules, and performance predictions.',
    features: [
      'Predictive scoring',
      'Adaptive practice tests',
      'Study schedule optimization',
      'Weakness identification'
    ],
    color: 'rose',
    cta: 'Prep for Exams',
    href: '/coming-soon'
  },
];

const additionalFeatures = [
  {
    icon: '🧬',
    title: 'Neuroadaptive Learning',
    description: 'AI that adapts to your brain patterns and cognitive load'
  },
  {
    icon: '🎮',
    title: 'Gamified Learning',
    description: 'Turn education into engaging games and challenges'
  },
  {
    icon: '🔮',
    title: 'Predictive Analytics',
    description: 'Forecast learning outcomes and optimize study paths'
  },
  {
    icon: '👥',
    title: 'Collaborative AI',
    description: 'Group learning with AI-facilitated discussions'
  },
  {
    icon: '🎨',
    title: 'Creative Learning Tools',
    description: 'AI-powered mind mapping and visual learning aids'
  },
  {
    icon: '⚡',
    title: 'Instant Feedback',
    description: 'Real-time corrections and improvement suggestions'
  },
  {
    icon: '🌟',
    title: 'Motivation Engine',
    description: 'AI-powered motivation and goal tracking system'
  },
  {
    icon: '�',
    title: 'Adaptive Curriculum',
    description: 'Curriculum that evolves based on your progress'
  },
  {
    icon: '📈',
    title: 'Performance Forecasting',
    description: 'Predict and prevent learning difficulties'
  }
];

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/10 to-purple-50/10 dark:from-gray-900 dark:via-blue-900/5 dark:to-purple-900/5">
      <div className="pt-40 pb-20">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <h1 className="text-4xl sm:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Our AI Services
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Discover powerful AI-driven educational tools designed to enhance your learning experience
            </p>
          </motion.div>

          <motion.div 
            className="grid lg:grid-cols-3 md:grid-cols-2 gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {services.map(service => (
              <motion.div 
                key={service.id}
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-all duration-300"
                variants={fadeIn}
              >
                <div className="flex items-center mb-6">
                  <div className={`w-12 h-12 bg-gradient-to-r from-${service.color}-500 to-${service.color}-600 rounded-lg flex items-center justify-center mr-4`}>
                    <span className="text-2xl">{service.icon}</span>
                  </div>
                  <h2 className="text-2xl font-bold">{service.title}</h2>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  {service.description}
                </p>
                <div className="space-y-3 mb-6">
                  {service.features.map((feature, index) => (
                    <div key={index} className="flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                <Button 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500"
                  asChild
                >
                  <Link href={service.href || "/contact"}>
                    {service.cta}
                  </Link>
                </Button>
              </motion.div>
            ))}
          </motion.div>


          {/* Pricing CTA */}
          <motion.div 
            className="mt-20 text-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <div className="glass-effect rounded-xl p-8 max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
                Contact us today to learn more about our services and pricing options.
              </p>
              <Button variant="gradient" size="lg" asChild>
                <Link href="/contact">
                  Contact Us
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
