import React from 'react';
import { Utensils, Flame } from 'lucide-react';

export function MealCard({ data }) {
  if (!data) return null;

  const {
    meal_type = 'Meal',
    total_calories = 0,
    total_protein_g = 0,
    total_carbs_g = 0,
    total_fat_g = 0,
    items = [],
  } = data;

  return (
    <div
      style={{
        margin: '12px 0',
        padding: '16px',
        borderRadius: 'var(--radius-md)',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              padding: '6px',
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--accent-emerald)',
              display: 'flex',
            }}
          >
            <Utensils size={18} />
          </div>
          <span style={{ fontWeight: 600, fontSize: '1rem', textTransform: 'capitalize', color: '#fff' }}>
            {meal_type}
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 'var(--radius-full)',
            color: 'var(--accent-emerald)',
            fontWeight: 700,
            fontSize: '0.9rem',
          }}
        >
          <Flame size={15} />
          <span>{total_calories} kcal</span>
        </div>
      </div>

      {/* Item list */}
      {items.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '14px' }}>
          {items.map((item, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.85rem',
                color: 'var(--text-muted)',
                padding: '4px 8px',
                borderRadius: '6px',
                background: 'rgba(255, 255, 255, 0.03)',
              }}
            >
              <span>
                {item.quantity ? `${item.quantity} ` : ''}
                {item.unit && item.unit !== 'serving' ? `${item.unit} ` : ''}
                <strong style={{ color: '#e2e8f0' }}>{item.name}</strong>
              </span>
              <span style={{ color: 'var(--accent-emerald)', fontWeight: 500 }}>
                {item.calories} kcal
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Macronutrient Pills */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', paddingTop: '10px', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
        <div style={{ textAlign: 'center', padding: '6px', borderRadius: '8px', background: 'rgba(6, 182, 212, 0.1)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>PROTEIN</div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e0f2fe' }}>{total_protein_g}g</div>
        </div>
        <div style={{ textAlign: 'center', padding: '6px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.1)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', fontWeight: 600 }}>CARBS</div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fef3c7' }}>{total_carbs_g}g</div>
        </div>
        <div style={{ textAlign: 'center', padding: '6px', borderRadius: '8px', background: 'rgba(244, 63, 94, 0.1)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-rose)', fontWeight: 600 }}>FAT</div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffe4e6' }}>{total_fat_g}g</div>
        </div>
      </div>
    </div>
  );
}
