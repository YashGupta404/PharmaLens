/**
 * Auth Context
 * 
 * React context for managing authentication state throughout the app.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { supabase, getCurrentUser, onAuthStateChange } from '@/lib/supabase';
import { User } from '@supabase/supabase-js';

interface UserProfile {
    id: string;
    name: string;
    email: string;
    location: string;
    age: number;
    sex: string;
}

interface AuthContextType {
    user: User | null;
    profile: UserProfile | null;
    loading: boolean;
    signUp: (email: string, password: string, profile: Omit<UserProfile, 'id'>) => Promise<{ error: Error | null }>;
    signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
    signOut: () => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    // Load user profile from Supabase
    const loadProfile = async (userId: string) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            if (error) throw error;
            setProfile(data);
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    };

    useEffect(() => {
        // Check for existing session
        getCurrentUser().then(({ user }) => {
            setUser(user);
            if (user) {
                loadProfile(user.id);
            }
            setLoading(false);
        });

        // Listen for auth changes
        const { data: { subscription } } = onAuthStateChange((event, session) => {
            setUser(session?.user ?? null);
            if (session?.user) {
                loadProfile(session.user.id);
            } else {
                setProfile(null);
            }
        });

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const signUp = async (email: string, password: string, profileData: Omit<UserProfile, 'id'>) => {
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
        });

        if (error) return { error };

        // Create profile
        if (data.user) {
            const { error: profileError } = await supabase
                .from('profiles')
                .insert({
                    id: data.user.id,
                    ...profileData,
                });

            if (profileError) {
                console.error('Profile creation error:', profileError);
            }
        }

        return { error: null };
    };

    const signIn = async (email: string, password: string) => {
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        return { error };
    };

    const signOut = async () => {
        await supabase.auth.signOut();
        setUser(null);
        setProfile(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                profile,
                loading,
                signUp,
                signIn,
                signOut,
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
