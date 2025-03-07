import { USER_KEY, USER_MENU_SETTING_KEY, USER_PERMISSION, USER_WORKSPACES_KEY } from '@/api-requests';
// import { getSetActiveWorkspace, getUserPermission } from '@/api-requests/auth';
import { ColorMode, COLORS } from '@/constant';
import { THEME_STORAGE_KEY, useThemeContext } from '@/contexts/color-mode';
import { ICustomThemedLayoutProps, IUser } from '@/interfaces';
import { getThemeColorNameByEnum } from '@/utils/converter';
import { PartitionOutlined } from '@ant-design/icons';
import { useThemedLayoutContext } from '@refinedev/antd';
import {
  CanAccess,
  ITreeMenu,
  useGetIdentity,
  useGetLocale,
  useIsExistAuthentication,
  useLogout,
  useMenu,
  useSetLocale,
  useTitle,
  useTranslate,
  useWarnAboutChange
} from '@refinedev/core';
import { Layout as AntdLayout, Avatar, Button, Image, Menu, MenuProps, theme } from 'antd';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import * as SolarIconSet from 'solar-icon-set';
import './style.scss';

const { useToken } = theme;

export const CustomSider: ICustomThemedLayoutProps['Sider'] = ({ setIsOpenSubMenu, Title: TitleFromProps }) => {
  const { token } = useToken();
  const { siderCollapsed } = useThemedLayoutContext();
  const { setMode, mode } = useThemeContext();

  const navigate = useNavigate();

  const isExistAuthentication = useIsExistAuthentication();
  const { warnWhen, setWarnWhen } = useWarnAboutChange();
  const TitleFromContext = useTitle();
  const { mutate: mutateLogout } = useLogout();
  const { menuItems, selectedKey, defaultOpenKeys } = useMenu();
  const [selectedMenu, setSelectedMenu] = useState<string>('');

  const translate = useTranslate();
  const locale = useGetLocale();
  const changeLanguage = useSetLocale();
  const currentLocale = locale();

  // Custom Menu
  const userProfile = JSON.parse(localStorage.getItem(USER_KEY) || '{}');
  const menu_settings = JSON.parse(localStorage.getItem(USER_MENU_SETTING_KEY) || '[]');
  const appTheme = localStorage.getItem(THEME_STORAGE_KEY ?? 'default') as ColorMode;

  const [colorTheme, setTheme] = useState({ colors: COLORS[appTheme as keyof typeof COLORS] });

  const themeApp = getThemeColorNameByEnum(userProfile?.workspace?.color);
  if (themeApp && themeApp != mode) {
    setMode(themeApp);
  }

  // Set Icon Favicon
  let link = document.querySelector("link[rel~='icon']");
  if (link) {
    let elementFavicon: HTMLLinkElement | null = document.querySelector('link[rel="icon"]');
    if (!elementFavicon) return;
    // elementFavicon.href = userProfile.workspace.logo_favicon ?? userProfile.workspace.logo;
  }

  menu_settings.map((data: any) => {
    const meta = data.meta;

    const IconComponent = SolarIconSet[meta.icon as keyof typeof SolarIconSet];

    data.icon = IconComponent ? <IconComponent iconStyle='Outline' {...(data.children && { size: 24 })} /> : null;
    data.meta.icon = <SolarIconSet.BillList size={24} iconStyle='Outline' />;

    if (!data.children) {
      return data;
    }

    data.children.map((child: any) => {
      const childMeta = child.meta;

      const ChildIconComponent = SolarIconSet[childMeta.icon as keyof typeof SolarIconSet];

      child.icon = ChildIconComponent ? <ChildIconComponent iconStyle='Outline' /> : null;
      child.meta.icon = child.icon;
      return child;
    });

    return data;
  });

  const fullMenuItems = [...menu_settings, ...menuItems];
  // ----------------

  useEffect(() => {
    if (setIsOpenSubMenu) {
      if (selectedMenu !== '' && selectedMenu !== 'reports') {
        setIsOpenSubMenu(true);
      } else {
        setIsOpenSubMenu(false);
      }
    }
  }, [selectedMenu]);

  const { data: user, refetch: refetchUser } = useGetIdentity<IUser>();

  // const RenderToTitle = TitleFromProps ?? TitleFromContext ?? ThemedTitleV2;

  const renderTreeView = (tree: ITreeMenu[], isParent: boolean) => {
    return tree.map((item: ITreeMenu) => {
      const { name, children, meta, key, list } = item;

      const icon = meta?.icon;
      const label = meta?.label ?? name;
      const route = typeof list === 'string' ? list : typeof list !== 'function' ? list?.path : key;

      const handleSelectedMenu = (name: string) => {
        if (isParent) setSelectedMenu(name);
      };

      let nameShow = translate(`sidebar.${name}`);
      let labelShow = translate(`sidebar.${label}`);

      if (meta?.nameShowTH && currentLocale == 'th') {
        nameShow = meta?.nameShowTH;
        labelShow = meta?.nameShowTH;
      } else if (meta?.nameShowEN) {
        nameShow = meta?.nameShowEN;
        labelShow = meta?.nameShowEN;
      }

      return (
        <CanAccess key={key} resource={name.toLowerCase()} action='list' params={{ resource: item }}>
          <Menu.Item
            className={isParent ? 'menu-parent' : 'sub-menu'}
            key={key}
            icon={icon ?? <SolarIconSet.BillList color='#1C274C' size={18} iconStyle='Outline' />}
            onClick={() => handleSelectedMenu(name)}
          >
            {route ? <Link to={route || '/'}>{nameShow}</Link> : labelShow}
          </Menu.Item>
        </CanAccess>
      );
    });
  };

  const profile = isExistAuthentication && (
    <Menu.Item
      className='menu-parent'
      key='/Profile'
      onClick={() => setSelectedMenu('Profile')}
      icon={<SolarIconSet.UserCircle color='#1C274C' size={24} iconStyle='Outline' />}
    >
      {translate('buttons.profile', 'Profile')}
    </Menu.Item>
  );

  const handleLogout = () => {
    if (warnWhen) {
      const confirm = window.confirm(
        translate('warnWhenUnsavedChanges', 'Are you sure you want to leave? You have unsaved changes.')
      );

      if (confirm) {
        setWarnWhen(false);
        mutateLogout();
      }
    } else {
      mutateLogout();
    }
  };

  const logout = isExistAuthentication && (
    <Menu.Item
      className='menu-parent'
      key='logout'
      onClick={handleLogout}
      icon={<SolarIconSet.Logout2 color='#1C274C' size={24} iconStyle='Outline' />}
    >
      {translate('buttons.logout', 'Logout')}
    </Menu.Item>
  );

  const items = renderTreeView(menuItems, true);
  const item_settings = renderTreeView(menu_settings, true);
  // const items = renderTreeView(fullMenuItems, true);

  // const renderSiderTop = () => {
  //   return <>{items}</>;
  // };

  const renderSiderBottom = () => {
    return (
      <>
        {profile}
        {logout}
      </>
    );
  };

  // const filteredMenuItems = menuItems.filter(menu => menu.name === selectedMenu);
  const filteredMenuItems = fullMenuItems.filter(menu => menu.name === selectedMenu);

  const filteredItems = renderTreeView(
    selectedMenu && selectedMenu !== 'Profile' ? filteredMenuItems[0]?.children : [],
    false
  );

  const userWorkspaces = localStorage.getItem(USER_WORKSPACES_KEY);
  let workspaceMenuItems: MenuProps['items'] = [];
  if (userWorkspaces) {
    try {
      const userWorkspacesObject = JSON.parse(userWorkspaces);

      userWorkspacesObject.forEach((item: any) => {
        workspaceMenuItems?.push({
          key: item.workspace.slug,
          onClick: async () => {
            const data = await getSetActiveWorkspace(item.workspace.slug);
            const permission = await getUserPermission();
            const user = await refetchUser();
            if (user) {
              const themeApp = getThemeColorNameByEnum(user?.data?.workspace?.color);
              setMode(themeApp);
            }

            localStorage.setItem(USER_PERMISSION, JSON.stringify(permission));
            localStorage.setItem(USER_KEY, JSON.stringify(data));
            window.location.reload();
          },
          icon: <PartitionOutlined />,
          label: item.workspace.name
        });
      });
    } catch (error) {}
  }

  const renderSubMenu = () => {
    const renderWorkspaceSubmenu = () => {
      return workspaceMenuItems?.map((workspace: any) => {
        return (
          <Menu.Item key={workspace.key} onClick={workspace.onClick} icon={workspace.icon}>
            {workspace.label}
          </Menu.Item>
        );
      });
    };

    if (selectedMenu === 'Profile') {
      return (
        <>
          <Menu.SubMenu title='Language'>
            <Menu.Item
              key={'en'}
              icon={<Avatar size={16} src='/images/flags/en.svg' />}
              onClick={() => changeLanguage('en')}
            >
              English
            </Menu.Item>
            <Menu.Item
              key={'th'}
              icon={<Avatar size={16} src='/images/flags/th.svg' />}
              onClick={() => changeLanguage('th')}
            >
              Thai
            </Menu.Item>
          </Menu.SubMenu>
          {user?.workspace && <Menu.SubMenu title='Workspace'>{renderWorkspaceSubmenu()}</Menu.SubMenu>}
        </>
      );
    }
    return (
      <>
        <div className='sub-menu-title'>
          <SolarIconSet.HamburgerMenu color='#1C274C' size={24} iconStyle='Outline' />
          {selectedMenu}
        </div>
        {filteredItems}
      </>
    );
  };

  const renderSubmenuSider = () => {
    return (
      <AntdLayout.Sider
        onCollapse={() => setSelectedMenu('')}
        breakpoint='lg'
        width={'224px'}
        style={{
          position: 'fixed',
          left: 56,
          top: 0,
          height: '100vh',
          zIndex: '999',
          backgroundColor: token.colorBgContainer,
          borderRight: `1px solid #E4E7EC`
        }}
      >
        {selectedMenu !== '' && (
          <Button
            style={{
              position: 'absolute',
              right: -16,
              top: 16,
              borderRadius: '50%',
              backgroundColor: token.colorBgElevated,
              width: '30px',
              height: '30px'
            }}
            onClick={() => setSelectedMenu('')}
            icon={<SolarIconSet.AltArrowLeft color='#344054' size={18} iconStyle='Outline' />}
          ></Button>
        )}
        <Menu
          className='sub-navbar-menu'
          defaultOpenKeys={defaultOpenKeys}
          selectedKeys={[selectedKey, user?.workspace?.slug, currentLocale]}
          mode='vertical'
          style={{
            marginTop: '8px',
            border: 'none'
          }}
        >
          {renderSubMenu()}
        </Menu>
      </AntdLayout.Sider>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'row' }}>
      <AntdLayout.Sider
        collapsed={true}
        breakpoint='lg'
        collapsedWidth={'56px'}
        style={{
          position: 'fixed',
          top: 0,
          height: '100vh',
          zIndex: 999,
          backgroundColor: colorTheme.colors.primary_02,
          borderRight: '1px solid #E4E7EC'
        }}
      >
        <div
          style={{
            width: '56px',
            padding: '8px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '48px',
            backgroundColor: colorTheme.colors.primary_02,
            fontSize: '14px',
            borderRight: '1px solid #E4E7EC'
          }}
        >
          {/* <RenderToTitle collapsed={siderCollapsed} /> */}
          <a onClick={() => navigate('/')}>
            <Image
              width={'100%'}
              // src={userProfile.workspace.logo}
              fallback='/assets/images/app-logo/logo.png'
              preview={false}
            />
          </a>
        </div>
        <div className='main-navbar-menu-container'>
          <Menu
            defaultOpenKeys={defaultOpenKeys}
            selectedKeys={[`/${selectedMenu}`]}
            style={{
              border: 'none',
              backgroundColor: colorTheme.colors.primary_02
            }}
          >
            {/* {renderSiderTop()} */}
            {item_settings}
            {items}
          </Menu>
          <Menu
            defaultOpenKeys={defaultOpenKeys}
            selectedKeys={[`/${selectedMenu}`]}
            style={{
              border: 'none',
              backgroundColor: colorTheme.colors.primary_02
            }}
          >
            {renderSiderBottom()}
          </Menu>
        </div>
      </AntdLayout.Sider>
      {(filteredItems.length > 0 || selectedMenu === 'Profile') && renderSubmenuSider()}
    </div>
  );
};
