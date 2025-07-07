import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Energy Consumption Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: black;
    }
    .consumption-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🏠 Energy Consumption Calculator</h1>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Habitation type
    habitation_type = st.selectbox(
        "Select your habitation type:",
        ["Flat", "House"],
        index=0
    )
    
    # BHK type
    bhk_type = st.selectbox(
        f"Select your {habitation_type.lower()} type:",
        ["1BHK", "2BHK", "3BHK"],
        index=1
    )
    
    st.markdown("---")
    st.subheader("🏠 Appliances")
    
    # Appliances
    ac_present = st.checkbox("Air Conditioner (AC)", value=False)
    fridge_present = st.checkbox("Refrigerator", value=True)
    washing_machine_present = st.checkbox("Washing Machine", value=True)
    
    st.markdown("---")
    
    # Monthly days for calculation
    days_in_month = st.slider("Days in month for calculation:", 28, 31, 30)

# Energy calculation function
def calculate_energy(habitation_type, bhk_type, ac_present, fridge_present, washing_machine_present, days_in_month):
    cal_energy = 0
    breakdown = {}
    
    # Base consumption based on BHK type
    if bhk_type.lower() == "1bhk":
        base_consumption = (2 * 0.4 + 2 * 0.8) * days_in_month
        breakdown["Lighting & Basic"] = base_consumption
    elif bhk_type.lower() == "2bhk":
        base_consumption = (3 * 0.4 + 3 * 0.8) * days_in_month
        breakdown["Lighting & Basic"] = base_consumption
    elif bhk_type.lower() == "3bhk":
        base_consumption = (4 * 0.4 + 4 * 0.8) * days_in_month
        breakdown["Lighting & Basic"] = base_consumption
    
    cal_energy += base_consumption
    
    # Appliance consumption
    if ac_present:
        ac_consumption = 3 * days_in_month
        cal_energy += ac_consumption
        breakdown["Air Conditioner"] = ac_consumption
    
    if fridge_present:
        fridge_consumption = 4 * days_in_month
        cal_energy += fridge_consumption
        breakdown["Refrigerator"] = fridge_consumption
    
    if washing_machine_present:
        washing_consumption = 2 * days_in_month
        cal_energy += washing_consumption
        breakdown["Washing Machine"] = washing_consumption
    
    return cal_energy, breakdown

# Calculate energy consumption
total_energy, energy_breakdown = calculate_energy(
    habitation_type, bhk_type, ac_present, fridge_present, washing_machine_present, days_in_month
)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Display total consumption
    st.markdown(f"""
    <div class="consumption-card">
        <h2>🌍 Total Monthly Energy Consumption</h2>
        <h1>{total_energy:.2f} kg CO₂ equivalent</h1>
        <p>For your {bhk_type} {habitation_type.lower()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Energy breakdown pie chart
    if energy_breakdown:
        fig_pie = px.pie(
            values=list(energy_breakdown.values()),
            names=list(energy_breakdown.keys()),
            title="Energy Consumption Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            title_font_size=20,
            title_x=0.5,
            font=dict(size=14),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Summary metrics
    st.subheader("📊 Summary")
    
    # Individual metrics
    for appliance, consumption in energy_breakdown.items():
        st.metric(
            label=appliance,
            value=f"{consumption:.1f} kg CO₂",
            delta=f"{(consumption/total_energy)*100:.1f}%"
        )
    
    # Comparison with average
    st.markdown("---")
    st.subheader("📈 Comparison")
    
    # Average consumption estimates
    avg_consumption = {
        "1bhk": 150,
        "2bhk": 200,
        "3bhk": 250
    }
    
    avg_for_type = avg_consumption.get(bhk_type.lower(), 200)
    difference = total_energy - avg_for_type
    
    if difference > 0:
        st.error(f"📈 {difference:.1f} kg CO₂ above average")
    else:
        st.success(f"📉 {abs(difference):.1f} kg CO₂ below average")

# Detailed breakdown section
st.markdown("---")
st.subheader("🔍 Detailed Analysis")

# Create comparison chart
comparison_data = pd.DataFrame({
    'Category': list(energy_breakdown.keys()),
    'Your Consumption': list(energy_breakdown.values()),
    'Efficient Range': [val * 0.8 for val in energy_breakdown.values()],
    'High Range': [val * 1.3 for val in energy_breakdown.values()]
})

fig_comparison = go.Figure()

fig_comparison.add_trace(go.Bar(
    x=comparison_data['Category'],
    y=comparison_data['Your Consumption'],
    name='Your Consumption',
    marker_color='#FF6B6B'
))

fig_comparison.add_trace(go.Bar(
    x=comparison_data['Category'],
    y=comparison_data['Efficient Range'],
    name='Efficient Range',
    marker_color='#4ECDC4'
))

fig_comparison.add_trace(go.Bar(
    x=comparison_data['Category'],
    y=comparison_data['High Range'],
    name='High Consumption',
    marker_color='#FFE66D'
))

fig_comparison.update_layout(
    title='Energy Consumption Comparison',
    xaxis_title='Appliance Category',
    yaxis_title='Monthly Consumption (kg CO₂)',
    barmode='group',
    height=400,
    title_font_size=20,
    title_x=0.5
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Tips section
st.markdown("---")
st.subheader("💡 Energy Saving Tips")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **🔌 Electrical Appliances:**
    - Use LED bulbs instead of incandescent
    - Unplug devices when not in use
    - Use energy-efficient appliances
    - Set AC temperature to 24°C or higher
    """)

with tips_col2:
    st.markdown("""
    **🏠 Home Optimization:**
    - Improve insulation
    - Use natural lighting during day
    - Regular maintenance of appliances
    - Use timers for water heaters
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🌱 Calculate your carbon footprint and contribute to a greener future!</p>
    <p><em>Energy consumption values are estimates based on typical usage patterns.</em></p>
</div>
""", unsafe_allow_html=True)