import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { Sparkles, Utensils, Target, ShieldCheck, Flame, Loader2 } from 'lucide-react';

export function MessageList({
  messages,
  streamingStatus,
  currentTool,
  onConfirm,
  onSendPreset,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingStatus]);

  if (!messages || messages.length === 0) {
    return (
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          textAlign: 'center',
          maxWidth: '700px',
          margin: '0 auto',
        }}
      >
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2))',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-emerald)',
            marginBottom: '18px',
            boxShadow: 'var(--shadow-glow)',
          }}
        >
          <Flame size={32} />
        </div>

        <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, color: '#fff', marginBottom: '8px' }}>
          Welcome to NutriAgent
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '520px', lineHeight: 1.5, marginBottom: '28px' }}>
          Your autonomous AI nutrition companion. Just describe what you ate, attach a photo of your plate, or ask for your daily metabolic summary.
        </p>

        {/* Suggested Prompts */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px', width: '100%' }}>
          {[
            {
              icon: <Utensils size={16} color="var(--accent-emerald)" />,
              label: 'Log a Meal',
              prompt: "I had 2 scrambled eggs, avocado toast, and black coffee for breakfast",
            },
            {
              icon: <Target size={16} color="var(--accent-cyan)" />,
              label: 'Daily Progress',
              prompt: "How many calories have I eaten today?",
            },
            {
              icon: <Sparkles size={16} color="var(--accent-amber)" />,
              label: 'Personalized Plan',
              prompt: "Create a weight-loss diet plan for 1900 kcal with high protein",
            },
            {
              icon: <Flame size={16} color="var(--accent-rose)" />,
              label: 'Set Goal',
              prompt: "Set my daily calorie goal to 2100 kcal",
            },
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSendPreset(item.prompt)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-glass)',
                color: '#cbd5e1',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                e.currentTarget.style.background = 'rgba(16, 185, 129, 0.06)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-glass)';
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
              }}
            >
              <div style={{ marginTop: '2px' }}>{item.icon}</div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#fff' }}>{item.label}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', marginTop: '2px' }}>
                  "{item.prompt}"
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px 0',
      }}
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} onConfirm={onConfirm} />
      ))}

      {/* Streaming / Agent Status Indicator */}
      {streamingStatus && (
        <div
          style={{
            maxWidth: '850px',
            margin: '0 auto 16px auto',
            padding: '0 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <div
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: 'var(--accent-emerald)',
              fontSize: '0.8rem',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              animation: 'pulseGlow 1.5s infinite',
            }}
          >
            <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
            <span>
              {streamingStatus === 'executing_tool'
                ? `Running tool: ${currentTool || 'calculating'}...`
                : 'NutriAgent is analyzing...'}
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
