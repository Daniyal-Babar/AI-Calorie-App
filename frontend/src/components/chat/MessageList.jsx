import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { Sparkles, Utensils, Target, Flame, Loader2 } from 'lucide-react';
import './MessageList.css';

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
      <div className="empty-state-container">
        <div className="empty-state-icon">
          <Flame size={32} />
        </div>

        <h2 className="empty-state-title">
          Welcome to NutriAgent
        </h2>
        <p className="empty-state-subtitle">
          Your autonomous AI nutrition companion. Just describe what you ate, attach a photo of your plate, or ask for your daily metabolic summary.
        </p>

        {/* Suggested Prompts */}
        <div className="suggested-prompts-grid">
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
              type="button"
              onClick={() => onSendPreset(item.prompt)}
              className="prompt-card-btn"
            >
              <div className="prompt-card-icon">{item.icon}</div>
              <div>
                <div className="prompt-card-label">{item.label}</div>
                <div className="prompt-card-text">
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
    <div className="message-list-container">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} onConfirm={onConfirm} />
      ))}

      {/* Streaming / Agent Status Indicator */}
      {streamingStatus && (
        <div className="streaming-indicator-wrapper">
          <div className="streaming-badge">
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