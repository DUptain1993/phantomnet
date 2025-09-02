# PhantomNet C2 Mobile App

A React Native mobile application for the PhantomNet Command & Control Center, designed to work seamlessly with Expo Go.

## 🚀 Features

- **Modern UI/UX**: Beautiful, responsive design with dark/light theme support
- **Cross-Platform**: Works on both Android and iOS devices
- **Expo Compatible**: Fully compatible with Expo Go for easy testing
- **Real-time Dashboard**: Live statistics and system monitoring
- **Bot Management**: View, manage, and control bot instances
- **Target Management**: Monitor and manage target systems
- **Command Execution**: Execute commands on remote systems
- **Task Automation**: Schedule and manage automated tasks
- **Secure Authentication**: Secure login with token-based authentication
- **Offline Support**: Works offline with cached data
- **Push Notifications**: Real-time alerts and notifications

## 📱 Screenshots

*Screenshots will be added here*

## 🛠️ Tech Stack

- **React Native**: 0.72.6
- **Expo**: ~49.0.0
- **TypeScript**: Full type safety
- **React Navigation**: Navigation between screens
- **React Native Paper**: Material Design components
- **Expo Linear Gradient**: Beautiful gradient backgrounds
- **Axios**: HTTP client for API communication
- **Expo Secure Store**: Secure storage for sensitive data

## 📋 Prerequisites

- Node.js 16+ 
- npm or yarn
- Expo CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)
- Expo Go app on your mobile device

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mobile-app
npm install
# or
yarn install
```

### 2. Start Development Server

```bash
npm start
# or
yarn start
# or
expo start
```

### 3. Run on Device

- Install **Expo Go** from App Store/Google Play
- Scan the QR code with your device's camera
- The app will load on your device

### 4. Run on Emulator

```bash
# Android
npm run android
# or
expo start --android

# iOS (macOS only)
npm run ios
# or
expo start --ios
```

## 🔧 Configuration

### API Configuration

Update the API base URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8443'  // Android emulator localhost
  : 'https://your-production-domain.com'; // Production URL
```

### Environment Variables

Create a `.env` file in the root directory:

```bash
# API Configuration
API_BASE_URL=https://your-domain.com
API_TIMEOUT=10000

# App Configuration
APP_NAME=PhantomNet C2
APP_VERSION=1.0.0

# Security
ENCRYPTION_KEY=your-encryption-key
```

## 📁 Project Structure

```
mobile-app/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── LoadingScreen.tsx
│   │   └── CustomDrawerContent.tsx
│   ├── context/            # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── screens/            # App screens
│   │   ├── LoginScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── BotsScreen.tsx
│   │   ├── TargetsScreen.tsx
│   │   ├── CommandsScreen.tsx
│   │   ├── TasksScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── services/           # API and external services
│   │   └── api.ts
│   ├── theme/              # Theme configuration
│   │   └── theme.ts
│   └── utils/              # Utility functions
├── assets/                 # Images, fonts, etc.
├── App.tsx                 # Main app component
├── app.json               # Expo configuration
├── package.json           # Dependencies
└── README.md              # This file
```

## 🎨 Theming

The app supports both light and dark themes with a comprehensive design system:

- **Custom Colors**: PhantomNet brand colors
- **Gradients**: Beautiful gradient combinations
- **Shadows**: Material Design shadows
- **Typography**: Consistent text styles
- **Spacing**: Standardized spacing system
- **Border Radius**: Consistent corner rounding

### Theme Switching

Themes automatically adapt to system preferences and can be manually toggled in settings.

## 🔐 Authentication

- **Secure Storage**: Uses Expo Secure Store for sensitive data
- **Token Management**: Automatic token refresh and management
- **Session Persistence**: Maintains login state across app restarts
- **Logout**: Secure logout with token cleanup

## 📊 Dashboard Features

- **Real-time Stats**: Live bot, target, and task statistics
- **System Health**: Monitor system status and health
- **Recent Activity**: View recent system events
- **Quick Actions**: Fast access to common operations
- **Status Indicators**: Visual status representation

