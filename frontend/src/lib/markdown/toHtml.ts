import MarkdownIt from 'markdown-it'
import DOMPurify from 'isomorphic-dompurify'

// Singleton parser to avoid re-instantiation
const md = new MarkdownIt({
  html: false, // do not trust raw HTML from AI
  linkify: true,
  breaks: true, // single newlines -> <br>
  typographer: true,
})

export function mdToHtml(markdown: string): string {
  const rendered = md.render(markdown || '')
  return DOMPurify.sanitize(rendered)
}


