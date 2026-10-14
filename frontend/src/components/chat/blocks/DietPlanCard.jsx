import React from 'react';
import { Sparkles } from 'lucide-react';
import './DietPlanCard.css';

export function DietPlanCard({ data }) {
  if (!data) return null;

  const {
    title = 'Personalized Nutrition Plan',
    target_daily_calories = 2000,
    duration_weeks = 4,
    meals_json = {},
    recommendations = '',
  } = data;

  const slots = meals_json.meals || [];

  return (
    <div className="diet-plan-card">
      {/* Title */}
      <div className="diet-plan-header">
        <div className="diet-plan-title-wrapper">
          <div className="diet-plan-icon-box">
            <Sparkles size={18} />
          </div>
          <div>
            <div className="diet-plan-title">{title}</div>
            <div className="diet-plan-subtitle">
              Target: {target_daily_calories} kcal/day • {duration_weeks} Weeks
            </div>
          </div>
        </div>
      </div>

      {recommendations && (
        <div className="diet-plan-recommendations">
          {recommendations}
        </div>
      )}

      {/* Meal slots breakdown */}
      {slots.length > 0 && (
        <div className="diet-plan-slots">
          {slots.map((slot, idx) => (
            <div key={idx} className="diet-slot-item">
              <div className="diet-slot-header">
                <span className="diet-slot-name">{slot.slot}</span>
                <span className="diet-slot-calories">
                  ~{slot.target_calories} kcal
                </span>
              </div>
              <ul className="diet-slot-list">
                {slot.suggestions?.map((item, sIdx) => (
                  <li key={sIdx}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}