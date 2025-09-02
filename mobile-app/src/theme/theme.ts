import { MD3DarkTheme, MD3LightTheme } from 'react-native-paper';

export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#FF5722',
    secondary: '#2196F3',
    accent: '#4CAF50',
    background: '#121212',
    surface: '#1E1E1E',
    text: '#FFFFFF',
    textSecondary: '#B0B0B0',
    border: '#333333',
    error: '#F44336',
    warning: '#FF9800',
    success: '#4CAF50',
    info: '#2196F3',
    card: '#2D2D2D',
    notification: '#FF5722',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onBackground: '#FFFFFF',
    onSurface: '#FFFFFF',
    onError: '#FFFFFF',
    onWarning: '#FFFFFF',
    onSuccess: '#FFFFFF',
    onInfo: '#FFFFFF',
  },
  dark: true,
};

export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#FF5722',
    secondary: '#2196F3',
    accent: '#4CAF50',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    text: '#212121',
    textSecondary: '#757575',
    border: '#E0E0E0',
    error: '#F44336',
    warning: '#FF9800',
    success: '#4CAF50',
    info: '#2196F3',
    card: '#FFFFFF',
    notification: '#FF5722',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onBackground: '#212121',
    onSurface: '#212121',
    onError: '#FFFFFF',
    onWarning: '#FFFFFF',
    onSuccess: '#FFFFFF',
    onInfo: '#FFFFFF',
  },
  dark: false,
};

export const customColors = {
  phantomRed: '#FF5722',
  phantomBlue: '#2196F3',
  phantomGreen: '#4CAF50',
  phantomOrange: '#FF9800',
  phantomPurple: '#9C27B0',
  phantomTeal: '#009688',
  phantomIndigo: '#3F51B5',
  phantomPink: '#E91E63',
  phantomLime: '#CDDC39',
  phantomCyan: '#00BCD4',
  phantomAmber: '#FFC107',
  phantomDeepPurple: '#673AB7',
  phantomDeepOrange: '#FF5722',
  phantomBlueGrey: '#607D8B',
  phantomBrown: '#795548',
  phantomGrey: '#9E9E9E',
  phantomLightBlue: '#03A9F4',
  phantomLightGreen: '#8BC34A',
  phantomLightCyan: '#4DD0E1',
  phantomLightPink: '#F8BBD9',
  phantomLightTeal: '#4DB6AC',
  phantomLightLime: '#DCE775',
  phantomLightYellow: '#FFF59D',
  phantomLightOrange: '#FFCC80',
  phantomLightRed: '#EF9A9A',
  phantomLightPurple: '#CE93D8',
  phantomLightIndigo: '#9FA8DA',
  phantomLightBlueGrey: '#B0BEC5',
  phantomLightBrown: '#BCAAA4',
  phantomLightGrey: '#EEEEEE',
};

export const gradients = {
  primary: ['#1e3c72', '#2a5298'],
  secondary: ['#FF5722', '#FF9800'],
  success: ['#4CAF50', '#8BC34A'],
  warning: ['#FF9800', '#FFC107'],
  error: ['#F44336', '#E91E63'],
  info: ['#2196F3', '#03A9F4'],
  dark: ['#121212', '#1E1E1E'],
  light: ['#F5F5F5', '#FFFFFF'],
  phantom: ['#1e3c72', '#FF5722'],
  sunset: ['#FF5722', '#FF9800', '#FFC107'],
  ocean: ['#1e3c72', '#2196F3', '#00BCD4'],
  forest: ['#4CAF50', '#8BC34A', '#CDDC39'],
  fire: ['#F44336', '#FF5722', '#FF9800'],
  ice: ['#2196F3', '#00BCD4', '#4DD0E1'],
  rainbow: ['#F44336', '#FF9800', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0'],
};

export const shadows = {
  small: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
  large: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.37,
    shadowRadius: 7.49,
    elevation: 12,
  },
  extraLarge: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 10,
    },
    shadowOpacity: 0.44,
    shadowRadius: 10.32,
    elevation: 16,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

export const borderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  round: 50,
};

export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold',
    lineHeight: 40,
  },
  h2: {
    fontSize: 28,
    fontWeight: 'bold',
    lineHeight: 36,
  },
  h3: {
    fontSize: 24,
    fontWeight: 'bold',
    lineHeight: 32,
  },
  h4: {
    fontSize: 20,
    fontWeight: 'bold',
    lineHeight: 28,
  },
  h5: {
    fontSize: 18,
    fontWeight: 'bold',
    lineHeight: 24,
  },
  h6: {
    fontSize: 16,
    fontWeight: 'bold',
    lineHeight: 22,
  },
  body1: {
    fontSize: 16,
    fontWeight: 'normal',
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: 'normal',
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal',
    lineHeight: 16,
  },
  button: {
    fontSize: 14,
    fontWeight: 'bold',
    lineHeight: 20,
    textTransform: 'uppercase',
  },
  overline: {
    fontSize: 10,
    fontWeight: 'bold',
    lineHeight: 14,
    textTransform: 'uppercase',
    letterSpacing: 1.5,
  },
};

export default {
  darkTheme,
  lightTheme,
  customColors,
  gradients,
  shadows,
  spacing,
  borderRadius,
  typography,
};
