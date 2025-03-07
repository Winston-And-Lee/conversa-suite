import { PageHeader } from '@refinedev/antd';
import { useBack, useNavigation, useParsed, useShow } from '@refinedev/core';
import { embedDashboard } from '@superset-ui/embedded-sdk';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { FullscreenExitOutlined, FullscreenOutlined } from '@ant-design/icons';

import { Button, Card, Space } from 'antd';

import { getGuestTokenReport } from '@/api-requests/report';
import { ReportLayout } from './reportLayout';

import { ROUTES } from '@/constant';
// import './style.css';

interface IShowReportProps {
  isFullScreen?: boolean;
}

export const ReportShow: React.FC<IShowReportProps> = ({ isFullScreen }) => {
  const { t } = useTranslation('reports');
  const title = t('show.dashboard');
  const resource = 'reports';
  const back = useBack();
  const params = useParsed();
  const { queryResult } = useShow({ resource: resource, id: params.id });
  const { data, isLoading } = queryResult;
  const record = data?.data;
  const { goBack, list: legacyGoList } = useNavigation();

  const [screenSize, setDimensionState] = useState({
    dynamicWidth: window.innerWidth,
    dynamicHeight: window.innerHeight
  });
  const setDimension = () => {
    setDimensionState({
      dynamicWidth: window.innerWidth,
      dynamicHeight: window.innerHeight
    });
  };

  useEffect(() => {
    window.addEventListener('resize', setDimension);

    return () => {
      window.removeEventListener('resize', setDimension);
    };
  }, [screenSize]);

  useEffect(() => {
    const getTokenAndEmbed = async () => {
      const fetchedToken = await getGuestTokenReport;

      const mountElement = document.getElementById('report-container');
      if (mountElement && fetchedToken && record) {
        embedDashboard({
          id: record?.report_id, // given by the Superset embedding UI
          supersetDomain: record?.report_service?.url,
          mountPoint: mountElement,
          fetchGuestToken: () => fetchedToken(record?.report_id),
          dashboardUiConfig: {
            hideTitle: true,
            filters: {
              expanded: true
            }
          }
        });
      }
    };
    // if(!isLoading){
    getTokenAndEmbed();
    // }
  }, [isLoading, record]);

  const headerButtons = (
    <>
      {isFullScreen ? (
        <Button icon={<FullscreenExitOutlined />} href={`/${ROUTES.REPORTS}/${record?.id}/`}>
          {t('show.exitFullScreen')}
        </Button>
      ) : (
        <Button icon={<FullscreenOutlined />} href={`/${ROUTES.REPORTS}/full/${record?.id}/`}>
          {t('show.fullScreen')}
        </Button>
      )}
    </>
  );

  if (isFullScreen) {
    return (
      <PageHeader
        ghost={false}
        onBack={back}
        title={record?.name ?? title}
        // extra={
        //     <Space
        //         key="extra-buttons"
        //         wrap
        //     >
        //         {headerButtons}
        //     </Space>
        // }
        style={{ paddingTop: 12 }}
        // childrenContentStyle={{background: "#aaa"}}
      >
        <div
          id='report-container'
          style={{ width: '100%', height: screenSize.dynamicHeight - 70, borderTop: '1px solid #f5f5f5' }}
        ></div>
      </PageHeader>
    );
  }

  return (
    <ReportLayout>
      <PageHeader
        ghost={false}
        onBack={() => {
          legacyGoList(resource);
        }}
        title={record?.name ?? title}
        extra={
          <Space key='extra-buttons' wrap>
            {headerButtons}
          </Space>
        }
      >
        <Card bodyStyle={{ padding: 5 }}>
          <div id='report-container' style={{ width: '100%', height: screenSize.dynamicHeight - 106 }}></div>
        </Card>
      </PageHeader>
    </ReportLayout>
  );
};
