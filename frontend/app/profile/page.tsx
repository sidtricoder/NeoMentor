'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  User, 
  Crown, 
  History, 
  Video, 
  Calendar,
  Download,
  Eye,
  Clock,
  BarChart3,
  TrendingUp,
  Award,
  X,
  Play
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/lib/auth-context'
import { Badge } from '@/components/ui/badge'
import AuthComponent from '@/components/auth-component'
import { fetchUserVideosFromStorage, VideoMetadata } from '@/lib/video-storage'

interface UserProfile {
  uid: string
  email?: string
  name?: string
  picture?: string
  total_sessions: number
  total_videos_generated: number
  subscription_tier: string
  created_at?: string
  last_login?: string
}

export default function ProfilePage() {
  const { currentUser, logout } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [videos, setVideos] = useState<VideoMetadata[]>([])
  const [loading, setLoading] = useState(false)
  const [videosLoading, setVideosLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUserProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      
      if (!currentUser) {
        throw new Error('User not authenticated')
      }
      
      const token = await currentUser.getIdToken()
      if (!token) {
        throw new Error('No authentication token available')
      }

      const response = await fetch(`https://neomentor-backend-140655189111.us-central1.run.app/auth/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        mode: 'cors',
        credentials: 'include'
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed - please sign in again')
        } else if (response.status === 403) {
          throw new Error('Access denied - insufficient permissions')
        } else {
          throw new Error(`Server error: ${response.status}`)
        }
      }

      const profileData = await response.json()
      setProfile(profileData)
    } catch (error: any) {
      console.error('Profile fetch error:', error)
      setError('Failed to fetch profile. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserSessions = async () => {
    // Sessions are no longer needed as we fetch videos directly from Firebase Storage
  }

  const fetchUserVideos = async () => {
    try {
      setVideosLoading(true)
      if (!currentUser) return
      
      // Fetch videos directly from Firebase Storage
      const storageVideos = await fetchUserVideosFromStorage(currentUser.uid)
      setVideos(storageVideos)
      
    } catch (error) {
      console.error('Videos fetch error:', error)
      setError('Failed to load videos from storage')
    } finally {
      setVideosLoading(false)
    }
  }

  useEffect(() => {
    if (currentUser) {
      fetchUserProfile()
      fetchUserSessions()
      fetchUserVideos()
    }
  }, [currentUser])

  const getTierColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'premium': return 'text-yellow-600 dark:text-yellow-400'
      case 'enterprise': return 'text-purple-600 dark:text-purple-400'
      default: return 'text-blue-600 dark:text-blue-400'
    }
  }

  const getTierBadgeColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'premium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'enterprise': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
      default: return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'premium': 
      case 'enterprise':
        return <Crown className="w-4 h-4" />
      default:
        return <User className="w-4 h-4" />
    }
  }

  const handleSignOut = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

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
              Profile
            </h1>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Please sign in to view your profile and activity.
            </p>
          </motion.div>
          
          <div className="max-w-md mx-auto">
            <AuthComponent />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-green-900/20 dark:to-blue-900/20">
      <div className="container mx-auto px-4 py-24 sm:py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          {/* Profile Header */}
          <Card className="mb-8 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-0 shadow-xl">
            <CardContent className="p-4 sm:p-6 lg:p-8">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
                <div className="flex items-center gap-3 sm:gap-4 w-full sm:w-auto">
                  {currentUser.photoURL ? (
                    <img
                      src={currentUser.photoURL}
                      alt="Profile"
                      className="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-4 border-white shadow-lg"
                    />
                  ) : (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center border-4 border-white shadow-lg">
                      <User className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white truncate">
                      {currentUser.displayName || 'User'}
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-2 text-sm sm:text-base truncate">
                      {currentUser.email}
                    </p>
                    {profile && (
                      <Badge className={getTierBadgeColor(profile.subscription_tier)}>
                        {getTierIcon(profile.subscription_tier)}
                        <span className="ml-1 capitalize">{profile.subscription_tier}</span>
                      </Badge>
                    )}
                  </div>
                </div>
                
                <div className="flex-1 hidden sm:block"></div>
                
                <div className="flex gap-3 w-full sm:w-auto">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleSignOut}
                    className="text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600 dark:hover:bg-red-900/20 flex-1 sm:flex-none"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Sign out
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <History className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {profile?.total_sessions || 0}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium">Total Sessions</p>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <Video className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {profile?.total_videos_generated || 0}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium">Videos Created</p>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <Award className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {profile?.subscription_tier 
                      ? profile.subscription_tier.charAt(0).toUpperCase() + profile.subscription_tier.slice(1) 
                      : 'Free'}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium">Plan</p>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* My Videos Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                  <Video className="w-5 h-5" />
                  My Generated Videos
                </CardTitle>
                <CardDescription className="text-sm sm:text-base">
                  All videos you've created with NeoMentor AI
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                  {videosLoading ? (
                    <div className="text-center py-8">
                      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">Loading videos...</p>
                    </div>
                  ) : videos.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                      {videos.map((video) => (
                        <div 
                          key={video.id}
                          className="group bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden hover:shadow-lg transition-all duration-300"
                        >
                          {/* Video Thumbnail */}
                          <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-500 relative overflow-hidden">
                            {video.thumbnail_url ? (
                              <img 
                                src={video.thumbnail_url} 
                                alt={video.title || 'Video thumbnail'}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <Video className="w-12 h-12 text-white" />
                              </div>
                            )}
                            
                            {/* Play Button Overlay */}
                            <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                              <Button
                                size="sm"
                                className="bg-white/90 text-gray-900 hover:bg-white"
                                onClick={() => {
                                  if (video.video_url) {
                                    window.open(video.video_url, '_blank')
                                  }
                                }}
                              >
                                <Play className="w-4 h-4 mr-1" />
                                Play
                              </Button>
                            </div>
                            
                            {/* Duration Badge */}
                            {video.duration && (
                              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                                {video.duration}s
                              </div>
                            )}
                          </div>
                          
                          {/* Video Info */}
                          <div className="p-3 sm:p-4">
                            <h3 className="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2 text-sm sm:text-base">
                              {video.title || 'Untitled Video'}
                            </h3>
                            
                            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(video.created_at).toLocaleDateString()}
                              </span>
                              {video.file_size && (
                                <span>{video.file_size}</span>
                              )}
                            </div>
                            
                            <div className="flex items-center justify-between">
                              <Badge 
                                className={`text-xs ${
                                  video.status === 'completed' 
                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                                  video.status === 'failed' 
                                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                                }`}
                              >
                                {video.status}
                              </Badge>
                              
                              <div className="flex gap-1">
                                {video.video_url && (
                                  <Button 
                                    variant="ghost" 
                                    size="sm"
                                    onClick={() => window.open(video.video_url, '_blank')}
                                  >
                                    <Eye className="w-3 h-3" />
                                  </Button>
                                )}
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => {
                                    if (video.video_url) {
                                      const a = document.createElement('a')
                                      a.href = video.video_url
                                      a.download = `${video.title || 'video'}.mp4`
                                      a.click()
                                    }
                                  }}
                                >
                                  <Download className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        No videos yet
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-6">
                        Create your first AI-powered educational video to get started.
                      </p>
                      <Button variant="gradient" asChild>
                        <Link href="/video-generation">
                          <Video className="w-4 h-4 mr-2" />
                          Create Video
                        </Link>
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

          {loading && (
            <div className="text-center py-8">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">Loading profile...</p>
            </div>
          )}

          {error && (
            <Card className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <CardContent className="p-6 text-center">
                <p className="text-red-600 dark:text-red-400">{error}</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-4"
                  onClick={fetchUserProfile}
                >
                  Retry
                </Button>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}
