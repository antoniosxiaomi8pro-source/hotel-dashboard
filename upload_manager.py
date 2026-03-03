"""
Upload Manager for COSMHOTEL Group
Handles file uploads, validation, parsing, and data ingestion to Supabase
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any
import hashlib
import io

from supabase_client import supabase_admin
from data_parsers import (
    parse_data_file,
    AccountsParser,
    RevenueParser,
    ForecastParser,
    PayrollParser,
    InventoryParser,
    ManagerReportParser,
)
from config import HOTEL_PROPERTIES


class FileUploadManager:
    """Manages file uploads and data ingestion to Supabase"""
    
    SUPPORTED_FILE_TYPES = {
        'revenue': 'Revenue Trial Balance (ισοζύγιο)',
        'occupancy': 'Manager Report (Occupancy)',
        'forecast': 'Room Forecast',
        'payroll': 'Payroll Data',
        'accounts': 'Chart of Accounts',
        'inventory': 'Warehouse Inventory'
    }
    
    SUPPORTED_HOTELS = list(HOTEL_PROPERTIES.keys())
    
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        return hashlib.sha256(file_bytes).hexdigest()
    
    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if uploaded_file is None:
            return False, "No file selected"
        
        # Check if file is empty
        if uploaded_file.size == 0:
            return False, "File is empty"
        
        # Check file size (max 10 MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False, "File size exceeds 10 MB limit"
        
        # Check file extension
        if not uploaded_file.name.lower().endswith(('.json', '.csv')):
            return False, "Only JSON and CSV files are supported"
        
        return True, "File is valid"
    
    @staticmethod
    def detect_file_type(filename: str) -> str:
        """Detect file type from filename"""
        filename_lower = filename.lower()
        
        if 'ισοζυγιο' in filename_lower or 'revenue' in filename_lower or 'trial' in filename_lower:
            return 'revenue'
        elif 'manager' in filename_lower or 'occupancy' in filename_lower or 'rooms' in filename_lower:
            return 'occupancy'
        elif 'forecast' in filename_lower or 'booking' in filename_lower:
            return 'forecast'
        elif 'payroll' in filename_lower or 'salary' in filename_lower:
            return 'payroll'
        elif 'accounts' in filename_lower or 'chart' in filename_lower:
            return 'accounts'
        elif 'inventory' in filename_lower or 'warehouse' in filename_lower or 'apothiki' in filename_lower:
            return 'inventory'
        
        return None
    
    @staticmethod
    def detect_hotel_from_filename(filename: str) -> str:
        """Detect hotel from filename"""
        filename_lower = filename.lower()
        
        for hotel_key, hotel_info in HOTEL_PROPERTIES.items():
            # Check if hotel key or name appears in filename
            if hotel_key.lower() in filename_lower:
                return hotel_key
            if hotel_info['code'].lower() in filename_lower:
                return hotel_key
        
        return None
    
    @staticmethod
    def read_file_content(uploaded_file) -> Tuple[Any, str]:
        """Read file content (JSON or CSV)"""
        try:
            if uploaded_file.name.lower().endswith('.json'):
                file_content = json.load(io.StringIO(uploaded_file.getvalue().decode('utf-8')))
                return file_content, None
            elif uploaded_file.name.lower().endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                return df.to_dict('records'), None
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
        
        return None, "Unsupported file format"
    
    @staticmethod
    def log_to_audit(
        filename: str,
        file_type: str,
        hotel_key: str,
        hotel_name: str,
        uploaded_by: str,
        records_extracted: int,
        records_inserted: int,
        processing_status: str = 'success',
        error_message: str = None,
        file_hash: str = None,
        file_size: int = 0
    ) -> bool:
        """Log upload event to audit table"""
        try:
            supabase_admin.table("data_audit_log").insert({
                "filename": filename,
                "file_type": file_type,
                "file_hash": file_hash,
                "file_size_bytes": file_size,
                "hotel_key": hotel_key,
                "hotel_name": hotel_name,
                "uploaded_by": uploaded_by,
                "processing_status": processing_status,
                "records_extracted": records_extracted,
                "records_inserted": records_inserted,
                "records_skipped": records_extracted - records_inserted,
                "records_with_errors": 1 if processing_status == 'error' else 0,
                "error_message": error_message,
                "parser_version": "1.0.0"
            }).execute()
            return True
        except Exception as e:
            st.error(f"⚠️ Failed to log upload: {str(e)}")
            return False
    
    @staticmethod
    def insert_revenue_data(
        data: list,
        hotel_key: str,
        hotel_name: str,
        source_file: str,
        uploaded_by: str
    ) -> Tuple[int, str]:
        """Insert revenue data into group_revenue table"""
        try:
            inserted = 0
            errors = []
            
            for record in data:
                try:
                    supabase_admin.table("group_revenue").insert({
                        "date_recorded": record.get('date_recorded') or datetime.now().date(),
                        "hotel_key": hotel_key,
                        "hotel_name": hotel_name,
                        "revenue_category": record.get('revenue_category'),
                        "operator": record.get('operator'),
                        "gross_revenue": float(record.get('gross_revenue', 0)),
                        "net_revenue": float(record.get('net_revenue', 0)),
                        "vat_amount": float(record.get('vat_amount', 0)),
                        "tax_amount": float(record.get('tax_amount', 0)),
                        "source_file": source_file,
                        "data_source": "import",
                        "uploaded_by": uploaded_by,
                        "is_verified": False
                    }).execute()
                    inserted += 1
                except Exception as e:
                    errors.append(f"Row error: {str(e)}")
            
            error_msg = "; ".join(errors) if errors else None
            return inserted, error_msg
        except Exception as e:
            return 0, f"Batch insert failed: {str(e)}"
    
    @staticmethod
    def insert_occupancy_data(
        data: list,
        hotel_key: str,
        hotel_name: str,
        source_file: str,
        uploaded_by: str
    ) -> Tuple[int, str]:
        """Insert occupancy data into group_occupancy table"""
        try:
            inserted = 0
            errors = []
            
            for record in data:
                try:
                    supabase_admin.table("group_occupancy").insert({
                        "date_recorded": record.get('date_recorded') or datetime.now().date(),
                        "hotel_key": hotel_key,
                        "hotel_name": hotel_name,
                        "total_rooms": int(record.get('total_rooms', 0)),
                        "rooms_occupied": int(record.get('rooms_occupied', 0)),
                        "rooms_available": int(record.get('rooms_available', 0)),
                        "occupancy_percentage": float(record.get('occupancy_percentage', 0)),
                        "total_guests": int(record.get('total_guests', 0)),
                        "adult_guests": int(record.get('adult_guests', 0)),
                        "child_guests": int(record.get('child_guests', 0)),
                        "avg_length_of_stay": float(record.get('avg_length_of_stay', 0)),
                        "source_file": source_file,
                        "data_source": "import",
                        "uploaded_by": uploaded_by,
                        "is_verified": False
                    }).execute()
                    inserted += 1
                except Exception as e:
                    errors.append(f"Row error: {str(e)}")
            
            error_msg = "; ".join(errors) if errors else None
            return inserted, error_msg
        except Exception as e:
            return 0, f"Batch insert failed: {str(e)}"


def render_upload_interface():
    """Render file upload interface in Streamlit"""
    st.title("📤 Data File Upload")
    st.markdown("Upload hotel operation files (revenue, occupancy, forecast, payroll, accounts, inventory)")
    
    # Create tabs for different sections
    upload_tab, history_tab = st.tabs(["📁 Upload File", "📋 Upload History"])
    
    with upload_tab:
        st.markdown("---")
        
        # File selection
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a file to upload",
                type=['json', 'csv'],
                help="Supported formats: JSON, CSV"
            )
        
        with col2:
            st.write("")  # Spacing
            if uploaded_file:
                st.write(f"**File**: {uploaded_file.name}")
                st.write(f"**Size**: {uploaded_file.size / 1024:.1f} KB")
        
        st.markdown("---")
        
        if uploaded_file:
            # Validate file
            is_valid, validation_msg = FileUploadManager.validate_file(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ {validation_msg}")
                return
            
            st.success(f"✅ {validation_msg}")
            
            # Auto-detect file type and hotel
            detected_file_type = FileUploadManager.detect_file_type(uploaded_file.name)
            detected_hotel = FileUploadManager.detect_hotel_from_filename(uploaded_file.name)
            
            # File type selection
            col1, col2 = st.columns(2)
            
            with col1:
                file_type = st.selectbox(
                    "📋 File Type",
                    options=list(FileUploadManager.SUPPORTED_FILE_TYPES.keys()),
                    index=list(FileUploadManager.SUPPORTED_FILE_TYPES.keys()).index(detected_file_type) 
                        if detected_file_type else 0,
                    format_func=lambda x: FileUploadManager.SUPPORTED_FILE_TYPES[x]
                )
            
            with col2:
                hotel_key = st.selectbox(
                    "🏨 Hotel",
                    options=FileUploadManager.SUPPORTED_HOTELS,
                    index=FileUploadManager.SUPPORTED_HOTELS.index(detected_hotel) 
                        if detected_hotel else 0,
                    format_func=lambda x: HOTEL_PROPERTIES[x]['name']
                )
            
            st.markdown("---")
            
            # Upload button with progress
            if st.button("🚀 Upload & Process", use_container_width=True, type="primary"):
                with st.spinner("Processing file..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Read file
                    status_text.text("Reading file...")
                    progress_bar.progress(10)
                    
                    file_content, read_error = FileUploadManager.read_file_content(uploaded_file)
                    if read_error:
                        st.error(f"❌ {read_error}")
                        return
                    
                    progress_bar.progress(25)
                    
                    # Parse data
                    status_text.text("Parsing data...")
                    
                    hotel_name = HOTEL_PROPERTIES[hotel_key]['name']
                    file_hash = FileUploadManager.calculate_file_hash(uploaded_file.getvalue())
                    
                    # Insert data based on file type
                    if file_type == 'revenue':
                        records_inserted, error = FileUploadManager.insert_revenue_data(
                            file_content, hotel_key, hotel_name, uploaded_file.name,
                            st.session_state.user_email
                        )
                    elif file_type == 'occupancy':
                        records_inserted, error = FileUploadManager.insert_occupancy_data(
                            file_content, hotel_key, hotel_name, uploaded_file.name,
                            st.session_state.user_email
                        )
                    else:
                        records_inserted, error = 0, f"File type '{file_type}' not yet implemented"
                    
                    progress_bar.progress(75)
                    
                    # Log to audit
                    status_text.text("Logging to audit trail...")
                    
                    audit_logged = FileUploadManager.log_to_audit(
                        filename=uploaded_file.name,
                        file_type=file_type,
                        hotel_key=hotel_key,
                        hotel_name=hotel_name,
                        uploaded_by=st.session_state.user_email,
                        records_extracted=len(file_content) if isinstance(file_content, list) else 1,
                        records_inserted=records_inserted,
                        processing_status='success' if not error else 'error',
                        error_message=error,
                        file_hash=file_hash,
                        file_size=uploaded_file.size
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("Upload complete!")
                    
                    # Show results
                    st.markdown("---")
                    
                    if error:
                        st.warning(f"⚠️ Partial success: {error}")
                    else:
                        st.success("✅ Upload successful!")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Records Processed", len(file_content) if isinstance(file_content, list) else 1)
                    
                    with col2:
                        st.metric("Records Inserted", records_inserted)
                    
                    with col3:
                        st.metric("File Hash", file_hash[:8] + "...")
                    
                    st.markdown("---")
                    st.info("📊 Data is now available in Supabase. Dashboards will be updated automatically.")
        
        else:
            st.info("👆 Upload a file to get started")
    
    with history_tab:
        st.markdown("### 📋 Recent Uploads")
        
        try:
            # Fetch recent uploads from audit log
            response = supabase_admin.table("data_audit_log")\
                .select("*")\
                .order("uploaded_at", desc=True)\
                .limit(20)\
                .execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Format columns
                df['uploaded_at'] = pd.to_datetime(df['uploaded_at']).dt.strftime('%Y-%m-%d %H:%M')
                df['file_size_bytes'] = (df['file_size_bytes'] / 1024).round(1).astype(str) + ' KB'
                
                # Display table
                st.dataframe(
                    df[[
                        'filename', 'file_type', 'hotel_key', 'processing_status',
                        'records_inserted', 'uploaded_at'
                    ]].rename(columns={
                        'filename': 'File',
                        'file_type': 'Type',
                        'hotel_key': 'Hotel',
                        'processing_status': 'Status',
                        'records_inserted': 'Records',
                        'uploaded_at': 'Uploaded'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No uploads yet")
        
        except Exception as e:
            st.error(f"Error fetching upload history: {str(e)}")


if __name__ == "__main__":
    render_upload_interface()
