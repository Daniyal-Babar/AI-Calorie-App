import React from 'react';
import { Activity } from 'lucide-react';
import './DailySummaryCard.css';

export function DailySummaryCard({ data }) {
  if (!data) return null;

  const consumed = data.consumed || {};
  const targets = data.targets || {};
  const remaining = data.remaining_calories !== undefined ? data.remaining_calories : (targets.calories || 2000) - (consumed.calories || 0);
  const percent = data.percent_consumed || (targets.calories ? Math.round((consumed.calories / targets.calories) * 100) : 0);
  
  const isOver = remaining < 0;

  return (
    <div className="summary-card">
      <div className="summary-header">
        <div className="summary-title-wrapper">
          <div className="summary-icon-box">
            <Activity size={18} />
          </div>
          <div>
            <div className="summary-title">Daily Nutrition Summary</div>
            <div className="summary-date">{data.date || "Today's Intake"}</div>
          </div>
        </div>

        <div className={`summary-badge ${isOver ? 'over' : 'left'}`}>
          {isOver ? `${Math.abs(remaining)} kcal over` : `${remaining} kcal left`}
        </div>
      </div>

      {/* Calorie Progress Bar */}
      <div className="summary-progress-section">
        <div className="summary-progress-labels">
          <span style={{ color: 'var(--text-muted)' }}>
            Consumed: <strong>{consumed.calories || 0} kcal</strong>
          </span>
          <span style={{ color: 'var(--text-muted)' }}>
            Goal: <strong>{targets.calories || 2000} kcal</strong>
          </span>
        </div>
        <div className="summary-progress-track">
          <div
            className={`summary-progress-fill ${isOver ? 'over' : 'normal'}`}
            style={{ width: `${Math.min(percent, 100)}%` }}
          />
        </div>
      </div>

      {/* Macronutrient breakdown */}
      <div className="summary-macros-grid">
        <div className="macro-box">
          <div className="macro-label protein">PROTEIN</div>
          <div className="macro-value">
            {consumed.protein_g || 0} / {targets.protein_g || 120}g
          </div>
        </div>

        <div className="macro-box">
          <div className="macro-label carbs">CARBS</div>
          <div className="macro-value">
            {consumed.carbs_g || 0} / {targets.carbs_g || 220}g
          </div>
        </div>

        <div className="macro-box">
          <div className="macro-label fat">FAT</div>
          <div className="macro-value">
            {consumed.fat_g || 0} / {targets.fat_g || 65}g
          </div>
        </div>
      </div>
    </div>
  );
}