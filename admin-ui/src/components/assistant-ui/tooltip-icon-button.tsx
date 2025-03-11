import React from 'react';
import { Button, Tooltip } from 'antd';
import { ButtonProps } from 'antd/lib/button';

export interface TooltipIconButtonProps extends ButtonProps {
  tooltip: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
  style?: any;
}

export const TooltipIconButton = React.forwardRef(
  (props: TooltipIconButtonProps, ref: any) => {
    const { children, tooltip, placement = 'bottom', className, style, ...rest } = props;
    
    return (
      <Tooltip title={tooltip} placement={placement}>
        <Button
          type="text"
          size="small"
          {...rest}
          className={className}
          style={{ 
            width: '24px', 
            height: '24px', 
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            ...style 
          }}
          ref={ref}
        >
          {children}
          <span className="sr-only">{tooltip}</span>
        </Button>
      </Tooltip>
    );
  }
);

TooltipIconButton.displayName = 'TooltipIconButton'; 