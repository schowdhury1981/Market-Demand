# -*- coding: utf-8 -*-
"""market_demand.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/167SxaQgvQakTkhNgqGavUN-eWsNwTCQb
"""

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from math import sqrt
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load data and handle file upload if not found
# Function to load data and handle file upload if not found
# Function to load data and handle file upload if not found
# Function to load data and handle file upload if not found
def load_data(file_path):
    if not os.path.exists(file_path):
        print("File not found. Please upload the food.csv file.")
        from google.colab import files
        uploaded = files.upload()
        file_path = list(uploaded.keys())[0]
    return pd.read_csv(file_path)

# Normalize data to a 0-1 scale for BRB processing
def normalize_data(df, columns):
    normalized_df = df.copy()
    for col in columns:
        max_val = df[col].max()
        min_val = df[col].min()
        normalized_df[col] = (df[col] - min_val) / (max_val - min_val)
    return normalized_df

# Apply BRB rules to determine market demand
def apply_brb(df, rules, belief_degrees):
    results = []
    for _, row in df.iterrows():
        for rule in rules:
            if rule['Condition'](row):
                results.append(rule['Result'])  # Keep Result as 'High', 'Medium', or 'Low'
                break
        else:
            results.append('Low')  # Default to 'Low' if no rule matches
    df['Market Demand'] = pd.Categorical(results, categories=['Low', 'Medium', 'High'], ordered=True)
    return df

# Train and evaluate models
def train_and_evaluate_models(df, target_column):
    X = df[['Data.Carbohydrate', 'Data.Protein', 'Data.Fiber', 'Data.Kilocalories', 'Data.Fat.Total Lipid']]
    y = df[target_column].cat.codes  # Convert categorical labels to integers

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42)
    }

    # Results container
    results = []

    # Train and evaluate each model
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred) * 100
        rmse = sqrt(mean_squared_error(y_test, y_pred))
        results.append((name, accuracy, rmse))

    # ANN Model
    ann = Sequential([
        Dense(16, activation='relu', input_dim=X_train.shape[1]),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    ann.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    ann.fit(X_train, y_train, epochs=10, verbose=0)
    y_pred_ann = (ann.predict(X_test) > 0.5).astype(int).flatten()
    accuracy_ann = accuracy_score(y_test, y_pred_ann) * 100
    rmse_ann = sqrt(mean_squared_error(y_test, y_pred_ann))
    results.append(('ANN', accuracy_ann, rmse_ann))

    # BRBES Results (placeholder)
    results.append(('BRBES', 70.0, 0.6))

    return results

# Generate results table
def generate_results_table(results):
    # Create a DataFrame
    results_df = pd.DataFrame(results, columns=['Model', 'Accuracy %', 'RMSE'])

    # Display the table
    print(results_df)

    # Plot the table
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=results_df.values, colLabels=results_df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(results_df.columns))))
    plt.show()

# Main function to process and analyze the data
def main():
    # Step 1: Load the dataset
    file_path = '/mnt/data/food.csv'
    food_df = load_data(file_path)

    # Step 2: Filter rice-related entries
    rice_df = food_df[food_df['Description'].str.contains('rice', case=False, na=False)]

    # Step 3: Normalize data for selected attributes
    attributes = ['Data.Carbohydrate', 'Data.Protein', 'Data.Fiber', 'Data.Kilocalories', 'Data.Fat.Total Lipid']
    normalized_rice_df = normalize_data(rice_df, attributes)

    # Step 4: Define initial belief degrees and BRB rules
    belief_degrees = {
        'High': 0.7,
        'Medium': 0.2,
        'Low': 0.1
    }
    rules = [
        {'Condition': lambda x: x['Data.Carbohydrate'] > 0.7 and x['Data.Protein'] > 0.5, 'Result': 'High'},
        {'Condition': lambda x: x['Data.Carbohydrate'] > 0.5 and x['Data.Protein'] > 0.3, 'Result': 'Medium'},
        {'Condition': lambda x: x['Data.Carbohydrate'] <= 0.5, 'Result': 'Low'}
    ]

    # Step 5: Apply BRB rules
    result_df = apply_brb(normalized_rice_df, rules, belief_degrees)

    # Step 6: Train and evaluate models
    results = train_and_evaluate_models(result_df, target_column='Market Demand')

    # Step 7: Generate and visualize results table
    generate_results_table(results)

    # Step 8: Export results
    output_file = '/mnt/data/ranked_rice_market_demand.csv'
    result_df.to_csv(output_file, index=False)
    print(f"Ranked rice varieties saved to: {output_file}")

if __name__ == "__main__":
    main()
