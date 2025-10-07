"use client";

import * as React from "react";
import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface TypewriterProps {
  text: string | string[];
  speed?: number;
  initialDelay?: number;
  waitTime?: number;
  deleteSpeed?: number;
  loop?: boolean;
  className?: string;
  showCursor?: boolean;
  hideCursorOnType?: boolean;
  cursorChar?: string | React.ReactNode;
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
  cursorChar = "|",
  cursorClassName = "ml-1",
}: TypewriterProps) => {
  const [displayText, setDisplayText] = React.useState("");
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [currentTextIndex, setCurrentTextIndex] = React.useState(0);

  const texts = React.useMemo(() => (Array.isArray(text) ? text : [text]), [text]);

  React.useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    const currentText = texts[currentTextIndex] ?? "";

    const startTyping = () => {
      if (isDeleting) {
        if (displayText === "") {
          setIsDeleting(false);
          if (currentTextIndex === texts.length - 1 && !loop) {
            return;
          }
          setCurrentTextIndex((prev) => (prev + 1) % texts.length);
          setCurrentIndex(0);
          timeout = setTimeout(() => undefined, waitTime);
        } else {
          timeout = setTimeout(() => {
            setDisplayText((prev) => prev.slice(0, -1));
          }, deleteSpeed);
        }
      } else if (currentIndex < currentText.length) {
        timeout = setTimeout(() => {
          setDisplayText((prev) => prev + currentText[currentIndex]);
          setCurrentIndex((prev) => prev + 1);
        }, speed);
      } else if (texts.length > 1) {
        timeout = setTimeout(() => {
          setIsDeleting(true);
        }, waitTime);
      }
    };

    if (currentIndex === 0 && !isDeleting && displayText === "") {
      timeout = setTimeout(startTyping, initialDelay);
    } else {
      startTyping();
    }

    return () => {
      clearTimeout(timeout);
    };
  }, [
    currentIndex,
    currentTextIndex,
    deleteSpeed,
    displayText,
    initialDelay,
    isDeleting,
    loop,
    speed,
    texts,
    waitTime,
  ]);

  return (
    <div className={cn("inline whitespace-pre-wrap tracking-tight", className)}>
      <span>{displayText}</span>
      {showCursor ? (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{
            opacity: 1,
            transition: {
              duration: 0.01,
              repeat: Infinity,
              repeatDelay: 0.4,
              repeatType: "reverse",
            },
          }}
          className={cn(
            cursorClassName,
            hideCursorOnType &&
              (currentIndex < (texts[currentTextIndex]?.length ?? 0) || isDeleting)
              ? "hidden"
              : undefined,
          )}
        >
          {cursorChar}
        </motion.span>
      ) : null}
    </div>
  );
};
