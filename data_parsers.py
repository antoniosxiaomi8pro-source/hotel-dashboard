"""
Data Parsers for COSMHOTEL Group
Handles parsing of real operational data files into standardized formats
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple
import config


class DataParserBase:
    """Base class for all data parsers"""
    
    def __init__(self, hotel_key: str = None):
        """
        Initialize parser
        
        Args:
            hotel_key: Key from HOTEL_PROPERTIES (e.g., 'porto_greco')
        """
        self.hotel_key = hotel_key
        self.hotel_name = None
        self.hotel_code = None
        
        if hotel_key and hotel_key in config.HOTEL_PROPERTIES:
            hotel = config.HOTEL_PROPERTIES[hotel_key]
            self.hotel_name = hotel["name"]
            self.hotel_code = hotel["code"]
        elif hotel_key == "kingscorpio":
            self.hotel_name = config.RESTAURANTS["kingscorpio"]["name"]
            self.hotel_code = "KS"
    
    def load_json_file(self, filepath: str) -> Any:
        """Load and parse JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file {filepath}: {e}")
            return None
    
    def load_csv_file(self, filepath: str) -> pd.DataFrame:
        """Load and parse CSV file"""
        try:
            return pd.read_csv(filepath, encoding='utf-8')
        except Exception as e:
            print(f"Error loading CSV file {filepath}: {e}")
            return None


class AccountsParser(DataParserBase):
    """Parse accounts/chart of accounts data"""
    
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse accounts file (accounts_porto_level3_60.json)
        
        Returns list of revenue/cost items with debit/credit values
        """
        data = self.load_json_file(filepath)
        if not data:
            return []
        
        parsed_records = []
        for item in data:
            record = {
                "hotel_key": self.hotel_key,
                "hotel_name": self.hotel_name,
                "account_code": item.get("Κωδικός", ""),
                "account_name": item.get("Περιγραφή Λογαριασμού", ""),
                "debit_period": float(item.get("Χρέωση Περιόδου", 0)),
                "credit_period": float(item.get("Πίστωση Περιόδου", 0)),
                "net_amount": float(item.get("Χρέωση Περιόδου", 0)) - float(item.get("Πίστωση Περιόδου", 0)),
                "data_type": "accounts",
                "parsed_at": datetime.now().isoformat(),
            }
            parsed_records.append(record)
        
        return parsed_records


class RevenueParser(DataParserBase):
    """Parse revenue data (ισοζύγιο - trial balance with revenue breakdown)"""
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """
        Parse revenue file (ισοζυγιο m.c. porto 01.10.json)
        
        Returns revenue breakdown by category with daily/monthly/yearly metrics
        """
        data = self.load_json_file(filepath)
        if not data:
            return {}
        
        result = {
            "hotel_key": self.hotel_key,
            "hotel_name": self.hotel_name,
            "report_date": datetime.now().date().isoformat(),
            "data_type": "revenue_breakdown",
            "categories": {},
            "totals": {
                "day": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
                "month": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
                "year": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
            },
        }
        
        for item in data:
            category_name = item.get("name", "Unknown")
            result["categories"][category_name] = {
                "day": item.get("day", {}),
                "month": item.get("month", {}),
                "year": item.get("year", {}),
            }
            
            # Accumulate totals
            for period in ["day", "month", "year"]:
                if period in item:
                    for key in ["gross", "net", "vat", "tax"]:
                        if key in item[period]:
                            result["totals"][period][key] += float(item[period][key])
        
        return result


class ForecastParser(DataParserBase):
    """Parse booking forecast data"""
    
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse forecast file (forecast_parsed.json)
        
        Returns room booking forecast by type and date
        """
        data = self.load_json_file(filepath)
        if not data:
            return []
        
        parsed_records = []
        
        for item in data:
            month = item.get("Month")
            year = item.get("Year")
            room_type = item.get("Τύπος", "Unknown")
            
            # Skip summary rows
            if room_type in ["ΔΥΝΑΜΙΚΟΤΗΤΑ ΔΩΜΑΤΙΑ", "ΔΥΝΑΜΙΚΟΤΗΤΑ Ατομα"]:
                continue
            
            # Extract daily booking data for days 1-31
            for day in range(1, 32):
                day_str = str(day)
                if day_str in item:
                    value = item[day_str]
                    if value is None:  # Skip null values (non-existent dates)
                        continue
                    
                    record = {
                        "hotel_key": self.hotel_key,
                        "hotel_name": self.hotel_name,
                        "year": year,
                        "month": month,
                        "day": day,
                        "date": f"{year}-{month:02d}-{day:02d}",
                        "room_type": room_type,
                        "bookings": int(value),
                        "data_type": "forecast",
                        "parsed_at": datetime.now().isoformat(),
                    }
                    parsed_records.append(record)
        
        return parsed_records


