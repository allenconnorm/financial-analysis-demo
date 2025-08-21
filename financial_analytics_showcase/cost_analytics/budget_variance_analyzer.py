'''
The purpose of this script is to analyze budget versus actual spending patterns for a municipal environmental program(s). 
It is meant to identify cost overflow, seasonal spending trends, as well as opportunities presented as a result of program
underspending.

Features of this script are:
    * Variance percentage calculation by cost center and time period
    * Budget deviations that go over or under 10% (although this metric can be changed depending on what is needed)
    * Analysis of spending patterns as they pertain to seasonality
    * Flagging of unusual spending spikes or drops
    * Exporting results in Power BI-ready formatting
    * Generating actionable recommendations for budget management

    
IMPORTANT: The data that is manipulated, analyzed, and speculated upon in this program is entirely made up for demo purposes
'''

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class BudgetVarianceAnalyzer:
    """
    
    Analyzes budget vs actual spending. Identifies variance, trend, and optimization opportunities

    """
    def __init__(self):
        self.variance_thresholds = {
            'significantly_over': -10, # >10% over budget
            'significantly_under': 25, # >25% under budget
            'slightly_over': -5, # >5% over budget
            'slightly_under': 15, # >15% under budget
        }

        self.cost_centers = {
            'AIR_QUALITY': 'Air Quality Monitoring',
            'WATER_TESTING': 'Water Quality Testing',
            'WASTE_MGMT': 'Waste Management',
            'SUSTAINABILITY': 'Sustainability Programs',
            'COMPLIANCE': 'Environmental Compliance'
        }

    
    def generate_sample_data(self) -> pd.DataFrame:
        '''My attempt at generating realistic (enough) municipal budget and spending data'''

        np.random.seed(42)

        #first 18 months of data (current fiscal year + previous fiscal year)
        start_date = datetime(2023, 7, 1) #python-speak for july 1st
        months = pd.date_range(start_date, periods=18, freq='MS')

        data = []

        for month in months:
            fiscal_year = month.year + 1 if month.month >= 7 else month.year

            for cost_center, name in self.cost_centers.items():
                #base monthly budgets, just spitballing numbers here
                base_budgets = {
                    'AIR_QUALITY': 37500, # $450k annual
                    'WATER_TESTING': 26667,  # $320K annual
                    'WASTE_MGMT': 23333,     # $280K annual
                    'SUSTAINABILITY': 18333, # $220K annual
                    'COMPLIANCE': 31667      # $380K annual
                }

                monthly_budget = base_budgets[cost_center]

                #adding some spending patterns
                seasonal_factor = 1.0

                if month.month in [10, 11]: #higher spending in Fall
                    seasonal_factor = 1.2
                elif month.month in [6]: # end of fiscal year spend-down
                    seasonal_factor = 1.4
                elif month.month in [7, 8] # lower Summer spending
                    seasonal_factor = 0.8

                #some randomness to simulate real-world variance
                variance_factor = np.random.uniform(0.7, 1.3)
                actual_spending = monthly_budget * seasonal_factor * variance_factor

                #create some significant variance that can only happen sometimes
                if np.random.random() < 0.1: #10% chance
                    if np.random.random() < 0.6: #60% over, 40% under
                        actual_spending *= np.random.uniform(1.3, 1.6) #over budget

                    else:
                        actual_spending *= np.random.uniform(0.4, 0.7) #under budget

                data.append({
                    'month': month,
                    'fiscal_year': fiscal_year,
                    'cost_center': cost_center,
                    'cost_center_name': name,
                    'monthly_budget': round(monthly_budget, 2),
                    'actual_spending': round(actual_spending, 2),
                    'quarter': f"Q{((month.month - 7) % 12 // 3) + 1}" if month.month >= 7 else f"Q{((month.month + 5) % 12 // 3) + 1}"
                })

        return pd.DataFrame(data)
    

    def calculate_variances(self, df: pd.DataFrame) -> pd.DataFrame:
        # this calculates budget variances and categorizes them

        # Calculate basic variance metrics
        df['budget_variance'] = df['actual_spending'] - df['monthly_budget']
        df['variance_pct'] = (df['budget_variance'] / df['monthly_budget'] * 100).round(2)
        df['spending_rate'] = (df['actual_spending'] / df['monthly_budget'] * 100).round(2)

        def categorize_variance(variance_pct):
            if variance_pct <= self.variance_thresholds['significantly_over']:
                return 'Significantly Overrun'
            elif variance_pct <= self.variance_thresholds['slightly_over']:
                return 'Slighty Overrun'
            elif variance_pct >= self.variance_thresholds['significantly_under']:
                return 'Significantly Underspending'
            elif variance_pct >= self.variance_thresholds['slightly_under']:
                return 'Slightly Underspending'
            else:
                return 'Within Target'
            
        df['variance_category'] = df['variance_pct'].apply(categorize_variance)

        #severity flags
        df['needs attention'] = df['variance_category'].isin(['Significantly Overrun', 'Significantly Underspending'])
        
        return df
    
    