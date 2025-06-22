'use client';

import { motion } from 'framer-motion';
import { 
  Brain, 
  Sparkles, 
  Target, 
  Users, 
  Zap, 
  Code, 
  Cloud, 
  Video, 
  Mic,
  Database,
  Shield,
  Globe,
  Rocket,
  Heart,
  Award,
  TrendingUp
} from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6
    }
  }
};

const featureVariants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.5
    }
  }
};

export default function AboutPageContent() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <motion.div
          className="text-center mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div 
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent text-lg font-semibold mb-4"
            variants={itemVariants}
          >
            <Sparkles className="w-6 h-6 text-blue-600" />
            About NeoMentor
          </motion.div>
          
          <motion.h1 
            className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight"
            variants={itemVariants}
          >
            Revolutionizing Education with
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent block">
              Multi-Agent AI
            </span>
          </motion.h1>
          
          <motion.p 
            className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed"
            variants={itemVariants}
          >
            We're building the future of personalized learning through cutting-edge artificial intelligence, 
            creating immersive educational experiences that adapt to every learner's unique needs.
          </motion.p>
        </motion.div>

        {/* Mission & Vision */}
        <motion.div
          className="grid md:grid-cols-2 gap-8 mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div 
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-white/20"
            variants={itemVariants}
          >
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-8 h-8 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Our Mission</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              To democratize high-quality education by leveraging advanced AI technologies, making personalized learning 
              accessible to everyone, everywhere. We believe every individual deserves tailored educational content that 
              adapts to their learning style and pace.
            </p>
          </motion.div>

          <motion.div 
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-white/20"
            variants={itemVariants}
          >
            <div className="flex items-center gap-3 mb-4">
              <Rocket className="w-8 h-8 text-purple-600" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Our Vision</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              To become the world's leading AI-powered education platform, where learning is not just personalized 
              but truly intelligent, engaging, and transformative. We envision a future where AI mentors guide 
              every learner to achieve their full potential.
            </p>
          </motion.div>
        </motion.div>

        {/* Why Choose NeoMentor */}
        <motion.div
          className="mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div className="text-center mb-12" variants={itemVariants}>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose NeoMentor?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Experience the next generation of AI-powered learning that goes beyond traditional education
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "Advanced Multi-Agent AI",
                description: "Our sophisticated AI agents work together to create personalized learning experiences using Google's latest Gemini 2.0 Flash model.",
                color: "text-blue-600"
              },
              {
                icon: Video,
                title: "Professional Video Generation",
                description: "Generate high-quality educational videos using Google Veo 2.0, ensuring engaging and professional content for every topic.",
                color: "text-purple-600"
              },
              {
                icon: Mic,
                title: "Natural Voice Cloning",
                description: "Advanced F5-TTS technology creates natural, human-like voices for personalized narration that enhances learning retention.",
                color: "text-green-600"
              },
              {
                icon: Zap,
                title: "Real-Time Processing",
                description: "Experience instant content generation with our FastAPI backend and WebSocket support for live updates and feedback.",
                color: "text-yellow-600"
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                description: "Built on Google Cloud infrastructure with Firebase Authentication, ensuring your data is secure and privacy-protected.",
                color: "text-red-600"
              },
              {
                icon: TrendingUp,
                title: "Adaptive Learning",
                description: "Our AI continuously learns from your interactions to provide increasingly personalized and effective educational content.",
                color: "text-indigo-600"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300"
                variants={featureVariants}
                whileHover={{ scale: 1.05 }}
              >
                <feature.icon className={`w-12 h-12 ${feature.color} mb-4`} />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Technology Stack */}
        <motion.div
          className="mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div className="text-center mb-12" variants={itemVariants}>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Powered by Cutting-Edge Technology
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Built with the most advanced frameworks and cloud technologies for optimal performance and scalability
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: "Next.js 14", icon: Code, category: "Frontend Framework" },
              { name: "TypeScript", icon: Code, category: "Language" },
              { name: "Tailwind CSS", icon: Code, category: "Styling" },
              { name: "React 18", icon: Code, category: "UI Library" },
              { name: "FastAPI", icon: Zap, category: "Backend Framework" },
              { name: "Google Cloud", icon: Cloud, category: "Cloud Platform" },
              { name: "Vertex AI", icon: Brain, category: "AI Platform" },
              { name: "Firebase", icon: Database, category: "Database & Auth" },
              { name: "Gemini 2.0", icon: Sparkles, category: "AI Model" },
              { name: "Google Veo 2.0", icon: Video, category: "Video AI" },
              { name: "F5-TTS", icon: Mic, category: "Voice AI" },
              { name: "Framer Motion", icon: Zap, category: "Animations" }
            ].map((tech, index) => (
              <motion.div
                key={index}
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-4 text-center shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300"
                variants={featureVariants}
                whileHover={{ scale: 1.05 }}
              >
                <tech.icon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                  {tech.name}
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {tech.category}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Competitive Advantages */}
        <motion.div
          className="mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div className="text-center mb-12" variants={itemVariants}>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How We're Different
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Setting new standards in AI-powered education with innovative features that competitors can't match
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Award,
                title: "Multi-Agent Architecture",
                description: "Unlike single AI systems, our multi-agent approach ensures specialized expertise for each aspect of content creation.",
                advantage: "vs. Traditional single-AI platforms"
              },
              {
                icon: Globe,
                title: "Google's Latest AI Models",
                description: "First to integrate Gemini 2.0 Flash and Veo 2.0, giving you access to the most advanced AI capabilities available.",
                advantage: "vs. Outdated AI models"
              },
              {
                icon: Heart,
                title: "Truly Personalized Content",
                description: "Every video, voice, and lesson is uniquely generated for you, not from a pre-made template library.",
                advantage: "vs. Template-based platforms"
              },
              {
                icon: Zap,
                title: "Real-Time Generation",
                description: "Watch your content being created live with WebSocket streaming, providing transparency and engagement.",
                advantage: "vs. Batch processing systems"
              },
              {
                icon: Users,
                title: "Enterprise-Grade Infrastructure",
                description: "Built on Google Cloud with enterprise security, scalability, and reliability from day one.",
                advantage: "vs. Smaller cloud providers"
              },
              {
                icon: Brain,
                title: "Continuous Learning AI",
                description: "Our AI gets smarter with every interaction, creating increasingly better content for your learning style.",
                advantage: "vs. Static AI systems"
              }
            ].map((advantage, index) => (
              <motion.div
                key={index}
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20"
                variants={featureVariants}
              >
                <advantage.icon className="w-10 h-10 text-blue-600 mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  {advantage.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-3">
                  {advantage.description}
                </p>
                <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                  {advantage.advantage}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white"
          variants={itemVariants}
          initial="hidden"
          animate="visible"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Learning?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of learners who are already experiencing the future of education with NeoMentor's AI-powered platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Start Learning Now
            </motion.button>
            <motion.button
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Schedule Demo
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
