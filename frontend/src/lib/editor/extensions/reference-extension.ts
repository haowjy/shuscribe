import { ReactRenderer } from '@tiptap/react';
import { SuggestionOptions } from '@tiptap/suggestion';
import { Mention } from '@tiptap/extension-mention';
import tippy from 'tippy.js';
import { ReferenceList, ReferenceListRef } from '@/components/editor/suggestions/reference-list';
import { ReferenceItem } from '@/data/reference-items';

// Icon SVG map for different file types
function getIconSvg(iconName: string): string {
  const icons: Record<string, string> = {
    'User': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
    'Skull': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="15" cy="12" r="1"></circle><path d="M8 20v2h8v-2"></path><path d="m12.5 17-.5-1-.5 1h1z"></path><path d="M16 20a2 2 0 0 0 1.56-3.25 8 8 0 1 0-11.12 0A2 2 0 0 0 8 20"></path></svg>',
    'Building': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path><path d="M6 12H4a2 2 0 0 0-2 2v8h4"></path><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-4"></path><path d="M10 6h4"></path><path d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path></svg>',
    'Landmark': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="22" x2="21" y2="22"></line><line x1="6" y1="18" x2="6" y2="11"></line><line x1="10" y1="18" x2="10" y2="11"></line><line x1="14" y1="18" x2="14" y2="11"></line><line x1="18" y1="18" x2="18" y2="11"></line><polygon points="12 2 20 7 4 7"></polygon></svg>',
    'Clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12,6 12,12 16,14"></polyline></svg>',
    'History': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l4 2"></path></svg>',
    'BookOpen': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
    'folder': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path></svg>',
    'file-text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10,9 9,9 8,9"></polyline></svg>',
  };
  
  return icons[iconName] || icons['file-text'];
}

export interface ReferenceExtensionOptions {
  suggestions: Omit<SuggestionOptions, 'editor'>;
  onReferenceClick?: (referenceId: string, referenceLabel: string) => void;
}

