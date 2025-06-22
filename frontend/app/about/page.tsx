import { Metadata } from 'next';
import AboutPageContent from './about-content';

export const metadata: Metadata = {
  title: 'About Us | NeoMentor - Revolutionary AI-Powered Education Platform',
  description: 'Discover how NeoMentor is transforming education with cutting-edge multi-agent AI, advanced video generation, and personalized learning experiences powered by Google\'s latest technologies.',
  keywords: 'AI education, personalized learning, video generation, voice cloning, multi-agent AI, Google Cloud, Vertex AI, educational technology',
  openGraph: {
    title: 'About NeoMentor - The Future of AI-Powered Learning',
    description: 'Learn how our advanced multi-agent AI system creates personalized educational content using Google\'s Gemini 2.0, Veo 2.0, and cutting-edge voice cloning technology.',
    type: 'website',
  },
};

export default function AboutPage() {
  return <AboutPageContent />;
}
