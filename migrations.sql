-- ============================================================================
-- COSMHOTEL BI DASHBOARD - SUPABASE SCHEMA
-- ============================================================================
-- Execute this in Supabase SQL Editor to create all tables
-- ============================================================================

-- 1. USERS TABLE (Authentication & Authorization)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT NOT NULL,
  hotel_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'manager', 'viewer')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. ROOM FORECAST TABLE (Daily room availability by type)
CREATE TABLE IF NOT EXISTS room_forecast (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  room_type TEXT NOT NULL,
  forecast_date DATE NOT NULL,
  forecast_value INT NOT NULL DEFAULT 0,
  month INT,
  year INT,
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(hotel_name, room_type, forecast_date)
);

-- 3. DAILY OPERATIONS TABLE (Revenue, occupancy, operations)
CREATE TABLE IF NOT EXISTS daily_operations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  operation_date DATE NOT NULL,
  occupancy_rate DECIMAL(5, 2),
  revenue DECIMAL(10, 2),
  guests_count INT,
  rooms_sold INT,
  manager_notes TEXT,
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(hotel_name, operation_date)
);

-- 4. WAREHOUSE INVENTORY TABLE
CREATE TABLE IF NOT EXISTS warehouse_inventory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  warehouse TEXT NOT NULL,
  category TEXT NOT NULL,
  item_name TEXT,
  balance_value DECIMAL(12, 2),
  purchases_value DECIMAL(12, 2),
  outflow_value DECIMAL(12, 2),
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 5. FINANCIAL COSTS TABLE (Payroll, expenses)
CREATE TABLE IF NOT EXISTS financial_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  cost_type TEXT NOT NULL,
  description TEXT,
  employee_name TEXT,
  amount DECIMAL(10, 2) NOT NULL,
  period TEXT,
  year INT,
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 6. REVENUE ACCOUNTS TABLE (Monthly revenue breakdown)
CREATE TABLE IF NOT EXISTS revenue_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  account_name TEXT NOT NULL,
  month INT NOT NULL,
  year INT NOT NULL,
  gross DECIMAL(12, 2),
  net DECIMAL(12, 2),
  vat DECIMAL(10, 2),
  tax DECIMAL(10, 2),
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 7. FINANCIAL ACCOUNTS TABLE (Chart of accounts)
CREATE TABLE IF NOT EXISTS financial_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  account_code TEXT NOT NULL,
  description TEXT NOT NULL,
  debit_amount DECIMAL(12, 2),
  credit_amount DECIMAL(12, 2),
  account_type TEXT,
  source_file TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 8. AUDIT LOG TABLE (File uploads and operations)
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_name TEXT NOT NULL,
  user_email TEXT,
  action TEXT NOT NULL,
  file_name TEXT,
  records_count INT,
  status TEXT CHECK (status IN ('success', 'error', 'warning')),
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_hotel ON users(hotel_name);

CREATE INDEX idx_forecast_hotel_date ON room_forecast(hotel_name, forecast_date);
CREATE INDEX idx_forecast_month_year ON room_forecast(month, year);

CREATE INDEX idx_operations_hotel_date ON daily_operations(hotel_name, operation_date);

CREATE INDEX idx_warehouse_hotel ON warehouse_inventory(hotel_name);
CREATE INDEX idx_warehouse_category ON warehouse_inventory(warehouse, category);

CREATE INDEX idx_costs_hotel ON financial_costs(hotel_name);
CREATE INDEX idx_costs_type ON financial_costs(cost_type);

CREATE INDEX idx_revenue_hotel_month ON revenue_accounts(hotel_name, month, year);

CREATE INDEX idx_accounts_hotel ON financial_accounts(hotel_name);
CREATE INDEX idx_accounts_code ON financial_accounts(account_code);

CREATE INDEX idx_audit_hotel_date ON audit_log(hotel_name, created_at DESC);

-- ============================================================================
-- INSERT DEMO USERS (PASSWORD HASHING HANDLED BY APP)
-- ============================================================================

INSERT INTO users (email, password_hash, full_name, hotel_name, role, is_active) VALUES
  ('admin@cosmhotel.gr', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator', 'Porto Greco', 'admin', true),
  ('manager@cosmhotel.gr', '866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5', 'Manager', 'Porto Greco', 'manager', true),
  ('viewer@cosmhotel.gr', '65375049b9e4d7cad6c9ba286fdeb9394b28135a3e84136404cfccfdcc438894', 'Viewer', 'Porto Greco', 'viewer', true)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_forecast ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE warehouse_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE revenue_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read users table
CREATE POLICY "Users can view users" ON users
  FOR SELECT USING (auth.role() = 'authenticated');

-- Allow authenticated users to read their own hotel's data
CREATE POLICY "Users can read their hotel forecast" ON room_forecast
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their hotel operations" ON daily_operations
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their hotel warehouse" ON warehouse_inventory
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their hotel costs" ON financial_costs
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their hotel revenue" ON revenue_accounts
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read their hotel accounts" ON financial_accounts
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read audit log" ON audit_log
  FOR SELECT USING (auth.role() = 'authenticated');

-- Allow service role (admin operations) full access
CREATE POLICY "Service role has full access to forecast" ON room_forecast
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to operations" ON daily_operations
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to warehouse" ON warehouse_inventory
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to costs" ON financial_costs
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to revenue" ON revenue_accounts
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to accounts" ON financial_accounts
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to audit" ON audit_log
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- DONE! Run this SQL in Supabase SQL Editor
-- ============================================================================
