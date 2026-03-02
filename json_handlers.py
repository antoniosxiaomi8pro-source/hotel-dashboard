"""
Intelligent JSON Handler for multiple file types
Processes JSON files and inserts into Supabase
"""
import json
import pandas as pd
from supabase_client import (
    insert_room_forecast,
    insert_daily_operation,
    insert_warehouse_item,
    insert_financial_cost,
    insert_revenue_account,
    insert_financial_account,
    insert_audit_log
)
from config import GREEK_MONTHS, MONTH_MAP
from datetime import datetime


def detect_json_type(df: pd.DataFrame, filename: str) -> str:
    """Auto-detect JSON file type from columns and filename"""
    columns = df.columns.tolist()
    filename_lower = filename.lower()
    
    # Check for specific patterns
    if "forecast" in filename_lower or ("month" in columns and "year" in columns and any(str(i) in columns for i in range(1, 32))):
        return "forecast"
    
    if "revenue" in filename_lower or any(greek_month in columns for greek_month in GREEK_MONTHS.values()):
        return "revenue"
    
    if "payroll" in filename_lower or "μισθοδοτ" in filename_lower:
        return "payroll"
    
    if "warehouse" in filename_lower or "apothiki" in filename_lower or "αποθήκη" in columns:
        return "warehouse"
    
    if "account" in filename_lower or "isozygio" in filename_lower or "κωδικός" in columns:
        return "accounts"
    
    if "operation" in filename_lower or "manager" in filename_lower:
        return "operations"
    
    return "unknown"


