import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet } from 'react-native';
import useThemeStore from '../../store/themeStore';

export default function KButton({ title, onPress, variant = 'primary', loading = false, disabled = false, style }) {
  const { colors } = useThemeStore();

  const bgColor = variant === 'primary' ? colors.primary
    : variant === 'success' ? colors.success
    : variant === 'danger' ? colors.error
    : 'transparent';

  const borderColor = variant === 'secondary' ? colors.primary : 'transparent';
  const textColor = variant === 'secondary' ? colors.primary : '#FFFFFF';

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.btn,
        { backgroundColor: bgColor, borderColor, opacity: disabled ? 0.5 : 1 },
        style,
      ]}
    >
      {loading
        ? <ActivityIndicator color="#FFFFFF" size="small" />
        : <Text style={[styles.text, { color: textColor }]}>{title}</Text>
      }
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    height: 52,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    paddingHorizontal: 20,
  },
  text: { fontSize: 16, fontWeight: '600' },
});
