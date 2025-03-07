export interface IInputSelectionForeignKeyProps {
  item: {
    name: string;
    model: string;
    references: string;
  };
  value: string;
  onChange?: (value: string) => void;
}
