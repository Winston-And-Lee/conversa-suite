import { RedoOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useEffect, useState } from 'react';

export const OtpButtonWithTimer = ({
  count,
  onStartTimer,
  onFinished
}: {
  count: number;
  onStartTimer?: () => void;
  onFinished?: () => void;
}) => {
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    setSeconds(count);
    setIsActive(true);
  }, []);

  useEffect(() => {
    let timer: string | number | NodeJS.Timeout | undefined;
    if (isActive && seconds > 0) {
      timer = setTimeout(() => {
        setSeconds(seconds - 1);
      }, 1000);
    } else if (seconds === 0 && isActive) {
      setIsActive(false);
      onFinished && onFinished();
    }
    return () => clearTimeout(timer);
  }, [isActive, seconds]);

  const startCountdown = () => {
    setSeconds(count);
    setIsActive(true);
    onStartTimer && onStartTimer();
  };

  return (
    <div>
      <Button disabled={isActive} block={true} icon={<RedoOutlined />} onClick={() => startCountdown()}>
        ขอรหัสใหม่ {seconds > 0 ? `${seconds}s` : `${count}s`}
      </Button>
    </div>
  );
};
