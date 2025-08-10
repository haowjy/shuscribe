"use client";

import { notFound } from "next/navigation";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronDown } from "lucide-react";
import { 
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider, 
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

// Gallery navigation config
type GalleryItem = { 
  title: string; 
  href: string; 
  description?: string;
};

type GallerySection = { 
  title: string; 
  items: GalleryItem[]; 
};

const galleryNav: GallerySection[] = [
  {
    title: "Editor",
    items: [
      { 
        title: "Full", 
        href: "/component-gallery/editor/full",
        description: "Full-featured editor with all toolbar sections"
      },
      { 
        title: "Chat", 
        href: "/component-gallery/editor/chat",
        description: "Lightweight editor for messaging interfaces"
      },
      { 
        title: "Notes", 
        href: "/component-gallery/editor/notes",
        description: "Minimal editor for quick note-taking"
      },
    ],
  },
];

function ComponentGallerySidebar() {
  const pathname = usePathname();

  return (
    <Sidebar side="left" collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2 p-2 group-data-[collapsible=icon]:justify-center">
          <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <span className="text-xs font-bold">📚</span>
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
            <span className="truncate font-semibold text-sidebar-foreground">Gallery</span>
            <span className="truncate text-xs text-sidebar-foreground/70">
              Components
            </span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        {galleryNav.map((section) => (
          <Collapsible key={section.title} defaultOpen={false} className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel asChild>
                <CollapsibleTrigger className="flex items-center justify-between w-full">
                  {section.title}
                  <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {section.items.map((item) => (
                      <SidebarMenuItem key={item.href}>
                        <SidebarMenuButton
                          asChild
                          isActive={pathname === item.href}
                          tooltip={item.description}
                        >
                          <Link href={item.href}>
                            <span>{item.title}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
        ))}
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}

export default function ComponentGalleryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const enabled =
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_ENABLE_COMPONENT_GALLERY === "true";

  if (!enabled) notFound();

  const pathname = usePathname();

  // Generate breadcrumb for gallery routes
  const getBreadcrumb = () => {
    const parts = pathname.split('/').filter(Boolean);
    if (parts[0] !== 'component-gallery') return 'Component Gallery';
    
    const breadcrumbs = ['Component Gallery'];
    
    if (parts[1] === 'editor' && parts[2]) {
      breadcrumbs.push('Editor');
      breadcrumbs.push(parts[2].charAt(0).toUpperCase() + parts[2].slice(1));
    }
    
    return breadcrumbs.join(' > ');
  };

  return (
    <SidebarProvider>
      <ComponentGallerySidebar />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <div className="text-sm">
            <span className="font-semibold text-foreground">
              {getBreadcrumb()}
            </span>
          </div>
        </header>
        <main className="flex flex-1 flex-col gap-4 p-4 pt-6">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}