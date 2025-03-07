import { DashboardOutlined, PartitionOutlined, RocketOutlined, UsergroupAddOutlined } from '@ant-design/icons';

import * as SolarIconSet from 'solar-icon-set';

export const resources = [
  {
    name: 'reports',
    list: '/reports/',
    edit: '/reports/edit/:id',
    create: '/reports/create',
    identifier: 'Reports',
    show: '/reports/:id',
    full: '/reports/full/:id',
    meta: {
      icon: <SolarIconSet.CourseUp color='#1C274C' size={24} iconStyle='Outline' />,
      label: 'Reports'
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
  {
    name: 'report-service',
    list: '/admin/report-service/',
    create: '/admin/report-service/create',
    edit: '/admin/report-service/edit/:id',
    identifier: 'Report Service',
    show: '/admin/report-service/:id',
    meta: {
      icon: <DashboardOutlined />,
      label: 'Report service',
      parent: 'Super Admin'
    }
  },
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
  }
];
