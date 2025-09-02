import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { TextInput, Button, Card, Title, Paragraph } from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { customColors, gradients, shadows, spacing, borderRadius } from '../theme/theme';

const { width, height } = Dimensions.get('window');

const LoginScreen: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { login } = useAuth();
  const { theme, isDark } = useTheme();

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter both username and password');
      return;
    }

    setIsLoading(true);
    try {
      const success = await login(username.trim(), password);
      if (!success) {
        Alert.alert('Login Failed', 'Invalid username or password');
      }
    } catch (error) {
      Alert.alert('Error', 'An error occurred during login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <LinearGradient
        colors={isDark ? gradients.dark : gradients.phantom}
        style={styles.gradient}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={[styles.logoContainer, shadows.large]}>
              <Ionicons
                name="shield"
                size={80}
                color={customColors.phantomRed}
              />
            </View>
            <Title style={[styles.title, { color: theme.colors.onPrimary }]}>
              PhantomNet C2
            </Title>
            <Paragraph style={[styles.subtitle, { color: theme.colors.onPrimary }]}>
              Command & Control Center
            </Paragraph>
          </View>

          {/* Login Form */}
          <Card style={[styles.loginCard, shadows.medium]}>
            <Card.Content style={styles.cardContent}>
              <Title style={[styles.cardTitle, { color: theme.colors.text }]}>
                Admin Login
              </Title>
              
              <TextInput
                label="Username"
                value={username}
                onChangeText={setUsername}
                mode="outlined"
                style={styles.input}
                left={<TextInput.Icon icon="account" />}
                autoCapitalize="none"
                autoCorrect={false}
                disabled={isLoading}
              />

              <TextInput
                label="Password"
                value={password}
                onChangeText={setPassword}
                mode="outlined"
                style={styles.input}
                secureTextEntry={!showPassword}
                left={<TextInput.Icon icon="lock" />}
                right={
                  <TextInput.Icon
                    icon={showPassword ? "eye-off" : "eye"}
                    onPress={() => setShowPassword(!showPassword)}
                  />
                }
                autoCapitalize="none"
                autoCorrect={false}
                disabled={isLoading}
              />

              <Button
                mode="contained"
                onPress={handleLogin}
                loading={isLoading}
                disabled={isLoading}
                style={[styles.loginButton, { backgroundColor: customColors.phantomRed }]}
                contentStyle={styles.buttonContent}
                labelStyle={styles.buttonLabel}
              >
                {isLoading ? 'Logging In...' : 'Login'}
              </Button>

              <View style={styles.credentials}>
                <Text style={[styles.credentialsText, { color: theme.colors.textSecondary }]}>
                  Default Credentials:
                </Text>
                <Text style={[styles.credentialsText, { color: theme.colors.textSecondary }]}>
                  Username: admin
                </Text>
                <Text style={[styles.credentialsText, { color: theme.colors.textSecondary }]}>
                  Password: admin123
                </Text>
              </View>
            </Card.Content>
          </Card>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={[styles.footerText, { color: theme.colors.onPrimary }]}>
              Secure Access Only
            </Text>
            <Text style={[styles.footerText, { color: theme.colors.onPrimary }]}>
              © 2024 PhantomNet C2
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xxl,
  },
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: borderRadius.round,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.8,
  },
  loginCard: {
    marginBottom: spacing.xl,
    borderRadius: borderRadius.lg,
  },
  cardContent: {
    padding: spacing.lg,
  },
  cardTitle: {
    textAlign: 'center',
    marginBottom: spacing.lg,
    fontSize: 24,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: spacing.md,
  },
  loginButton: {
    marginTop: spacing.md,
    marginBottom: spacing.lg,
    borderRadius: borderRadius.md,
  },
  buttonContent: {
    paddingVertical: spacing.sm,
  },
  buttonLabel: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  credentials: {
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: borderRadius.md,
  },
  credentialsText: {
    fontSize: 12,
    marginBottom: spacing.xs,
  },
  footer: {
    alignItems: 'center',
    marginTop: spacing.xl,
  },
  footerText: {
    fontSize: 12,
    opacity: 0.7,
    marginBottom: spacing.xs,
  },
});

export default LoginScreen;
