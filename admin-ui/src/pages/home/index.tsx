import { CustomLayout } from '@/components/customLayout';
// import { Player } from '@lottiefiles/react-lottie-player';
import { useGetIdentity } from '@refinedev/core';
import { Card, Col, Input, Row, Typography } from 'antd';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { resources } from '@/contexts/resources';
import { IUser } from '@/interfaces';
import { SearchOutlined } from '@ant-design/icons';
import { useFilteredResources } from './hooks';

const { Meta } = Card;
const { Title } = Typography;

export const HomePage: React.FC = () => {
  const { data: user } = useGetIdentity<IUser>();
  const { t } = useTranslation('home');
  const [filter, setFilter] = useState('');
  const filteredResources = useFilteredResources(resources, filter);
  const resourceMenu = filteredResources;

  // const permission = await accessControlProvider.can({ resource: resource.name, action: 'list' });

  return (
    <CustomLayout>
      {/* <Player
        autoplay={true}
        loop={true}
        controls={false}
        src={'/assets/lottiefiles/welcome.json'}
        style={{ height: '200px', width: '200px' }}
      ></Player> */}

      {/* <Title style={{ textAlign: 'center', marginBottom: '6px', marginTop: '26px' }} level={2} >
        {user?.workspace.name}
      </Title> */}
      <Title style={{ textAlign: 'center', marginBottom: '16px', marginTop: '16px' }} level={3} >
        {t('label.welcome')}
        {user?.name}
      </Title>
      <Input
        size="large"
        prefix={<SearchOutlined />}
        placeholder="Filter resources"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        style={{ marginBottom: '16px' }}
      />
      <Row gutter={[16, 16]}>
        {resourceMenu.map((resource) => {
          return (
            <Col key={resource.name} span={6}>
              <Card hoverable>
                <Meta
                  avatar={<div style={{ fontSize: '24px' }}>{resource.meta.icon}</div>}
                  title={<a href={resource.list}>{resource.meta.label}</a>}
                  description={resource.meta.parent}
                />
              </Card>
            </Col>
          )
        } ) }
      </Row>
    </CustomLayout>
  );
};
