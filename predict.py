import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/fault_model.pkl")

# Load one sample from Fault 5
sample = pd.read_excel("data/mode1_5_1.xlsx")

# Use same features as training
feature_cols = [c for c in sample.columns if c.startswith("XMEAS-") or c.startswith("XMV-")]

X = sample[feature_cols]

row = 1000  # Fault has developed

prediction = model.predict(X.iloc[[row]])[0]
probabilities = model.predict_proba(X.iloc[[row]])[0]

print(f"\nPredicted Condition : {prediction}")

print("\nPrediction Probability")
for cls, prob in zip(model.classes_, probabilities):
    print(f"{cls:10s} : {prob*100:.2f}%")

# Process Health Score
if prediction == "Normal":
    health_score = max(probabilities) * 100
else:
    health_score = (1 - max(probabilities)) * 100

print(f"\nProcess Health Score : {health_score:.1f}/100")

if health_score >= 80:
    status = "🟢 Healthy"
elif health_score >= 50:
    status = "🟡 Warning"
else:
    status = "🔴 Critical"

print("Status :", status)

# Top contributing variables
importance = pd.DataFrame({
    "Feature": feature_cols,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print("\nTop 5 Important Variables")
print(importance.head(5))