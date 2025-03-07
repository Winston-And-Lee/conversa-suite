import { Player } from '@lottiefiles/react-lottie-player';
import { Typography } from 'antd';
import React from 'react';
import { useTranslation } from 'react-i18next';

const { Title } = Typography;

export const FallbackPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <>
      <Player
        autoplay={true}
        loop={true}
        controls={false}
        src={'/assets/lottiefiles/loading.json'}
        style={{ height: '400px', width: '400px' }}
      ></Player>
      <Title style={{ textAlign: 'center' }} level={3}>
        {t('fallback.loading')}
      </Title>
    </>
  );
};
