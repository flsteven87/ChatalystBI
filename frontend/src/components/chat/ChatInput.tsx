'use client';

import { useState, FormEvent } from 'react';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const isDisabled = !message.trim() || isLoading;

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="輸入您的查詢..."
        className={styles.input}
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={isDisabled}
        className={`${styles.button} ${
          isDisabled ? styles.buttonDisabled : styles.buttonEnabled
        }`}
      >
        {isLoading ? '處理中...' : '發送'}
      </button>
    </form>
  );
} 