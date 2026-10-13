import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { MessageList } from '../components/chat/MessageList';
import { Composer } from '../components/chat/Composer';
import { Toast } from '../components/common/Toast';
import { Flame, LogOut, User as UserIcon, Activity, Sparkles, Plus } from 'lucide-react';

export function Chat() {
  const { user, logout } = useAuth();
  const {
    messages,
    streamingStatus,
    currentTool,
    error,
    sendMessage,
    confirmAction,
    loadHistory,
  } = useChat();

  const [toastError, setToastError] = useState(null);

  const handleSend = (text, imageId) => {
    sendMessage(text, imageId);
  };

  const handleSendPreset = (prompt) => {
    sendMessage(prompt);
  };

  const handleNewChat = () => {
    // Reload without conversation ID or clear local messages
    window.location.reload();
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        width: '100vw',
        background: 'var(--bg-primary)',
        overflow: 'hidden',
      }}
    >
      {/* Top Header Bar */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 24px',
          borderBottom: '1px solid var(--border-glass)',
          background: 'rgba(9, 13, 22, 0.85)',
          backdropFilter: 'blur(16px)',
          zIndex: 10,
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #10b981, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              boxShadow: '0 0 15px rgba(16, 185, 129, 0.35)',
            }}
          >
            <Flame size={20} />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.1rem', color: '#fff', letterSpacing: '-0.02em' }}>
              NutriAgent
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-emerald)', fontWeight: 500 }}>
              AI Nutrition & Calorie Coach
            </div>
          </div>
        </div>

        {/* Quick Actions / Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => handleSendPreset("Show my today's nutrition summary and remaining calories")}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(6, 182, 212, 0.1)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              color: 'var(--accent-cyan)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <Activity size={14} />
            <span style={{ display: 'none', md: 'inline' }}>Daily Totals</span>
          </button>

          <button
            onClick={() => handleSendPreset("What is my current active diet plan and recommended calories?")}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(139, 92, 246, 0.1)',
              border: '1px solid rgba(139, 92, 246, 0.25)',
              color: '#c4b5fd',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <Sparkles size={14} />
            <span>Diet Plan</span>
          </button>

          {/* User Profile Pill & Logout */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              paddingLeft: '12px',
              borderLeft: '1px solid var(--border-glass)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#e2e8f0',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                }}
              >
                {user?.name ? user.name[0].toUpperCase() : 'U'}
              </div>
              <span style={{ fontSize: '0.85rem', fontWeight: 500, color: '#e2e8f0' }}>
                {user?.name || 'User'}
              </span>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-subtle)',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-rose)')}
              onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-subtle)')}
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Stream Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
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
