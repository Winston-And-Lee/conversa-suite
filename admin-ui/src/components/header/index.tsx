import { DownOutlined } from '@ant-design/icons';
import type { RefineThemedLayoutV2HeaderProps } from '@refinedev/antd';
import { useGetIdentity, useGetLocale, useLogout, useSetLocale } from '@refinedev/core';
import { Layout as AntdLayout, Avatar, Button, Dropdown, MenuProps, Space, theme, Typography } from 'antd';

import { IUser } from '@/interfaces';

import { LogoutOutlined } from '@ant-design/icons';

import React from 'react';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;
const { useToken } = theme;

export const Header: React.FC<RefineThemedLayoutV2HeaderProps> = ({ sticky }) => {
  const { token } = useToken();
  const { i18n } = useTranslation();
  const locale = useGetLocale();
  const changeLanguage = useSetLocale();
  const { data: user } = useGetIdentity<IUser>();
  const { mutate: logout } = useLogout();

  let workspaceMenuItems: MenuProps['items'] = [];

  const currentLocale = locale();

  const menuLangItems: MenuProps['items'] = [...(i18n.languages || [])].sort().map((lang: string) => ({
    key: lang,
    onClick: () => changeLanguage(lang),
    icon: (
      <span style={{ marginRight: 8 }}>
        <Avatar size={16} src={`/images/flags/${lang}.svg`} />
      </span>
    ),
    label: lang === 'th' ? 'ภาษาไทย' : 'English'
  }));

  const menuAccountItems: MenuProps['items'] = [
    {
      key: 'logout',
      onClick: () => logout(),
      icon: (
        <span style={{ marginRight: 8 }}>
          <LogoutOutlined />
        </span>
      ),
      label: 'Logout'
    }
  ];

  const menuWorkspaceItems: MenuProps['items'] = [
    {
      key: 'workspace',
      label: <Text strong>{'Switch Workspace'}</Text>
    },
    ...workspaceMenuItems
  ];

  const headerStyles: React.CSSProperties = {
    backgroundColor: token.colorBgElevated,
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: '0px 24px',
    height: '64px'
  };

  if (sticky) {
    headerStyles.position = 'sticky';
    headerStyles.top = 0;
    headerStyles.zIndex = 1;
  }

  return (
    <AntdLayout.Header style={headerStyles}>
      <Space>
        <Dropdown
          menu={{
            items: menuLangItems,
            selectedKeys: currentLocale ? [currentLocale] : []
          }}
        >
          <Button type='text'>
            <Space>
              <Avatar size={16} src={`/images/flags/${currentLocale}.svg`} />
              {currentLocale === 'th' ? 'ภาษาไทย' : 'English'}
              <DownOutlined />
            </Space>
          </Button>
        </Dropdown>
        {/* TODO: Change to theme switcher ? */}
        {/* <Switch 
          checkedChildren='🌛'
          unCheckedChildren='🔆'
          onChange={() => setMode(mode === 'light' ? 'dark' : 'light')}
          defaultChecked={mode === 'dark'}
        /> */}
        <Dropdown
          menu={{
            items: menuAccountItems
            // selectedKeys: currentLocale ? [currentLocale] : [],
          }}
        >
          <Button type='text' style={{ height: 42 }}>
            <Space style={{ marginLeft: '8px' }} size='middle'>
              {user?.name && <Text strong>{user.name}</Text>}
              {user?.avatar && <Avatar src={user?.avatar} alt={user?.name} />}
            </Space>
          </Button>
        </Dropdown>
      </Space>
    </AntdLayout.Header>
  );
};
