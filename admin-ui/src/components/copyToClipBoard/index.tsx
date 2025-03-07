import { Tooltip, message } from 'antd';
import React, { useState } from 'react';
import * as SolarIconSet from 'solar-icon-set';
import { useTheme } from 'styled-components';

interface CopyToClipboardProps {
  value: string;
  children: React.ReactNode;
}

export const CopyToClipBoard: React.FC<CopyToClipboardProps> = ({ value, children }) => {
  const [hover, setHover] = useState(false);
  const copyToClipboard = () => {
    navigator.clipboard.writeText(value);
    message.success('Copied to clipboard');
  };

  const theme = useTheme();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
        gap: 8
      }}
    >
      {children}
      <Tooltip title='Copy to Clipboard'>
        <SolarIconSet.Copy
          onClick={copyToClipboard}
          onMouseEnter={() => setHover(true)}
          onMouseLeave={() => setHover(false)}
          color={hover ? theme.colors.primary_03 : 'var(--neutral_08'}
          size={14}
          iconStyle='Outline'
        />
      </Tooltip>
    </div>
  );
};
