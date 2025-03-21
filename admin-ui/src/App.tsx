import { useEffect } from 'react';

import { ErrorComponent, notificationProvider, ThemedTitleV2 } from '@refinedev/antd';
import '@refinedev/antd/dist/reset.css';
import { Authenticated, CanAccess, Refine } from '@refinedev/core';
import { DevtoolsPanel, DevtoolsProvider } from '@refinedev/devtools';
import { RefineKbarProvider } from '@refinedev/kbar';

import routerBindings, {
  CatchAllNavigate,
  DocumentTitleHandler,
  UnsavedChangesNotifier
} from '@refinedev/react-router-v6';

import { useTranslation } from 'react-i18next';
import { BrowserRouter, Outlet, Route, Routes, Navigate } from 'react-router-dom';

import { resources } from './contexts/resources';
import { authProvider } from './providers/authProvider';
import { dataProvider } from './providers/data/dataProvider';
import { accessControlProvider } from './providers/permissionProvider';

import { HomePage } from './pages/home';
import { LoginPage } from './pages/login';
import { SignupPage, VerifyPage } from './pages/register';
import { AssistantUIPage } from './pages/assistant-ui/page';
import { DataIngestionList } from './pages/data-ingestion/list';
import { DataIngestionShow } from './pages/data-ingestion/show';
import { DataIngestionCreate } from './pages/data-ingestion/create';
import { FileList } from './pages/super-admin/files';

import { Avatar } from 'antd';
import 'reactflow/dist/style.css';
import { CustomSider } from './components/customSider';
import { CustomThemedLayout } from './layouts/customTheme';

import { ReportCreate, ReportEdit, ReportList, ReportShow } from './pages/reports/report';

import {
  ReportServiceCreate,
  ReportServiceEdit,
  ReportServiceList,
  ReportServiceShow
} from './pages/super-admin/report-services';

import { UserList, UserShow } from './pages/super-admin/users';

import { ROUTES } from '@/constant';
import { KhaojaiThemeProvider } from './contexts/color-mode';

import './style.scss';

import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { MSAL_CONFIG } from './constant/authConfig';

const MSAL_INSTANCE = new PublicClientApplication(MSAL_CONFIG);
const appName = import.meta.env.VITE_APP_NAME;

function App() {
  const { t, i18n } = useTranslation();

  useEffect(() => {
    const storedLanguage = localStorage.getItem('i18nextLng');
    if (storedLanguage && i18n.language !== storedLanguage) {
      i18n.changeLanguage(storedLanguage);
    }
  }, [i18n]);

  const defaultUrl = import.meta.env.VITE_APP_API_ENDPOINT;
  const iconUrl = import.meta.env.VITE_APP_ICON_URL
    ? import.meta.env.VITE_APP_ICON_URL
    : '/assets/images/app-logo/kaben.png';

  const i18nProvider = {
    translate: (key: string, params: object) => t(key, params),
    changeLocale: (lang: string) => {
      localStorage.setItem('i18nextLng', lang);
      return i18n.changeLanguage(lang);
    },
    getLocale: () => i18n.language
  };

  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <KhaojaiThemeProvider>
          <DevtoolsProvider>
          <MsalProvider instance={MSAL_INSTANCE}>
            <Refine
              dataProvider={{
                default: dataProvider(`${defaultUrl}/api`),
                custom: dataProvider(`${defaultUrl}/api`)
              }}
              notificationProvider={notificationProvider}
              authProvider={authProvider}
              i18nProvider={i18nProvider}
              routerProvider={routerBindings}
              accessControlProvider={accessControlProvider}
              resources={resources}
            >
              <Routes>
                <Route
                  element={
                    <Authenticated
                      key={'authenticated'}
                      fallback={<CatchAllNavigate to={`/${ROUTES.WELCOME_LOGIN_REGISTER}`} />}
                    >
                      <CustomThemedLayout
                        initialSiderCollapsed={true}
                        Header={() => null}
                        Sider={CustomSider}
                        Title={({ collapsed }: { collapsed: boolean }) => (
                          <ThemedTitleV2
                            collapsed={collapsed}
                            text={appName ? appName : 'Conversa Suite'}
                            icon={<Avatar src={iconUrl} />}
                            wrapperStyles={{
                              height: '32px',
                              width: '32px',
                              paddingTop: '-12px'
                            }}
                          />
                        )}
                      >
                        <CanAccess fallback={<div>Unauthorized!</div>}>
                          <Outlet />
                        </CanAccess>
                      </CustomThemedLayout>
                    </Authenticated>
                  }
                >
                  <Route path={ROUTES.REPORTS}>
                    <Route path='create' element={<ReportCreate />} />
                    <Route path='edit/:id' element={<ReportEdit />} />
                    <Route index={true} element={<ReportList />} />
                    <Route path=':id' element={<ReportShow isFullScreen={true} />} />
                  </Route>

                  <Route path={ROUTES.ADMIN_USERS}>
                    <Route index={true} element={<UserList />} />
                    <Route path=':id' element={<UserShow />} />
                  </Route>

                  <Route path={ROUTES.ADMIN_FILES}>
                    <Route index={true} element={<FileList />} />
                  </Route>

                  <Route path={ROUTES.ADMIN_REPORT_SERVICE}>
                    <Route index={true} element={<ReportServiceList />} />
                    <Route path=':id' element={<ReportServiceShow />} />
                    <Route path='create' element={<ReportServiceCreate />} />
                    <Route path='edit/:id' element={<ReportServiceEdit />} />
                  </Route>

                  <Route path={ROUTES.ASSISTANT_UI}>
                    <Route index={true} element={<AssistantUIPage />} />
                  </Route>

                  <Route path={ROUTES.DATA_INGESTION}>
                    <Route index={true} element={<DataIngestionList />} />
                    <Route path=':id' element={<DataIngestionShow />} />
                    <Route path='create' element={<DataIngestionCreate />} />
                  </Route>

                  <Route path='' element={<HomePage />} />

                  <Route path='*' element={<ErrorComponent />} />
                </Route>
                <Route
                  element={
                    <Authenticated fallback={<Outlet />} key='authenticated'>
                       <Navigate to="/" />
                    </Authenticated>
                  }
                >
                  <Route path={ROUTES.WELCOME_LOGIN_REGISTER} element={<LoginPage />} />
                  <Route path={ROUTES.REGISTER} element={<SignupPage />} />
                  <Route path={ROUTES.VERIFY_ACCOUNT} element={<VerifyPage />} />
                </Route>
              </Routes>

              <UnsavedChangesNotifier />
              <DocumentTitleHandler />
            </Refine>
            </MsalProvider>
            <DevtoolsPanel />
          </DevtoolsProvider>
        </KhaojaiThemeProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

export default App;
