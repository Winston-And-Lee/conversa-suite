import { DashboardOutlined, PartitionOutlined, RocketOutlined, UsergroupAddOutlined } from '@ant-design/icons';

import * as SolarIconSet from 'solar-icon-set';

export const resources = [
  // {
  //   name: 'reports',
  //   list: '/reports/',
  //   edit: '/reports/edit/:id',
  //   create: '/reports/create',
  //   identifier: 'Reports',
  //   show: '/reports/:id',
  //   full: '/reports/full/:id',
  //   meta: {
  //     icon: <SolarIconSet.CourseUp color='#1C274C' size={24} iconStyle='Outline' />,
  //     label: 'Reports'
  //   }
  // },
  {
    name: 'AI Assistant',
    meta: {
      icon: <SolarIconSet.ChatRound color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'AI Assistant'
    }
  },
  {
    name: 'assistant-ui',
    list: '/assistant-ui/',
    identifier: 'AssistantUI',
    meta: {
      icon: <SolarIconSet.ChatRound color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'Assistant',
      parent: 'AI Assistant'
    }
  },
  {
    name: 'data-ingestion',
    list: '/data-ingestion/',
    identifier: 'DataIngestion',
    show: '/data-ingestion/:id',
    meta: {
      icon: <SolarIconSet.Document color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'ข้อมูลสำหรับ AI',
      parent: 'AI Assistant'
    }
  },
  {
    name: 'Settings',
    meta: {
      icon: <SolarIconSet.Settings color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'Settings'
    }
  },
  {
    name: 'Super Admin',
    meta: {
      icon: <SolarIconSet.PlugCircle color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'Super Admin'
    }
  },
  // {
  //   name: 'report-service',
  //   list: '/admin/report-service/',
  //   create: '/admin/report-service/create',
  //   edit: '/admin/report-service/edit/:id',
  //   identifier: 'Report Service',
  //   show: '/admin/report-service/:id',
  //   meta: {
  //     icon: <DashboardOutlined />,
  //     label: 'Report service',
  //     parent: 'Super Admin'
  //   }
  // },
  {
    name: 'users',
    list: '/admin/users/',
    identifier: 'users',
    show: '/admin/users/:id',
    meta: {
      canDelete: false,
      icon: <UsergroupAddOutlined />,
      label: 'Users',
      parent: 'Super Admin'
    }
  },
  {
    name: 'files',
    list: '/admin/files/',
    identifier: 'files',
    meta: {
      icon: <SolarIconSet.Document color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'Files',
      parent: 'Super Admin'
    }
  }
];
