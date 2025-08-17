'use client'

import { useEffect, useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useUser } from '@/hooks/useUser'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import { seedSampleProject } from '@/lib/localdb/seeds'
import { ProjectList } from '@/components/projects/ProjectList'
import { ProjectListItem } from '@/components/projects/ProjectListItem'
import type { Project } from '@/lib/localdb/types'
import { 
  Plus, 
  Search, 
  BookOpen
} from 'lucide-react'

export default function ProjectsPage() {
  const { userId, loading } = useUser()
  const [projects, setProjects] = useState<Project[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loadingProjects, setLoadingProjects] = useState(true)

  const loadProjects = useCallback(async () => {
    if (!userId) return
    
    try {
      const provider = createLocalDataProvider(userId)
      const userProjects = await provider.getProjects()
      setProjects(userProjects)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoadingProjects(false)
    }
  }, [userId])

  useEffect(() => {
    if (!loading && userId) {
      loadProjects()
    }
  }, [loading, userId, loadProjects])

  const handleCreateSampleProject = async () => {
    if (!userId) return
    
    try {
      await seedSampleProject(userId)
      await loadProjects()
    } catch (error) {
      console.error('Failed to create sample project:', error)
    }
  }


  const filteredProjects = projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  if (loading || loadingProjects) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading your projects...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        {/* Top Bar */}
        <div className="flex items-center justify-start mb-8">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">Projects</h1>
          </div>
        </div>
        {/* Search and Actions */}
        <div className="flex items-center justify-between mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-80"
            />
          </div>

          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        </div>

        {/* Projects List */}
        {filteredProjects.length > 0 ? (
          <div className="max-w-4xl">
            <ProjectList>
              {filteredProjects.map((project) => (
                <ProjectListItem
                  key={project.id}
                  id={project.id}
                  title={project.title}
                  description={project.description}
                  wordCount={project.wordCount || 0}
                  documentCount={project.documentCount || 0}
                  tags={project.tags}
                  updatedAt={project.updatedAt}
                />
              ))}
            </ProjectList>
          </div>
        ) : projects.length === 0 ? (
          // Empty State
          <div className="max-w-4xl">
            <div className="text-center py-20">
              <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-6">
                <BookOpen className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                Create your first universe and start building your story world.
              </p>
              <div className="flex items-center justify-center gap-3">
                <Button onClick={handleCreateSampleProject}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Sample Project
                </Button>
                <Button variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  New Project
                </Button>
              </div>
            </div>
          </div>
        ) : (
          // No Search Results
          <div className="max-w-4xl">
            <div className="text-center py-20">
              <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-6">
                <Search className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No projects found</h3>
              <p className="text-muted-foreground mb-8">
                Try adjusting your search terms or create a new project.
              </p>
              <Button variant="outline" onClick={() => setSearchQuery('')}>
                Clear Search
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}