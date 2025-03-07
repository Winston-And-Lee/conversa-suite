// React
declare module 'react';
declare module 'react-dom';

// Refine Libraries
declare module '@refinedev/antd';
declare module '@refinedev/core';
declare module '@refinedev/devtools';
declare module '@refinedev/kbar';
declare module '@refinedev/react-router-v6';

// Router and i18n
declare module 'react-router-dom';
declare module 'react-i18next';

// Azure MSAL
declare module '@azure/msal-browser';
declare module '@azure/msal-react';

// Style declarations
declare module '*.scss' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

// Image declarations
declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
} 