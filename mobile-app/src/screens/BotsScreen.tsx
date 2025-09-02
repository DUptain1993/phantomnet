import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Card, Title, Paragraph, Button, Chip, FAB, Searchbar, ActivityIndicator } from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import { apiService } from '../services/api';
import { customColors, shadows, spacing, borderRadius } from '../theme/theme';

interface Bot {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  ip: string;
  os: string;
  lastSeen: string;
  version: string;
  capabilities: string[];
}

const BotsScreen: React.FC = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [filteredBots, setFilteredBots] = useState<Bot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);

  const { theme } = useTheme();

  useEffect(() => {
    loadBots();
  }, []);

  useEffect(() => {
    filterBots();
  }, [searchQuery, selectedStatus, bots]);

  const loadBots = async () => {
    try {
      setIsLoading(true);
      const botsData = await apiService.getBots();
      setBots(botsData);
    } catch (error) {
      console.error('Error loading bots:', error);
      Alert.alert('Error', 'Failed to load bots');
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadBots();
    setIsRefreshing(false);
  };

  const filterBots = () => {
    let filtered = bots;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(bot =>
        bot.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        bot.ip.includes(searchQuery) ||
        bot.os.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by status
    if (selectedStatus) {
      filtered = filtered.filter(bot => bot.status === selectedStatus);
    }

    setFilteredBots(filtered);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return customColors.phantomGreen;
      case 'offline':
        return customColors.phantomGrey;
      case 'busy':
        return customColors.phantomOrange;
      case 'error':
        return customColors.phantomRed;
      default:
        return customColors.phantomGrey;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return 'checkmark-circle';
      case 'offline':
        return 'close-circle';
      case 'busy':
        return 'time';
      case 'error':
        return 'alert-circle';
      default:
        return 'help-circle';
    }
  };

  const handleBotAction = (bot: Bot, action: string) => {
    Alert.alert(
      `${action} Bot`,
      `Are you sure you want to ${action.toLowerCase()} ${bot.name}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: action, onPress: () => executeBotAction(bot.id, action) },
      ]
    );
  };

  const executeBotAction = async (botId: string, action: string) => {
    try {
      switch (action) {
        case 'Connect':
          // Implement connect logic
          break;
        case 'Disconnect':
          // Implement disconnect logic
          break;
        case 'Restart':
          // Implement restart logic
          break;
        case 'Delete':
          await apiService.deleteBot(botId);
          await loadBots();
          break;
      }
    } catch (error) {
      console.error(`Error executing ${action}:`, error);
      Alert.alert('Error', `Failed to ${action.toLowerCase()} bot`);
    }
  };

  const getStatusCounts = () => {
    const counts = {
      online: 0,
      offline: 0,
      busy: 0,
      error: 0,
    };
    bots.forEach(bot => {
      counts[bot.status]++;
    });
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={[styles.loadingText, { color: theme.colors.text }]}>
          Loading Bots...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="Search bots..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchBar}
        />
      </View>

      {/* Status Summary */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.statusScroll}>
        <TouchableOpacity
          style={[
            styles.statusChip,
            selectedStatus === null && styles.statusChipSelected
          ]}
          onPress={() => setSelectedStatus(null)}
        >
          <Text style={[styles.statusChipText, { color: theme.colors.text }]}>
            All ({bots.length})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.statusChip,
            selectedStatus === 'online' && styles.statusChipSelected
          ]}
          onPress={() => setSelectedStatus('online')}
        >
          <Text style={[styles.statusChipText, { color: customColors.phantomGreen }]}>
            Online ({statusCounts.online})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.statusChip,
            selectedStatus === 'offline' && styles.statusChipSelected
          ]}
          onPress={() => setSelectedStatus('offline')}
        >
          <Text style={[styles.statusChipText, { color: customColors.phantomGrey }]}>
            Offline ({statusCounts.offline})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.statusChip,
            selectedStatus === 'busy' && styles.statusChipSelected
          ]}
          onPress={() => setSelectedStatus('busy')}
        >
          <Text style={[styles.statusChipText, { color: customColors.phantomOrange }]}>
            Busy ({statusCounts.busy})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.statusChip,
            selectedStatus === 'error' && styles.statusChipSelected
          ]}
          onPress={() => setSelectedStatus('error')}
        >
          <Text style={[styles.statusChipText, { color: customColors.phantomRed }]}>
            Error ({statusCounts.error})
          </Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Bots List */}
      <ScrollView
        style={styles.botsList}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {filteredBots.length > 0 ? (
          filteredBots.map((bot) => (
            <Card key={bot.id} style={[styles.botCard, shadows.medium]}>
              <Card.Content>
                <View style={styles.botHeader}>
                  <View style={styles.botInfo}>
                    <Title style={[styles.botName, { color: theme.colors.text }]}>
                      {bot.name}
                    </Title>
                    <View style={styles.botStatus}>
                      <Ionicons
                        name={getStatusIcon(bot.status) as any}
                        size={16}
                        color={getStatusColor(bot.status)}
                      />
                      <Chip
                        mode="outlined"
                        textStyle={{ fontSize: 10 }}
                        style={[
                          styles.statusChip,
                          { borderColor: getStatusColor(bot.status) }
                        ]}
                      >
                        {bot.status.toUpperCase()}
                      </Chip>
                    </View>
                  </View>
                  <View style={styles.botActions}>
                    <TouchableOpacity
                      style={[styles.actionButton, { backgroundColor: customColors.phantomBlue }]}
                      onPress={() => handleBotAction(bot, 'Connect')}
                    >
                      <Ionicons name="link" size={16} color="white" />
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.actionButton, { backgroundColor: customColors.phantomOrange }]}
                      onPress={() => handleBotAction(bot, 'Restart')}
                    >
                      <Ionicons name="refresh" size={16} color="white" />
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.actionButton, { backgroundColor: customColors.phantomRed }]}
                      onPress={() => handleBotAction(bot, 'Delete')}
                    >
                      <Ionicons name="trash" size={16} color="white" />
                    </TouchableOpacity>
                  </View>
                </View>

                <View style={styles.botDetails}>
                  <View style={styles.detailRow}>
                    <Text style={[styles.detailLabel, { color: theme.colors.textSecondary }]}>
                      IP Address:
                    </Text>
                    <Text style={[styles.detailValue, { color: theme.colors.text }]}>
                      {bot.ip}
                    </Text>
                  </View>
                  
                  <View style={styles.detailRow}>
                    <Text style={[styles.detailLabel, { color: theme.colors.textSecondary }]}>
                      OS:
                    </Text>
                    <Text style={[styles.detailValue, { color: theme.colors.text }]}>
                      {bot.os}
                    </Text>
                  </View>
                  
                  <View style={styles.detailRow}>
                    <Text style={[styles.detailLabel, { color: theme.colors.textSecondary }]}>
                      Version:
                    </Text>
                    <Text style={[styles.detailValue, { color: theme.colors.text }]}>
                      {bot.version}
                    </Text>
                  </View>
                  
                  <View style={styles.detailRow}>
                    <Text style={[styles.detailLabel, { color: theme.colors.textSecondary }]}>
                      Last Seen:
                    </Text>
                    <Text style={[styles.detailValue, { color: theme.colors.text }]}>
                      {new Date(bot.lastSeen).toLocaleString()}
                    </Text>
                  </View>
                </View>

                {bot.capabilities.length > 0 && (
                  <View style={styles.capabilities}>
                    <Text style={[styles.capabilitiesTitle, { color: theme.colors.textSecondary }]}>
                      Capabilities:
                    </Text>
                    <View style={styles.capabilitiesList}>
                      {bot.capabilities.map((capability, index) => (
                        <Chip
                          key={index}
                          mode="outlined"
                          textStyle={{ fontSize: 10 }}
                          style={styles.capabilityChip}
                        >
                          {capability}
                        </Chip>
                      ))}
                    </View>
                  </View>
                )}
              </Card.Content>
            </Card>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="phone-portrait-outline" size={64} color={theme.colors.textSecondary} />
            <Text style={[styles.emptyStateText, { color: theme.colors.textSecondary }]}>
              {searchQuery || selectedStatus ? 'No bots found' : 'No bots available'}
            </Text>
            <Text style={[styles.emptyStateSubtext, { color: theme.colors.textSecondary }]}>
              {searchQuery || selectedStatus ? 'Try adjusting your search or filters' : 'Add your first bot to get started'}
            </Text>
          </View>
        )}
      </ScrollView>

      {/* FAB for adding new bot */}
      <FAB
        style={[styles.fab, { backgroundColor: customColors.phantomRed }]}
        icon="plus"
        onPress={() => Alert.alert('Add Bot', 'Add bot functionality coming soon')}
      />
    </View>
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
  searchContainer: {
    padding: spacing.md,
  },
  searchBar: {
    elevation: 2,
  },
  statusScroll: {
    paddingHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  statusChip: {
    marginRight: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.1)',
  },
  statusChipSelected: {
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
  },
  statusChipText: {
    fontSize: 12,
    fontWeight: '500',
  },
  botsList: {
    flex: 1,
    paddingHorizontal: spacing.md,
  },
  botCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.md,
  },
  botHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  botInfo: {
    flex: 1,
  },
  botName: {
    fontSize: 18,
    marginBottom: spacing.xs,
  },
  botStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  botActions: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  actionButton: {
    width: 32,
    height: 32,
    borderRadius: borderRadius.round,
    justifyContent: 'center',
    alignItems: 'center',
  },
  botDetails: {
    marginBottom: spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  detailLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  capabilities: {
    marginTop: spacing.sm,
  },
  capabilitiesTitle: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: spacing.xs,
  },
  capabilitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  capabilityChip: {
    height: 20,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing.xxl,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: spacing.md,
    marginBottom: spacing.xs,
  },
  emptyStateSubtext: {
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: spacing.lg,
  },
  fab: {
    position: 'absolute',
    margin: spacing.md,
    right: 0,
    bottom: 0,
  },
});

export default BotsScreen;
