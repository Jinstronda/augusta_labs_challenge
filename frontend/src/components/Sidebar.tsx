"use client";

import React, { useState, createContext, useContext } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X } from 'lucide-react';

/**
 * Utility function to combine class names
 */
function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}

/**
 * Sidebar Context for state management
 */
interface SidebarContextProps {
  /** Whether sidebar is open/expanded */
  open: boolean;
  /** Function to set open state */
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  /** Whether animations are enabled */
  animate: boolean;
}

const SidebarContext = createContext<SidebarContextProps | undefined>(undefined);

/**
 * Hook to access sidebar context
 * @throws Error if used outside SidebarProvider
 */
export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};

/**
 * SidebarProvider - Context provider for sidebar state
 *
 * Manages the open/close state of the sidebar and provides it to all child components.
 *
 * @param children - Child components that can access sidebar context
 * @param open - Controlled open state (optional)
 * @param setOpen - Controlled state setter (optional)
 * @param animate - Whether to enable animations (default: true)
 */
export const SidebarProvider = ({
  children,
  open: openProp,
  setOpen: setOpenProp,
  animate = true,
}: {
  children: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  const [openState, setOpenState] = useState(false);

  // Use controlled state if provided, otherwise use internal state
  const open = openProp !== undefined ? openProp : openState;
  const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState;

  return (
    <SidebarContext.Provider value={{ open, setOpen, animate }}>
      {children}
    </SidebarContext.Provider>
  );
};

/**
 * Sidebar - Root wrapper component
 *
 * Simple wrapper that provides context to all sidebar components.
 *
 * @param children - Child components (usually SidebarBody)
 * @param open - Optional controlled open state
 * @param setOpen - Optional controlled state setter
 * @param animate - Whether to enable animations
 */
export const Sidebar = ({
  children,
  open,
  setOpen,
  animate,
}: {
  children: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  );
};

/**
 * SidebarBody - Renders both desktop and mobile sidebar variants
 *
 * Automatically renders both versions and uses CSS (hidden/flex) to show
 * the appropriate one based on screen size.
 *
 * @param props - Standard div props for styling
 */
export const SidebarBody = (props: React.ComponentProps<typeof motion.div>) => {
  return (
    <>
      <DesktopSidebar {...props} />
      <MobileSidebar {...(props as React.ComponentProps<'div'>)} />
    </>
  );
};

/**
 * DesktopSidebar - Collapsible sidebar for desktop screens (md and up)
 *
 * Behavior:
 * - Default width: 60px (collapsed)
 * - Expanded width: 260px (on hover)
 * - Smooth width animation via framer-motion
 * - Hidden on mobile (< md breakpoint)
 *
 * @param className - Additional CSS classes
 * @param children - Sidebar content (nav links, user info, etc.)
 * @param props - Additional motion.div props
 */
export const DesktopSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<typeof motion.div>) => {
  const { open, setOpen, animate } = useSidebar();

  return (
    <motion.div
      className={cn(
        'h-full px-4 py-6 hidden md:flex md:flex-col bg-[#202123] text-slate-200 border-r border-black/20 w-[260px] flex-shrink-0',
        className
      )}
      animate={{
        // Animate width only if animate is enabled
        width: animate ? (open ? '260px' : '60px') : '260px',
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      {...props}
    >
      {children}
    </motion.div>
  );
};

/**
 * MobileSidebar - Hamburger menu with slide-in drawer for mobile
 *
 * Behavior:
 * - Shows hamburger menu icon in top bar
 * - Clicking opens full-screen drawer with slide animation
 * - Drawer slides in from left (-100% → 0%)
 * - Close button (X) in top-right corner
 * - Visible only on mobile (< md breakpoint)
 *
 * @param className - Additional CSS classes for the drawer
 * @param children - Sidebar content for mobile view
 * @param props - Additional div props
 */
export const MobileSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) => {
  const { open, setOpen } = useSidebar();

  return (
    <>
      {/* Top bar with hamburger menu */}
      <div
        className={cn(
          'h-14 px-4 py-4 flex flex-row md:hidden items-center justify-between bg-[#202123] text-slate-200 border-b border-black/20 w-full'
        )}
        {...props}
      >
        <div className="flex justify-end z-20 w-full">
          <Menu
            className="text-foreground cursor-pointer"
            onClick={() => setOpen(!open)}
            aria-label="Open menu"
          />
        </div>

        {/* Slide-in drawer */}
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ x: '-100%', opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: '-100%', opacity: 0 }}
              transition={{
                duration: 0.3,
                ease: 'easeInOut',
              }}
              className={cn(
                'fixed h-full w-full inset-0 bg-[#202123] text-slate-200 p-10 z-[100] flex flex-col justify-between',
                className
              )}
            >
              {/* Close button */}
              <div
                className="absolute right-10 top-10 z-50 text-foreground cursor-pointer"
                onClick={() => setOpen(!open)}
                aria-label="Close menu"
              >
                <X />
              </div>
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
};

/**
 * Link structure for sidebar navigation
 */
interface Links {
  /** Display text for the link */
  label: string;
  /** URL or route (use "#" for placeholder) */
  href: string;
  /** Icon element to display */
  icon: React.JSX.Element | React.ReactNode;
}

/**
 * SidebarLink - Navigation link with icon and label
 *
 * Features:
 * - Icon always visible (even when sidebar collapsed)
 * - Label fades in/out with sidebar expansion
 * - Hover effect: background change + label slide
 * - Smooth transitions via framer-motion
 *
 * @param link - Link object with label, href, and icon
 * @param className - Additional CSS classes
 * @param props - Additional link props
 */
export const SidebarLink = ({
  link,
  className,
  ...props
}: {
  link: Links;
  className?: string;
  props?: React.ComponentProps<'a'>;
}) => {
  const { open, animate } = useSidebar();

  return (
    <a
      href={link.href}
      className={cn(
        'flex items-center justify-start gap-2 group/sidebar py-2 px-3 rounded-md text-slate-200/90 hover:bg-white/10 hover:text-white transition-colors cursor-pointer',
        className
      )}
      {...props}
    >
      {/* Icon - always visible */}
      {link.icon}

      {/* Label - fades in when sidebar opens */}
      <motion.span
        animate={{
          display: animate ? (open ? 'inline-block' : 'none') : 'inline-block',
          opacity: animate ? (open ? 1 : 0) : 1,
        }}
        className="text-slate-200/80 text-sm group-hover/sidebar:translate-x-1 transition duration-150 whitespace-pre inline-block !p-0 !m-0"
      >
        {link.label}
      </motion.span>
    </a>
  );
};