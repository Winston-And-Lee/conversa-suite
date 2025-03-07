import React from 'react';

export const Padding = (props: {
  vertical?: string | number;
  horizontal?: string | number;
  children: React.ReactNode;
}) => {
  return React.createElement(
    'div',
    {
      style: {
        paddingTop: props.vertical,
        paddingBottom: props.vertical,
        paddingLeft: props.horizontal,
        paddingRight: props.horizontal
      }
    },
    props.children
  );
};
