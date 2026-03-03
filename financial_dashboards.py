"""
Advanced Financial Dashboards - P&L, Budget, Analysis
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from supabase_client import (
    get_revenue_accounts,
    get_financial_costs,
    get_financial_accounts,
    get_room_forecast
)


def calculate_pl_statement(hotel_name: str, month: int = None, year: int = None) -> dict:
    """Calculate P&L statement for a hotel"""
    
    revenue_data = get_revenue_accounts(hotel_name)
    cost_data = get_financial_costs(hotel_name)
    
    if month and year:
        revenue_data = [r for r in revenue_data if r.get('month') == month and r.get('year') == year]
        cost_data = [c for c in cost_data if c.get('period') == f"{month:02d}/{year}"]
    
    # Calculate totals
    total_revenue = sum(r.get('gross', 0) for r in revenue_data if r.get('gross'))
    total_costs = sum(c.get('amount', 0) for c in cost_data if c.get('amount'))
    gross_profit = total_revenue - total_costs
    profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_costs': total_costs,
        'gross_profit': gross_profit,
        'profit_margin': profit_margin,
        'revenue_data': revenue_data,
        'cost_data': cost_data
    }


def show_pl_dashboard(hotel_name: str):
    """Display P&L Statement Dashboard"""
    st.subheader("📊 Profit & Loss Statement")
    
    col1, col2, col3, col4 = st.columns(4)
    
    pl_data = calculate_pl_statement(hotel_name)
    
    with col1:
        st.metric(
            "💰 Total Revenue",
            f"€{pl_data['total_revenue']:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "💸 Total Costs",
            f"€{pl_data['total_costs']:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "📈 Gross Profit",
            f"€{pl_data['gross_profit']:,.2f}",
            delta=f"{pl_data['profit_margin']:.1f}%"
        )
    
    with col4:
        st.metric(
            "📊 Profit Margin",
            f"{pl_data['profit_margin']:.1f}%",
            delta=None
        )
    
    st.divider()
    
    # P&L Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**P&L Breakdown**")
        pl_fig = go.Figure(data=[
            go.Bar(name='Revenue', x=['Total'], y=[pl_data['total_revenue']], marker_color='#00D96F'),
            go.Bar(name='Costs', x=['Total'], y=[-pl_data['total_costs']], marker_color='#FF4757'),
            go.Bar(name='Profit', x=['Total'], y=[pl_data['gross_profit']], marker_color='#0066CC')
        ])
        pl_fig.update_layout(barmode='relative', height=400)
        st.plotly_chart(pl_fig, use_container_width=True)
    
    with col2:
        st.write("**Income Statement**")
        # Create simple P&L table visualization
        pl_items = [
            {'Item': 'Gross Revenue', 'Amount': pl_data['total_revenue']},
            {'Item': 'Less: Operating Costs', 'Amount': -pl_data['total_costs']},
            {'Item': 'Net Profit', 'Amount': pl_data['gross_profit']}
        ]
        df_pl = pd.DataFrame(pl_items)
        
        fig_table = go.Figure(data=[go.Table(
            header=dict(values=['<b>Item</b>', '<b>Amount (€)</b>'],
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[df_pl['Item'], df_pl['Amount'].apply(lambda x: f'{x:,.2f}')],
                      fill_color='lavender',
                      align='left')
        )])
        fig_table.update_layout(height=400)
        st.plotly_chart(fig_table, use_container_width=True)


def show_budget_vs_actual(hotel_name: str):
    """Display Budget vs Actual Dashboard"""
    st.subheader("📋 Budget vs Actual Analysis")
    
    # Load revenue data from database
    revenue_data = get_revenue_accounts(hotel_name)
    
    if not revenue_data:
        st.info("📊 No revenue data available. Upload financial reports to view comparisons.")
        return
    
    st.warning("⚠️ Budget comparison feature will be available once budget files are uploaded to Supabase.")


def show_revenue_breakdown(hotel_name: str):
    """Display Revenue Breakdown Analysis"""
    st.subheader("💰 Revenue Breakdown by Source")
    
    revenue_data = get_revenue_accounts(hotel_name)
    
    if not revenue_data:
        st.info("No revenue data available")
        return
    
    df_revenue = pd.DataFrame(revenue_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart by account
        revenue_by_account = df_revenue.groupby('account_name')['gross'].sum().sort_values(ascending=False)
        
        fig_pie = px.pie(
            values=revenue_by_account.values,
            names=revenue_by_account.index,
            title='Revenue by Source'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Monthly trend
        monthly_revenue = df_revenue.groupby('month')['gross'].sum()
        
        fig_line = px.line(
            x=monthly_revenue.index,
            y=monthly_revenue.values,
            markers=True,
            title='Monthly Revenue Trend',
            labels={'x': 'Month', 'y': 'Revenue (€)'}
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)


def show_cost_analysis(hotel_name: str):
    """Display Cost Analysis Dashboard"""
    st.subheader("💼 Cost Analysis & Breakdown")
    
    cost_data = get_financial_costs(hotel_name)
    
    if not cost_data:
        st.info("No cost data available")
        return
    
    df_costs = pd.DataFrame(cost_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Costs by type
        costs_by_type = df_costs.groupby('cost_type')['amount'].sum().sort_values(ascending=False)
        
        fig_bar = px.bar(
            x=costs_by_type.index,
            y=costs_by_type.values,
            title='Costs by Category',
            labels={'x': 'Cost Type', 'y': 'Amount (€)'},
            color=costs_by_type.values,
            color_continuous_scale='Reds'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart
        fig_pie = px.pie(
            values=costs_by_type.values,
            names=costs_by_type.index,
            title='Cost Distribution'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)


def show_kpi_dashboard(hotel_name: str):
    """Display KPI Dashboard"""
    st.subheader("🎯 Key Performance Indicators")
    
    pl_data = calculate_pl_statement(hotel_name)
    revenue_data = get_revenue_accounts(hotel_name)
    cost_data = get_financial_costs(hotel_name)
    forecast_data = get_room_forecast(hotel_name)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_daily_revenue = pl_data['total_revenue'] / 30 if pl_data['total_revenue'] else 0
        st.metric(
            "📅 Avg Daily Revenue",
            f"€{avg_daily_revenue:,.2f}"
        )
    
    with col2:
        avg_daily_cost = pl_data['total_costs'] / 30 if pl_data['total_costs'] else 0
        st.metric(
            "📅 Avg Daily Cost",
            f"€{avg_daily_cost:,.2f}"
        )
    
    with col3:
        occupancy = len(forecast_data) / 30 * 100 if forecast_data else 0
        st.metric(
            "🛏️ Occupancy Rate",
            f"{occupancy:.1f}%"
        )
    
    with col4:
        revenue_per_cost = (pl_data['total_revenue'] / pl_data['total_costs']) if pl_data['total_costs'] > 0 else 0
        st.metric(
            "📊 Revenue/Cost Ratio",
            f"{revenue_per_cost:.2f}x"
        )


def show_multi_hotel_comparison(hotels: list):
    """Display Multi-Hotel Comparison (for Group Director)"""
    st.subheader("🏢 Multi-Hotel Comparison")
    
    # Calculate P&L for each hotel
    comparison_data = []
    for hotel in hotels:
        pl_data = calculate_pl_statement(hotel)
        comparison_data.append({
            'Hotel': hotel,
            'Revenue': pl_data['total_revenue'],
            'Costs': pl_data['total_costs'],
            'Profit': pl_data['gross_profit'],
            'Margin %': pl_data['profit_margin']
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Revenue Comparison**")
        fig_revenue = px.bar(
            df_comparison,
            x='Hotel',
            y='Revenue',
            color='Revenue',
            color_continuous_scale='Greens'
        )
        fig_revenue.update_layout(height=400)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.write("**Profit Margin Comparison**")
        fig_margin = px.bar(
            df_comparison,
            x='Hotel',
            y='Margin %',
            color='Margin %',
            color_continuous_scale='Blues'
        )
        fig_margin.update_layout(height=400)
        st.plotly_chart(fig_margin, use_container_width=True)
    
    st.divider()
    st.write("**Detailed Comparison Table**")
    st.dataframe(df_comparison, use_container_width=True)
