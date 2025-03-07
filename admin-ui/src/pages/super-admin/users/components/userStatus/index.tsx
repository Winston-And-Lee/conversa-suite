import { Space } from 'antd';
import React from 'react';
import { useTranslation } from 'react-i18next';

interface UserStatusProps {
  status: number;
}

// UserStatusTypeAdmin   UserStatusType = 107
// UserStatusTypeUser    UserStatusType = 209
// UserStatusTypeInvited UserStatusType = 303
// UserStatusTypePending UserStatusType = 401
// UserStatusTypeInactive UserStatusType = 945

export const UserStatus: React.FC<UserStatusProps> = ({ status }) => {
  const { t } = useTranslation('super-admin');

  const renderStatus = () => {
    switch (status) {
      case 401:
        return (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                background: '#FADB14',
                borderRadius: '100%',
                width: '5px',
                height: '5px',
                margin: '5px'
              }}
            ></div>
            {t('user_status.pending')}
          </div>
        );
      case 209:
        return (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                background: '#52C41A',
                borderRadius: '100%',
                width: '5px',
                height: '5px',
                margin: '5px'
              }}
            ></div>
            {t('user_status.active')}
          </div>
        );
      case 107:
        return (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                background: '#001F3D',
                borderRadius: '100%',
                width: '5px',
                height: '5px',
                margin: '5px'
              }}
            ></div>
            {t('user_status.active')}
          </div>
        );
      case 945:
        return (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                background: '#FF4D4F',
                borderRadius: '100%',
                width: '5px',
                height: '5px',
                margin: '5px'
              }}
            ></div>
            {t('user_status.inactive')}
          </div>
        );
      default:
        return status;
    }
  };

  return <Space>{renderStatus()}</Space>;
};

export default UserStatus;
