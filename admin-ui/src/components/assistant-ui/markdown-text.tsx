import React, { memo } from 'react';
import { Typography } from 'antd';

const { Text, Paragraph } = Typography;

interface MarkdownTextProps {
  children?: any;
  fontSize?: number;
  style?: any;
}

// Simple implementation to render markdown-like content
export const MarkdownText = memo(({ children, fontSize = 16, style = {} }: MarkdownTextProps) => {
  console.log('Rendering MarkdownText with children:', children);
  
  // If children is null or undefined, return a placeholder
  if (children === null || children === undefined) {
    return <Text type="secondary" style={{ fontSize, ...style }}>No content available</Text>;
  }
  
  // If children is a string, render it with Typography
  if (typeof children === 'string') {
    return (
      <Paragraph style={{ 
        margin: 0,
        padding: 0,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        fontSize,
        lineHeight: '1.5',
        ...style
      }}>
        {children}
      </Paragraph>
    );
  }
  
  // If children is an object, try to extract content
  if (typeof children === 'object') {
    // Try to extract content from common message formats
    if (children.content) {
      return (
        <Paragraph style={{ 
          margin: 0,
          padding: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          fontSize,
          lineHeight: '1.5',
          ...style
        }}>
          {children.content}
        </Paragraph>
      );
    }
    
    // If it's an array, join the contents
    if (Array.isArray(children)) {
      const content = children.map(item => 
        typeof item === 'string' ? item : 
        (item && item.content) ? item.content : 
        JSON.stringify(item)
      ).join('\n');
      
      return (
        <Paragraph style={{ 
          margin: 0,
          padding: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          fontSize,
          lineHeight: '1.5',
          ...style
        }}>
          {content}
        </Paragraph>
      );
    }
  }
  
  // If all else fails, try to stringify the content
  try {
    const content = JSON.stringify(children, null, 2);
    return (
      <Paragraph style={{ 
        margin: 0,
        padding: 0,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        fontFamily: 'monospace',
        fontSize,
        lineHeight: '1.5',
        ...style
      }}>
        {content}
      </Paragraph>
    );
  } catch (error) {
    console.error('Error stringifying content', error);
    return <Text type="danger" style={{ fontSize, padding: 0, margin: 0, ...style }}>Error rendering content</Text>;
  }
}); 