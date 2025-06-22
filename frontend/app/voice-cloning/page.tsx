'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { 
  Mic, 
  Upload, 
  Download, 
  Play, 
  Pause,
  Loader2,
  CheckCircle,
  AlertCircle,
  Radio,
  VolumeX,
  Volume2,
  Square,
  MicOff
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/lib/auth-context';
import { voiceAPI, type VoiceCloneResponse } from '@/lib/api';
import AuthComponent from '@/components/auth-component';

const voiceCloneSchema = z.object({
  text: z.string().min(10, 'Text must be at least 10 characters'),
  voice_name: z.string().optional(),
});

type VoiceCloneFormData = z.infer<typeof voiceCloneSchema>;

export default function VoiceClonePage() {
  const { currentUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<VoiceCloneResponse | null>(null);
  const [referenceAudio, setReferenceAudio] = useState<File | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  
  // Recording states
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingInterval, setRecordingInterval] = useState<NodeJS.Timeout | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<VoiceCloneFormData>({
    resolver: zodResolver(voiceCloneSchema),
    defaultValues: {
      voice_name: 'custom_voice',
    },
  });

  // Cleanup effect for recording
  useEffect(() => {
    return () => {
      // Stop recording and clear interval on unmount
      if (isRecording && mediaRecorder) {
        mediaRecorder.stop();
      }
      if (recordingInterval) {
        clearInterval(recordingInterval);
      }
    };
  }, [isRecording, mediaRecorder, recordingInterval]);

  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('audio/')) {
        toast({
          title: 'Invalid file type',
          description: 'Please upload an audio file',
          variant: 'destructive',
        });
        return;
      }
      setReferenceAudio(file);
    }
  };

  const playAudio = async (audioUrl: string) => {
    if (isPlaying && audio) {
      audio.pause();
      setIsPlaying(false);
      return;
    }

    try {
      const newAudio = new Audio(voiceAPI.getAudioUrl(audioUrl));
      newAudio.onended = () => setIsPlaying(false);
      newAudio.onpause = () => setIsPlaying(false);
      
      await newAudio.play();
      setAudio(newAudio);
      setIsPlaying(true);
    } catch (error) {
      toast({
        title: 'Playback Error',
        description: 'Failed to play audio',
        variant: 'destructive',
      });
    }
  };

  const downloadAudio = (audioUrl: string) => {
    const link = document.createElement('a');
    link.href = voiceAPI.getAudioUrl(audioUrl);
    link.download = `cloned_voice_${Date.now()}.wav`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setRecordedBlob(blob);
        
        // Convert blob to file for upload
        const file = new File([blob], `recording_${Date.now()}.wav`, { type: 'audio/wav' });
        setReferenceAudio(file);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start recording timer
      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      setRecordingInterval(interval);

      toast({
        title: 'Recording Started',
        description: 'Speak clearly into your microphone',
      });
    } catch (error) {
      console.error('Error starting recording:', error);
      toast({
        title: 'Recording Error',
        description: 'Failed to access microphone. Please check permissions.',
        variant: 'destructive',
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      
      if (recordingInterval) {
        clearInterval(recordingInterval);
        setRecordingInterval(null);
      }

      toast({
        title: 'Recording Stopped',
        description: 'Audio recorded successfully!',
      });
    }
  };

  const clearRecording = () => {
    setRecordedBlob(null);
    setReferenceAudio(null);
    setRecordingTime(0);
    
    if (recordingInterval) {
      clearInterval(recordingInterval);
      setRecordingInterval(null);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const onSubmit = async (data: VoiceCloneFormData) => {
    if (!currentUser) {
      toast({
        title: 'Authentication Required',
        description: 'Please sign in to use voice cloning.',
        variant: 'destructive',
      });
      return;
    }

    if (!referenceAudio) {
      toast({
        title: 'Reference Audio Required',
        description: 'Please upload a reference audio file.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const token = await currentUser.getIdToken();
      const formData = new FormData();
      
      formData.append('text', data.text);
      formData.append('voice_name', data.voice_name || 'custom_voice');
      formData.append('reference_audio', referenceAudio);

      const response = await voiceAPI.cloneVoice(formData, token);
      
      setResult(response);
      
      if (response.status === 'completed') {
        toast({
          title: 'Success!',
          description: 'Voice cloning completed successfully.',
        });
      } else if (response.status === 'quota_exceeded') {
        toast({
          title: 'Quota Exceeded',
          description: response.message,
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Error',
          description: response.message,
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      console.error('Voice cloning error:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'An unexpected error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser) {
    return <AuthComponent />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/10 to-pink-50/10 dark:from-gray-900 dark:via-purple-900/5 dark:to-pink-900/5">
      <div className="pt-40 pb-20">
        <div className="container mx-auto px-4 max-w-4xl">
          <motion.div 
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl sm:text-5xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Voice Cloning
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Clone any voice using advanced F5-TTS technology. Upload a reference audio file or record directly to generate speech with that voice.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mic className="w-5 h-5" />
                    Voice Cloning Setup
                  </CardTitle>
                  <CardDescription>
                    Provide reference audio (upload or record) and text to generate cloned speech
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    {/* Reference Audio Upload & Recording */}
                    <div className="space-y-4">
                      <Label>Reference Audio *</Label>
                      
                      {/* Tab selector for Upload vs Record */}
                      <div className="flex gap-2 mb-4">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="flex items-center gap-2"
                          onClick={() => document.getElementById('reference-audio')?.click()}
                        >
                          <Upload className="w-4 h-4" />
                          Upload File
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="flex items-center gap-2"
                          onClick={isRecording ? stopRecording : startRecording}
                          disabled={isLoading}
                        >
                          {isRecording ? (
                            <>
                              <Square className="w-4 h-4 text-red-500" />
                              Stop Recording
                            </>
                          ) : (
                            <>
                              <Mic className="w-4 h-4" />
                              Record Audio
                            </>
                          )}
                        </Button>
                        {(referenceAudio || recordedBlob) && (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                            onClick={clearRecording}
                          >
                            <MicOff className="w-4 h-4" />
                            Clear
                          </Button>
                        )}
                      </div>

                      {/* Upload area */}
                      <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
                        <input
                          type="file"
                          id="reference-audio"
                          accept="audio/*"
                          onChange={handleAudioUpload}
                          className="hidden"
                        />
                        
                        {isRecording ? (
                          /* Recording indicator */
                          <div className="text-center">
                            <div className="flex items-center justify-center gap-2 mb-2">
                              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                              <span className="text-red-600 font-semibold">Recording...</span>
                            </div>
                            <div className="text-2xl font-mono text-red-600">
                              {formatTime(recordingTime)}
                            </div>
                            <p className="text-sm text-gray-500 mt-2">
                              Speak clearly into your microphone
                            </p>
                          </div>
                        ) : referenceAudio ? (
                          /* Audio file selected */
                          <div className="text-center">
                            <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                            <span className="text-sm text-gray-600 dark:text-gray-400 block">
                              {referenceAudio.name}
                            </span>
                            <span className="text-xs text-green-600">
                              ✓ Audio ready for voice cloning
                            </span>
                          </div>
                        ) : (
                          /* Default state */
                          <div className="text-center">
                            <div className="flex items-center justify-center gap-4 mb-3">
                              <Upload className="w-8 h-8 text-gray-400" />
                              <span className="text-gray-400">or</span>
                              <Mic className="w-8 h-8 text-gray-400" />
                            </div>
                            <span className="text-sm text-gray-600 dark:text-gray-400 block mb-1">
                              Upload audio file or record directly
                            </span>
                            <span className="text-xs text-gray-500">
                              Supported: WAV, MP3, M4A (max 10MB) • 10-30 seconds recommended
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {/* Recording preview */}
                      {recordedBlob && (
                        <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              <span className="text-sm text-green-800 dark:text-green-200">
                                Recording completed ({formatTime(recordingTime)})
                              </span>
                            </div>
                            <Button
                              type="button"
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                const audio = new Audio(URL.createObjectURL(recordedBlob));
                                audio.play();
                              }}
                            >
                              <Play className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Voice Name */}
                    <div className="space-y-2">
                      <Label htmlFor="voice_name">Voice Name (Optional)</Label>
                      <Input
                        {...register('voice_name')}
                        placeholder="e.g., John's Voice"
                        className="bg-white/50 dark:bg-gray-800/50"
                      />
                    </div>

                    {/* Text Input */}
                    <div className="space-y-2">
                      <Label htmlFor="text">Text to Synthesize *</Label>
                      <Textarea
                        {...register('text')}
                        placeholder="Enter the text you want to convert to speech using the cloned voice..."
                        rows={4}
                        className="bg-white/50 dark:bg-gray-800/50"
                      />
                      {errors.text && (
                        <p className="text-sm text-red-500">{errors.text.message}</p>
                      )}
                    </div>

                    <Button
                      type="submit"
                      disabled={isLoading}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Cloning Voice...
                        </>
                      ) : (
                        <>
                          <Radio className="w-4 h-4 mr-2" />
                          Clone Voice
                        </>
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </motion.div>

            {/* Results */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <VolumeX className="w-5 h-5" />
                    Cloned Audio
                  </CardTitle>
                  <CardDescription>
                    Your generated voice cloning results will appear here
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading && (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
                      <p className="text-gray-600 dark:text-gray-400">
                        Processing your voice cloning request...
                      </p>
                    </div>
                  )}

                  {result && (
                    <div className="space-y-4">
                      {result.status === 'completed' && result.audio_url && (
                        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-green-800 dark:text-green-200">
                              Voice Cloning Completed!
                            </span>
                          </div>
                          
                          <div className="flex gap-2">
                            <Button
                              onClick={() => playAudio(result.audio_url!)}
                              size="sm"
                              variant="outline"
                              className="flex-1"
                            >
                              {isPlaying ? (
                                <>
                                  <Pause className="w-4 h-4 mr-2" />
                                  Pause
                                </>
                              ) : (
                                <>
                                  <Play className="w-4 h-4 mr-2" />
                                  Play
                                </>
                              )}
                            </Button>
                            <Button
                              onClick={() => downloadAudio(result.audio_url!)}
                              size="sm"
                              variant="outline"
                            >
                              <Download className="w-4 h-4 mr-2" />
                              Download
                            </Button>
                          </div>
                        </div>
                      )}

                      {result.status === 'failed' && (
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                          <div className="flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-red-600" />
                            <span className="font-medium text-red-800 dark:text-red-200">
                              {result.message}
                            </span>
                          </div>
                        </div>
                      )}

                      {result.status === 'quota_exceeded' && (
                        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                          <div className="flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-yellow-600" />
                            <span className="font-medium text-yellow-800 dark:text-yellow-200">
                              {result.message}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {!result && !isLoading && (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      <Volume2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Upload reference audio and submit to start voice cloning</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Tips */}
              <Card className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    💡 Voice Cloning Tips
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-2 text-blue-700 dark:text-blue-300">
                  <p>• Use high-quality reference audio (clear speech, no background noise)</p>
                  <p>• Reference audio should be 10-30 seconds long</p>
                  <p>• Speak clearly and naturally in the reference</p>
                  <p>• Avoid music or multiple speakers in reference audio</p>
                  <p>• Text length affects processing time</p>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
