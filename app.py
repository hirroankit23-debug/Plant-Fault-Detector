import os
import time
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import FAULT_INFO, VARIABLE_NAMES, ENGINEERING_LIMITS

st.set_page_config(
    page_title="PLANT FAULT DETECTION",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.getcwd()

@st.cache_resource
def load_artifacts():
    model = joblib.load(os.path.join(BASE_DIR, "rf_model.joblib"))
    encoder = joblib.load(os.path.join(BASE_DIR, "label_encoder.joblib"))
    features = joblib.load(os.path.join(BASE_DIR, "feature_columns.joblib"))
    return model, encoder, list(features)

MODEL_TEST_ACCURACY = 99.09

try:
    model, label_encoder, feature_columns = load_artifacts()
except Exception as error:
    st.error("Model files could not be loaded. Keep app.py, rf_model.joblib, label_encoder.joblib and feature_columns.joblib in the same folder.")
    st.exception(error)
    st.stop()

def prepare_input(df):
    x = df.reindex(columns=feature_columns).copy()
    x = x.apply(pd.to_numeric, errors="coerce")
    for col in x.columns:
        median = x[col].median()
        if pd.isna(median):
            median = 0.0
        x[col] = x[col].fillna(median)
    return x

def predict_all(df):
    x = prepare_input(df)
    raw_prediction = model.predict(x)
    probabilities = model.predict_proba(x)
    labels = label_encoder.inverse_transform(raw_prediction)
    confidence = probabilities.max(axis=1) * 100
    classes = list(label_encoder.classes_)
    normal_index = classes.index("Normal") if "Normal" in classes else None

    if normal_index is None:
        fault_probability = probabilities.max(axis=1)
    else:
        fault_probabilities = np.delete(
            probabilities,
            normal_index,
            axis=1
        )
        fault_probability = fault_probabilities.max(axis=1)

    # Health is a continuous operating-condition indicator.
    # It is intentionally not equal to Normal-class probability,
    # because that value can remain near zero whenever a fault is predicted.
    health = 100.0 * (1.0 - 0.75 * fault_probability)
    health = np.clip(health, 5.0, 100.0)

    return labels, probabilities, confidence, health

def fault_details(label):
    value = FAULT_INFO.get(
        label,
        (label, "Review process conditions and investigate the event.")
    )
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return str(value[0]), str(value[1])
    return str(label), "Review process conditions and investigate the event."

def status_text(label, confidence):
    if label == "Normal":
        return "NORMAL", "🟢"
    if confidence >= 90:
        return "CRITICAL", "🔴"
    if confidence >= 70:
        return "WARNING", "🟠"
    return "ABNORMAL", "🟡"

def deviation_table(df, row_number):
    baseline_end = max(1, row_number)
    baseline = df.iloc[:baseline_end][feature_columns]
    current = df.iloc[row_number][feature_columns]
    rows = []
    for col in feature_columns:
        series = pd.to_numeric(baseline[col], errors="coerce")
        mean = series.mean()
        std = series.std()
        value = pd.to_numeric(pd.Series([current[col]]), errors="coerce").iloc[0]
        if pd.isna(std) or std < 1e-12:
            score = 0.0
        else:
            score = abs((value - mean) / std)
        rows.append({
            "Tag": col,
            "Variable": VARIABLE_NAMES.get(col, col),
            "Current Value": value,
            "Baseline Mean": mean,
            "Deviation Score": score
        })
    return pd.DataFrame(rows).sort_values("Deviation Score", ascending=False)

def limit_alarms(row):
    alarms = []
    for tag, details in ENGINEERING_LIMITS.items():
        if tag not in row.index:
            continue
        name, low, high = details
        value = pd.to_numeric(pd.Series([row[tag]]), errors="coerce").iloc[0]
        if pd.notna(value) and (value < low or value > high):
            alarms.append({
                "Variable": name,
                "Tag": tag,
                "Value": value,
                "Low Limit": low,
                "High Limit": high,
                "Status": "OUT OF LIMIT"
            })
    return pd.DataFrame(alarms)

st.markdown("""
<style>
.block-container {max-width: 1700px; padding-top: 1rem;}
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid #374151;
    padding: 14px;
    border-radius: 14px;
}
div[data-testid="stMetricLabel"] {color: #cbd5e1;}
div[data-testid="stMetricValue"] {color: #f8fafc;}
</style>
""", unsafe_allow_html=True)

def info_note(title, text):
    st.markdown(
        f'<div style="padding:10px 14px;border:1px solid #334155;'
        f'border-radius:10px;background:#0f172a;color:#cbd5e1;'
        f'margin:6px 0 14px 0;line-height:1.5;">'
        f'<b>ⓘ {title}</b><br>{text}</div>',
        unsafe_allow_html=True
    )

st.title("🏭 PLANT FAULT DETECTION DASHBOARD")
st.caption("Developed by Ankit Yadav")

top1, top2, top3, top4, top5 = st.columns(5)
top1.metric("MODEL TYPE", "Random Forest")
top2.metric("TEST ACCURACY", f"{MODEL_TEST_ACCURACY:.2f}%")
top3.metric("PROCESS TAGS", len(feature_columns))
top4.metric("FAULT CLASSES", len(label_encoder.classes_))
top5.metric("SYSTEM", "● ONLINE")

with st.expander("ⓘ Dashboard guide: what each top indicator means"):
    st.markdown(
        f"""
        **Model Type** — The algorithm used for classification.  
        **Test Accuracy ({MODEL_TEST_ACCURACY:.2f}%)** — Percentage of correct predictions on the held-out test dataset.  
        **Process Tags** — Number of input variables used by the model.  
        **Fault Classes** — Number of conditions the model can classify, including Normal.  
        **System Online** — The dashboard and model files loaded successfully; it does not confirm a live plant connection.
        """
    )

upload_col, control_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "Upload live plant historian data",
        type=["xlsx"],
        help="The app reads XLSX data row-by-row to simulate a live data stream."
    )

