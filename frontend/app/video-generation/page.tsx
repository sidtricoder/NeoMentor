"use client"

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Play, Download, Loader2, FileText, Image, Music, X, CheckCircle, AlertCircle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/lib/auth-context';
import { videoGenerationAPI, type ProcessingResponse } from '@/lib/api';
import AuthComponent from '@/components/auth-component';

const VideoGenerationPage = () => {
  const { currentUser, getAuthToken } = useAuth();
  const { toast } = useToast();
  
  const [prompt, setPrompt] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [videoDuration, setVideoDuration] = useState<number>(8);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [timer, setTimer] = useState<number>(0);
  const [estimatedTime, setEstimatedTime] = useState<number>(0);
  
  const imageInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  // If not authenticated, show auth component
  if (!currentUser) {
    return <AuthComponent />;
  }

  const calculateEstimatedTime = (duration: number): number => {
    return Math.round((duration * 37.5 + 120) / 60); // Convert to minutes
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast({
          title: "File too large",
          description: "Please select an image smaller than 10MB.",
          variant: "destructive",
        });
        return;
      }
      setImageFile(file);
    }
  };

  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 25 * 1024 * 1024) { // 25MB limit
        toast({
          title: "File too large",
          description: "Please select an audio file smaller than 25MB.",
          variant: "destructive",
        });
        return;
      }
      setAudioFile(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    if (imageInputRef.current) {
      imageInputRef.current.value = '';
    }
  };

  const removeAudio = () => {
    setAudioFile(null);
    if (audioInputRef.current) {
      audioInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      toast({
        title: "Missing prompt",
        description: "Please enter a prompt for video generation.",
        variant: "destructive",
      });
      return;
    }

    if (!imageFile) {
      toast({
        title: "Missing image",
        description: "Please upload an image file.",
        variant: "destructive",
      });
      return;
    }

    if (!audioFile) {
      toast({
        title: "Missing audio",
        description: "Please upload an audio file.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    
    const estimated = calculateEstimatedTime(videoDuration);
    setEstimatedTime(estimated);
    setTimer(0);

    // Start timer
    const timerInterval = setInterval(() => {
      setTimer(prev => prev + 1);
    }, 1000);

    try {
      const token = await getAuthToken();
      
      if (!token) {
        setError('Authentication failed. Please sign in again.');
        setIsProcessing(false);
        clearInterval(timerInterval);
        return;
      }

      // Generate a session ID for tracking
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('image', imageFile);
      formData.append('audio', audioFile);
      formData.append('duration', videoDuration.toString());
      formData.append('session_id', sessionId);

      const response = await videoGenerationAPI.generateVideo(formData, token, (progressEvent) => {
        // Handle upload progress if needed
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload Progress: ${percentCompleted}%`);
      });
      
      setResult(response);
      
      toast({
        title: "Video generated successfully!",
        description: "Your video is ready for download.",
      });
      
    } catch (error: any) {
      console.error('Error processing video:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred while processing your video';
      setError(errorMessage);
      
      toast({
        title: "Generation failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      clearInterval(timerInterval);
    }
  };

  const resetForm = () => {
    setPrompt('');
    setImageFile(null);
    setAudioFile(null);
    setVideoDuration(8);
    setResult(null);
    setError(null);
    setTimer(0);
    setEstimatedTime(0);
    
    if (imageInputRef.current) imageInputRef.current.value = '';
    if (audioInputRef.current) audioInputRef.current.value = '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/10 to-purple-50/10 dark:from-gray-900 dark:via-blue-900/5 dark:to-purple-900/5">
      <div className="pt-40 pb-20">
        <div className="container mx-auto px-4 max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🎥 AI Video Generation
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Transform your ideas into engaging educational videos using advanced AI technology
            </p>
          </motion.div>

          {!isProcessing && !result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <Card className="glass-effect border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl font-bold">Create Your Video</CardTitle>
                  <CardDescription>
                    Provide a prompt and optional media files to generate your educational video
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <Label htmlFor="prompt" className="text-base font-medium">
                        Video Prompt *
                      </Label>
                      <Textarea
                        id="prompt"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe what you want to learn about... (e.g., 'Explain quantum physics concepts with visual examples')"
                        className="mt-2 min-h-[100px]"
                        required
                      />
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <Label className="text-base font-medium">Reference Image (Optional)</Label>
                        <div className="mt-2">
                          {imageFile ? (
                            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border">
                              <div className="flex items-center space-x-2">
                                <Image className="w-5 h-5 text-blue-600" />
                                <span className="text-sm text-blue-700 dark:text-blue-300">{imageFile.name}</span>
                              </div>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={removeImage}
                                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-50 dark:hover:bg-red-900/20"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          ) : (
                            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                              <Image className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                              <Button
                                type="button"
                                variant="outline"
                                onClick={() => imageInputRef.current?.click()}
                                className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                              >
                                <Upload className="w-4 h-4 mr-2" />
                                Upload Image
                              </Button>
                              <p className="text-sm text-gray-500 mt-2">Max 10MB</p>
                            </div>
                          )}
                          <input
                            ref={imageInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            className="hidden"
                          />
                        </div>
                      </div>

                      <div>
                        <Label className="text-base font-medium">Voice Audio (Optional)</Label>
                        <div className="mt-2">
                          {audioFile ? (
                            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border">
                              <div className="flex items-center space-x-2">
                                <Music className="w-5 h-5 text-green-600" />
                                <span className="text-sm text-green-700 dark:text-green-300">{audioFile.name}</span>
                              </div>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={removeAudio}
                                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-50 dark:hover:bg-red-900/20"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          ) : (
                            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                              <Music className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                              <Button
                                type="button"
                                variant="outline"
                                onClick={() => audioInputRef.current?.click()}
                                className="text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                              >
                                <Upload className="w-4 h-4 mr-2" />
                                Upload Audio
                              </Button>
                              <p className="text-sm text-gray-500 mt-2">Max 25MB</p>
                            </div>
                          )}
                          <input
                            ref={audioInputRef}
                            type="file"
                            accept="audio/*"
                            onChange={handleAudioUpload}
                            className="hidden"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="duration" className="text-base font-medium">
                        Video Duration: {videoDuration} seconds
                      </Label>
                      <input
                        id="duration"
                        type="range"
                        min="8"
                        max="56"
                        step="8"
                        value={videoDuration}
                        onChange={(e) => setVideoDuration(Number(e.target.value))}
                        className="w-full mt-2"
                      />
                      <div className="flex justify-between text-sm text-gray-500 mt-1">
                        <span>8s</span>
                        <span>16s</span>
                        <span>24s</span>
                        <span>32s</span>
                        <span>40s</span>
                        <span>48s</span>
                        <span>56s</span>
                      </div>
                    </div>

                    <Button type="submit" className="w-full" variant="gradient" size="lg">
                      <Play className="w-5 h-5 mr-2" />
                      Generate Video
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <Card className="glass-effect border-0 shadow-xl">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center space-y-4">
                    <div className="relative">
                      <Loader2 className="w-16 h-16 animate-spin text-blue-600" />
                      <div className="absolute inset-0 w-16 h-16 border-4 border-transparent rounded-full animate-pulse border-t-purple-500"></div>
                    </div>
                    
                    <div className="text-center">
                      <h3 className="text-xl font-semibold mb-2">Generating Your Video</h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Our AI is creating your personalized educational video...
                      </p>
                      
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Progress</span>
                          <span className="text-sm text-gray-500">
                            {formatTime(timer)} / ~{estimatedTime} min
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-1000"
                            style={{
                              width: `${Math.min((timer / (estimatedTime * 60)) * 100, 90)}%`
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <Card className="glass-effect border-0 shadow-xl">
                <CardContent className="pt-6">
                  <div className="text-center space-y-6">
                    <div className="flex justify-center">
                      <CheckCircle className="w-16 h-16 text-green-500" />
                    </div>
                    
                    <div>
                      <h3 className="text-2xl font-bold text-green-600 mb-2">Video Generated Successfully!</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        Your educational video is ready for viewing and download.
                      </p>
                    </div>

                    {result.result_video_url && (
                      <div className="space-y-4">
                        <video
                          controls
                          className="w-full max-w-2xl mx-auto rounded-lg shadow-lg"
                          preload="metadata"
                        >
                          <source src={videoGenerationAPI.getVideoUrl(result.result_video_url)} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                        
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                          <Button variant="outline" asChild>
                            <a
                              href={videoGenerationAPI.getVideoUrl(result.result_video_url)}
                              download
                              className="flex items-center"
                            >
                              <Download className="w-4 h-4 mr-2" />
                              Download Video
                            </a>
                          </Button>
                          
                          <Button onClick={resetForm} variant="gradient">
                            Create Another Video
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <Card className="glass-effect border-0 shadow-xl border-red-200 dark:border-red-800">
                <CardContent className="pt-6">
                  <div className="text-center space-y-4">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
                    <div>
                      <h3 className="text-xl font-semibold text-red-600 mb-2">Generation Failed</h3>
                      <p className="text-gray-600 dark:text-gray-400">{error}</p>
                    </div>
                    <Button onClick={resetForm} variant="outline">
                      Try Again
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoGenerationPage;
