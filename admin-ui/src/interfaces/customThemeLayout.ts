import { TitleProps } from '@refinedev/core';
import { ReactNode } from 'react';

export interface ICustomThemedLayoutProps {
  initialSiderCollapsed?: boolean;
  Sider?: React.FC<{
    Title?: React.FC<TitleProps>;
    setIsOpenSubMenu?: any;
    render?: (props: {
      items: JSX.Element[];
      logout: React.ReactNode;
      dashboard: React.ReactNode;
      collapsed: boolean;
    }) => React.ReactNode;
    meta?: Record<string, unknown>;
  }>;
  Header?: React.FC;
  Title?: React.FC<TitleProps>;
  Footer?: React.FC;
  OffLayoutArea?: React.FC;
  dashboard?: boolean;
  children?: ReactNode;
  subSider?: boolean;
}