with control_col:
    live_mode = st.toggle("Live simulation", value=True)
    refresh_seconds = st.select_slider(
        "Refresh interval (seconds)",
        options=[1, 2, 3, 5, 10],
        value=2
    )

if uploaded_file is None:
    st.info("Upload an XLSX file containing all model tags to start the live dashboard.")
    st.stop()

try:
    process_data = pd.read_excel(uploaded_file)
except Exception as error:
    st.error("The XLSX file could not be read.")
    st.exception(error)
    st.stop()

missing = [c for c in feature_columns if c not in process_data.columns]
if missing:
    st.error("Required model tags are missing from the XLSX file.")
    st.write(missing)
    st.stop()

if len(process_data) == 0:
    st.error("The XLSX file contains no process rows.")
    st.stop()

raw_model_data = process_data[feature_columns].copy()
numeric_model_data = raw_model_data.apply(
    pd.to_numeric,
    errors="coerce"
)

missing_cells = int(numeric_model_data.isna().sum().sum())
total_cells = int(numeric_model_data.shape[0] * numeric_model_data.shape[1])

if total_cells > 0:
    data_quality = 100.0 * (1.0 - missing_cells / total_cells)
else:
    data_quality = 0.0

labels, probabilities, confidence_values, health_values = predict_all(process_data)

results = pd.DataFrame({
    "Row": np.arange(len(process_data)),
    "Prediction": labels,
    "Confidence": confidence_values,
    "Health Score": health_values
})

if "live_row" not in st.session_state:
    st.session_state.live_row = 0

c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

with c1:
    selected_row = st.slider(
        "Live operating point",
        0,
        len(process_data) - 1,
        min(st.session_state.live_row, len(process_data) - 1)
    )

with c2:
    if st.button("◀ Previous", use_container_width=True):
        selected_row = max(0, selected_row - 1)

with c3:
    if st.button("Next ▶", use_container_width=True):
        selected_row = min(len(process_data) - 1, selected_row + 1)

with c4:
    if st.button("Reset", use_container_width=True):
        selected_row = 0

st.session_state.live_row = selected_row

current = results.iloc[selected_row]
prediction = str(current["Prediction"])
confidence = float(current["Confidence"])
health = float(current["Health Score"])
fault_name, recommendation = fault_details(prediction)
status, icon = status_text(prediction, confidence)

if prediction == "Normal":
    st.success(f"{icon} {status} — Plant is operating normally")
else:
    st.error(f"{icon} {status} — {fault_name}")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("CURRENT CONDITION", prediction)
m2.metric("FAULT CONFIDENCE", f"{confidence:.1f}%")
m3.metric("PLANT HEALTH INDEX", f"{health:.1f}%")
m4.metric("DATA QUALITY", f"{data_quality:.1f}%")
m5.metric("DATA ROW", selected_row + 1)