class PayrollParser(DataParserBase):
    """Parse payroll data"""
    
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse payroll file (payroll_parsed.json)
        
        Returns employee payroll records with costs and contributions
        """
        data = self.load_json_file(filepath)
        if not data:
            return []
        
        parsed_records = []
        
        for item in data:
            record = {
                "hotel_key": self.hotel_key,
                "hotel_name": self.hotel_name,
                "department": item.get("Περιγραφή Υποκαταστήματος", ""),
                "period": item.get("Περίοδος", ""),
                "year": int(item.get("Έτος", 0)),
                "last_name": item.get("Επώνυμο", ""),
                "first_name": item.get("Όνομα", ""),
                "position": item.get("Ειδικότητα", ""),
                "insurance_days": float(item.get("Ημ. Ασφ.", 0)),
                "gross_salary": float(item.get("Φ.Μ.Υ", 0)),
                "employee_contribution": float(item.get("Εισφ. Εργάζ. Κύριου Ταμείου", 0)),
                "employer_contribution": float(item.get("Εισφ. Εργόδ. Κύριου Ταμείου", 0)),
                "net_pay": float(item.get("Καθαρές Αποδοχές", 0)),
                "total_cost": float(item.get("Συνολικό Κόστος", 0)),
                "data_type": "payroll",
                "parsed_at": datetime.now().isoformat(),
            }
            parsed_records.append(record)
        
        return parsed_records


class InventoryParser(DataParserBase):
    """Parse warehouse/inventory data"""
    
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse inventory file (iszigio_apothikis_parsed.json)
        
        Returns warehouse inventory items with values
        """
        data = self.load_json_file(filepath)
        if not data:
            return []
        
        parsed_records = []
        
        for item in data:
            record = {
                "hotel_key": self.hotel_key,
                "hotel_name": self.hotel_name,
                "warehouse": item.get("Αποθήκη", ""),
                "category_level1": item.get("1o Βάθμιος Δενδ.1", ""),
                "category_level2": item.get("Δενδροειδής Κατηγορία 1", ""),
                "opening_value": float(item.get("Εξ Απογραφής Αξία Υπολοίπου", 0)),
                "purchases_value": float(item.get("Αξία Αγορών", 0)),
                "other_inputs": float(item.get("Αξία Λοιπών Εισαγωγών", 0)),
                "other_outputs": float(item.get("Αξία Λοιπών Εξαγωγών", 0)),
                "sales_value": float(item.get("Αξία Εισαγωγών", 0)),
                "closing_value": float(item.get("Αξία Υπολοίπου", 0)),
                "data_type": "inventory",
                "parsed_at": datetime.now().isoformat(),
            }
            parsed_records.append(record)
        
        return parsed_records


class ManagerReportParser(DataParserBase):
    """Parse manager report data (occupancy, operations metrics)"""
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """
        Parse manager report file (manager report porto_manager_report.json)
        
        Returns occupancy and operational metrics
        """
        data = self.load_json_file(filepath)
        if not data or not isinstance(data, dict):
            return {}
        
        result = {
            "hotel_key": self.hotel_key,
            "hotel_name": self.hotel_name,
            "report_date": datetime.now().date().isoformat(),
            "data_type": "manager_report",
            "occupancy_metrics": {},
        }
        
        if "rooms" in data:
            for metric_name, metric_data in data["rooms"].items():
                if isinstance(metric_data, dict):
                    result["occupancy_metrics"][metric_name] = {
                        "current_day": metric_data.get("day_current", 0),
                        "current_month": metric_data.get("month_current", 0),
                        "year_to_date": metric_data.get("year_current", 0),
                    }
        
        return result


