import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & PREMIUM UI CSS
# ==========================================
st.set_page_config(page_title="Auto Command Center", layout="wide", page_icon="️")

st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #ffffff; font-weight: 700; margin-bottom: 5px; }
    .subtitle { color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px; }
    h2, h3 { color: #e2e8f0; font-weight: 600; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
    .sidebar-header { text-align: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #334155; }
    .sidebar-header h2 { color: #38bdf8; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; margin: 0; font-weight: 800; }
    .filter-group { background: rgba(30, 41, 59, 0.4); border: 1px solid #334155; border-radius: 10px; padding: 15px; margin-bottom: 15px; transition: all 0.3s ease; }
    .filter-group:hover { border-color: #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.1); }
    .record-count { text-align: center; background: linear-gradient(90deg, #0f172a, #1e293b); border: 1px solid #38bdf8; color: #38bdf8; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 1.1rem; margin-top: 20px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); letter-spacing: 1px; }
    
    /* KPI Cards */
    div[data-testid="stMetric"] { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div[data-testid="stMetricLabel"] { color: #94a3b8; font-size: 0.9rem; }
    div[data-testid="stMetricValue"] { color: #ffffff; font-size: 1.8rem; font-weight: 700; }
    
    /* Insight Cards */
    .insight-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-left: 4px solid #38bdf8; padding: 15px 20px; border-radius: 8px; margin-bottom: 10px; }
    .insight-title { font-weight: 600; color: #fbbf24; font-size: 0.9rem; text-transform: uppercase; }
    .insight-text { color: #e2e8f0; font-size: 1rem; margin-top: 5px; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING
# ==========================================
@st.cache_data
def load_data(file_source):
    df = pd.read_excel(file_source)
    df['Service_Date'] = pd.to_datetime(df['Service_Date'])
    numeric_cols = ['Vehicle_Age_Years', 'Vehicle_Mileage_KM', 'Parts_Cost', 'Labour_Cost', 'GST_Amount', 'Discount_Amount', 'Bill_Amount', 'Customer_Rating']
    for col in numeric_cols:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Gross_Profit'] = df['Bill_Amount'] - df['Parts_Cost'] - df['Labour_Cost']
    df['Month_Year'] = df['Service_Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Service_Date'].dt.to_period('Q').astype(str)
    return df

# Smart Loading Logic
try:
    df = load_data('Automotive_After_Sales_Service_Analytics_Dataset(2).xlsx')
except:
    uploaded_file = st.file_uploader("Upload Dataset (.xlsx)", type=["xlsx"])
    if uploaded_file: df = load_data(uploaded_file)
    else: st.stop()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>⚡ Dashboard Filters </h2><p style="color: #64748b; font-size: 0.75rem; margin-top: 5px;">ADVANCED TELEMETRY FILTERS</p></div>', unsafe_allow_html=True)
    
    
    st.markdown("️ **Timeframe**")
    date_range = st.date_input("Select Date Range", value=(df['Service_Date'].min().date(), df['Service_Date'].max().date()), min_value=df['Service_Date'].min().date(), max_value=df['Service_Date'].max().date())
    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown("📍 **Location & Center**")
    cities = st.multiselect("City", options=sorted(df['City'].unique()), default=sorted(df['City'].unique())[:5])
    center_types = st.multiselect("Service Center", options=sorted(df['Service_Center_Type'].unique()), default=sorted(df['Service_Center_Type'].unique()))
    st.markdown('</div>', unsafe_allow_html=True)

   
    st.markdown("🚗 **Vehicle & Service**")
    brands = st.multiselect("Brand", options=sorted(df['Brand'].unique()), default=sorted(df['Brand'].unique())[:3])
    service_types = st.multiselect("Service Type", options=sorted(df['Service_Type'].unique()), default=sorted(df['Service_Type'].unique()))
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Reset All Filters", use_container_width=True): st.rerun()

    # Filtering Logic
    start_date, end_date = date_range
    df_filtered = df[
        (df['Service_Date'].dt.date >= start_date) & (df['Service_Date'].dt.date <= end_date) &
        (df['Brand'].isin(brands) if brands else True) & 
        (df['City'].isin(cities) if cities else True) & 
        (df['Service_Type'].isin(service_types) if service_types else True) &
        (df['Service_Center_Type'].isin(center_types) if center_types else True)
    ]
    
    st.markdown(f'<div class="record-count">📊 {len(df_filtered):,} Records Matched</div>', unsafe_allow_html=True)

# ==========================================
# 4. HEADER & KPIs
# ==========================================
st.markdown("<h1>🚗 Automotive After-Sales Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Service • Revenue • Customers • Warranty • Vehicle Performance</p>", unsafe_allow_html=True)

total_revenue = df_filtered['Bill_Amount'].sum()
avg_bill = df_filtered['Bill_Amount'].mean()
total_services = len(df_filtered)
customers_served = df_filtered['Customer_ID'].nunique()
avg_rating = df_filtered['Customer_Rating'].mean()
repeat_rate = (df_filtered['Repeat_Customer'] == 'Yes').mean() * 100
warranty_rate = (df_filtered['Warranty_Claim'] == 'Yes').mean() * 100
total_profit = df_filtered['Gross_Profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"₹{total_revenue/100000:,.1f} L")
col2.metric("🧾 Average Bill", f"₹{avg_bill:,.0f}")
col3.metric("🔧 Total Services", f"{total_services:,}")
col4.metric("👥 Customers Served", f"{customers_served:,}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("⭐ Avg Rating", f"{avg_rating:.2f}/5")
col6.metric("🔄 Repeat Rate", f"{repeat_rate:.1f}%")
col7.metric("🛡️ Warranty Rate", f"{warranty_rate:.1f}%")
col8.metric("💹 Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# ==========================================
# 5. TABS & CHARTS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🧠 Decision Intelligence", "🔬 Deep Analytics", " Raw Data"])

with tab1:
    col9, col10 = st.columns([2, 1])
    with col9:
        st.markdown("### 📈 Revenue Trend (Monthly)")
        revenue_trend = df_filtered.groupby('Month_Year')['Bill_Amount'].sum().reset_index()
        fig_trend = px.area(revenue_trend, x='Month_Year', y='Bill_Amount', template="plotly_dark", color_discrete_sequence=["#38bdf8"])
        fig_trend.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
        st.plotly_chart(fig_trend, use_container_width=True)
    with col10:
        st.markdown("### 🍩 Service Type Mix")
        service_dist = df_filtered['Service_Type'].value_counts().reset_index()
        service_dist.columns = ['Service_Type', 'Count']
        fig_pie = px.pie(service_dist, values='Count', names='Service_Type', template="plotly_dark", hole=0.6, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pie.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"))
        st.plotly_chart(fig_pie, use_container_width=True)

    col11, col12 = st.columns(2)
    with col11:
        st.markdown("### 🏆 Top Brands by Revenue")
        brand_perf = df_filtered.groupby('Brand')['Bill_Amount'].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_brand = px.bar(brand_perf, x='Bill_Amount', y='Brand', orientation='h', template="plotly_dark", color_discrete_sequence=["#818cf8"])
        fig_brand.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_brand, use_container_width=True)
    with col12:
        st.markdown("### 🏙️ Top Cities by Revenue")
        city_perf = df_filtered.groupby('City')['Bill_Amount'].sum().sort_values(ascending=True).tail(10).reset_index()
        fig_city = px.bar(city_perf, x='Bill_Amount', y='City', orientation='h', template="plotly_dark", color_discrete_sequence=["#34d399"])
        fig_city.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_city, use_container_width=True)

with tab2:
    st.markdown("### 🧠 Decision Intelligence - Auto Insights")
    best_city = df_filtered.groupby('City')['Bill_Amount'].sum().idxmax() if not df_filtered.empty else "N/A"
    highest_rated_brand = df_filtered.groupby('Brand')['Customer_Rating'].mean().idxmax() if not df_filtered.empty else "N/A"
    riskiest_brand = df_filtered[df_filtered['Warranty_Claim']=='Yes'].groupby('Brand').size().idxmax() if (df_filtered['Warranty_Claim']=='Yes').any() else "N/A"
    most_profitable_service = df_filtered.groupby('Service_Type')['Gross_Profit'].mean().idxmax() if not df_filtered.empty else "N/A"

    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #00ff88;"><div class="insight-title">🏆 Revenue Champion</div><div class="insight-text"><b>{best_city}</b> leads with ₹{df_filtered[df_filtered['City']==best_city]['Bill_Amount'].sum()/100000:.1f}L revenue</div></div>
        <div class="insight-card" style="border-left-color: #38bdf8;"><div class="insight-title">⭐ CX Leader</div><div class="insight-text"><b>{highest_rated_brand}</b> has highest avg rating ({df_filtered[df_filtered['Brand']==highest_rated_brand]['Customer_Rating'].mean():.2f})</div></div>
        """, unsafe_allow_html=True)
    with col_ins2:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #fbbf24;"><div class="insight-title">️ Warranty Risk Alert</div><div class="insight-text"><b>{riskiest_brand}</b> has highest warranty claims - investigate quality</div></div>
        <div class="insight-card" style="border-left-color: #a855f7;"><div class="insight-title">💰 Margin Optimizer</div><div class="insight-text"><b>{most_profitable_service}</b> yields highest profit per ticket</div></div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔥 Brand × Service Revenue Matrix")
    matrix_data = df_filtered.pivot_table(values='Bill_Amount', index='Brand', columns='Service_Type', aggfunc='sum', fill_value=0)
    fig_matrix = px.imshow(matrix_data, aspect="auto", color_continuous_scale=[[0, "#0f172a"], [0.5, "#005f73"], [1, "#00d4ff"]], title="Revenue Concentration Heatmap")
    fig_matrix.update_layout(height=450, paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"))
    st.plotly_chart(fig_matrix, use_container_width=True)

    st.markdown("---")
    st.markdown("###  Customer Retention Map (Rating vs Repeat Rate)")
    retention_data = df_filtered.groupby('Brand').agg(Avg_Rating=('Customer_Rating', 'mean'), Repeat_Rate=('Repeat_Customer', lambda x: (x=='Yes').mean()*100), Total_Revenue=('Bill_Amount', 'sum')).reset_index()
    fig_retention = px.scatter(retention_data, x="Avg_Rating", y="Repeat_Rate", size="Total_Revenue", color="Brand", hover_name="Brand", size_max=60, title="Brand Performance: Rating vs Retention (Bubble = Revenue)", template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Set2)
    fig_retention.update_layout(height=450, paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(title="Avg Customer Rating", showgrid=True, gridcolor='#1e293b'), yaxis=dict(title="Repeat Customer Rate (%)", showgrid=True, gridcolor='#1e293b'))
    st.plotly_chart(fig_retention, use_container_width=True)

with tab3:
    st.markdown("### 📊 Quarterly Performance Trend")
    quarterly = df_filtered.groupby('Quarter')['Bill_Amount'].sum().reset_index()
    fig_quarter = px.bar(quarterly, x='Quarter', y='Bill_Amount', template="plotly_dark", color_discrete_sequence=["#fbbf24"])
    fig_quarter.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
    st.plotly_chart(fig_quarter, use_container_width=True)

    col_pay, col_center = st.columns(2)
    with col_pay:
        st.markdown("### 💳 Payment Mode Distribution")
        payment_data = df_filtered.groupby('Payment_Mode')['Bill_Amount'].sum().reset_index()
        fig_payment = px.pie(payment_data, values='Bill_Amount', names='Payment_Mode', template="plotly_dark", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_payment.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"))
        st.plotly_chart(fig_payment, use_container_width=True)
    with col_center:
        st.markdown("### 🏢 Service Center Type Performance")
        center_data = df_filtered.groupby('Service_Center_Type')['Bill_Amount'].sum().reset_index()
        fig_center = px.bar(center_data, x='Service_Center_Type', y='Bill_Amount', template="plotly_dark", color_discrete_sequence=["#34d399"])
        fig_center.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
        st.plotly_chart(fig_center, use_container_width=True)

    col_war, col_age = st.columns(2)
    with col_war:
        st.markdown("### 🛡️ Warranty Exposure by Brand")
        warranty_data = df_filtered[df_filtered['Warranty_Claim']=='Yes'].groupby('Brand').size().reset_index(name='Claims').sort_values('Claims', ascending=True)
        if not warranty_data.empty:
            fig_war = px.bar(warranty_data, x='Claims', y='Brand', orientation='h', template="plotly_dark", color='Claims', color_continuous_scale='Reds')
            fig_war.update_layout(height=350, paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), showlegend=False)
            st.plotly_chart(fig_war, use_container_width=True)
        else: st.info("No warranty claims in selected data.")
    with col_age:
        st.markdown("### 📅 Vehicle Age vs Revenue")
        age_bins = pd.cut(df_filtered['Vehicle_Age_Years'], bins=[0, 2, 5, 8, 11], labels=['0-2 yrs', '3-5 yrs', '6-8 yrs', '9-11 yrs'])
        age_data = df_filtered.groupby(age_bins)['Bill_Amount'].sum().reset_index()
        age_data.columns = ['Age_Group', 'Revenue']
        fig_age = px.bar(age_data, x='Age_Group', y='Revenue', template="plotly_dark", color_discrete_sequence=["#a855f7"])
        fig_age.update_layout(paper_bgcolor='#0b1120', plot_bgcolor='#0b1120', font=dict(color="#e2e8f0"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
        st.plotly_chart(fig_age, use_container_width=True)

with tab4:
    st.markdown("### 📋 Raw Service Data")
    st.dataframe(df_filtered, use_container_width=True, height=500)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>AXION COMMAND CENTER v3.0 • Powered by Streamlit & Plotly • Data updated in real-time</p>", unsafe_allow_html=True)