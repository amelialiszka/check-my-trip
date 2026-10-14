import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class TravelDataPreprocessorV2(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.train_categories = {}
        self.rare_regions = []

    def fit(self, X, y=None):
        if 'region' in X.columns:
            region_counts = X['region'].value_counts()
            self.rare_regions = region_counts[region_counts < 10].index.tolist()

        X_temp = self._transform_logic(X)
        
        cat_cols = ['country', 'room_type', 'meal_plan', 'region']
        for c in cat_cols:
            if c in X_temp.columns:
                self.train_categories[c] = X_temp[c].astype('category').dtype
                
        return self
    
    def transform(self, X):
        X_out = self._transform_logic(X)
        
        cat_cols = ['country', 'room_type', 'meal_plan', 'region']
        for c in cat_cols:
            if c in X_out.columns:
                if c in self.train_categories:
                    allowed_categories = self.train_categories[c].categories
                    mask = ~X_out[c].isin(allowed_categories)
                    X_out.loc[mask, c] = np.nan
                    
                    X_out[c] = pd.Categorical(X_out[c], categories=allowed_categories)
                else:
                    X_out[c] = X_out[c].astype('category')
                    
        return X_out

    def _transform_logic(self, X):
        X_out = X.copy()
        
        if 'id' in X_out.columns:
            X_out = X_out.set_index('id')

        cols_to_drop = ['url', 'hotel_name', 'flight_departure_time', 'flight_return_time', 'is_public_transport_nearby']
        X_out = X_out.drop(columns=[c for c in cols_to_drop if c in X_out.columns])

        if 'departure_date' in X_out.columns and 'scraped_at' in X_out.columns:
            X_out['departure_date'] = pd.to_datetime(X_out['departure_date'], errors='coerce')
            X_out['scraped_at'] = pd.to_datetime(X_out['scraped_at'], errors='coerce')

            X_out['days_to_departure'] = (X_out['departure_date'] - X_out['scraped_at']).dt.days
            X_out['is_last_minute'] = (X_out['days_to_departure'] <= 7).astype(int)
            
            X_out['departure_month'] = X_out['departure_date'].dt.month
            
            X_out = X_out.drop(columns=['departure_date', 'scraped_at'], errors='ignore')
        elif 'departure_date' in X_out.columns:
            X_out['departure_month'] = pd.to_datetime(X_out['departure_date'], errors='coerce').dt.month
            X_out = X_out.drop(columns=['departure_date'])
            
        if 'hotel_stars' in X_out.columns:
            X_out['hotel_stars'] = np.round(X_out['hotel_stars'])
            
        if 'average_rating' in X_out.columns and 'review_count' in X_out.columns:
            rating_filled = X_out['average_rating'].fillna(X_out['average_rating'].median())
            rating_filled = np.where(rating_filled <= 5.0, rating_filled * 2, rating_filled)
            review_filled = X_out['review_count'].fillna(0)
            X_out['credibility_score'] = rating_filled * np.log1p(review_filled)
            X_out = X_out.drop(columns=['average_rating', 'review_count'])
            
        for col, new_col in zip(['number_of_pools', 'number_of_bars', 'number_of_restaurants'], ['has_pool', 'has_bar', 'has_restaurant']):
            if col in X_out.columns:
                X_out[new_col] = (X_out[col] > 0).astype(int)
                X_out = X_out.drop(columns=[col])
                
        if 'is_direct_flight' in X_out.columns:
            X_out['is_direct_flight'] = X_out['is_direct_flight'].fillna(-1)

        if 'room_type' in X_out.columns:
            X_out['room_type'] = X_out['room_type'].replace('Apartament', 'Apartment')
            
        if 'meal_plan' in X_out.columns:
            X_out['meal_plan'] = X_out['meal_plan'].replace('FB', 'HB')
            
        if 'region' in X_out.columns:
            X_out['region'] = X_out['region'].replace(self.rare_regions, 'Other')

        # --- ŻELAZNE ZABEZPIECZENIE TYPÓW DLA XGBOOSTA ---
        # Upewniamy się, że kolumny numeryczne są liczbami, a nie stringami
        num_cols = [
            'duration_days', 'days_to_departure', 'is_last_minute', 'departure_month',
            'hotel_stars', 'credibility_score', 'distance_to_beach_meters', 'distance_to_center_meters',
            'has_pool', 'has_bar', 'has_restaurant', 'is_direct_flight', 'is_transfer_included',
            'has_sea_view', 'is_wifi_free', 'is_sunbed_included'
        ]
        for col in num_cols:
            if col in X_out.columns:
                X_out[col] = pd.to_numeric(X_out[col], errors='coerce')

        return X_out