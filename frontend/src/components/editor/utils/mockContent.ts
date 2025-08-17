// Mock content generator for demo purposes
export function getContentForTab(tabName: string): string {
  if (tabName.includes('chapter')) {
    return `# Chapter 1: The Beginning

The rain fell steadily against the windows of the old manor, each drop tracing intricate patterns down the glass. Sarah pressed her face closer to the pane, watching the storm rage outside while the warmth of the fireplace danced across her back.

## The Discovery

In the attic, beneath layers of dust and forgotten memories, she found the journal. Its leather binding was worn smooth by countless hands, and the pages yellowed with age.

> "Every story has a beginning, but not every beginning leads to the same end." - *From the journal of Margaret Thornfield*

The first entry was dated fifty years ago, written in a delicate script that spoke of secrets and shadows.`
  } 
  
  if (tabName.includes('character')) {
    return `# Characters

## Main Characters

### Sarah Mitchell
- **Age**: 28
- **Occupation**: Historian
- **Key Traits**: Curious, determined, intuitive
- **Background**: Recently inherited the Thornfield Manor from a distant relative

### Margaret Thornfield (Historical)
- **Age**: Unknown (deceased)
- **Role**: Former manor owner
- **Significance**: Author of the mysterious journal
- **Connection**: Sarah's great-grandmother

## Supporting Characters

### Thomas Grey
- **Age**: 35
- **Role**: Local historian and Sarah's research partner
- **Personality**: Methodical, skeptical, protective`
  }
  
  return `# ${tabName.replace('.md', '').replace('-', ' ').toUpperCase()}

Start writing your content here...

This is a mock document for the workspace skeleton. You can begin editing and the @-reference system will help you connect related content throughout your project.`
}