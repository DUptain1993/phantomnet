import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { DrawerContentScrollView, DrawerItem } from '@react-navigation/drawer';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { customColors, spacing, borderRadius } from '../theme/theme';

const CustomDrawerContent: React.FC<any> = (props) => {
  const { theme } = useTheme();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      // Navigation will be handled by the auth context
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <DrawerContentScrollView
      {...props}
      style={[styles.container, { backgroundColor: theme.colors.surface }]}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Ionicons
            name="shield"
            size={48}
            color={customColors.phantomRed}
          />
        </View>
        <Text style={[styles.appName, { color: theme.colors.text }]}>
          PhantomNet C2
        </Text>
        <Text style={[styles.appSubtitle, { color: theme.colors.textSecondary }]}>
          Command & Control
        </Text>
      </View>

      {/* User Info */}
      <View style={styles.userSection}>
        <View style={styles.userAvatar}>
          <Ionicons
            name="person"
            size={32}
            color={theme.colors.primary}
          />
        </View>
        <View style={styles.userInfo}>
          <Text style={[styles.userName, { color: theme.colors.text }]}>
            {user?.username || 'Admin'}
          </Text>
          <Text style={[styles.userRole, { color: theme.colors.textSecondary }]}>
            {user?.role || 'Administrator'}
          </Text>
        </View>
      </View>

      {/* Drawer Items */}
      <View style={styles.drawerItems}>
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          )}
          label="Dashboard"
          onPress={() => props.navigation.navigate('MainTabs')}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
        
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="phone-portrait" size={size} color={color} />
          )}
          label="Bots"
          onPress={() => props.navigation.navigate('MainTabs', { screen: 'Bots' })}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
        
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="target" size={size} color={color} />
          )}
          label="Targets"
          onPress={() => props.navigation.navigate('MainTabs', { screen: 'Targets' })}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
        
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="terminal" size={size} color={color} />
          )}
          label="Commands"
          onPress={() => props.navigation.navigate('MainTabs', { screen: 'Commands' })}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
        
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="list" size={size} color={color} />
          )}
          label="Tasks"
          onPress={() => props.navigation.navigate('MainTabs', { screen: 'Tasks' })}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
      </View>

      {/* Divider */}
      <View style={[styles.divider, { backgroundColor: theme.colors.border }]} />

      {/* Additional Items */}
      <View style={styles.additionalItems}>
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="settings" size={size} color={color} />
          )}
          label="Settings"
          onPress={() => props.navigation.navigate('Settings')}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
        
        <DrawerItem
          icon={({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          )}
          label="Profile"
          onPress={() => props.navigation.navigate('Profile')}
          activeTintColor={customColors.phantomRed}
          inactiveTintColor={theme.colors.text}
        />
      </View>

      {/* Logout Button */}
      <View style={styles.logoutSection}>
        <TouchableOpacity
          style={[styles.logoutButton, { backgroundColor: customColors.phantomRed }]}
          onPress={handleLogout}
        >
          <Ionicons name="log-out-outline" size={20} color="white" />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={[styles.footerText, { color: theme.colors.textSecondary }]}>
          PhantomNet C2 v1.0.0
        </Text>
        <Text style={[styles.footerText, { color: theme.colors.textSecondary }]}>
          © 2024 All Rights Reserved
        </Text>
      </View>
    </DrawerContentScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 0, 0, 0.1)',
  },
  logoContainer: {
    width: 64,
    height: 64,
    borderRadius: borderRadius.round,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  appName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: spacing.xs,
  },
  appSubtitle: {
    fontSize: 12,
    opacity: 0.7,
  },
  userSection: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 0, 0, 0.1)',
  },
  userAvatar: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.round,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: spacing.xs,
  },
  userRole: {
    fontSize: 12,
    opacity: 0.7,
  },
  drawerItems: {
    paddingTop: spacing.sm,
  },
  divider: {
    height: 1,
    marginVertical: spacing.md,
    marginHorizontal: spacing.md,
  },
  additionalItems: {
    paddingBottom: spacing.md,
  },
  logoutSection: {
    padding: spacing.md,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0, 0, 0, 0.1)',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.md,
  },
  logoutText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: spacing.sm,
  },
  footer: {
    alignItems: 'center',
    padding: spacing.md,
    marginTop: 'auto',
  },
  footerText: {
    fontSize: 10,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
});

export default CustomDrawerContent;
