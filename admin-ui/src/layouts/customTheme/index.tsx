import { Layout as AntdLayout, Grid } from 'antd';
import React, { useState } from 'react';

import { ICustomThemedLayoutProps } from '@/interfaces';
import {
  ThemedHeaderV2 as DefaultHeader,
  ThemedSiderV2 as DefaultSider,
  ThemedLayoutContextProvider
} from '@refinedev/antd';
import styled from 'styled-components';

export const CustomThemedLayout: React.FC<ICustomThemedLayoutProps> = ({
  children,
  Header,
  Sider,
  Title,
  Footer,
  OffLayoutArea,
  initialSiderCollapsed
}) => {
  const breakpoint = Grid.useBreakpoint();
  const SiderToRender = Sider ?? DefaultSider;
  const HeaderToRender = Header ?? DefaultHeader;
  const isSmall = typeof breakpoint.sm === 'undefined' ? true : breakpoint.sm;
  const hasSider = !!SiderToRender({ Title });

  const [isOpenSubMenu, setIsOpenSubMenu] = useState<boolean>(false);

  return (
    <ThemedLayoutContextProvider initialSiderCollapsed={initialSiderCollapsed}>
      <AntdLayout style={{ minHeight: '100vh' }} hasSider={hasSider}>
        <SiderToRender Title={Title} setIsOpenSubMenu={setIsOpenSubMenu} />
        <CustomAntdLayout className='main-layout'>
          <HeaderToRender />
          <AntdLayout.Content>
            <div
              style={{
                minHeight: 360,
                height: '100vh',
                marginLeft: isOpenSubMenu ? 280 : 56
              }}
            >
              {children}
            </div>
            {OffLayoutArea && <OffLayoutArea />}
          </AntdLayout.Content>
          {Footer && <Footer />}
        </CustomAntdLayout>
      </AntdLayout>
    </ThemedLayoutContextProvider>
  );
};

const CustomAntdLayout = styled(AntdLayout)`
  background-color: var(--neutral_13);
`;
