import { formatNumberWithCommas } from '@/utils';
import { useTranslate } from '@refinedev/core';
import { Pagination, PaginationProps } from 'antd';
import styled from 'styled-components';
import { IPaginationProps } from './interface';

// if you want to display pagination at bootom
// set outer div position as relative
const CustomPagination = styled(Pagination)`
  z-index: 1;
  padding: 8px 16px;
  width: 100%;
  background-color: ${props => props.theme.colors.neutral_12};
  position: absolute;
  bottom: 0;

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

export const PaginationComponent = ({ totalRecords, setCurrent, setPageSize }: IPaginationProps) => {
  const t = useTranslate();
  const handleChagePagination: PaginationProps['onChange'] = (page, pageSize) => {
    setCurrent(page);
    setPageSize(pageSize);
  };

  return (
    <CustomPagination
      align='end'
      total={totalRecords}
      showSizeChanger
      showQuickJumper
      showTotal={total =>
        `${t('components.pagination.fields.paginationTotal', {
          total: formatNumberWithCommas(total)
        })}`
      }
      defaultPageSize={20}
      onChange={(page, pageSize) => handleChagePagination(page, pageSize)}
    />
  );
};
