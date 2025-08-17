import { useRef, useEffect, useState } from 'react'

export function useTabScroll(dependencies: any[] = []) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(false)
  const [hasOverflow, setHasOverflow] = useState(false)

  // Check scroll state
  const updateScrollState = () => {
    if (!scrollContainerRef.current) return
    
    const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current
    setCanScrollLeft(scrollLeft > 0)
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1)
    setHasOverflow(scrollWidth > clientWidth)
  }

  useEffect(() => {
    updateScrollState()
    const container = scrollContainerRef.current
    if (container) {
      container.addEventListener('scroll', updateScrollState)
      const resizeObserver = new ResizeObserver(updateScrollState)
      resizeObserver.observe(container)
      
      return () => {
        container.removeEventListener('scroll', updateScrollState)
        resizeObserver.disconnect()
      }
    }
  }, dependencies)

  return {
    scrollContainerRef,
    canScrollLeft,
    canScrollRight,
    hasOverflow,
    updateScrollState
  }
}