import React, { useEffect, useRef } from 'react';

export default function ClientMermaid({ chart, className = '' }) {
  const mermaidRef = useRef(null);
  const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 11)}`;

  useEffect(() => {
    // Dynamically import mermaid only on the client side
    import('mermaid').then((mermaid) => {
      // Initialize mermaid with default configuration
      mermaid.default.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'system-ui, sans-serif',
      });

      if (mermaidRef.current) {
        try {
          mermaid.default.render(uniqueId, chart).then(({ svg }) => {
            mermaidRef.current.innerHTML = svg;
          });
        } catch (error) {
          console.error('Failed to render mermaid diagram:', error);
          mermaidRef.current.innerHTML = `<pre>Error rendering diagram: ${error.message}</pre>`;
        }
      }
    });
  }, [chart, uniqueId]);

  return (
    <div className={`mermaid-wrapper ${className}`} style={{ margin: '2rem 0', overflowX: 'auto' }}>
      <div ref={mermaidRef} className="mermaid" />
    </div>
  );
} 