import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

// Initialize mermaid with default configuration
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'system-ui, sans-serif',
});

export default function Mermaid({ chart, className = '' }) {
  const mermaidRef = useRef(null);
  const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 11)}`;

  useEffect(() => {
    if (mermaidRef.current) {
      mermaid.render(uniqueId, chart).then(({ svg }) => {
        mermaidRef.current.innerHTML = svg;
      });
    }
  }, [chart, uniqueId]);

  return (
    <div className={`mermaid-wrapper ${className}`}>
      <div ref={mermaidRef} className="mermaid" />
    </div>
  );
} 