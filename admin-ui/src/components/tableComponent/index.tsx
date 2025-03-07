import { Pagination, Table } from 'antd';
import styled from 'styled-components';

export const CustomTable = styled(Table)`
  .ant-table-cell-row-hover {
    /* background-color: ${props => props.theme.colors.primary_05} !important; */
  }
  & > .ant-table-thead .ant-table-cell {
    background-color: var(--neutral_13) !important;
  }
  .ant-table-row-expand-icon {
    color: ${props => props.theme.colors.primary_02} !important;
  }
  .ant-table-expanded-row .ant-table-cell {
    background-color: white !important;
  }
  .ant-table-cell .ant-table {
    margin-inline: -8px -8px !important;
  }
  .ant-table-tbody > tr.ant-table-row-selected > td {
    background-color: ${props => props.theme.colors.neutral_10} !important;
  }
`;

export const CustomPagination = styled(Pagination)`
  position: sticky;
  bottom: 0;
  z-index: 1;
  margin-left: -24px;
  padding: 8px 16px;
  width: calc(100% + 24px);
  background-color: var(--neutral_12);
  text-align: right;
  justify-content: flex-end;
  align-items: center;

  .ant-pagination-item,
  .ant-pagination-prev,
  .ant-pagination-next {
    border-radius: 0px;
    border: 1px solid var(--neutral_08);
  }
  .ant-pagination-item-active {
    border: 1px solid ${props => props.theme.colors.primary_02};
  }
  .ant-select-selector,
  .ant-pagination-options-quick-jumper input {
    border-radius: 0px;
  }
`;
