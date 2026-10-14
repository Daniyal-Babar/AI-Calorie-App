import React from 'react';
import { Bot, User as UserIcon } from 'lucide-react';
import { MealCard } from './blocks/MealCard';
import { DailySummaryCard } from './blocks/DailySummaryCard';
import { DietPlanCard } from './blocks/DietPlanCard';
import { ConfirmButtons } from './ConfirmButtons';
import { API_BASE } from '../../api/client';
import './MessageBubble.css';

export function MessageBubble({ message, onConfirm }) {
  const isUser = message.role === 'user';
  const blocks = message.blocks || [];
  const roleClass = isUser ? 'user' : 'assistant';

  return (
    <div className={`message-bubble-wrapper ${roleClass}`}>
      {/* Avatar */}
      <div className={`message-avatar ${roleClass}`}>
        {isUser ? <UserIcon size={18} /> : <Bot size={20} />}
      </div>

      {/* Bubble Content */}
      <div className={`message-content-container ${roleClass}`}>
        {/* User image attachment if present */}
        {message.image_id && (
          <div className="message-image-wrapper">
            <img
              src={`${API_BASE}/uploads/${message.image_id}`}
              alt="Meal attachment"
              className="message-image-attachment"
            />
          </div>
        )}

        <div className={`message-bubble-body ${roleClass}`}>
          {/* Render Rich Typed Blocks */}
          {blocks.length > 0 ? (
            blocks.map((block, index) => {
              if (block.type === 'text') {
                return (
                  <p key={index} className="message-text-block">
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
            <p className="message-text-block plain">
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
        <span className="message-timestamp">
          {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
        </span>
      </div>
    </div>
  );
}