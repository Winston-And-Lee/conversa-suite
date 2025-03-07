export interface IPaginationProps {
  totalRecords: number | undefined;
  setCurrent: React.Dispatch<React.SetStateAction<number>>;
  setPageSize: React.Dispatch<React.SetStateAction<number>>;
}
