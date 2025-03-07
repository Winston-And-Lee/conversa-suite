import React, { useEffect, useState } from 'react';
import { styled } from 'styled-components';

const SelectableCardStyled = styled.div`
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  &.active {
    border: 1px solid rgb(0, 51, 94);
  }
`;

interface ISelectableCard {
  children: React.ReactNode;
  id?: string;
  active?: boolean;
  toggled?: boolean;
  onClick?: (id: string) => void;
}

const SelectableCards: React.FC<ISelectableCard> = ({ toggled = true, ...props }) => {
  const [activeCard, setActiveCard] = useState<boolean>(false);

  useEffect(() => {
    props.active ? setActiveCard(true) : setActiveCard(false);
  }, [props.active]);

  const handleCardClick = () => {
    if (!toggled && props.active) return;
    setActiveCard(!activeCard);
    if (props.onClick) {
      props.onClick(props.id ?? '');
    }
  };

  return (
    <SelectableCardStyled className={`${activeCard ? 'active' : ''}`} onClick={() => handleCardClick()}>
      {props.children}
    </SelectableCardStyled>
  );
};

export default SelectableCards;