def handle_forecast_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process forecast JSON (room availability by date/type)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                month = row.get("Month") or row.get("month")
                year = row.get("Year") or row.get("year")
                room_type = row.get("Τύπος") or row.get("room_type")
                
                if not all([month, year, room_type]):
                    continue
                
                # Process day columns (1-31)
                for day in range(1, 32):
                    day_col = str(day)
                    if day_col in row:
                        value = row[day_col]
                        if pd.notna(value) and value != "":
                            try:
                                forecast_date = f"{year:04d}-{month:02d}-{day:02d}"
                                insert_room_forecast(
                                    hotel_name=hotel_name,
                                    room_type=room_type,
                                    forecast_date=forecast_date,
                                    forecast_value=int(value),
                                    month=month,
                                    year=year,
                                    source_file=source_file
                                )
                                inserted += 1
                            except Exception as e:
                                errors.append(f"Day {day}: {str(e)}")
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Forecast error: {str(e)}"
    
    msg = f"Inserted {inserted} forecast records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def handle_revenue_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process revenue JSON (monthly revenue by operator)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                account_name = row.get("Operator") or row.get("operator")
                if not account_name:
                    continue
                
                # Process month columns
                for month_num in range(1, 13):
                    greek_month = GREEK_MONTHS.get(month_num)
                    
                    if greek_month in row:
                        value = row[greek_month]
                        if pd.notna(value) and value != "":
                            try:
                                gross = float(value)
                                insert_revenue_account(
                                    hotel_name=hotel_name,
                                    account_name=account_name,
                                    month=month_num,
                                    year=2026,
                                    gross=gross,
                                    net=None,
                                    vat=None,
                                    tax=None,
                                    source_file=source_file
                                )
                                inserted += 1
                            except Exception as e:
                                errors.append(f"Month {month_num}: {str(e)}")
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Revenue error: {str(e)}"
    
    msg = f"Inserted {inserted} revenue records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def handle_payroll_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process payroll JSON (employee costs)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                # Extract relevant columns
                employee_name = row.get("Περιγραφή") or row.get("description")
                period = row.get("Περίοδος") or row.get("period")
                year = row.get("Έτος") or row.get("year") or 2026
                
                if not employee_name:
                    continue
                
                # Look for numeric columns (costs)
                for col in df.columns:
                    if col not in ["Κωδικός", "Περιγραφή", "Περίοδος", "Έτος"]:
                        value = row[col]
                        if pd.notna(value) and value != "":
                            try:
                                amount = float(value)
                                insert_financial_cost(
                                    hotel_name=hotel_name,
                                    cost_type="Payroll",
                                    description=col,
                                    amount=amount,
                                    employee_name=employee_name,
                                    period=period,
                                    year=year,
                                    source_file=source_file
                                )
                                inserted += 1
                            except Exception as e:
                                errors.append(f"Column {col}: {str(e)}")
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Payroll error: {str(e)}"
    
    msg = f"Inserted {inserted} payroll records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def handle_warehouse_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process warehouse JSON (inventory)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                warehouse = row.get("Αποθήκη") or row.get("warehouse") or "Main"
                
                # Extract category from column patterns
                category = None
                balance = None
                purchases = None
                outflow = None
                
                for col in df.columns:
                    if "Κατηγορία" in col or "Category" in col:
                        category = row[col]
                    elif "Balance" in col or "Υπόλοιπο" in col:
                        balance = row[col]
                    elif "Purchase" in col or "Αγορές" in col:
                        purchases = row[col]
                    elif "Outflow" in col or "Εκροή" in col:
                        outflow = row[col]
                
                if category:
                    insert_warehouse_item(
                        hotel_name=hotel_name,
                        warehouse=warehouse,
                        category=category,
                        balance_value=float(balance) if balance and pd.notna(balance) else None,
                        purchases_value=float(purchases) if purchases and pd.notna(purchases) else None,
                        outflow_value=float(outflow) if outflow and pd.notna(outflow) else None,
                        source_file=source_file
                    )
                    inserted += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Warehouse error: {str(e)}"
    
    msg = f"Inserted {inserted} warehouse records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def handle_accounts_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process accounts JSON (chart of accounts)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                account_code = row.get("Κωδικός") or row.get("code")
                description = row.get("Λογαριασμός") or row.get("description")
                debit = row.get("Χρέωση") or row.get("debit")
                credit = row.get("Πίστωση") or row.get("credit")
                
                if not (account_code or description):
                    continue
                
                insert_financial_account(
                    hotel_name=hotel_name,
                    account_code=account_code or "",
                    description=description or "",
                    debit_amount=float(debit) if debit and pd.notna(debit) else None,
                    credit_amount=float(credit) if credit and pd.notna(credit) else None,
                    account_type="Account",
                    source_file=source_file
                )
                inserted += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Accounts error: {str(e)}"
    
    msg = f"Inserted {inserted} account records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def handle_operations_json(data: list, hotel_name: str, source_file: str) -> tuple[int, str]:
    """Process operations JSON (daily operations)"""
    inserted = 0
    errors = []
    
    try:
        df = pd.DataFrame(data)
        
        for _, row in df.iterrows():
            try:
                operation_date = row.get("date") or row.get("Date")
                occupancy = row.get("occupancy") or row.get("Occupancy")
                revenue = row.get("revenue") or row.get("Revenue")
                
                if operation_date:
                    insert_daily_operation(
                        hotel_name=hotel_name,
                        operation_date=str(operation_date),
                        occupancy_rate=float(occupancy) if occupancy and pd.notna(occupancy) else None,
                        revenue=float(revenue) if revenue and pd.notna(revenue) else None,
                        source_file=source_file
                    )
                    inserted += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
    
    except Exception as e:
        return 0, f"Operations error: {str(e)}"
    
    msg = f"Inserted {inserted} operation records"
    if errors:
        msg += f" ({len(errors)} errors)"
    
    return inserted, msg


def process_json_file(file_content: bytes, filename: str, hotel_name: str) -> tuple[int, str]:
    """
    Main entry point - detect type and process JSON file
    Returns: (total_inserted, message)
    """
    try:
        data = json.loads(file_content)
        
        if not isinstance(data, list):
            if isinstance(data, dict):
                data = [data]
            else:
                return 0, "Invalid JSON format"
        
        df = pd.DataFrame(data)
        file_type = detect_json_type(df, filename)
        
        handlers = {
            "forecast": handle_forecast_json,
            "revenue": handle_revenue_json,
            "payroll": handle_payroll_json,
            "warehouse": handle_warehouse_json,
            "accounts": handle_accounts_json,
            "operations": handle_operations_json,
        }
        
        handler = handlers.get(file_type, None)
        
        if not handler:
            return 0, f"Unknown file type: {file_type}"
        
        inserted, msg = handler(data, hotel_name, filename)
        return inserted, msg
    
    except json.JSONDecodeError:
        return 0, "Invalid JSON format"
    except Exception as e:
        return 0, f"Error processing file: {str(e)}"
