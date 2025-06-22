"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X, Sun, Moon, User, LogOut, History, Crown } from "lucide-react"
import { motion } from "framer-motion"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import NeoMentorIcon from "@/components/neo-mentor-icon"
import { cn } from "@/lib/utils"
import { useAuth } from "@/lib/auth-context"

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const { currentUser, signInWithGoogle, logout } = useAuth()

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true)
      } else {
        setScrolled(false)
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleMenu = () => setIsOpen(!isOpen)
  const closeMenu = () => setIsOpen(false)
  
  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const handleSignIn = async () => {
    try {
      await signInWithGoogle()
    } catch (error) {
      console.error('Error signing in:', error)
    }
  }

  const handleSignOut = async () => {
    try {
      await logout()
      setShowProfile(false)
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "About", path: "/about" },
    { 
      name: "Services", 
      path: "/services",
      children: [
        { name: "Video Generation", path: "/video-generation" },
        { name: "Course Scheduler", path: "/course-scheduler" },
        { name: "Syllabus Generation", path: "/syllabus-generation" },
        { name: "Voice Cloning", path: "/voice-cloning" },
        { name: "Analytics", path: "/analytics" },
      ]
    },
    { name: "Contact", path: "/contact" },
  ]

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled 
          ? "bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-md py-2" 
          : "bg-transparent py-4"
      )}
    >
      <div className="container mx-auto px-4">
        <nav className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <NeoMentorIcon className="w-8 h-8" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              NeoMentor
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                href={link.path}
                className={cn(
                  "font-medium text-sm transition-colors hover:text-blue-600 dark:hover:text-blue-400",
                  pathname === link.path 
                    ? "text-blue-600 dark:text-blue-400" 
                    : "text-gray-700 dark:text-gray-200"
                )}
              >
                {link.name}
              </Link>
            ))}
            
            <Button 
              variant="outline" 
              size="icon" 
              onClick={toggleTheme}
              className="rounded-full"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            
            {/* Authentication Section */}
            {currentUser ? (
              <div className="relative">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowProfile(!showProfile)}
                  className="rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  {currentUser.photoURL ? (
                    <img
                      src={currentUser.photoURL}
                      alt="Profile"
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <User className="w-5 h-5" />
                  )}
                </Button>

                {/* Profile Dropdown */}
                {showProfile && (
                  <>
                    {/* Backdrop */}
                    <div 
                      className="fixed inset-0 z-[9998]" 
                      onClick={() => setShowProfile(false)}
                    />
                    
                    {/* Profile Menu */}
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-[9999]"
                    >
                      {/* Profile Header */}
                      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-t-lg">
                        <div className="flex items-center space-x-3">
                          {currentUser.photoURL ? (
                            <img
                              src={currentUser.photoURL}
                              alt="Profile"
                              className="w-10 h-10 rounded-full border-2 border-white shadow-sm"
                            />
                          ) : (
                            <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center border-2 border-white shadow-sm">
                              <User className="w-5 h-5" />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                              {currentUser.displayName || 'User'}
                            </h3>
                            <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                              {currentUser.email}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Profile Content */}
                      <div className="p-4 space-y-3">
                        <Button
                          variant="ghost"
                          className="w-full justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                          onClick={() => {
                            setShowProfile(false)
                            window.location.href = '/profile'
                          }}
                        >
                          <History className="w-4 h-4 mr-3" />
                          My Videos
                        </Button>
                        
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                          <Button
                            variant="ghost"
                            onClick={handleSignOut}
                            className="w-full justify-start text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            <LogOut className="w-4 h-4 mr-3" />
                            Sign out
                          </Button>
                        </div>
                      </div>
                    </motion.div>
                  </>
                )}
              </div>
            ) : (
              <Button 
                variant="gradient" 
                size="sm"
                onClick={handleSignIn}
              >
                Sign In
              </Button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-4">
            <Button 
              variant="outline" 
              size="icon" 
              onClick={toggleTheme}
              className="rounded-full"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleMenu}
              className="text-gray-700 dark:text-gray-200"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </nav>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="md:hidden absolute top-full left-0 right-0 bg-white dark:bg-gray-900 shadow-lg"
        >
          <div className="container mx-auto px-4 py-4 flex flex-col space-y-4">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                href={link.path}
                className={cn(
                  "font-medium text-lg py-2 transition-colors",
                  pathname === link.path 
                    ? "text-blue-600 dark:text-blue-400" 
                    : "text-gray-700 dark:text-gray-200"
                )}
                onClick={closeMenu}
              >
                {link.name}
              </Link>
            ))}
            
            {/* Mobile Auth Section */}
            {currentUser ? (
              <div className="space-y-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-3">
                  {currentUser.photoURL ? (
                    <img
                      src={currentUser.photoURL}
                      alt="Profile"
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <User className="w-6 h-6" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {currentUser.displayName || 'User'}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {currentUser.email}
                    </p>
                  </div>
                </div>
                <Link
                  href="/profile"
                  onClick={closeMenu}
                  className="w-full"
                >
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                  >
                    <History className="w-4 h-4 mr-2" />
                    My Videos
                  </Button>
                </Link>
                <Button 
                  variant="outline" 
                  onClick={handleSignOut}
                  className="w-full"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button 
                variant="gradient"
                onClick={handleSignIn}
                className="w-full"
              >
                Sign In
              </Button>
            )}
          </div>
        </motion.div>
      )}
    </header>
  )
}

export default Navbar
