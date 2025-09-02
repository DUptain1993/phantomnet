import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card, Title } from 'react-native-paper';
import { useTheme } from '../context/ThemeContext';

const CommandsScreen: React.FC = () => {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={[styles.title, { color: theme.colors.text }]}>
            Commands Management
          </Title>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Command execution and management functionality coming soon...
          </Text>
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginTop: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
});

export default CommandsScreen;
