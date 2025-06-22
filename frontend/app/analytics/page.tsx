'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart, 
  LineChart, 
  TrendingUp, 
  Users, 
  Video, 
  Calendar,
  Award,
  Target,
  Clock,
  CheckCircle,
  RefreshCw,
  Download
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/lib/auth-context';
import { analyticsAPI, type AnalyticsData } from '@/lib/api';
import AuthComponent from '@/components/auth-component';

export default function AnalyticsPage() {
  const { currentUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [dateRange, setDateRange] = useState('30d');

  const fetchAnalytics = async () => {
    if (!currentUser) return;

    setIsLoading(true);
    try {
      const token = await currentUser.getIdToken();
      const analyticsData = await analyticsAPI.getDashboard(dateRange, token);
      setData(analyticsData);
    } catch (error: any) {
      console.error('Analytics error:', error);
      toast({
        title: 'Error',
        description: 'Failed to load analytics data',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchAnalytics();
    }
  }, [currentUser, dateRange]);

  if (!currentUser) {
    return <AuthComponent />;
  }

  const StatCard = ({ title, value, icon: Icon, color, subtitle }: {
    title: string;
    value: string | number;
    icon: any;
    color: string;
    subtitle?: string;
  }) => (
    <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && (
              <p className="text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
            )}
          </div>
          <div className={`p-3 rounded-full bg-gradient-to-r ${color}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/10 to-green-50/10 dark:from-gray-900 dark:via-blue-900/5 dark:to-green-900/5">
      <div className="pt-40 pb-20">
        <div className="container mx-auto px-4 max-w-7xl">
          <motion.div 
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl sm:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
              Learning Analytics
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Track your progress, analyze patterns, and optimize your learning journey with AI-powered insights.
            </p>
          </motion.div>

          {/* Controls */}
          <motion.div 
            className="flex flex-wrap gap-4 mb-8 justify-between items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="flex gap-2">
              {['7d', '30d', '90d', '1y'].map((range) => (
                <Button
                  key={range}
                  variant={dateRange === range ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDateRange(range)}
                  className={dateRange === range ? 'bg-blue-600 hover:bg-blue-700' : ''}
                >
                  {range === '7d' ? '7 Days' :
                   range === '30d' ? '30 Days' :
                   range === '90d' ? '90 Days' : '1 Year'}
                </Button>
              ))}
            </div>
            <Button
              onClick={fetchAnalytics}
              disabled={isLoading}
              size="sm"
              variant="outline"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Refresh
            </Button>
          </motion.div>

          {isLoading && !data && (
            <div className="text-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-gray-600 dark:text-gray-400">Loading analytics data...</p>
            </div>
          )}

          {data && (
            <>
              {/* Summary Stats */}
              <motion.div 
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <StatCard
                  title="Total Sessions"
                  value={data.summary.total_sessions}
                  icon={Calendar}
                  color="from-blue-500 to-blue-600"
                />
                <StatCard
                  title="Completed Sessions"
                  value={data.summary.completed_sessions}
                  icon={CheckCircle}
                  color="from-green-500 to-green-600"
                />
                <StatCard
                  title="Videos Generated"
                  value={data.summary.total_videos}
                  icon={Video}
                  color="from-purple-500 to-purple-600"
                />
                <StatCard
                  title="Success Rate"
                  value={`${data.summary.success_rate.toFixed(1)}%`}
                  icon={Award}
                  color="from-orange-500 to-orange-600"
                />
              </motion.div>

              <div className="grid lg:grid-cols-2 gap-8">
                {/* Usage by Day */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                >
                  <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart className="w-5 h-5" />
                        Daily Activity
                      </CardTitle>
                      <CardDescription>
                        Your learning activity over time
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {Object.keys(data.usage_patterns.by_day).length > 0 ? (
                        <div className="space-y-3">
                          {Object.entries(data.usage_patterns.by_day)
                            .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
                            .slice(-10) // Show last 10 days
                            .map(([date, count]) => (
                              <div key={date} className="flex items-center justify-between">
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                  {formatDate(date)}
                                </span>
                                <div className="flex items-center gap-2">
                                  <div 
                                    className="bg-blue-200 dark:bg-blue-800 h-2 rounded"
                                    style={{ width: `${Math.max(20, (count / Math.max(...Object.values(data.usage_patterns.by_day))) * 100)}px` }}
                                  />
                                  <span className="text-sm font-medium w-8 text-right">{count}</span>
                                </div>
                              </div>
                            ))}
                        </div>
                      ) : (
                        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                          No activity data available for the selected period
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Service Usage */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        Service Usage
                      </CardTitle>
                      <CardDescription>
                        Which services you use most
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {Object.keys(data.usage_patterns.by_service).length > 0 ? (
                        <div className="space-y-4">
                          {Object.entries(data.usage_patterns.by_service)
                            .sort(([,a], [,b]) => b - a)
                            .map(([service, count]) => (
                              <div key={service} className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm font-medium capitalize">
                                    {service.replace('_', ' ')}
                                  </span>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">
                                    {count} uses
                                  </span>
                                </div>
                                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                  <div 
                                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full"
                                    style={{ 
                                      width: `${(count / Math.max(...Object.values(data.usage_patterns.by_service))) * 100}%` 
                                    }}
                                  />
                                </div>
                              </div>
                            ))}
                        </div>
                      ) : (
                        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                          No service usage data available
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              </div>

              {/* Insights and Recommendations */}
              <div className="grid lg:grid-cols-2 gap-8 mt-8">
                {/* AI Insights */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                >
                  <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-blue-800 dark:text-blue-200">
                        <TrendingUp className="w-5 h-5" />
                        AI Insights
                      </CardTitle>
                      <CardDescription className="text-blue-600 dark:text-blue-300">
                        Patterns identified in your learning behavior
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {data.insights.length > 0 ? (
                          data.insights.map((insight, index) => (
                            <div key={index} className="flex items-start gap-2">
                              <div className="w-2 h-2 rounded-full bg-blue-500 mt-2" />
                              <p className="text-sm text-blue-800 dark:text-blue-200">{insight}</p>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-blue-600 dark:text-blue-300">
                            Keep using NeoMentor to generate insights about your learning patterns!
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Recommendations */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                >
                  <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
                        <Clock className="w-5 h-5" />
                        Recommendations
                      </CardTitle>
                      <CardDescription className="text-green-600 dark:text-green-300">
                        AI-powered suggestions to improve your learning
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {data.recommendations.map((recommendation, index) => (
                          <div key={index} className="flex items-start gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 mt-2" />
                            <p className="text-sm text-green-800 dark:text-green-200">{recommendation}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            </>
          )}

          {!data && !isLoading && (
            <motion.div 
              className="text-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <BarChart className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-semibold mb-2">No Data Available</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Start using NeoMentor services to see your analytics data here.
              </p>
              <Button onClick={fetchAnalytics} className="bg-blue-600 hover:bg-blue-700">
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Loading Again
              </Button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
