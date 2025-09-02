import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { customColors, gradients, shadows, spacing, borderRadius } from '../theme/theme';

const LoadingScreen: React.FC = () => {
  return (
    <LinearGradient
      colors={gradients.phantom}
      style={styles.container}
    >
      <View style={styles.content}>
        <View style={[styles.logoContainer, shadows.large]}>
          <Ionicons
            name="shield"
            size={100}
            color={customColors.phantomRed}
          />
        </View>
        
        <Text style={styles.title}>PhantomNet C2</Text>
        <Text style={styles.subtitle}>Command & Control Center</Text>
        
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="white" />
          <Text style={styles.loadingText}>Initializing...</Text>
        </View>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  logoContainer: {
    width: 150,
    height: 150,
    borderRadius: borderRadius.round,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: spacing.xxl,
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
  },
  loadingText: {
    color: 'white',
    fontSize: 16,
    marginTop: spacing.md,
    opacity: 0.8,
  },
});

export default LoadingScreen;
