"use client"

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { Video, Zap, Shield, Sparkles, Play, ArrowRight, Lightbulb, BookOpen, PieChart, Award } from 'lucide-react';

import { Button } from '@/components/ui/button';

const features = [
  {
    icon: <Zap className="w-8 h-8 text-white" />,
    title: 'AI-Powered',
    description: 'Advanced artificial intelligence creates personalized educational content tailored to your learning style and pace.',
    gradient: 'from-blue-500 to-purple-500',
  },
  {
    icon: <Video className="w-8 h-8 text-white" />,
    title: 'Interactive Videos',
    description: 'Engaging video lessons with visual aids, animations, and clear explanations to enhance understanding.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: <Shield className="w-8 h-8 text-white" />,
    title: 'Secure & Private',
    description: 'Your data and learning progress are protected with enterprise-grade security and privacy measures.',
    gradient: 'from-pink-500 to-red-500',
  },
];

const testimonials = [
  {
    quote: "NeoMentor has transformed how I study complex topics. The AI tutor explains concepts in a way that's easy to understand.",
    name: "Alex Johnson",
    role: "Student",
    avatar: "/neomentor-icon.png"
  },
  {
    quote: "As an educator, NeoMentor has given me powerful tools to create personalized content for all my students' learning styles.",
    name: "Dr. Sarah Williams",
    role: "Professor",
    avatar: "/neomentor-icon.png"
  },
  {
    quote: "The AI-generated videos helped me learn at my own pace, with explanations tailored to my knowledge level.",
    name: "Michael Chen",
    role: "Self-learner",
    avatar: "/neomentor-icon.png"
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

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-40 pb-20 bg-gradient-to-b from-white via-gray-50/50 to-white dark:from-gray-900 dark:via-gray-900/50 dark:to-gray-900">
        <div className="container mx-auto px-4">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
            <motion.div 
              className="flex-1 max-w-2xl"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
            >
              <div className="inline-flex items-center px-6 py-3 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 text-sm font-semibold text-blue-800 dark:text-blue-200 mb-8 shadow-lg">
                <Sparkles className="w-5 h-5 mr-2" />
                Multi-Agent AI System
              </div>
              
              <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold mb-8 leading-tight">
                Your <span className="bg-gradient-to-r from-blue-700 via-purple-700 to-indigo-800 dark:from-blue-400 dark:via-purple-400 dark:to-indigo-500 bg-clip-text text-transparent font-extrabold">AI Learning</span>
                <br />& <span className="bg-gradient-to-r from-purple-700 via-pink-700 to-red-700 dark:from-purple-400 dark:via-pink-400 dark:to-red-400 bg-clip-text text-transparent font-extrabold">Education Platform</span>
              </h1>
              
              <p className="text-xl text-gray-700 dark:text-gray-300 mb-12 leading-relaxed">
                Transform your learning journey with <span className="font-bold text-blue-600 dark:text-blue-400">personalized educational videos</span> powered by advanced AI. 
                Ask any question and get <span className="font-bold text-purple-600 dark:text-purple-400">clear, engaging explanations</span> through interactive video lessons created just for you.
              </p>

              <div className="flex flex-col sm:flex-row gap-6">
                <Button variant="gradient" size="xl" className="group" asChild>
                  <Link href="/contact">
                    <Video className="mr-2 h-5 w-5" />
                    Create Learning Video
                    <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                  </Link>
                </Button>
                
                <Button variant="outline" size="xl" className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800" asChild>
                  <Link href="#how-it-works">
                    <Play className="mr-2 h-5 w-5" />
                    Watch Demo
                  </Link>
                </Button>
              </div>
            </motion.div>
            
            <motion.div 
              className="flex-1 relative h-[500px] w-full max-w-[500px]"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 rounded-3xl animate-pulse"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-full h-full relative">
                  <Image
                    src="/neomentor-icon.png"
                    alt="NeoMentor AI"
                    fill
                    className="object-contain p-10"
                  />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center max-w-3xl mx-auto mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Why Choose NeoMentor?
            </h2>
            <p className="text-xl text-gray-700 dark:text-gray-300">
              Our platform combines cutting-edge AI technology with proven educational methodologies to create a personalized learning experience.
            </p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                className="glass-effect rounded-2xl p-8 hover:scale-105 transition-all duration-300 hover:shadow-2xl"
                variants={fadeIn}
              >
                <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center max-w-3xl mx-auto mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              How NeoMentor Works
            </h2>
            <p className="text-xl text-gray-700 dark:text-gray-300">
              Our advanced AI system transforms complex topics into engaging, personalized video lessons
            </p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-4 gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.div 
              className="flex flex-col items-center text-center"
              variants={fadeIn}
            >
              <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4 text-blue-600 dark:text-blue-400">
                <Lightbulb size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">Ask a Question</h3>
              <p className="text-gray-600 dark:text-gray-400">Submit any topic or question you want to learn about</p>
            </motion.div>
            
            <motion.div 
              className="flex flex-col items-center text-center"
              variants={fadeIn}
            >
              <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-4 text-purple-600 dark:text-purple-400">
                <BookOpen size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">AI Processing</h3>
              <p className="text-gray-600 dark:text-gray-400">Our AI creates a personalized learning plan for your needs</p>
            </motion.div>
            
            <motion.div 
              className="flex flex-col items-center text-center"
              variants={fadeIn}
            >
              <div className="w-16 h-16 rounded-full bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center mb-4 text-pink-600 dark:text-pink-400">
                <Video size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">Video Generation</h3>
              <p className="text-gray-600 dark:text-gray-400">Watch as your custom educational video is generated</p>
            </motion.div>
            
            <motion.div 
              className="flex flex-col items-center text-center"
              variants={fadeIn}
            >
              <div className="w-16 h-16 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center mb-4 text-indigo-600 dark:text-indigo-400">
                <PieChart size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">Track Progress</h3>
              <p className="text-gray-600 dark:text-gray-400">Monitor your learning journey with intuitive analytics</p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center max-w-3xl mx-auto mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-700 dark:text-gray-300">
              Join thousands of students and educators who have transformed their learning journey with NeoMentor
            </p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8"
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {testimonials.map((testimonial, index) => (
              <motion.div 
                key={index}
                className="glass-effect rounded-2xl p-8"
                variants={fadeIn}
              >
                <div className="flex items-center mb-6">
                  <div className="mr-4 rounded-full overflow-hidden w-12 h-12 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <Image
                      src={testimonial.avatar}
                      alt={testimonial.name}
                      width={48}
                      height={48}
                    />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900 dark:text-white">{testimonial.name}</h4>
                    <p className="text-gray-600 dark:text-gray-400">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-700 dark:text-gray-300 italic">"{testimonial.quote}"</p>
                <div className="mt-4 flex">
                  {[...Array(5)].map((_, i) => (
                    <Award key={i} className="w-5 h-5 text-yellow-500" />
                  ))}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div 
            className="rounded-3xl overflow-hidden relative p-12"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-90"></div>
            <div className="absolute inset-0 bg-[url('/neomentor-icon.png')] opacity-5 bg-repeat"></div>
            
            <div className="relative z-10 text-center max-w-3xl mx-auto">
              <h2 className="text-3xl sm:text-4xl font-bold mb-6 text-white">
                Ready to Transform Your Learning Experience?
              </h2>
              <p className="text-xl text-white/90 mb-8">
                Join thousands of students and educators who have already discovered the power of AI-assisted learning.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="xl" variant="default" className="bg-white text-blue-600 hover:bg-gray-100" asChild>
                  <Link href="/contact">
                    Get Started Today
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                <Button size="xl" variant="outline" className="border-white text-black hover:bg-white/10 dark:border-white dark:text-white dark:hover:bg-white/20" asChild>
                  <Link href="/services">
                    Explore Services
                  </Link>
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
