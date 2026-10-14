import React from 'react';
import { Utensils, Flame } from 'lucide-react';
import './MealCard.css';

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
    <div className="meal-card">
      {/* Header */}
      <div className="meal-card-header">
        <div className="meal-card-title-wrapper">
          <div className="meal-card-icon-box">
            <Utensils size={18} />
          </div>
          <span className="meal-card-title">
            {meal_type}
          </span>
        </div>

        <div className="meal-card-calories-badge">
          <Flame size={15} />
          <span>{total_calories} kcal</span>
        </div>
      </div>

      {/* Item list */}
      {items.length > 0 && (
        <div className="meal-items-list">
          {items.map((item, idx) => (
            <div key={idx} className="meal-item-row">
              <span>
                {item.quantity ? `${item.quantity} ` : ''}
                {item.unit && item.unit !== 'serving' ? `${item.unit} ` : ''}
                <strong className="meal-item-name">{item.name}</strong>
              </span>
              <span className="meal-item-calories">
                {item.calories} kcal
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Macronutrient Pills */}
      <div className="meal-macros-grid">
        <div className="meal-macro-pill protein">
          <div className="meal-macro-label">PROTEIN</div>
          <div className="meal-macro-value">{total_protein_g}g</div>
        </div>
        <div className="meal-macro-pill carbs">
          <div className="meal-macro-label">CARBS</div>
          <div className="meal-macro-value">{total_carbs_g}g</div>
        </div>
        <div className="meal-macro-pill fat">
          <div className="meal-macro-label">FAT</div>
          <div className="meal-macro-value">{total_fat_g}g</div>
        </div>
      </div>
    </div>
  );
}