class GroupDataAggregator:
    """Aggregate data across all hotels for group-level reporting"""
    
    @staticmethod
    def aggregate_revenue(all_hotels_revenue: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate revenue data from all hotels
        
        Args:
            all_hotels_revenue: List of parsed revenue dicts from each hotel
        
        Returns:
            Consolidated group revenue summary
        """
        group_totals = {
            "day": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
            "month": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
            "year": {"gross": 0, "net": 0, "vat": 0, "tax": 0},
        }
        
        hotel_breakdown = {}
        
        for hotel_revenue in all_hotels_revenue:
            hotel_key = hotel_revenue.get("hotel_key")
            hotel_name = hotel_revenue.get("hotel_name")
            totals = hotel_revenue.get("totals", {})
            
            hotel_breakdown[hotel_name] = totals
            
            for period in ["day", "month", "year"]:
                if period in totals:
                    for key in ["gross", "net", "vat", "tax"]:
                        group_totals[period][key] += totals[period].get(key, 0)
        
        return {
            "data_type": "group_revenue_summary",
            "date": datetime.now().date().isoformat(),
            "group_totals": group_totals,
            "hotel_breakdown": hotel_breakdown,
            "number_of_properties": len(hotel_breakdown),
        }
    
    @staticmethod
    def aggregate_occupancy(all_hotels_reports: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate occupancy data from all hotels
        
        Args:
            all_hotels_reports: List of parsed manager reports from each hotel
        
        Returns:
            Consolidated group occupancy summary
        """
        hotel_occupancy = {}
        total_occupied = 0
        total_available = 0
        
        for report in all_hotels_reports:
            hotel_name = report.get("hotel_name")
            metrics = report.get("occupancy_metrics", {})
            
            if "Κατειλημμένα" in metrics and "Διαθέσιμα" in metrics:
                occupied = metrics["Κατειλημμένα"].get("current_day", 0)
                available = metrics["Διαθέσιμα"].get("current_day", 0)
                
                if available > 0:
                    occupancy_rate = (occupied / available) * 100
                    hotel_occupancy[hotel_name] = {
                        "occupied_rooms": occupied,
                        "available_rooms": available,
                        "occupancy_rate": occupancy_rate,
                    }
                    
                    total_occupied += occupied
                    total_available += available
        
        group_occupancy_rate = (total_occupied / total_available * 100) if total_available > 0 else 0
        
        return {
            "data_type": "group_occupancy_summary",
            "date": datetime.now().date().isoformat(),
            "group_occupancy_rate": group_occupancy_rate,
            "total_occupied_rooms": total_occupied,
            "total_available_rooms": total_available,
            "hotel_breakdown": hotel_occupancy,
            "number_of_properties": len(hotel_occupancy),
        }


def detect_file_type(filename: str) -> str:
    """Detect the type of data file based on filename"""
    filename_lower = filename.lower()
    
    if "accounts" in filename_lower or "level" in filename_lower:
        return "accounts"
    elif "forecast" in filename_lower:
        return "forecast"
    elif "payroll" in filename_lower:
        return "payroll"
    elif "iszigio" in filename_lower or "inventory" in filename_lower:
        return "inventory"
    elif "manager report" in filename_lower or "ισοζυγιο" in filename_lower:
        if "ισοζυγιο" in filename_lower:
            return "revenue"  # Trial balance file shows revenue
        return "manager_report"
    
    return "unknown"


def parse_data_file(filepath: str, hotel_key: str = None) -> Tuple[str, Any]:
    """
    Automatically detect and parse a data file
    
    Args:
        filepath: Path to the data file
        hotel_key: Optional hotel key for mapping
    
    Returns:
        Tuple of (file_type, parsed_data)
    """
    import os
    
    filename = os.path.basename(filepath)
    file_type = detect_file_type(filename)
    
    if file_type == "accounts":
        parser = AccountsParser(hotel_key)
        data = parser.parse(filepath)
    elif file_type == "revenue":
        parser = RevenueParser(hotel_key)
        data = parser.parse(filepath)
    elif file_type == "forecast":
        parser = ForecastParser(hotel_key)
        data = parser.parse(filepath)
    elif file_type == "payroll":
        parser = PayrollParser(hotel_key)
        data = parser.parse(filepath)
    elif file_type == "inventory":
        parser = InventoryParser(hotel_key)
        data = parser.parse(filepath)
    elif file_type == "manager_report":
        parser = ManagerReportParser(hotel_key)
        data = parser.parse(filepath)
    else:
        data = None
    
    return file_type, data
