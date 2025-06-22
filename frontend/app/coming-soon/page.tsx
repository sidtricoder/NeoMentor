"use client"

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

const features = [
  'Advanced AI algorithms in development',
  'Beta testing with select users',
  'Continuous improvement and optimization',
  'Integration with existing NeoMentor ecosystem'
];

export default function ComingSoonPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/10 to-purple-50/10 dark:from-gray-900 dark:via-blue-900/5 dark:to-purple-900/5">
      <div className="pt-40 pb-20">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center max-w-4xl mx-auto"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            {/* Icon */}
            <div className="mb-8">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🚀</span>
              </div>
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl sm:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Coming Soon
            </h1>
            
            <p className="text-2xl text-gray-600 dark:text-gray-400 mb-8">
              We're working on something amazing!
            </p>

            <p className="text-lg text-gray-500 dark:text-gray-500 mb-12 max-w-2xl mx-auto">
              Our team is developing cutting-edge AI educational features that will revolutionize your learning experience. 
              Stay tuned for exciting new capabilities that will enhance your educational journey.
            </p>

            {/* Features List */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-8 mb-12 max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">What to Expect</h2>
              <div className="space-y-4">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center justify-center">
                    <span className="text-green-500 mr-3">✓</span>
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="mb-12">
              <div className="flex items-center justify-center mb-4">
                <span className="text-gray-600 dark:text-gray-400 mr-4">Development Progress</span>
                <div className="w-48 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                    initial={{ width: 0 }}
                    animate={{ width: '65%' }}
                    transition={{ duration: 2, delay: 0.5 }}
                  />
                </div>
                <span className="text-gray-600 dark:text-gray-400 ml-4">65%</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                variant="gradient" 
                size="lg"
                asChild
              >
                <Link href="/contact">
                  Get Notified When Available
                </Link>
              </Button>
              
              <Button 
                variant="outline" 
                size="lg"
                asChild
              >
                <Link href="/services">
                  Explore Current Services
                </Link>
              </Button>
            </div>

            {/* Newsletter Signup */}
            <div className="mt-16 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-8">
              <h3 className="text-2xl font-bold mb-4">Stay in the Loop</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Be the first to know when these exciting new features launch!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                <input 
                  type="email" 
                  placeholder="Enter your email" 
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  Notify Me
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
