"""
Chart of Accounts (General Ledger) Dashboard
Displays financial accounts and balances
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase_client import supabase

def get_hotel_accounts(hotel_name: str) -> pd.DataFrame:
    """Get financial accounts for a hotel"""
    try:
        response = supabase.table("financial_accounts").select("*").eq("hotel_name", hotel_name).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching accounts: {str(e)}")
        return pd.DataFrame()

def get_all_hotels_accounts() -> pd.DataFrame:
    """Get financial accounts for all hotels"""
    try:
        response = supabase.table("financial_accounts").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching accounts: {str(e)}")
        return pd.DataFrame()

def show_accounts_dashboard(hotel_name: str):
    """Display chart of accounts for a specific hotel"""
    st.title(f"📊 {hotel_name} - Chart of Accounts")
    
    accounts = get_hotel_accounts(hotel_name)
    
    if accounts.empty:
        st.info(f"No account data available for {hotel_name}")
        return
    
    # Calculate balances
    accounts['balance'] = accounts['debit_amount'].fillna(0) - accounts['credit_amount'].fillna(0)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Accounts", "📈 Analysis"])
    
    with tab1:
        st.subheader("General Ledger Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Accounts", len(accounts))
        
        with col2:
            total_debit = accounts['debit_amount'].sum()
            st.metric("Total Debit", f"€{total_debit:,.2f}")
        
        with col3:
            total_credit = accounts['credit_amount'].sum()
            st.metric("Total Credit", f"€{total_credit:,.2f}")
        
        with col4:
            total_balance = accounts['balance'].sum()
            st.metric("Net Balance", f"€{total_balance:,.2f}")
        
        st.divider()
        
        # By account type
        st.subheader("Accounts by Type")
        
        type_data = accounts.groupby('account_type').agg({
            'balance': 'sum',
            'account_code': 'count'
        }).reset_index()
        
        type_data.columns = ['Type', 'Balance', 'Count']
        
        st.dataframe(type_data, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            type_data,
            x='Type',
            y='Balance',
            title='Account Balance by Type',
            color='Balance',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Detailed Account List")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_type = st.selectbox(
                "Filter by Account Type",
                ["All"] + accounts['account_type'].unique().tolist(),
                key="acct_type"
            )
        
        with col2:
            sort_by = st.radio(
                "Sort by",
                ["Balance", "Debit", "Credit", "Code"],
                horizontal=True
            )
        
        # Filter
        filtered = accounts.copy()
        
        if selected_type != "All":
            filtered = filtered[filtered['account_type'] == selected_type]
        
        # Sort
        if sort_by == "Balance":
            filtered = filtered.sort_values('balance', ascending=False, key=abs)
        elif sort_by == "Debit":
            filtered = filtered.sort_values('debit_amount', ascending=False)
        elif sort_by == "Credit":
            filtered = filtered.sort_values('credit_amount', ascending=False)
        else:
            filtered = filtered.sort_values('account_code')
        
        # Display
        display_cols = ['account_code', 'description', 'account_type', 'debit_amount', 'credit_amount', 'balance']
        df_display = filtered[display_cols].copy()
        df_display.columns = ['Code', 'Description', 'Type', 'Debit', 'Credit', 'Balance']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"accounts_{hotel_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("Account Analysis")
        
        # Top accounts by balance
        st.subheader("Top 10 Accounts by Balance")
        
        top_accounts = accounts.nlargest(10, 'balance')[['account_code', 'description', 'balance']]
        
        fig = px.bar(
            top_accounts,
            x='account_code',
            y='balance',
            title='Top 10 Accounts by Balance',
            labels={'account_code': 'Account Code', 'balance': 'Balance (€)'},
            color='balance',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Debit vs Credit comparison
        st.subheader("Debit vs Credit Summary")
        
        debit_by_type = accounts.groupby('account_type')['debit_amount'].sum()
        credit_by_type = accounts.groupby('account_type')['credit_amount'].sum()
        
        comparison_data = pd.DataFrame({
            'Type': debit_by_type.index,
            'Debit': debit_by_type.values,
            'Credit': credit_by_type.values
        })
        
        fig = px.bar(
            comparison_data,
            x='Type',
            y=['Debit', 'Credit'],
            title='Debit vs Credit by Account Type',
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_group_accounts_analysis():
    """Display chart of accounts with hotel selection"""
    st.title("📊 Chart of Accounts")
    
    all_accounts = get_all_hotels_accounts()
    
    if all_accounts.empty:
        st.info("No account data available in the system")
        return
    
    hotels_with_accounts = sorted(all_accounts['hotel_name'].unique().tolist())
    
    tab1, tab2 = st.tabs(["📊 Group Overview", "🏨 Hotel Details"])
    
    with tab1:
        st.subheader("Group General Ledger Summary")
        
        all_accounts['balance'] = all_accounts['debit_amount'].fillna(0) - all_accounts['credit_amount'].fillna(0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hotels", all_accounts['hotel_name'].nunique())
        
        with col2:
            st.metric("Total Accounts", len(all_accounts))
        
        with col3:
            total_debit = all_accounts['debit_amount'].sum()
            st.metric("Total Debit", f"€{total_debit:,.2f}")
        
        with col4:
            total_balance = all_accounts['balance'].sum()
            st.metric("Net Balance", f"€{total_balance:,.2f}")
        
        st.divider()
        
        # Hotels comparison
        st.subheader("Account Balance by Hotel")
        
        hotel_data = all_accounts.groupby('hotel_name').agg({
            'balance': 'sum',
            'account_code': 'count'
        }).reset_index()
        
        hotel_data.columns = ['Hotel', 'Balance', 'Accounts']
        
        st.dataframe(hotel_data, use_container_width=True, hide_index=True)
        
        fig = px.bar(
            hotel_data,
            x='Hotel',
            y='Balance',
            title='Net Balance by Hotel',
            color='Balance',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed View")
        
        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotels_with_accounts,
            index=0
        )
        
        if selected_hotel:
            st.divider()
            show_accounts_dashboard(selected_hotel)
