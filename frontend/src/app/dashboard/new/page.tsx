"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { projectTemplates } from "@/data/projects";
import { 
  ArrowLeft, 
  BookOpen, 
  Loader2,
  Sparkles,
  Users,
  Folder,
  Plus
} from "lucide-react";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    genre: ""
  });

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = projectTemplates.find(t => t.id === templateId);
    if (template) {
      setFormData(prev => ({
        ...prev,
        genre: template.genre
      }));
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTemplate || !formData.title.trim()) return;

    setLoading(true);
    
    try {
      // TODO: API call to create project
      // const response = await createProject({
      //   ...formData,
      //   template: selectedTemplate
      // });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Redirect to the new project workspace
      router.push(`/?project=new&template=${selectedTemplate}`);
    } catch (error) {
      console.error("Failed to create project:", error);
    } finally {
      setLoading(false);
    }
  };

  const selectedTemplateData = projectTemplates.find(t => t.id === selectedTemplate);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 h-16">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Link>
            </Button>
            <div className="h-4 w-px bg-border" />
            <h1 className="text-lg font-semibold">Create New Project</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Project Templates */}
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Choose a Template</h2>
              <p className="text-muted-foreground">
                Select a template that matches your writing style and genre. 
                This will set up the initial folder structure and organization.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projectTemplates.map((template) => (
                <Card 
                  key={template.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedTemplate === template.id 
                      ? "ring-2 ring-primary border-primary" 
                      : ""
                  }`}
                  onClick={() => handleTemplateSelect(template.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{template.icon}</span>
                      <div>
                        <CardTitle className="text-base">{template.name}</CardTitle>
                        {template.genre && (
                          <Badge variant="secondary" className="mt-1 text-xs">
                            {template.genre}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm mb-3">
                      {template.description}
                    </CardDescription>
                    {template.folders.length > 0 && (
                      <div className="space-y-2">
                        <div className="text-xs font-medium text-muted-foreground">
                          Includes folders:
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {template.folders.map((folder, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              <Folder className="h-3 w-3 mr-1" />
                              {folder}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Project Details Form */}
          {selectedTemplate && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Project Details
                </CardTitle>
                <CardDescription>
                  Provide basic information about your new writing project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateProject} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="title">Project Title *</Label>
                      <Input
                        id="title"
                        placeholder="e.g., The Chronicles of Elara"
                        value={formData.title}
                        onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="genre">Genre</Label>
                      <Input
                        id="genre"
                        placeholder="e.g., Fantasy, Mystery, Romance"
                        value={formData.genre}
                        onChange={(e) => setFormData(prev => ({ ...prev, genre: e.target.value }))}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="Describe your story, its themes, or anything that will help you remember what this project is about..."
                      rows={3}
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    />
                  </div>

                  {selectedTemplateData && selectedTemplateData.folders.length > 0 && (
                    <div className="bg-secondary/30 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">Template: {selectedTemplateData.name}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mb-3">
                        This will create the following folder structure to help organize your project:
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {selectedTemplateData.folders.map((folder, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            <Folder className="h-3 w-3 mr-1" />
                            {folder}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end gap-3 pt-4">
                    <Button variant="outline" type="button" asChild>
                      <Link href="/dashboard">Cancel</Link>
                    </Button>
                    <Button type="submit" disabled={loading || !formData.title.trim()}>
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating...
                        </>
                      ) : (
                        <>
                          <Plus className="mr-2 h-4 w-4" />
                          Create Project
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}