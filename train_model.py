import pandas as pd
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path.cwd()

DATA_FOLDER = BASE_DIR / "data"

MODEL_PATH = BASE_DIR / "rf_model.joblib"

ENCODER_PATH = BASE_DIR / "label_encoder.joblib"

FEATURE_PATH = BASE_DIR / "feature_columns.joblib"


# ============================================================
# DATA FILES
# ============================================================

files = {
    "Normal": "mode1_normal_500.xlsx"
}

for fault_number in range(1, 22):
    files[f"Fault_{fault_number}"] = f"mode1_{fault_number}_1.xlsx"


# ============================================================
# LOAD ALL EXCEL FILES
# ============================================================

all_data = []

print("\nLoading Tennessee Eastman datasets...\n")

for label, filename in files.items():

    filepath = DATA_FOLDER / filename

    print(f"Loading: {filepath}")

    if not filepath.exists():

        raise FileNotFoundError(
            f"\nFile not found:\n{filepath}\n\n"
            "Check that the filename is correct and that "
            "the file is inside the data folder."
        )

    df = pd.read_excel(filepath)

    df["Condition"] = label

    all_data.append(df)


# ============================================================
# COMBINE ALL DATA
# ============================================================

data = pd.concat(
    all_data,
    ignore_index=True
)

print(f"\nTotal rows: {len(data)}")

print(f"Total columns: {len(data.columns)}")


# ============================================================
# SELECT XMEAS AND XMV FEATURES
# ============================================================

feature_columns = [
    column
    for column in data.columns
    if (
        column.startswith("XMEAS-")
        or column.startswith("XMV-")
    )
]

if len(feature_columns) == 0:

    raise ValueError(
        "\nNo XMEAS or XMV columns were found.\n"
        "Check the column names in the Excel files."
    )

print(
    f"\nNumber of features: "
    f"{len(feature_columns)}"
)


# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================

X = data[feature_columns].copy()

y = data["Condition"].astype(str)


# ============================================================
# CHECK FOR MISSING VALUES
# ============================================================

missing_count = int(
    X.isna().sum().sum()
)

print(
    f"Missing feature values: "
    f"{missing_count}"
)

if missing_count > 0:

    X = X.apply(
        lambda column: column.fillna(
            column.median()
        )
    )


# ============================================================
# ENCODE FAULT LABELS
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print(
    f"\nNumber of classes: "
    f"{len(label_encoder.classes_)}"
)

print("\nClasses:")

for class_name in label_encoder.classes_:

    print(class_name)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print(
    f"\nTraining rows: "
    f"{len(X_train)}"
)

print(
    f"Testing rows: "
    f"{len(X_test)}"
)


# ============================================================
# TRAIN RANDOM FOREST
# ============================================================

print(
    "\nTraining Random Forest model..."
)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)


# ============================================================
# MODEL EVALUATION
# ============================================================

y_pred = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(
    f"\nModel accuracy: "
    f"{accuracy * 100:.2f}%"
)

print(
    "\nClassification report:\n"
)

print(
    classification_report(
        y_test,
        y_pred,
        labels=range(
            len(label_encoder.classes_)
        ),
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ============================================================
# SAVE MODEL FILES
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    label_encoder,
    ENCODER_PATH
)

joblib.dump(
    feature_columns,
    FEATURE_PATH
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame(
    {
        "Feature": feature_columns,
        "Importance": model.feature_importances_
    }
)

importance_df = importance_df.sort_values(
    "Importance",
    ascending=False
)

print(
    "\nTop 15 important variables:\n"
)

print(
    importance_df.head(15).to_string(
        index=False
    )
)


# ============================================================
# COMPLETED
# ============================================================

print(
    "\nTraining completed successfully."
)

print(
    f"\nModel saved at:\n"
    f"{MODEL_PATH}"
)

print(
    f"\nLabel encoder saved at:\n"
    f"{ENCODER_PATH}"
)

print(
    f"\nFeature columns saved at:\n"
    f"{FEATURE_PATH}"
)