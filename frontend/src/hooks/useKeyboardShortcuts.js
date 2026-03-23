import { useEffect } from 'react';

export default function useKeyboardShortcuts(handlers) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        handlers.onNew?.();
      }
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        handlers.onSearch?.();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
}