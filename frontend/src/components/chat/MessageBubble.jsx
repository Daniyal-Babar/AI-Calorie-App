import React from 'react';
import { Bot, User as UserIcon, Sparkles } from 'lucide-react';
import { MealCard } from './blocks/MealCard';
import { DailySummaryCard } from './blocks/DailySummaryCard';
import { DietPlanCard } from './blocks/DietPlanCard';
import { ConfirmButtons } from './ConfirmButtons';
import { API_BASE } from '../../api/client';

export function MessageBubble({ message, onConfirm }) {
  const isUser = message.role === 'user';
  const blocks = message.blocks || [];

  return (
    <div
      style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '20px',
        maxWidth: '850px',
        margin: '0 auto 20px auto',
        padding: '0 16px',
        flexDirection: isUser ? 'row-reverse' : 'row',
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          background: isUser
            ? 'linear-gradient(135deg, #3b82f6, #6366f1)'
            : 'linear-gradient(135deg, #10b981, #06b6d4)',
          color: '#fff',
          boxShadow: isUser
            ? '0 4px 14px rgba(59, 130, 246, 0.3)'
            : '0 4px 14px rgba(16, 185, 129, 0.3)',
        }}
      >
        {isUser ? <UserIcon size={18} /> : <Bot size={20} />}
      </div>

      {/* Bubble Content */}
      <div
        style={{
          maxWidth: '75%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        {/* User image attachment if present */}
        {message.image_id && (
          <div style={{ marginBottom: '8px' }}>
            <img
              src={`${API_BASE}/uploads/${message.image_id}`}
              alt="Meal attachment"
              style={{
                maxWidth: '240px',
                maxHeight: '200px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-glass)',
                objectFit: 'cover',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              }}
            />
          </div>
        )}

        <div
          style={{
            padding: isUser ? '12px 18px' : '14px 20px',
            borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            background: isUser
              ? 'linear-gradient(135deg, #2563eb, #1d4ed8)'
              : 'rgba(21, 30, 52, 0.85)',
            border: isUser ? 'none' : '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(14px)',
            color: isUser ? '#fff' : '#f1f5f9',
            fontSize: '0.925rem',
            lineHeight: 1.55,
            boxShadow: isUser
              ? '0 4px 15px rgba(37, 99, 235, 0.25)'
              : '0 8px 25px rgba(0, 0, 0, 0.35)',
            width: '100%',
          }}
        >
          {/* Render Rich Typed Blocks */}
          {blocks.length > 0 ? (
            blocks.map((block, index) => {
              if (block.type === 'text') {
                return (
                  <p key={index} style={{ whiteSpace: 'pre-wrap', margin: '4px 0' }}>
                    {block.content}
                  </p>
                );
              }
              if (block.type === 'meal_card') {
                return <MealCard key={index} data={block.data} />;
              }
              if (block.type === 'daily_summary_card') {
                return <DailySummaryCard key={index} data={block.data} />;
              }
              if (block.type === 'diet_plan_card') {
                return <DietPlanCard key={index} data={block.data} />;
              }
              if (block.type === 'actions') {
                return <ConfirmButtons key={index} data={block.data} onConfirm={onConfirm} />;
              }
              return null;
            })
          ) : (
            <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
              {message.content}
            </p>
          )}

          {/* Pending action fallback if not in blocks */}
          {!blocks.some((b) => b.type === 'actions') && message.pending_action && (
            <ConfirmButtons
              data={{
                action_id: message.pending_action.action_id,
                description: message.pending_action.description,
              }}
              onConfirm={onConfirm}
            />
          )}
        </div>

        {/* Timestamp */}
        <span
          style={{
            fontSize: '0.7rem',
            color: 'var(--text-subtle)',
            marginTop: '4px',
            padding: '0 4px',
          }}
        >
          {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
        </span>
      </div>
    </div>
  );
}
