/**
 * MessageLoading Component
 *
 * Displays an animated loading indicator with three bouncing dots.
 * Used to show that the assistant is processing a response.
 *
 * Features:
 * - Three circles that animate vertically
 * - Smooth spline animation for natural motion
 * - Staggered timing (0.1s delay between each dot)
 * - Matches theme colors (inherits currentColor)
 *
 * Animation Details:
 * - Duration: 0.6s per cycle
 * - Movement: Y-axis from 12 to 6 and back to 12
 * - Easing: Cubic bezier spline for smooth acceleration/deceleration
 */

export function MessageLoading() {
  return (
    <div className="flex items-center gap-1">
      <div className="loading-dots">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  );
}