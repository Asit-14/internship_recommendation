import { toast } from 'react-hot-toast';

const baseClassName = 'rounded-md border bg-white px-4 py-3 text-sm font-medium shadow-lg';

export const showSuccess = (message: string) =>
  toast.success(message, {
    className: `${baseClassName} border-[#478356] text-[#478356]`,
  });

export const showError = (message: any) => {
  let displayMessage = 'An error occurred';

  if (typeof message === 'string') {
    displayMessage = message;
  } else if (message?.detail) {
    if (typeof message.detail === 'string') {
      displayMessage = message.detail;
    } else if (Array.isArray(message.detail)) {
      displayMessage = message.detail[0]?.msg || JSON.stringify(message.detail[0]);
    }
  } else if (message?.msg) {
    displayMessage = message.msg;
  } else if (typeof message === 'object') {
    displayMessage = message.message || JSON.stringify(message);
  }

  return toast.error(displayMessage, {
    className: `${baseClassName} border-[#ac2b49] text-[#ac2b49]`,
  });
};

export const showInfo = (message: string) =>
  toast(message, {
    icon: 'i',
    className: `${baseClassName} border-[#11486b] text-[#11486b]`,
  });
