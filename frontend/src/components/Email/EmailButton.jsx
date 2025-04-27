import React from 'react';
import { MdEmail } from 'react-icons/md';

const EmailButton = ({ onClick }) => {
  return (
    <button className="email-button" onClick={onClick} aria-label="이메일 보기">
      <MdEmail />
    </button>
  );
};

export default EmailButton;