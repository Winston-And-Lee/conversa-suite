import { useTranslate } from '@refinedev/core';
import { Badge, Space } from 'antd';
import React from 'react';

interface ProjectStatusProps {
  status: string;
}

export const ProjectStatus: React.FC<ProjectStatusProps> = ({ status }) => {
  const t = useTranslate();
  const tPageFieldBaseKey = 'components.approvalRequestStatus';

  const renderStatus = () => {
    switch (status) {
      case 'PENDING':
        return <Badge color='gray' text={t(`${tPageFieldBaseKey}.fields.pending`)} />;
      case 'IN_PROGRESS':
        return <Badge color='blue' text={t(`${tPageFieldBaseKey}.fields.inProgress`)} />;
      case 'DONE':
        return <Badge color='green' text={t(`${tPageFieldBaseKey}.fields.done`)} />;
      case 'CANCELLED':
        return <Badge color='red' text={t(`${tPageFieldBaseKey}.fields.cancelled`)} />;

      default:
        return status;
    }
  };

  return <Space>{renderStatus()}</Space>;
};

export default ProjectStatus;
