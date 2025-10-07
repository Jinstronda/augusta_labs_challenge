/**
 * Virtual Scrolling Hook
 * 
 * Optimizes rendering of long lists by only rendering visible items.
 * Currently not needed for top 5 results, but useful for future enhancements
 * like showing all matching companies or incentives.
 * 
 * Usage:
 * ```tsx
 * const { visibleItems, containerRef, scrollToIndex } = useVirtualScroll({
 *   items: allItems,
 *   itemHeight: 100,
 *   containerHeight: 600,
 *   overscan: 3,
 * });
 * 
 * return (
 *   <div ref={containerRef} style={{ height: '600px', overflow: 'auto' }}>
 *     {visibleItems.map(item => (
 *       <div key={item.index} style={{ height: '100px' }}>
 *         {item.data}
 *       </div>
 *     ))}
 *   </div>
 * );
 * ```
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface VirtualScrollOptions<T> {
  /** Array of items to render */
  items: T[];
  /** Height of each item in pixels */
  itemHeight: number;
  /** Height of the scrollable container in pixels */
  containerHeight: number;
  /** Number of items to render outside visible area (for smooth scrolling) */
  overscan?: number;
}

interface VirtualScrollResult<T> {
  /** Items currently visible (plus overscan) */
  visibleItems: Array<{ index: number; data: T; style: React.CSSProperties }>;
  /** Ref to attach to the scrollable container */
  containerRef: React.RefObject<HTMLDivElement | null>;
  /** Function to scroll to a specific item index */
  scrollToIndex: (index: number) => void;
  /** Total height of all items (for scrollbar) */
  totalHeight: number;
}

/**
 * Hook for virtual scrolling optimization
 */
export function useVirtualScroll<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 3,
}: VirtualScrollOptions<T>): VirtualScrollResult<T> {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  // Calculate visible range
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  // Total height for scrollbar
  const totalHeight = items.length * itemHeight;

  // Handle scroll events
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Scroll to specific index
  const scrollToIndex = useCallback(
    (index: number) => {
      const container = containerRef.current;
      if (!container) return;

      const targetScrollTop = index * itemHeight;
      container.scrollTo({
        top: targetScrollTop,
        behavior: 'smooth',
      });
    },
    [itemHeight]
  );

  // Build visible items with positioning
  const visibleItems = [];
  for (let i = startIndex; i <= endIndex; i++) {
    if (i >= 0 && i < items.length) {
      visibleItems.push({
        index: i,
        data: items[i],
        style: {
          position: 'absolute' as const,
          top: i * itemHeight,
          height: itemHeight,
          width: '100%',
        },
      });
    }
  }

  return {
    visibleItems,
    containerRef,
    scrollToIndex,
    totalHeight,
  };
}

/**
 * Example usage:
 * 
 * ```tsx
 * function VirtualScrollExample() {
 *   const items = Array.from({ length: 10000 }, (_, i) => `Item ${i + 1}`);
 * 
 *   const { visibleItems, containerRef, totalHeight } = useVirtualScroll({
 *     items,
 *     itemHeight: 50,
 *     containerHeight: 400,
 *     overscan: 5,
 *   });
 * 
 *   return (
 *     <div
 *       ref={containerRef}
 *       style={{
 *         height: '400px',
 *         overflow: 'auto',
 *         position: 'relative',
 *         border: '1px solid #ccc',
 *       }}
 *     >
 *       <div style={{ height: totalHeight, position: 'relative' }}>
 *         {visibleItems.map((item) => (
 *           <div
 *             key={item.index}
 *             style={{
 *               ...item.style,
 *               padding: '10px',
 *               borderBottom: '1px solid #eee',
 *             }}
 *           >
 *             {item.data}
 *           </div>
 *         ))}
 *       </div>
 *     </div>
 *   );
 * }
 * ```
 */
