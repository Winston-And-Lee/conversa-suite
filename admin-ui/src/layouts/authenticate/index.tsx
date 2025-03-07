import { USER_ICON_TEMP } from '@/api-requests';
import { Player } from '@lottiefiles/react-lottie-player';
import { Flex, Typography } from 'antd';
import { ReactNode } from 'react';
import { BlueBg, Container, ContentContainer, MainFormBox, TemplateIcon, WhiteBg } from './layout';

interface AuthenticateTemplateProps {
  children: ReactNode;
  decoratedImage: string;
}

export const AuthenticateTemplate = ({ children, decoratedImage }: AuthenticateTemplateProps) => {
  const themeTemp = JSON.parse(localStorage.getItem(USER_ICON_TEMP) || '{}');
  let link = document.querySelector("link[rel~='icon']");
  if (themeTemp && link) {
    let elementFavicon: HTMLLinkElement | null = document.querySelector('link[rel="icon"]');
    if (!elementFavicon) return;
    elementFavicon.href = themeTemp.logo_favicon ?? themeTemp.logo;
  }

  const iconUrl = themeTemp?.logo ?? import.meta.env.VITE_APP_ICON_URL;

  return (
    <Container>
      <BlueBg />
      <WhiteBg />
      <TemplateIcon src={iconUrl} />
      <ContentContainer>
        <Flex gap={16} vertical={true} flex={1} style={{ paddingLeft: '5%', maxWidth: 500 }}>
          <Typography.Title level={2} style={{ color: 'var(--neutral_13)' }}>
            Empowering Insight-Driven Decisions
          </Typography.Title>
          <Typography.Title level={5} style={{ color: 'var(--neutral_13)' }}>
            A comprehensive solution for business intelligence, streamlined workflows, and enhanced organizational
            management—all in one package.
          </Typography.Title>
        </Flex>
        <MainFormBox>{children}</MainFormBox>
        <Flex gap={16} vertical={true} flex={1} style={{ maxWidth: 500 }}>
          {/* <CustomSvg src={decoratedImage} /> */}
          <Player
            autoplay={true}
            loop={true}
            controls={false}
            src={decoratedImage}
            style={{ height: '400px', width: '400px' }}
          ></Player>
        </Flex>
      </ContentContainer>
    </Container>
  );
};
