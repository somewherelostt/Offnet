import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TextInput,
} from "react-native";

// Color scheme for Offnet
export const OffnetColors = {
  primary: "#6366f1", // Indigo
  secondary: "#8b5cf6", // Purple
  accent: "#06b6d4", // Cyan
  background: "#0f172a", // Dark blue
  surface: "#1e293b", // Lighter dark blue
  onSurface: "#f1f5f9", // Light gray
  onPrimary: "#ffffff", // White
  success: "#10b981", // Green
  warning: "#f59e0b", // Amber
  error: "#ef4444", // Red
  border: "#334155", // Gray border
  muted: "#64748b", // Muted gray
};

// Typography
export const OffnetTypography = {
  h1: {
    fontSize: 32,
    fontWeight: "700" as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 24,
    fontWeight: "600" as const,
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: "600" as const,
    lineHeight: 28,
  },
  body: {
    fontSize: 16,
    fontWeight: "400" as const,
    lineHeight: 24,
  },
  caption: {
    fontSize: 14,
    fontWeight: "400" as const,
    lineHeight: 20,
  },
  small: {
    fontSize: 12,
    fontWeight: "400" as const,
    lineHeight: 16,
  },
};

// Spacing
export const OffnetSpacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Card Component
interface OffnetCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  onPress?: () => void;
}

export const OffnetCard: React.FC<OffnetCardProps> = ({
  children,
  style,
  onPress,
}) => {
  const CardComponent = onPress ? TouchableOpacity : View;

  return (
    <CardComponent
      onPress={onPress}
      style={[styles.card, style]}
      activeOpacity={onPress ? 0.7 : 1}
    >
      {children}
    </CardComponent>
  );
};

// Button Component
interface OffnetButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "small" | "medium" | "large";
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
}

export const OffnetButton: React.FC<OffnetButtonProps> = ({
  title,
  onPress,
  variant = "primary",
  size = "medium",
  disabled = false,
  loading = false,
  icon,
  style,
}) => {
  const getButtonStyle = () => {
    const baseStyle = [styles.button, styles[`button_${size}`]];

    if (disabled || loading) {
      baseStyle.push(styles.button_disabled);
    } else {
      baseStyle.push(styles[`button_${variant}`]);
    }

    return baseStyle;
  };

  const getTextStyle = () => {
    const baseStyle = [styles.buttonText, styles[`buttonText_${size}`]];

    if (variant === "outline" || variant === "ghost") {
      baseStyle.push(styles.buttonText_outline);
    } else {
      baseStyle.push(styles.buttonText_solid);
    }

    return baseStyle;
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[...getButtonStyle(), style]}
      activeOpacity={0.7}
    >
      <View style={styles.buttonContent}>
        {icon && <View style={styles.buttonIcon}>{icon}</View>}
        <Text style={getTextStyle()}>{loading ? "Loading..." : title}</Text>
      </View>
    </TouchableOpacity>
  );
};

// Text Component
interface OffnetTextProps {
  children: React.ReactNode;
  variant?: "h1" | "h2" | "h3" | "body" | "caption" | "small";
  color?: keyof typeof OffnetColors;
  style?: TextStyle;
}

export const OffnetText: React.FC<OffnetTextProps> = ({
  children,
  variant = "body",
  color = "onSurface",
  style,
}) => {
  return (
    <Text
      style={[OffnetTypography[variant], { color: OffnetColors[color] }, style]}
    >
      {children}
    </Text>
  );
};

// Input Component
interface OffnetInputProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  multiline?: boolean;
  numberOfLines?: number;
  editable?: boolean;
  style?: ViewStyle;
}

export const OffnetInput: React.FC<OffnetInputProps> = ({
  value,
  onChangeText,
  placeholder,
  multiline = false,
  numberOfLines = 1,
  editable = true,
  style,
}) => {
  return (
    <TextInput
      value={value}
      onChangeText={onChangeText}
      placeholder={placeholder}
      placeholderTextColor={OffnetColors.muted}
      multiline={multiline}
      numberOfLines={numberOfLines}
      editable={editable}
      style={[styles.input, style]}
    />
  );
};

const styles = StyleSheet.create({
  // Card styles
  card: {
    backgroundColor: OffnetColors.surface,
    borderRadius: 12,
    padding: OffnetSpacing.md,
    borderWidth: 1,
    borderColor: OffnetColors.border,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },

  // Button styles
  button: {
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
  },
  button_small: {
    paddingVertical: OffnetSpacing.xs,
    paddingHorizontal: OffnetSpacing.sm,
    minHeight: 32,
  },
  button_medium: {
    paddingVertical: OffnetSpacing.sm,
    paddingHorizontal: OffnetSpacing.md,
    minHeight: 44,
  },
  button_large: {
    paddingVertical: OffnetSpacing.md,
    paddingHorizontal: OffnetSpacing.lg,
    minHeight: 56,
  },
  button_primary: {
    backgroundColor: OffnetColors.primary,
  },
  button_secondary: {
    backgroundColor: OffnetColors.secondary,
  },
  button_outline: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: OffnetColors.primary,
  },
  button_ghost: {
    backgroundColor: "transparent",
  },
  button_disabled: {
    backgroundColor: OffnetColors.muted,
    opacity: 0.5,
  },
  buttonContent: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  buttonIcon: {
    marginRight: OffnetSpacing.xs,
  },
  buttonText: {
    fontWeight: "600",
  },
  buttonText_small: {
    fontSize: 14,
  },
  buttonText_medium: {
    fontSize: 16,
  },
  buttonText_large: {
    fontSize: 18,
  },
  buttonText_solid: {
    color: OffnetColors.onPrimary,
  },
  buttonText_outline: {
    color: OffnetColors.primary,
  },

  // Input styles
  input: {
    backgroundColor: OffnetColors.surface,
    borderWidth: 1,
    borderColor: OffnetColors.border,
    borderRadius: 8,
    paddingVertical: OffnetSpacing.sm,
    paddingHorizontal: OffnetSpacing.md,
    color: OffnetColors.onSurface,
    fontSize: 16,
    minHeight: 44,
  },
});