info_note(
    "What do these current indicators mean?",
    f"<b>Current Condition:</b> {prediction} is the fault class predicted for the "
    "selected process row. "
    f"<br><b>Fault Confidence:</b> {confidence:.1f}% is the Random Forest model's "
    "probability for the predicted class at this row. It is not the same as the "
    f"overall test accuracy of {MODEL_TEST_ACCURACY:.2f}%. "
    f"<br><b>Plant Health Index:</b> {health:.1f}% is a continuous AI monitoring "
    "indicator derived from the predicted fault probability; higher is better. "
    "It is not a physical equipment-health percentage. "
    f"<br><b>Data Quality:</b> {data_quality:.1f}% is the percentage of required "
    "model-input cells that are present and numeric in the uploaded XLSX data. "
    f"<br><b>Data Row:</b> {selected_row + 1} is the current row being analyzed "
    "from the uploaded historian sequence."
)

st.markdown("### Fault diagnosis and operator response")

diagnosis_col, action_col = st.columns([1, 2])

with diagnosis_col:
    st.markdown(
        f"""
        <div style="
            min-height: 155px;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #475569;
            background-color: #111827;
        ">
        <div style="font-size: 15px; color: #94a3b8;">
        DETECTED CONDITION
        </div>
        <div style="
            font-size: 24px;
            font-weight: 700;
            margin-top: 12px;
            color: #f8fafc;
            overflow-wrap: anywhere;
        ">
        {fault_name}
        </div>
        <div style="
            margin-top: 14px;
            color: #cbd5e1;
            line-height: 1.5;
        ">
        Predicted class: {prediction}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with action_col:
    st.markdown(
        f"""
        <div style="
            min-height: 155px;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #2563eb;
            background-color: #0f172a;
        ">
        <div style="font-size: 15px; color: #93c5fd;">
        RECOMMENDED OPERATOR ACTION
        </div>
        <div style="
            font-size: 18px;
            margin-top: 12px;
            color: #f8fafc;
            line-height: 1.6;
            overflow-wrap: anywhere;
        ">
        {recommendation}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

trend_col, probability_col = st.columns([3, 2])

with trend_col:
    st.subheader("Live plant health trend")
    info_note(
        "What does this show?",
        "Plant Health Index is a continuous monitoring indicator derived from the "
        "largest predicted fault probability. Higher is better. It is not a "
        "physical equipment-health percentage. Prediction Confidence is the "
        "model probability for the selected class, not the model's overall accuracy."
    )
    start = max(0, selected_row - 300)
    trend = results.iloc[start:selected_row + 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["Row"],
        y=trend["Health Score"],
        mode="lines",
        name="Health Score"
    ))
    fig.add_trace(go.Scatter(
        x=trend["Row"],
        y=trend["Confidence"],
        mode="lines",
        name="Prediction Confidence"
    ))
    fig.add_vline(x=selected_row, line_dash="dash")
    fig.update_layout(
        height=390,
        yaxis=dict(range=[0, 100], title="Percent"),
        xaxis_title="Historian Row",
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

with probability_col:
    st.subheader("Most likely conditions")
    info_note(
        "How to read this chart",
        "The bars show the model probability for each possible condition at the "
        "current row. The probabilities across all classes add to approximately "
        "100%. A high value means the model strongly favors that class."
    )
    probability_df = pd.DataFrame({
        "Condition": label_encoder.classes_,
        "Probability": probabilities[selected_row] * 100
    }).sort_values("Probability", ascending=False).head(7)
    fig = px.bar(
        probability_df,
        x="Probability",
        y="Condition",
        orientation="h",
        text_auto=".1f"
    )
    fig.update_layout(
        height=390,
        xaxis_title="Probability (%)",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

importance_col, deviation_col = st.columns(2)

with importance_col:
    st.subheader("Variables most important to the AI model")
    info_note(
        "What does Model Importance mean?",
        "Random Forest importance is a relative score showing how much a variable "
        "helped reduce classification uncertainty across all trees and all training "
        "samples. The scores are normalized so all feature importances together "
        "sum to about 1.0. Therefore, 0.055 means about 5.5% of the model's total "
        "importance is assigned to that variable. It does not mean a 5.5% change "
        "in plant performance, and it does not prove the variable caused the "
        "current fault."
    )
    if hasattr(model, "feature_importances_"):
        importance_df = pd.DataFrame({
            "Tag": feature_columns,
            "Variable": [VARIABLE_NAMES.get(c, c) for c in feature_columns],
            "Model Importance": model.feature_importances_
        }).sort_values("Model Importance", ascending=False).head(12)
        fig = px.bar(
            importance_df.sort_values("Model Importance"),
            x="Model Importance",
            y="Variable",
            orientation="h",
            text_auto=".3f"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Global model importance: variables the Random Forest uses most across the training dataset. This is not a fault-specific causal explanation.")
    else:
        st.warning("The loaded model does not expose feature_importances_.")

with deviation_col:
    st.subheader("Variables changing most at this operating point")
    info_note(
        "What does Deviation Score mean?",
        "This is an absolute standardized difference from the earlier-data baseline. "
        "A score near 0 means the value is close to its baseline. Around 1 means "
        "roughly one baseline standard deviation away; around 2 is more unusual; "
        "3 or higher is a strong deviation. It identifies unusual variables, not "
        "proven root causes."
    )
    deviation_df = deviation_table(process_data, selected_row).head(12)
    fig = px.bar(
        deviation_df.sort_values("Deviation Score"),
        x="Deviation Score",
        y="Variable",
        orientation="h",
        text_auto=".2f"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Current deviation score: absolute change relative to the earlier data baseline. High deviation does not by itself prove causation.")

st.divider()

st.subheader("Selected process variable trends")
info_note(
    "How to use these trends",
    "Select one or more process tags to inspect their recent behavior. Different "
    "variables may have different units and ranges, so compare the trend shape "
    "carefully rather than comparing line heights directly."
)

default_tags = [
    tag for tag in ["XMEAS-7", "XMEAS-9", "XMEAS-13", "XMEAS-21", "XMV-10"]
    if tag in feature_columns
]

selected_tags = st.multiselect(
    "Choose variables",
    options=feature_columns,
    default=default_tags,
    format_func=lambda x: f"{x} — {VARIABLE_NAMES.get(x, x)}"
)

if selected_tags:
    start = max(0, selected_row - 300)
    plot_data = process_data.iloc[start:selected_row + 1].copy()
    plot_data["Row"] = np.arange(start, selected_row + 1)
    fig = go.Figure()
    for tag in selected_tags:
        fig.add_trace(go.Scatter(
            x=plot_data["Row"],
            y=plot_data[tag],
            mode="lines",
            name=VARIABLE_NAMES.get(tag, tag)
        ))
    fig.update_layout(
        height=430,
        xaxis_title="Historian Row",
        yaxis_title="Process Value"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

alarm_col, table_col = st.columns([1, 2])

with alarm_col:
    st.subheader("Engineering limit alarms")
    info_note(
        "What triggers an alarm?",
        "An alarm appears when the current value is outside the low or high "
        "engineering limit configured in config.py. These are configured screening "
        "limits and should be reviewed against approved plant operating limits."
    )
    alarms = limit_alarms(process_data.iloc[selected_row])
    if alarms.empty:
        st.success("No configured engineering limits are violated.")
    else:
        st.dataframe(alarms, use_container_width=True, hide_index=True)

with table_col:
    st.subheader("Current process measurements")
    info_note(
        "What is shown here?",
        "These are the raw values from the selected XLSX row for all model input "
        "tags. They are the measurements used by the model after numeric conversion "
        "and missing-value handling."
    )
    current_table = pd.DataFrame({
        "Tag": feature_columns,
        "Variable": [VARIABLE_NAMES.get(c, c) for c in feature_columns],
        "Current Value": [process_data.iloc[selected_row][c] for c in feature_columns]
    })
    st.dataframe(
        current_table,
        use_container_width=True,
        hide_index=True,
        height=360
    )

st.divider()

st.subheader("Download prediction results")
info_note(
    "What will be downloaded?",
    "The CSV contains one record for every row in the uploaded XLSX file. "
    "It includes the original row number, the AI-predicted operating condition, "
    "the model confidence for that prediction, and the Plant Health Index. "
    "This export can be used for reporting, trend analysis, alarm review, or "
    "comparison with plant historian events."
)

export_data = results.copy()
export_data["Row"] = export_data["Row"] + 1
export_data = export_data.rename(
    columns={
        "Row": "Source Data Row",
        "Prediction": "AI Predicted Condition",
        "Confidence": "Prediction Confidence (%)",
        "Health Score": "Plant Health Index (%)"
    }
)

csv_data = export_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download complete prediction report (CSV)",
    data=csv_data,
    file_name="Complete_prediction_report.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption(
    "The downloaded results are AI predictions and should be reviewed with "
    "process trends, operating procedures, alarms, and engineering judgment."
)

st.caption(
    "Live mode is a historian replay simulation: the XLSX rows are treated as "
    "sequential incoming data. For a real plant, replace the XLSX input with "
    "OPC UA, PI historian, SQL, MQTT or another approved plant-data connector."
)

if live_mode and selected_row < len(process_data) - 1:
    time.sleep(refresh_seconds)
    st.session_state.live_row = selected_row + 1
    st.rerun()
