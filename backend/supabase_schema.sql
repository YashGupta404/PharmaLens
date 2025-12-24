-- Create search_history table
CREATE TABLE IF NOT EXISTS search_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  medicine_name TEXT NOT NULL,
  search_type TEXT DEFAULT 'manual' CHECK (search_type IN ('prescription', 'manual')),
  results_count INTEGER DEFAULT 0,
  cheapest_price DECIMAL(10,2),
  cheapest_pharmacy TEXT,
  prescription_image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at DESC);

-- Enable Row Level Security
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own history" ON search_history;
DROP POLICY IF EXISTS "Users can insert own history" ON search_history;
DROP POLICY IF EXISTS "Users can delete own history" ON search_history;

-- Policy: Users can only see their own history
CREATE POLICY "Users can view own history" ON search_history
  FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own history
CREATE POLICY "Users can insert own history" ON search_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own history
CREATE POLICY "Users can delete own history" ON search_history
  FOR DELETE USING (auth.uid() = user_id);
