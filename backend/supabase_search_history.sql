-- Search History Table for PharmaLens
-- Run this in your Supabase SQL Editor

-- Create the search_history table
CREATE TABLE IF NOT EXISTS public.search_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    medicine_name TEXT NOT NULL,
    search_type TEXT DEFAULT 'manual' CHECK (search_type IN ('prescription', 'manual')),
    results_count INTEGER DEFAULT 0,
    cheapest_price DECIMAL(10, 2),
    cheapest_pharmacy TEXT,
    prescription_image_url TEXT,
    results_data JSONB,  -- Store full search results
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS search_history_user_id_idx ON public.search_history(user_id);
CREATE INDEX IF NOT EXISTS search_history_created_at_idx ON public.search_history(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.search_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own search history
CREATE POLICY "Users can view own search history" ON public.search_history
    FOR SELECT
    USING (auth.uid() = user_id);

-- RLS Policy: Users can insert their own search history
CREATE POLICY "Users can insert own search history" ON public.search_history
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can delete their own search history
CREATE POLICY "Users can delete own search history" ON public.search_history
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant access to authenticated users
GRANT ALL ON public.search_history TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Done! Your search_history table is ready.
