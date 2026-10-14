import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { MessageList } from '../components/chat/MessageList';
import { Composer } from '../components/chat/Composer';
import { Toast } from '../components/common/Toast';
import { Flame, LogOut, Activity, Sparkles } from 'lucide-react';
import './Chat.css';

export function Chat() {
  const { user, logout } = useAuth();
  const {
    messages,
    streamingStatus,
    currentTool,
    error,
    sendMessage,
    confirmAction,
  } = useChat();

  const [toastError, setToastError] = useState(null);

  const handleSend = (text, imageId) => {
    sendMessage(text, imageId);
  };

  const handleSendPreset = (prompt) => {
    sendMessage(prompt);
  };

  return (
    <div className="chat-container">
      {/* Top Header Bar */}
      <header className="chat-header">
        {/* Brand */}
        <div className="chat-brand">
          <div className="chat-brand-icon">
            <Flame size={20} />
          </div>
          <div>
            <div className="chat-brand-title">NutriAgent</div>
            <div className="chat-brand-subtitle">AI Nutrition & Calorie Coach</div>
          </div>
        </div>

        {/* Quick Actions / Status */}
        <div className="chat-actions">
          <button
            onClick={() => handleSendPreset("Show my today's nutrition summary and remaining calories")}
            className="preset-btn-cyan"
          >
            <Activity size={14} />
            <span>Daily Totals</span>
          </button>

          <button
            onClick={() => handleSendPreset("What is my current active diet plan and recommended calories?")}
            className="preset-btn-purple"
          >
            <Sparkles size={14} />
            <span>Diet Plan</span>
          </button>

          {/* User Profile Pill & Logout */}
          <div className="chat-user-section">
            <div className="chat-user-info">
              <div className="chat-user-avatar">
                {user?.name ? user.name[0].toUpperCase() : 'U'}
              </div>
              <span className="chat-user-name">
                {user?.name || 'User'}
              </span>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="chat-logout-btn"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Stream Area */}
      <main className="chat-main">
        <MessageList
          messages={messages}
          streamingStatus={streamingStatus}
          currentTool={currentTool}
          onConfirm={confirmAction}
          onSendPreset={handleSendPreset}
        />

        {/* Input Composer */}
        <Composer onSend={handleSend} disabled={!!streamingStatus} />
      </main>

      {/* Toast Alert */}
      {(error || toastError) && (
        <Toast
          message={error || toastError}
          onClose={() => setToastError(null)}
        />
      )}
    </div>
  );
}