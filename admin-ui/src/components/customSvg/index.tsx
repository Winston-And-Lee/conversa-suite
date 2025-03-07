'use client';

import { ReactSVG } from 'react-svg';
import { styled } from 'styled-components';

type StyledSVGProps = {
  isFill?: boolean;
  isStroke?: boolean;
  customColor?: string;
};

const StyledSvg = styled(ReactSVG)<StyledSVGProps>`
  display: flex;
  * {
    width: 100%;
    height: 100%;
  }
  svg {
    stroke: ${({ isStroke, customColor }) => isStroke && (customColor ?? 'currentColor')};
    fill: ${({ isFill, customColor }) => isFill && (customColor ?? 'currentColor')};
    path {
      stroke: ${({ isStroke, customColor }) => isStroke && (customColor ?? 'currentColor')};
      fill: ${({ isFill, customColor }) => isFill && (customColor ?? 'currentColor')};
    }
  }
` as any;

type Props = {
  src: string;
  width?: string | number;
  height?: string | number;
  color?: string;
  fill?: boolean;
  stroke?: boolean;
};

export const CustomSvg = ({ src, width, height, color, fill, stroke, ...props }: Props) => {
  return (
    <StyledSvg
      src={src}
      customColor={color}
      isFill={fill}
      isStroke={stroke}
      style={{
        width,
        height,
        minWidth: width,
        minHeight: height
      }}
      {...props}
    />
  );
};
