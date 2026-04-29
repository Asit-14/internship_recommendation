import { toast } from 'react-hot-toast';

const baseClassName = 'rounded-md border bg-white px-4 py-3 text-sm font-medium shadow-lg';

export const showSuccess = (message: string) =>
  toast.success(message, {
    className: `${baseClassName} border-[#478356] text-[#478356]`,
  });

export const showError = (message: unknown) => {
  let displayMessage = 'An error occurred';
  const msg = message as Record<string, unknown>;

  if (typeof message === 'string') {
    displayMessage = message;
  } else if (msg && typeof msg === 'object') {
    if (msg.detail) {
      if (typeof msg.detail === 'string') {
        displayMessage = msg.detail;
      } else if (Array.isArray(msg.detail)) {
        const firstDetail = msg.detail[0];
        if (firstDetail && typeof firstDetail === 'object') {
          displayMessage = (firstDetail as any).msg || JSON.stringify(firstDetail);
        } else {
          displayMessage = String(firstDetail);
        }
      }
    } else if (typeof msg.msg === 'string') {
      displayMessage = msg.msg;
    } else if (typeof msg.message === 'string') {
      displayMessage = msg.message;
    } else if (msg.message || msg.msg) {
      displayMessage = String(msg.message || msg.msg);
    }
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
