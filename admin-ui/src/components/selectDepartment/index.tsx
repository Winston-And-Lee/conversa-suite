import {
  getDepartmentFromParentID,
  getParentDepartment,
  searchDepartmentWithNameLike
} from '@/api-requests/organization';
import { IDepartmentTableProps, IDepartmentTree } from '@/pages/organization/interfaces';
import { formatNumberWithCommas } from '@/utils';
import { DownOutlined } from '@ant-design/icons';
import { Card, Flex, Input, Pagination, Tree, TreeDataNode } from 'antd';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ISelectDepartment } from './interface';
import axios from 'axios';
import { message } from 'antd';

const CustomPagination = styled(Pagination)`
  z-index: 1;
  padding: 8px 16px;
  width: 100%;
  background-color: ${props => props.theme.colors.neutral_12};

  .ant-pagination-item,
  .ant-pagination-prev,
  .ant-pagination-next {
    border-radius: 0px;
    border: 1px solid ${props => props.theme.colors.neutral_08};
  }
  .ant-pagination-item-active {
    border: 1px solid ${props => props.theme.colors.primary_02};
  }
`;

interface DepartmentData {
  id: string | number;
  name: string;
  [key: string]: any;
}

export const SelectDepartmentComponent: React.FC<ISelectDepartment> = ({ onChange, selectedValue }) => {
  const { t } = useTranslation('organization');
  const tPageFieldBaseKey = '_user_department';

  const [treeData, setTreeData] = useState<IDepartmentTree[]>([]);
  const [checkNodes, setCheckNodes] = useState<TreeDataNode[]>(selectedValue || []);
  const [departmentTableProps, setDepartmentTableProps] = useState<IDepartmentTableProps>();
  const [departmentCurrent, setDepartmentCurrent] = useState<number>(1);
  const [departmentPageSize, setDepartmentPageSize] = useState<number>(20);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const generateParentTreeData = useCallback(
    (departmentData: DepartmentData[], isLeaf?: boolean): IDepartmentTree[] => {
      if (!departmentData || !Array.isArray(departmentData)) return [];

      return departmentData.map(dep => ({
        key: dep.id,
        title: dep.name,
        isLeaf: isLeaf
      }));
    },
    []
  );

  const generateData = useCallback(
    (data: IDepartmentTableProps, isLeaf?: boolean) => {
      setDepartmentTableProps(data);
      const dataArray = Array.isArray(data?.data) ? data.data : [];
      setTreeData(generateParentTreeData(dataArray, isLeaf));
    },
    [generateParentTreeData]
  );

  const fetchData = useCallback(
    async (searchValue?: string) => {
      setIsLoading(true);
      try {
        if (searchValue) {
          const { data } = await searchDepartmentWithNameLike(searchValue, departmentCurrent, departmentPageSize);
          generateData(data, true);
        } else {
          const { data } = await getParentDepartment(departmentCurrent, departmentPageSize);
          generateData(data);
        }
      } catch (error) {
        message.error('Failed to fetch department data');
      } finally {
        setIsLoading(false);
      }
    },
    [departmentCurrent, departmentPageSize, generateData]
  );

  const updateTreeData = useCallback(
    (list: IDepartmentTree[], key: React.Key, children: IDepartmentTree[]): IDepartmentTree[] =>
      list.map(node => {
        if (node.key === key) {
          return {
            ...node,
            children
          };
        }
        if (node.children) {
          return {
            ...node,
            children: updateTreeData(node.children, key, children)
          };
        }
        return node;
      }),
    []
  );

  const onLoadData = useCallback(
    async ({ key, children }: { key: React.Key; children?: IDepartmentTree[] }) => {
      if (children) {
        return;
      }

      try {
        const { data } = await getDepartmentFromParentID(key.toString());
        const childList = data.data.map((d: DepartmentData) => ({
          key: d.id,
          title: d.name
        }));

        setTreeData(origin => updateTreeData(origin, key, childList));
      } catch (error) {
        message.error('Failed to load child departments');
      }
    },
    [updateTreeData]
  );

  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      const value = (e.target as HTMLInputElement).value;

      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }

      debounceTimeout.current = setTimeout(() => {
        fetchData(value);
      }, 1000);
    },
    [fetchData]
  );

  const onCheck = useCallback(
    (checkedKeysValue: React.Key[] | { checked: React.Key[]; halfChecked: React.Key[] }, info: any) => {
      const { key, title, isLeaf, checked } = info.node;

      setCheckNodes((prev: TreeDataNode[]) => {
        let newCheckNodes: TreeDataNode[];

        if (!checked) {
          newCheckNodes = [...prev, { key, title, isLeaf }];
        } else {
          newCheckNodes = prev.filter(node => node.key !== key);
        }

        onChange?.(newCheckNodes);
        return newCheckNodes;
      });
    },
    [onChange]
  );

  const handleChangePagination = useCallback((page: number, pageSize: number) => {
    setDepartmentCurrent(page);
    setDepartmentPageSize(pageSize);
  }, []);

  useEffect(() => {
    fetchData();
  }, [departmentCurrent, departmentPageSize, fetchData]);

  useEffect(() => {
    if (selectedValue) {
      setCheckNodes(selectedValue);
    }
  }, [selectedValue]);

  useEffect(() => {
    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    };
  }, []);

  const countDisplay = useMemo(() => {
    const dataLength = departmentTableProps?.data?.length ?? 0;
    const totalData = departmentTableProps?.total_data ?? 0;

    return (
      <>
        {formatNumberWithCommas(dataLength)} / {formatNumberWithCommas(totalData)}{' '}
        {t(`${tPageFieldBaseKey}.fields.item`)}
      </>
    );
  }, [departmentTableProps?.data?.length, departmentTableProps?.total_data, t, tPageFieldBaseKey]);

  return (
    <>
      <Flex align='center' gap={8} style={{ marginBottom: 16 }}>
        <Flex gap={8} flex={1}>
          <Input
            allowClear
            placeholder={t(`${tPageFieldBaseKey}.fields.searchPlaceholder`)}
            onKeyUpCapture={handleKeyPress}
            onClear={() => fetchData()}
          />
        </Flex>
        {countDisplay}
      </Flex>
      <Card size='small'>
        <Tree
          selectable={false}
          showLine
          checkable
          height={900}
          switcherIcon={<DownOutlined />}
          loadData={onLoadData}
          onCheck={onCheck}
          checkedKeys={checkNodes?.map(node => node.key)}
          treeData={treeData}
        />
      </Card>

      <CustomPagination
        align='end'
        total={departmentTableProps?.total_data ?? 0}
        showSizeChanger
        showQuickJumper
        defaultPageSize={20}
        onChange={handleChangePagination}
        current={departmentCurrent}
        pageSize={departmentPageSize}
      />
    </>
  );
};
