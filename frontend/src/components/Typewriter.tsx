/**
 * Typewriter Component
 *
 * Creates an animated typewriter effect that types out text character by character.
 * Supports multiple text strings with automatic deletion and cycling.
 *
 * Features:
 * - Types text letter by letter at configurable speed
 * - Optional blinking cursor during or after typing
 * - Supports single text string or array of strings
 * - Can loop through multiple strings (type → wait → delete → next)
 * - Configurable delays, speeds, and cursor appearance
 *
 * Use Cases:
 * - Hero headings with animated text
 * - Rotating taglines or messages
 * - Welcome screens with dynamic greetings
 *
 * @example
 * // Single text, no loop
 * <Typewriter text="What can I help you find?" loop={false} />
 *
 * @example
 * // Multiple rotating texts
 * <Typewriter
 *   text={["Hello World", "Welcome Back", "Start Typing"]}
 *   loop={true}
 *   speed={50}
 * />
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

/**
 * Utility function to combine class names
 */
function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}

interface TypewriterProps {
  /** Single text string or array of strings to type */
  text: string | string[];
  /** Typing speed in milliseconds per character (default: 50ms) */
  speed?: number;
  /** Initial delay before typing starts (default: 0ms) */
  initialDelay?: number;
  /** Wait time before starting to delete text (default: 2000ms) */
  waitTime?: number;
  /** Deletion speed in milliseconds per character (default: 30ms) */
  deleteSpeed?: number;
  /** Whether to loop through texts infinitely (default: true) */
  loop?: boolean;
  /** Additional CSS classes for the text container */
  className?: string;
  /** Whether to show blinking cursor (default: true) */
  showCursor?: boolean;
  /** Hide cursor while typing (default: false) */
  hideCursorOnType?: boolean;
  /** Custom cursor character or element (default: "|") */
  cursorChar?: string | React.ReactNode;
  /** Additional CSS classes for the cursor */
  cursorClassName?: string;
}

export const Typewriter = ({
  text,
  speed = 50,
  initialDelay = 0,
  waitTime = 2000,
  deleteSpeed = 30,
  loop = true,
  className,
  showCursor = true,
  hideCursorOnType = false,
  cursorChar = '|',
  cursorClassName = 'ml-1',
}: TypewriterProps) => {
  // Current text being displayed
  const [displayText, setDisplayText] = useState('');
  // Current character index in the current text
  const [currentIndex, setCurrentIndex] = useState(0);
  // Whether we're in deletion mode
  const [isDeleting, setIsDeleting] = useState(false);
  // Index of current text in the array (if multiple texts)
  const [currentTextIndex, setCurrentTextIndex] = useState(0);

  // Convert single text to array for consistent handling
  const texts = Array.isArray(text) ? text : [text];

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    const currentText = texts[currentTextIndex];

    const startTyping = () => {
      if (isDeleting) {
        // DELETION MODE: Remove characters one by one
        if (displayText === '') {
          // Finished deleting, move to next text
          setIsDeleting(false);

          // Check if we should stop (no loop and at end)
          if (currentTextIndex === texts.length - 1 && !loop) {
            return; // Stop animation
          }

          // Move to next text (or loop back to first)
          setCurrentTextIndex((prev) => (prev + 1) % texts.length);
          setCurrentIndex(0);
          timeout = setTimeout(() => {}, waitTime);
        } else {
          // Continue deleting characters
          timeout = setTimeout(() => {
            setDisplayText((prev) => prev.slice(0, -1));
          }, deleteSpeed);
        }
      } else {
        // TYPING MODE: Add characters one by one
        if (currentIndex < currentText.length) {
          // Continue typing characters
          timeout = setTimeout(() => {
            setDisplayText((prev) => prev + currentText[currentIndex]);
            setCurrentIndex((prev) => prev + 1);
          }, speed);
        } else if (texts.length > 1) {
          // Finished typing, wait then start deleting (if multiple texts)
          timeout = setTimeout(() => {
            setIsDeleting(true);
          }, waitTime);
        }
        // If single text and done typing, just stop
      }
    };

    // Initial delay only on first character of first text
    if (currentIndex === 0 && !isDeleting && displayText === '') {
      timeout = setTimeout(startTyping, initialDelay);
    } else {
      startTyping();
    }

    return () => clearTimeout(timeout);
  }, [
    currentIndex,
    displayText,
    isDeleting,
    speed,
    deleteSpeed,
    waitTime,
    texts,
    currentTextIndex,
    loop,
    initialDelay,
  ]);

  return (
    <div className={`inline whitespace-pre-wrap tracking-tight ${className}`}>
      {/* The typed text */}
      <span>{displayText}</span>

      {/* Blinking cursor */}
      {showCursor && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{
            opacity: 1,
            transition: {
              duration: 0.01,
              repeat: Infinity,
              repeatDelay: 0.4,
              repeatType: 'reverse',
            },
          }}
          className={cn(
            cursorClassName,
            // Hide cursor during typing if hideCursorOnType is true
            hideCursorOnType &&
              (currentIndex < texts[currentTextIndex].length || isDeleting)
              ? 'hidden'
              : ''
          )}
        >
          {cursorChar}
        </motion.span>
      )}
    </div>
  );
};