import { Button } from 'antd';

export interface IStepProps extends IStepNavigateProps {
  title: string;
  content: JSX.Element;
}

export interface IStepNavigateProps {
  cancelStepLabel?: string;
  onCancelClick?: () => void;
  nextStepLabel?: string;
  onNextClick?: () => void;
  prevStepLabel?: string;
  onPrevClick?: () => void;
  displayFullWidthSubmitButton?: boolean;
}

export const StepNavigate = (props: IStepNavigateProps) => {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between'
      }}
    >
      {props.onCancelClick && (
        <Button
          type='text'
          onClick={() => {
            if (props.onCancelClick) {
              props.onCancelClick();
            }
          }}
        >
          {props.cancelStepLabel ?? 'ยกเลิก'}
        </Button>
      )}
      <div
        style={
          props.onCancelClick
            ? { display: 'flex' }
            : { display: 'flex', justifyContent: 'space-between', width: '100%' }
        }
      >
        {props.onPrevClick && (
          <Button
            type='text'
            style={{
              borderWidth: '1px',
              borderColor: '#D0D5DD',
              marginRight: '8px'
            }}
            onClick={() => {
              if (props.onPrevClick) {
                props.onPrevClick();
              }
            }}
          >
            {props.prevStepLabel ?? 'ย้อนกลับ'}
          </Button>
        )}
        <Button
          block={props.displayFullWidthSubmitButton ? true : false}
          type='primary'
          onClick={() => {
            if (props.onNextClick) {
              props.onNextClick();
            }
          }}
        >
          {props.nextStepLabel ?? 'ถัดไป'}
        </Button>
      </div>
    </div>
  );
};
