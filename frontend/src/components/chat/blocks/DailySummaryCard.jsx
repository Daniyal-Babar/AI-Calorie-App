import React from 'react';
import { Target, Activity, CheckCircle2 } from 'lucide-react';

export function DailySummaryCard({ data }) {
  if (!data) return null;

  const consumed = data.consumed || {};
  const targets = data.targets || {};
  const remaining = data.remaining_calories !== undefined ? data.remaining_calories : (targets.calories || 2000) - (consumed.calories || 0);
  const percent = data.percent_consumed || (targets.calories ? Math.round((consumed.calories / targets.calories) * 100) : 0);

  return (
    <div
      style={{
        margin: '12px 0',
        padding: '18px',
        borderRadius: 'var(--radius-md)',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.75) 100%)',
        border: '1px solid rgba(6, 182, 212, 0.3)',
        boxShadow: '0 8px 25px rgba(0, 0, 0, 0.4)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              padding: '6px',
              borderRadius: '8px',
              background: 'rgba(6, 182, 212, 0.15)',
              color: 'var(--accent-cyan)',
              display: 'flex',
            }}
          >
            <Activity size={18} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fff' }}>Daily Nutrition Summary</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{data.date || "Today's Intake"}</div>
          </div>
        </div>

        <div
          style={{
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            background: remaining >= 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            color: remaining >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)',
            fontWeight: 700,
            fontSize: '0.85rem',
          }}
        >
          {remaining >= 0 ? `${remaining} kcal left` : `${Math.abs(remaining)} kcal over`}
        </div>
      </div>

      {/* Calorie Progress Bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
          <span style={{ color: 'var(--text-muted)' }}>
            Consumed: <strong style={{ color: '#fff' }}>{consumed.calories || 0} kcal</strong>
          </span>
          <span style={{ color: 'var(--text-muted)' }}>
            Goal: <strong style={{ color: '#fff' }}>{targets.calories || 2000} kcal</strong>
          </span>
        </div>
        <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${Math.min(percent, 100)}%`,
              height: '100%',
              background: remaining < 0 ? 'var(--accent-rose)' : 'linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald))',
              borderRadius: '4px',
              transition: 'width 0.4s ease',
            }}
          />
        </div>
      </div>

      {/* Macronutrient breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
        <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>PROTEIN</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
            {consumed.protein_g || 0} / {targets.protein_g || 120}g
          </div>
        </div>

        <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', fontWeight: 600 }}>CARBS</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
            {consumed.carbs_g || 0} / {targets.carbs_g || 220}g
          </div>
        </div>

        <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-rose)', fontWeight: 600 }}>FAT</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
            {consumed.fat_g || 0} / {targets.fat_g || 65}g
          </div>
        </div>
      </div>
    </div>
  );
}
