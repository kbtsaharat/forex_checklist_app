import streamlit as st
import json
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def load_data():
    try:
        with open('checklist_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_data(data):
    with open('checklist_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# CSS Styling
st.markdown("""
    <style>
    .month-header {
        font-size: 24px;
        margin-top: 30px;
        margin-bottom: 10px;
        font-weight: bold;
        border-bottom: 2px solid #eee;
    }
    .day-card {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    .today {
        background-color: #e0f7e9 !important;
    }
    .day-header {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 8px;
    }
    .empty-plan {
        color: #999;
        font-style: italic;
    }
    .result-win {
        color: green;
        font-weight: bold;
    }
    .result-loss {
        color: red;
        font-weight: bold;
    }
    .result-breakeven {
        color: gray;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📅 Forex Trading Planner")

data = load_data()

today = datetime.today()
selected_month = today.month
selected_year = today.year

# Always show only today's date
dates = [today]

# Month Header
st.markdown(f"<div class='month-header'>{today.strftime('%B %Y')}</div>", unsafe_allow_html=True)

# Modify the logic to allow adding multiple plans per day
# Add an input for the plan name
# Update the result calculation logic

for date in dates:
    date_str = date.strftime('%Y-%m-%d')
    day_plans = data.get(date_str, {}).get('trades', [])

    # Card Classes
    card_class = "day-card"
    if date.date() == today.date():
        card_class += " today"

    # Day Card
    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    st.markdown(f"<div class='day-header'>{date.strftime('%A, %d %B')}</div>", unsafe_allow_html=True)

    # Plan Details
    if day_plans:
        for trade in day_plans:
            # Enhanced Plan Details
            direction_icon = "🟢 Buy" if trade.get('direction') == "Buy" else "🔴 Sell"
            tp = trade.get('tp', 0)
            sl = trade.get('sl', 0)
            notes = trade.get('note', '')

            # Calculate result dynamically
            if tp - sl > 10:
                result = "Win"
                result_class = "result-win"
            elif sl - tp > 10:
                result = "Loss"
                result_class = "result-loss"
            else:
                result = "Breakeven"
                result_class = "result-breakeven"

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    background-color: #ffffff;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                ">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">
                        Plan Name: {trade.get('name', 'Unnamed Plan')}
                    </div>
                    <div style="font-size: 14px; margin-bottom: 5px;">
                        <span style="font-weight: bold;">Direction:</span> {direction_icon}
                    </div>
                    <div style="font-size: 14px; margin-bottom: 5px;">
                        <span style="font-weight: bold;">TP:</span> {tp} | <span style="font-weight: bold;">SL:</span> {sl}
                    </div>
                    <div style="font-size: 14px; margin-bottom: 5px; color: {result_class}; font-weight: bold;">
                        Result: {result}
                    </div>
                    <div style="font-size: 14px; margin-bottom: 5px;">
                        <span style="font-weight: bold;">Notes:</span> {notes if notes else 'No notes provided'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='empty-plan'>No trading plans yet</div>", unsafe_allow_html=True)

    # Expander for adding/editing plans
    with st.expander("➕ Add/Edit Plans"):
        plan_name = st.text_input(f"Plan Name for {date_str}", key=f"name_{date_str}")
        direction = st.selectbox(f"Direction for {date_str}", ["", "Buy", "Sell"], key=f"dir_{date_str}")
        tp = st.number_input(f"Take Profit (TP) for {date_str}", key=f"tp_{date_str}")
        sl = st.number_input(f"Stop Loss (SL) for {date_str}", key=f"sl_{date_str}")
        note = st.text_area(f"Notes for {date_str}", height=100, key=f"note_{date_str}")

        if st.button(f"💾 Save Plan for {date_str}", key=f"save_{date_str}"):
            # Calculate result dynamically before saving
            if tp - sl > 10:
                result = "Win"
            elif sl - tp > 10:
                result = "Loss"
            else:
                result = "Breakeven"

            new_trade = {
                "name": plan_name,
                "direction": direction,
                "tp": tp,
                "sl": sl,
                "result": result,
                "note": note
            }

            if date_str not in data:
                data[date_str] = {"trades": []}

            data[date_str]["trades"].append(new_trade)
            save_data(data)
            st.success(f"Plan for {date_str} saved!")

    st.markdown("</div>", unsafe_allow_html=True)

# Update the Last 5 Days Trading History to remove 'Net Result:' text and add conditional coloring for results

st.header("📅 Last 5 Days Trading History")

last_5_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

for date_str in last_5_days:
    day_plan = data.get(date_str, {})
    trades = day_plan.get('trades', [])

    if trades:
        # Calculate net result for the day
        net_result = sum(trade.get('tp', 0) - trade.get('sl', 0) for trade in trades)
        result_status = "Win" if net_result > 0 else "Loss" if net_result < 0 else "Breakeven"

        # Set color based on result status
        result_color = "green" if result_status == "Win" else "red" if result_status == "Loss" else "gray"

        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                background-color: #ffffff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
            ">
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">{date_str}</div>
                <div style="font-size: 18px; font-weight: bold; color: {result_color};">{net_result:.2f} ({result_status})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                background-color: #ffffff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
            ">
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">{date_str}</div>
                <div style="font-size: 18px; font-weight: bold; color: gray;">No Data</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