## 🤖 Bot Management

- **Bot Overview**: List all bot instances
- **Status Monitoring**: Real-time bot status
- **Action Controls**: Connect, disconnect, restart bots
- **Capability Display**: Show bot capabilities
- **Search & Filter**: Find specific bots quickly

## 🎯 Target Management

- **Target Discovery**: Scan and discover targets
- **Vulnerability Assessment**: Identify security weaknesses
- **Exploitation Tools**: Execute payloads and exploits
- **Status Tracking**: Monitor target status

## ⚡ Command Execution

- **Command Library**: Pre-built command templates
- **Custom Commands**: Create custom commands
- **Execution History**: Track command results
- **Real-time Output**: Live command output

## 📋 Task Automation

- **Task Scheduling**: Schedule automated tasks
- **Workflow Builder**: Create complex task workflows
- **Status Monitoring**: Track task execution
- **Result Collection**: Gather and analyze results

## 🔧 Development

### Adding New Screens

1. Create a new screen component in `src/screens/`
2. Add navigation routes in `App.tsx`
3. Update the drawer navigation if needed
4. Add any required API endpoints

### Adding New Components

1. Create component in `src/components/`
2. Export with proper TypeScript interfaces
3. Add to the appropriate screen
4. Follow the existing design patterns

### API Integration

1. Add new endpoints in `src/services/api.ts`
2. Create service functions for the endpoints
3. Use in components with proper error handling
4. Add loading states and user feedback

## 🧪 Testing

### Unit Tests

```bash
npm test
# or
yarn test
```

### Integration Tests

```bash
npm run test:integration
# or
yarn test:integration
```

### E2E Tests

```bash
npm run test:e2e
# or
yarn test:e2e
```

## 📱 Building for Production

### Android APK

```bash
expo build:android
```

### Android AAB

```bash
expo build:android -t app-bundle
```

### iOS IPA

```bash
expo build:ios
```

### Web Build

```bash
expo build:web
```

## 🚀 Deployment

### Expo Application Services (EAS)

1. Install EAS CLI:
```bash
npm install -g @expo/eas-cli
```

2. Configure EAS:
```bash
eas build:configure
```

3. Build and submit:
```bash
eas build --platform all
eas submit --platform all
```

### Manual Build

1. Eject from Expo:
```bash
expo eject
```

2. Build manually:
```bash
# Android
cd android && ./gradlew assembleRelease

# iOS
cd ios && xcodebuild -workspace YourApp.xcworkspace -scheme YourApp -configuration Release
```

## 🔒 Security Features

- **Secure Storage**: Sensitive data encrypted at rest
- **Network Security**: HTTPS-only API communication
- **Token Management**: Secure JWT token handling
- **Input Validation**: Client-side input sanitization
- **Session Management**: Secure session handling

## 📈 Performance

- **Lazy Loading**: Screens load on demand
- **Image Optimization**: Optimized image loading
- **Memory Management**: Efficient memory usage
- **Network Caching**: Intelligent API response caching
- **Bundle Optimization**: Minimal app bundle size

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `expo start -c`
2. **Build failures**: Check Expo SDK compatibility
3. **API connection**: Verify API URL and network settings
4. **Authentication**: Check token validity and expiration

### Debug Mode

Enable debug mode in development:

```typescript
// In App.tsx
if (__DEV__) {
  console.log('Debug mode enabled');
}
```

### Logging

Use the built-in logging system:

```typescript
import { logger } from '../utils/logger';

logger.info('User logged in', { userId: user.id });
logger.error('API call failed', error);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Use TypeScript for all new code
- Follow existing component patterns
- Use proper error handling
- Add JSDoc comments for complex functions
- Maintain consistent naming conventions

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide
- Contact the development team

## 🔄 Updates

### Updating Dependencies

```bash
npm update
# or
yarn upgrade
```

### Updating Expo SDK

```bash
expo upgrade
```

### Checking for Updates

```bash
expo doctor
```

---

**PhantomNet C2 Mobile App** - Command & Control at your fingertips 📱
