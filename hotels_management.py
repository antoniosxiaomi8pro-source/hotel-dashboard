"""
Hotels Management Module
Admin interface for managing hotels, rooms, restaurants, etc.
"""
import streamlit as st
import pandas as pd
from supabase_client import supabase_admin
from datetime import datetime


def get_all_hotels():
    """Get all hotels from the database"""
    try:
        response = supabase_admin.table("hotels").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching hotels: {e}")
        return []


def add_hotel(name: str, code: str, hotel_type: str, location: str, 
              rooms: int, capacity: int, opening_date: str):
    """Add a new hotel"""
    try:
        response = supabase_admin.table("hotels").insert({
            "name": name,
            "code": code,
            "type": hotel_type,
            "location": location,
            "rooms": rooms,
            "capacity_guests": capacity,
            "opening_date": opening_date,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        if response.data:
            return True, "✅ Hotel added successfully"
        return False, "❌ Failed to add hotel"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def update_hotel(hotel_id: str, **kwargs):
    """Update hotel information"""
    try:
        response = supabase_admin.table("hotels").update(kwargs).eq("id", hotel_id).execute()
        
        if response.data:
            return True, "✅ Hotel updated successfully"
        return False, "❌ Failed to update hotel"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def delete_hotel(hotel_id: str):
    """Delete a hotel"""
    try:
        response = supabase_admin.table("hotels").delete().eq("id", hotel_id).execute()
        return True, "✅ Hotel deleted successfully"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def get_hotel_restaurants(hotel_id: str):
    """Get all restaurants for a hotel"""
    try:
        response = supabase_admin.table("restaurants").select("*").eq("hotel_id", hotel_id).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching restaurants: {e}")
        return []


def add_restaurant(hotel_id: str, name: str, cuisine_type: str, capacity: int):
    """Add a restaurant to a hotel"""
    try:
        response = supabase_admin.table("restaurants").insert({
            "hotel_id": hotel_id,
            "name": name,
            "type": cuisine_type,
            "capacity": capacity,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        if response.data:
            return True, "✅ Restaurant added successfully"
        return False, "❌ Failed to add restaurant"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def delete_restaurant(restaurant_id: str):
    """Delete a restaurant"""
    try:
        response = supabase_admin.table("restaurants").delete().eq("id", restaurant_id).execute()
        return True, "✅ Restaurant deleted successfully"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def render_hotels_management():
    """Render the Hotels Management page"""
    st.title("🏨 Hotels Management")
    
    # Tabs for different management sections
    tab1, tab2, tab3 = st.tabs(["Hotels List", "Add Hotel", "Hotel Details"])
    
    # TAB 1: Hotels List
    with tab1:
        st.subheader("All Hotels")
        
        hotels = get_all_hotels()
        
        if hotels:
            df = pd.DataFrame(hotels)
            
            # Display table
            st.dataframe(
                df[["name", "code", "type", "location", "rooms", "capacity_guests"]],
                use_container_width=True
            )
            
            # Quick actions
            st.markdown("### ⚙️ Quick Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_hotel = st.selectbox(
                    "Select hotel to edit/delete",
                    options=[h["name"] for h in hotels],
                    key="hotel_select"
                )
                
                if selected_hotel:
                    hotel = next(h for h in hotels if h["name"] == selected_hotel)
                    
                    if st.button("🗑️ Delete Hotel", key=f"delete_{hotel['id']}"):
                        success, msg = delete_hotel(hotel["id"])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            with col2:
                st.info("Click on a hotel in the table to see full details in the 'Hotel Details' tab")
        else:
            st.info("No hotels found. Add one in the 'Add Hotel' tab.")
    
    # TAB 2: Add Hotel
    with tab2:
        st.subheader("Add New Hotel")
        
        with st.form("add_hotel_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Hotel Name *", placeholder="e.g., Porto Greco Beach & Village")
                code = st.text_input("Hotel Code *", placeholder="e.g., PG", max_chars=5)
                hotel_type = st.selectbox("Type *", ["Resort", "Hotel", "Villaggio", "Beach Resort", "Boutique"])
                location = st.text_input("Location *", placeholder="e.g., Porto Greco, Greece")
            
            with col2:
                rooms = st.number_input("Total Rooms *", min_value=10, max_value=1000, value=250)
                capacity = st.number_input("Total Capacity (guests) *", min_value=20, max_value=2000, value=500)
                opening_date = st.date_input("Opening Date")
            
            submitted = st.form_submit_button("✅ Add Hotel", use_container_width=True)
        
        if submitted:
            if not name or not code or not hotel_type or not location:
                st.error("❌ Please fill all required fields (*)")
            else:
                success, msg = add_hotel(
                    name=name,
                    code=code,
                    hotel_type=hotel_type,
                    location=location,
                    rooms=int(rooms),
                    capacity=int(capacity),
                    opening_date=str(opening_date)
                )
                
                if success:
                    st.success(msg)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)
    
    # TAB 3: Hotel Details & Restaurants
    with tab3:
        st.subheader("Hotel Details & Management")
        
        hotels = get_all_hotels()
        
        if hotels:
            selected_hotel = st.selectbox(
                "Select a hotel",
                options=[h["name"] for h in hotels],
                key="hotel_details_select"
            )
            
            hotel = next(h for h in hotels if h["name"] == selected_hotel)
            
            # Hotel Details
            st.markdown("### 📋 Hotel Information")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Code", hotel["code"])
            col2.metric("Type", hotel["type"])
            col3.metric("Rooms", hotel["rooms"])
            col4.metric("Capacity", hotel["capacity_guests"])
            
            st.markdown("---")
            
            # Restaurants Management
            st.markdown("### 🍽️ Restaurants")
            
            restaurants = get_hotel_restaurants(hotel["id"])
            
            if restaurants:
                st.dataframe(
                    pd.DataFrame(restaurants)[["name", "type", "capacity"]],
                    use_container_width=True
                )
            else:
                st.info("No restaurants added yet.")
            
            # Add Restaurant
            with st.expander("➕ Add New Restaurant", expanded=False):
                with st.form("add_restaurant_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        rest_name = st.text_input("Restaurant Name", placeholder="e.g., White Rabbit")
                        rest_cuisine = st.selectbox("Cuisine Type", [
                            "International", "Greek", "Seafood", "Italian", 
                            "Asian", "Mediterranean", "Fusion"
                        ])
                    
                    with col2:
                        rest_capacity = st.number_input("Capacity (guests)", min_value=10, max_value=500, value=100)
                    
                    submitted_rest = st.form_submit_button("✅ Add Restaurant", use_container_width=True)
                
                if submitted_rest:
                    if not rest_name:
                        st.error("Please enter restaurant name")
                    else:
                        success, msg = add_restaurant(
                            hotel_id=hotel["id"],
                            name=rest_name,
                            cuisine_type=rest_cuisine,
                            capacity=int(rest_capacity)
                        )
                        
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            # Delete Restaurants
            if restaurants:
                st.markdown("### 🗑️ Delete Restaurant")
                rest_to_delete = st.selectbox(
                    "Select restaurant to delete",
                    options=[r["name"] for r in restaurants],
                    key="rest_delete"
                )
                
                if st.button("Delete", key="delete_restaurant_btn"):
                    rest = next(r for r in restaurants if r["name"] == rest_to_delete)
                    success, msg = delete_restaurant(rest["id"])
                    
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("No hotels found. Please add a hotel first in the 'Add Hotel' tab.")
