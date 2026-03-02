-- ============================================================================
-- UPDATED SCHEMA FOR COSMHOTEL GROUP - MULTI-HOTEL SUPPORT
-- ============================================================================
-- Execute this to update the users table and add new demo users

-- 1. DROP OLD USERS AND RECREATE WITH NEW ROLES
DELETE FROM users;

-- 2. INSERT NEW DEMO USERS WITH 5 ROLES
INSERT INTO users (email, password_hash, full_name, hotel_name, role, is_active) VALUES
  -- ADMINS (can upload files)
  ('admin@cosmhotel.gr', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Admin User', 'Porto Greco Beach & Village', 'admin', true),
  ('admin2@cosmhotel.gr', 'c46e21a59699eded32adfad86c0a957f2a73b83f6edecf99e9c7c24e7edab23e', 'Admin User 2', 'Theros Resort', 'admin', true),
  
  -- GROUP DIRECTOR (sees all hotels)
  ('director@cosmhotel.gr', '9b0b2b6e3e3c0d8f0a0e0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d', 'George Papadopoulos', 'Porto Greco Beach & Village', 'group_director', true),
  
  -- HOTEL MANAGERS (see own hotel only)
  ('manager.porto@cosmhotel.gr', '866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5', 'Porto Manager', 'Porto Greco Beach & Village', 'hotel_manager', true),
  ('manager.theros@cosmhotel.gr', 'e5e6f8d9c0e1b2a3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6', 'Theros Manager', 'Theros Resort', 'hotel_manager', true),
  ('manager.apollon@cosmhotel.gr', 'f1f2f3f4f5f6f7f8f9fafbfcfdfeffff0f1f2f3f4f5f6f7f8f9fafbfcfdfe', 'Apollon Manager', 'Apollon Hotel', 'hotel_manager', true),
  ('manager.axelcrete@cosmhotel.gr', '1a1b1c1d1e1f1a1b1c1d1e1f1a1b1c1d1e1f1a1b1c1d1e1f1a1b1c1d1e1f', 'Axel Crete Manager', 'Axel Crete Villaggio', 'hotel_manager', true),
  ('manager.axelmykonos@cosmhotel.gr', '2a2b2c2d2e2f2a2b2c2d2e2f2a2b2c2d2e2f2a2b2c2d2e2f2a2b2c2d2e2f', 'Axel Mykonos Manager', 'Axel Beach Mykonos', 'hotel_manager', true),
  ('manager.kingscorpio@cosmhotel.gr', '3a3b3c3d3e3f3a3b3c3d3e3f3a3b3c3d3e3f3a3b3c3d3e3f3a3b3c3d3e3f', 'Restaurant Manager', 'KingScorpio Restaurant', 'hotel_manager', true),
  
  -- ACCOUNTANT (sees financials only)
  ('accountant@cosmhotel.gr', '65375049b9e4d7cad6c9ba286fdeb9394b28135a3e84136404cfccfdcc438894', 'Finance Officer', 'Porto Greco Beach & Village', 'accountant', true),
  
  -- VIEWER (read-only)
  ('viewer@cosmhotel.gr', '4a4b4c4d4e4f4a4b4c4d4e4f4a4b4c4d4e4f4a4b4c4d4e4f4a4b4c4d4e4f', 'Viewer User', 'Porto Greco Beach & Village', 'viewer', true);

-- ============================================================================
-- DONE! All users updated with new roles and hotels
-- ============================================================================
