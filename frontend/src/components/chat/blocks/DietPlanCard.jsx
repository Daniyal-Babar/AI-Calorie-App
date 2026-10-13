import React from 'react';
import { Sparkles, Calendar, CheckCircle } from 'lucide-react';

export function DietPlanCard({ data }) {
  if (!data) return null;

  const {
    title = 'Personalized Nutrition Plan',
    goal_type = 'weight_loss',
    target_daily_calories = 2000,
    duration_weeks = 4,
    meals_json = {},
    recommendations = '',
  } = data;

  const slots = meals_json.meals || [];

  return (
    <div
      style={{
        margin: '12px 0',
        padding: '18px',
        borderRadius: 'var(--radius-md)',
        background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%)',
        border: '1px solid rgba(139, 92, 246, 0.35)',
        boxShadow: '0 8px 25px rgba(0, 0, 0, 0.4)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              padding: '6px',
              borderRadius: '8px',
              background: 'rgba(139, 92, 246, 0.2)',
              color: '#c4b5fd',
              display: 'flex',
            }}
          >
            <Sparkles size={18} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: '#fff' }}>{title}</div>
            <div style={{ fontSize: '0.75rem', color: '#a78bfa' }}>
              Target: {target_daily_calories} kcal/day • {duration_weeks} Weeks
            </div>
          </div>
        </div>
      </div>

      {recommendations && (
        <div
          style={{
            fontSize: '0.85rem',
            color: '#cbd5e1',
            marginBottom: '14px',
            lineHeight: 1.4,
            padding: '8px 12px',
            borderRadius: '8px',
            background: 'rgba(255, 255, 255, 0.04)',
          }}
        >
          {recommendations}
        </div>
      )}

      {/* Meal slots breakdown */}
      {slots.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {slots.map((slot, idx) => (
            <div
              key={idx}
              style={{
                padding: '10px 12px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f1f5f9' }}>{slot.slot}</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                  ~{slot.target_calories} kcal
                </span>
              </div>
              <ul style={{ paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {slot.suggestions?.map((item, sIdx) => (
                  <li key={sIdx} style={{ margin: '2px 0' }}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