export const ReferenceExtension = Mention.extend<ReferenceExtensionOptions>({
  name: 'reference',

  addStorage() {
    return {
      onReferenceClick: null,
    };
  },

  addOptions() {
    return {
      ...this.parent?.(),
      HTMLAttributes: {
        class: 'reference-link',
        'data-type': 'reference',
      },
      renderText({ node }) {
        return `@${node.attrs.label || node.attrs.id}`;
      },
      suggestion: {
        char: '@',
        allowSpaces: false,
        allowedPrefixes: [' ', '\n'],
        startOfLine: false,
        
        items: () => {
          // This will be overridden by the parent component
          return [];
        },
        
        render: () => {
          let component: ReactRenderer<ReferenceListRef>;
          let popup: ReturnType<typeof tippy> | undefined;

          return {
            onStart: (props) => {
              component = new ReactRenderer(ReferenceList, {
                props,
                editor: props.editor,
              });

              if (!props.clientRect) {
                return;
              }

              popup = tippy(document.body, {
                getReferenceClientRect: props.clientRect,
                appendTo: () => document.body,
                content: component.element,
                showOnCreate: true,
                interactive: true,
                trigger: 'manual',
                placement: 'bottom-start',
                theme: 'light',
                maxWidth: 'none',
                offset: [0, 8],
                onHidden: () => {
                  component.destroy();
                  if (Array.isArray(popup)) {
                    popup[0]?.destroy();
                  } else {
                    popup?.destroy();
                  }
                },
              });
            },

            onUpdate(props) {
              component?.updateProps(props);

              if (!props.clientRect) {
                return;
              }

              if (Array.isArray(popup)) {
                popup[0]?.setProps({
                  getReferenceClientRect: props.clientRect,
                });
              } else {
                popup?.setProps({
                  getReferenceClientRect: props.clientRect,
                });
              }
            },

            onKeyDown(props) {
              if (props.event.key === 'Escape') {
                if (Array.isArray(popup)) {
                  popup[0]?.hide();
                } else {
                  popup?.hide();
                }
                return true;
              }

              return component?.ref?.onKeyDown(props.event) || false;
            },

            onExit() {
              if (Array.isArray(popup)) {
                popup[0]?.destroy();
              } else {
                popup?.destroy();
              }
              component?.destroy();
            },
          };
        },
        
        command: ({ editor, range, props }) => {
          const item = props as ReferenceItem;
          
          // Insert the reference as a mention node
          editor
            .chain()
            .focus()
            .insertContentAt(range, [
              {
                type: 'reference',
                attrs: {
                  id: item.id,
                  label: item.label,
                  type: item.type,
                  path: item.path,
                  icon: item.icon,
                },
              },
              {
                type: 'text',
                text: ' ',
              },
            ])
            .run();
        },
      },
    };
  },

  onCreate() {
    // Store the click handler in extension storage
    if (this.options.onReferenceClick) {
      this.storage.onReferenceClick = this.options.onReferenceClick;
      console.log('ReferenceExtension: Stored click handler in storage');
    } else {
      console.warn('ReferenceExtension: No onReferenceClick option provided');
    }
  },

  addAttributes() {
    return {
      ...this.parent?.(),
      type: {
        default: 'file',
        parseHTML: element => element.getAttribute('data-reference-type'),
        renderHTML: attributes => {
          if (!attributes.type) {
            return {};
          }
          return {
            'data-reference-type': attributes.type,
          };
        },
      },
      path: {
        default: null,
        parseHTML: element => element.getAttribute('data-reference-path'),
        renderHTML: attributes => {
          if (!attributes.path) {
            return {};
          }
          return {
            'data-reference-path': attributes.path,
          };
        },
      },
      icon: {
        default: null,
        parseHTML: element => element.getAttribute('data-reference-icon'),
        renderHTML: attributes => {
          if (!attributes.icon) {
            return {};
          }
          return {
            'data-reference-icon': attributes.icon,
          };
        },
      },
    };
  },

  addNodeView() {
    return ({ node, editor }) => {
      const dom = document.createElement('span');
      dom.className = 'reference-link inline-flex items-center gap-1 px-2 py-1 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md cursor-pointer transition-colors text-sm font-medium text-blue-700 hover:text-blue-800';
      dom.setAttribute('data-reference-id', node.attrs.id);
      dom.setAttribute('data-reference-type', node.attrs.type);
      dom.setAttribute('data-reference-path', node.attrs.path);
      dom.setAttribute('data-reference-icon', node.attrs.icon || '');
      
      // Create icon element
      const iconElement = document.createElement('span');
      iconElement.className = 'w-3 h-3 flex-shrink-0';
      
      // Set icon based on type and icon attribute
      const iconName = node.attrs.icon || (node.attrs.type === 'folder' ? 'folder' : 'file-text');
      iconElement.innerHTML = getIconSvg(iconName);
      
      // Create text element
      const textElement = document.createElement('span');
      textElement.textContent = `@${node.attrs.label}`;
      
      // Append icon and text
      dom.appendChild(iconElement);
      dom.appendChild(textElement);
      
      // Add click handler
      dom.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        
        console.log('Reference clicked:', node.attrs.id, node.attrs.label);
        
        // Get the click handler from extension storage
        const referenceStorage = editor.storage.reference || {};
        const clickHandler = referenceStorage.onReferenceClick;
        
        // Call the click handler if provided
        if (clickHandler && typeof clickHandler === 'function') {
          console.log('Calling reference click handler');
          clickHandler(node.attrs.id, node.attrs.label);
        } else {
          console.warn('No reference click handler found. Storage contents:', referenceStorage);
        }
      });

      return {
        dom,
        contentDOM: null,
        update: (updatedNode) => {
          if (updatedNode.type.name !== 'reference') {
            return false;
          }
          
          // Update attributes
          dom.setAttribute('data-reference-id', updatedNode.attrs.id);
          dom.setAttribute('data-reference-type', updatedNode.attrs.type);
          dom.setAttribute('data-reference-path', updatedNode.attrs.path);
          dom.setAttribute('data-reference-icon', updatedNode.attrs.icon || '');
          
          // Update icon
          const iconElement = dom.querySelector('.w-3.h-3') as HTMLElement;
          if (iconElement) {
            const iconName = updatedNode.attrs.icon || (updatedNode.attrs.type === 'folder' ? 'folder' : 'file-text');
            iconElement.innerHTML = getIconSvg(iconName);
          }
          
          // Update text
          const textElement = dom.querySelector('span:last-child') as HTMLElement;
          if (textElement) {
            textElement.textContent = `@${updatedNode.attrs.label}`;
          }
          
          return true;
        },
      };
    };
  },
});

// Add tippy.js styles
const tippyStyles = `
  .tippy-box[data-theme~='light'] {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    padding: 4px 0;
    font-size: 14px;
    line-height: 1.4;
    color: #1f2937;
  }
  
  .tippy-box[data-theme~='light'] .tippy-content {
    padding: 0;
  }
  
  .tippy-box[data-theme~='light'] .tippy-arrow {
    color: white;
  }
  
  .tippy-box[data-theme~='light'] .tippy-arrow:before {
    border-top-color: #e2e8f0;
  }
`;

// Inject styles if not already present
if (typeof document !== 'undefined' && !document.getElementById('tiptap-reference-styles')) {
  const styleElement = document.createElement('style');
  styleElement.id = 'tiptap-reference-styles';
  styleElement.textContent = tippyStyles;
  document.head.appendChild(styleElement);
}

export default ReferenceExtension;