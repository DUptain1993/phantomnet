import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
} from 'react-native';
import { Card, Title, Paragraph, Button, Chip, ActivityIndicator } from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { customColors, gradients, shadows, spacing, borderRadius } from '../theme/theme';

const { width } = Dimensions.get('window');

interface DashboardStats {
  totalBots: number;
  activeBots: number;
  totalTargets: number;
  activeTasks: number;
  totalCommands: number;
  systemStatus: string;
}

interface RecentActivity {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

const DashboardScreen: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemHealth, setSystemHealth] = useState<string>('unknown');

  const { theme } = useTheme();
  const { user } = useAuth();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [statsData, activityData, healthData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getRecentActivity(),
        apiService.getSystemHealth(),
      ]);
      
      setStats(statsData);
      setRecentActivity(activityData);
      setSystemHealth(healthData.status);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    setIsRefreshing(false);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return customColors.phantomRed;
      case 'high':
        return customColors.phantomOrange;
      case 'medium':
        return customColors.phantomAmber;
      case 'low':
        return customColors.phantomGreen;
      default:
        return customColors.phantomGrey;
    }
  };

  const getSystemStatusColor = () => {
    switch (systemHealth) {
      case 'healthy':
        return customColors.phantomGreen;
      case 'warning':
        return customColors.phantomOrange;
      case 'error':
        return customColors.phantomRed;
      default:
        return customColors.phantomGrey;
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={[styles.loadingText, { color: theme.colors.text }]}>
          Loading Dashboard...
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
      showsVerticalScrollIndicator={false}
    >
      {/* Welcome Header */}
      <LinearGradient
        colors={gradients.phantom}
        style={styles.welcomeHeader}
      >
        <View style={styles.welcomeContent}>
          <Text style={styles.welcomeText}>
            Welcome back, {user?.username || 'Admin'}!
          </Text>
          <Text style={styles.welcomeSubtext}>
            PhantomNet Command & Control Center
          </Text>
        </View>
        <View style={styles.systemStatusContainer}>
          <Chip
            mode="outlined"
            textStyle={{ color: 'white' }}
            style={[
              styles.systemStatusChip,
              { borderColor: getSystemStatusColor() }
            ]}
          >
            System: {systemHealth}
          </Chip>
        </View>
      </LinearGradient>

      {/* Statistics Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statsRow}>
          <Card style={[styles.statCard, shadows.medium]}>
            <Card.Content style={styles.statContent}>
              <View style={styles.statIconContainer}>
                <Ionicons name="phone-portrait" size={24} color={customColors.phantomBlue} />
              </View>
              <Text style={[styles.statNumber, { color: theme.colors.text }]}>
                {stats?.activeBots || 0}
              </Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
                Active Bots
              </Text>
            </Card.Content>
          </Card>

          <Card style={[styles.statCard, shadows.medium]}>
            <Card.Content style={styles.statContent}>
              <View style={styles.statIconContainer}>
                <Ionicons name="target" size={24} color={customColors.phantomGreen} />
              </View>
              <Text style={[styles.statNumber, { color: theme.colors.text }]}>
                {stats?.totalTargets || 0}
              </Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
                Targets
              </Text>
            </Card.Content>
          </Card>
        </View>

        <View style={styles.statsRow}>
          <Card style={[styles.statCard, shadows.medium]}>
            <Card.Content style={styles.statContent}>
              <View style={styles.statIconContainer}>
                <Ionicons name="list" size={24} color={customColors.phantomOrange} />
              </View>
              <Text style={[styles.statNumber, { color: theme.colors.text }]}>
                {stats?.activeTasks || 0}
              </Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
                Active Tasks
              </Text>
            </Card.Content>
          </Card>

          <Card style={[styles.statCard, shadows.medium]}>
            <Card.Content style={styles.statContent}>
              <View style={styles.statIconContainer}>
                <Ionicons name="terminal" size={24} color={customColors.phantomPurple} />
              </View>
              <Text style={[styles.statNumber, { color: theme.colors.text }]}>
                {stats?.totalCommands || 0}
              </Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
                Commands
              </Text>
            </Card.Content>
          </Card>
        </View>
      </View>

      {/* Quick Actions */}
      <Card style={[styles.actionsCard, shadows.medium]}>
        <Card.Content>
          <Title style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Quick Actions
          </Title>
          <View style={styles.actionsGrid}>
            <TouchableOpacity style={styles.actionButton}>
              <View style={[styles.actionIcon, { backgroundColor: customColors.phantomBlue }]}>
                <Ionicons name="add" size={24} color="white" />
              </View>
              <Text style={[styles.actionText, { color: theme.colors.text }]}>Add Bot</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <View style={[styles.actionIcon, { backgroundColor: customColors.phantomGreen }]}>
                <Ionicons name="scan" size={24} color="white" />
              </View>
              <Text style={[styles.actionText, { color: theme.colors.text }]}>Scan Target</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <View style={[styles.actionIcon, { backgroundColor: customColors.phantomOrange }]}>
                <Ionicons name="play" size={24} color="white" />
              </View>
              <Text style={[styles.actionText, { color: theme.colors.text }]}>Start Task</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <View style={[styles.actionIcon, { backgroundColor: customColors.phantomPurple }]}>
                <Ionicons name="code" size={24} color="white" />
              </View>
              <Text style={[styles.actionText, { color: theme.colors.text }]}>Execute</Text>
            </TouchableOpacity>
          </View>
        </Card.Content>
      </Card>

      {/* Recent Activity */}
      <Card style={[styles.activityCard, shadows.medium]}>
        <Card.Content>
          <Title style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Recent Activity
          </Title>
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <View key={activity.id} style={styles.activityItem}>
                <View style={styles.activityHeader}>
                  <Chip
                    mode="outlined"
                    textStyle={{ fontSize: 10 }}
                    style={[
                      styles.severityChip,
                      { borderColor: getSeverityColor(activity.severity) }
                    ]}
                  >
                    {activity.severity.toUpperCase()}
                  </Chip>
                  <Text style={[styles.activityTime, { color: theme.colors.textSecondary }]}>
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </Text>
                </View>
                <Text style={[styles.activityMessage, { color: theme.colors.text }]}>
                  {activity.message}
                </Text>
              </View>
            ))
          ) : (
            <Text style={[styles.noActivityText, { color: theme.colors.textSecondary }]}>
              No recent activity
            </Text>
          )}
        </Card.Content>
      </Card>

      {/* System Info */}
      <Card style={[styles.systemCard, shadows.medium]}>
        <Card.Content>
          <Title style={[styles.sectionTitle, { color: theme.colors.text }]}>
            System Information
          </Title>
          <View style={styles.systemInfo}>
            <View style={styles.systemInfoRow}>
              <Text style={[styles.systemInfoLabel, { color: theme.colors.textSecondary }]}>
                Status:
              </Text>
              <Text style={[styles.systemInfoValue, { color: getSystemStatusColor() }]}>
                {systemHealth}
              </Text>
            </View>
            <View style={styles.systemInfoRow}>
              <Text style={[styles.systemInfoLabel, { color: theme.colors.textSecondary }]}>
                Total Bots:
              </Text>
              <Text style={[styles.systemInfoValue, { color: theme.colors.text }]}>
                {stats?.totalBots || 0}
              </Text>
            </View>
            <View style={styles.systemInfoRow}>
              <Text style={[styles.systemInfoLabel, { color: theme.colors.textSecondary }]}>
                Last Update:
              </Text>
              <Text style={[styles.systemInfoValue, { color: theme.colors.text }]}>
                {new Date().toLocaleString()}
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: 16,
  },
  welcomeHeader: {
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  welcomeContent: {
    flex: 1,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: spacing.xs,
  },
  welcomeSubtext: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  systemStatusContainer: {
    marginTop: spacing.md,
  },
  systemStatusChip: {
    alignSelf: 'flex-start',
  },
  statsContainer: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  statCard: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
  statContent: {
    alignItems: 'center',
    padding: spacing.md,
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.round,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: spacing.xs,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  actionsCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: spacing.md,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: (width - spacing.lg * 4) / 2,
    alignItems: 'center',
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  actionIcon: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.round,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  actionText: {
    fontSize: 12,
    textAlign: 'center',
  },
  activityCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  activityItem: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 0, 0, 0.1)',
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  severityChip: {
    height: 20,
  },
  activityTime: {
    fontSize: 10,
  },
  activityMessage: {
    fontSize: 14,
    lineHeight: 20,
  },
  noActivityText: {
    textAlign: 'center',
    fontStyle: 'italic',
    padding: spacing.lg,
  },
  systemCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  systemInfo: {
    marginTop: spacing.sm,
  },
  systemInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: spacing.xs,
  },
  systemInfoLabel: {
    fontSize: 14,
  },
  systemInfoValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default DashboardScreen;
