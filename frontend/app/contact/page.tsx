"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Send, AlertCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

const contactFormSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }),
  email: z.string().email({ message: 'Please enter a valid email address.' }),
  message: z.string().min(10, { message: 'Message must be at least 10 characters.' }),
});

type ContactFormValues = z.infer<typeof contactFormSchema>;

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

export default function ContactPage() {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
  });

  const onSubmit = async (data: ContactFormValues) => {
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    console.log('Contact form submitted:', data);
    
    toast({
      title: "Message sent successfully!",
      description: "We'll get back to you as soon as possible.",
    });
    
    reset();
    setIsSubmitting(false);
  };

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
              <Mail className="inline-block mr-2 h-10 w-10" />
              Contact Us
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Get in touch with our team. We're here to help you with your AI learning journey.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* Contact Form */}
            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Send us a Message</CardTitle>
                  <CardDescription>
                    Fill out the form below and we'll get back to you as soon as possible.
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <form onSubmit={handleSubmit(onSubmit)}>
                    <div className="grid gap-6">
                      <div className="grid gap-2">
                        <Label htmlFor="name">
                          Name
                        </Label>
                        <Input
                          id="name"
                          placeholder="Your name"
                          {...register("name")}
                        />
                        {errors.name && (
                          <div className="text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.name.message}
                          </div>
                        )}
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="email">
                          Email
                        </Label>
                        <Input
                          id="email"
                          placeholder="your.email@example.com"
                          type="email"
                          {...register("email")}
                        />
                        {errors.email && (
                          <div className="text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.email.message}
                          </div>
                        )}
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="message">
                          Message
                        </Label>
                        <Textarea
                          id="message"
                          placeholder="How can we help you?"
                          rows={5}
                          {...register("message")}
                        />
                        {errors.message && (
                          <div className="text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.message.message}
                          </div>
                        )}
                      </div>
                      
                      <Button 
                        type="submit" 
                        className="w-full"
                        disabled={isSubmitting}
                        variant="gradient"
                      >
                        {isSubmitting ? (
                          <>
                            <span className="animate-spin mr-2">⏳</span>
                            Sending...
                          </>
                        ) : (
                          <>
                            <Send className="mr-2 h-4 w-4" />
                            Send Message
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>

            {/* Contact Information */}
            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              className="flex flex-col gap-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Contact Information</CardTitle>
                  <CardDescription>
                    Reach out to us through these channels
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-6">
                    <div className="flex items-start">
                      <MapPin className="h-6 w-6 text-blue-600 dark:text-blue-400 mr-4 mt-0.5" />
                      <div>
                        <h3 className="font-medium mb-1">Our Location</h3>
                        <p className="text-gray-600 dark:text-gray-400">
                          123 AI Avenue<br />
                          Tech City, TC 12345<br />
                          United States
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start">
                      <Mail className="h-6 w-6 text-blue-600 dark:text-blue-400 mr-4 mt-0.5" />
                      <div>
                        <h3 className="font-medium mb-1">Email Us</h3>
                        <p className="text-gray-600 dark:text-gray-400">
                          <a href="mailto:info@neomentor.app" className="hover:text-blue-600 dark:hover:text-blue-400">
                            info@neomentor.app
                          </a>
                        </p>
                        <p className="text-gray-600 dark:text-gray-400">
                          <a href="mailto:support@neomentor.app" className="hover:text-blue-600 dark:hover:text-blue-400">
                            support@neomentor.app
                          </a>
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start">
                      <Phone className="h-6 w-6 text-blue-600 dark:text-blue-400 mr-4 mt-0.5" />
                      <div>
                        <h3 className="font-medium mb-1">Call Us</h3>
                        <p className="text-gray-600 dark:text-gray-400">
                          <a href="tel:+1234567890" className="hover:text-blue-600 dark:hover:text-blue-400">
                            +1 (234) 567-890
                          </a>
                        </p>
                        <p className="text-gray-600 dark:text-gray-400">
                          Monday - Friday: 9am - 5pm EST
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Frequently Asked Questions</CardTitle>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-1">How quickly can I expect a response?</h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      We typically respond to inquiries within 24-48 business hours.
                    </p>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-1">Do you offer technical support?</h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Yes, our technical support team is available during business hours via email.
                    </p>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-1">Can I schedule a consultation?</h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Yes, you can request a consultation through this form or by emailing us directly.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
